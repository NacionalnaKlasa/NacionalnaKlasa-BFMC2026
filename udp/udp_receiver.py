import socket
import struct
import cv2
import numpy as np
import time
from udp.udp import UDP
from udp.config import UDP_PORT, MAX_CHUNK_SIZE
from udp.types import DATA_TYPES

class UDP_Receiver(UDP):
    def __init__(self, address:str = "", port:int = UDP_PORT):
        super().__init__()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((address, port))
        
        # Timeout za recvfrom
        self.socket.settimeout(0.02) # 20 milisekundi
        
        self._assembly_buffer = {}
        self.current_msg_id = -1
        self.expected_type = None
        self.cached_chunk_0 = None
        
        # TIMEOUT MEHANIZAM - ako nema novog chunk-a u X vremenske, preskočи
        self.last_chunk_time = time.time()
        self.chunk_timeout = 0.2  # 200ms - timeout za čekanje chunk-ova
        
        # Slot za poslednju primljenu poruku
        self._last_received_data = None
        self._last_received_type = None
        
    def tick(self):
        """
        Ovu metodu korisnik poziva unutar svoje while petlje.
        """
        try:
            # Čitamo jedan paket iz bafera
            result = super().recv(MAX_CHUNK_SIZE + 256)
            if result is None or result[0] is None:
                # Ako nema paketa na mreži, proveri timeout
                if time.time() - self.last_chunk_time > self.chunk_timeout:
                    if self.current_msg_id != -1 and self.current_msg_id in self._assembly_buffer:
                        # Timeout - odustani od ove nedovršene poruke
                        del self._assembly_buffer[self.current_msg_id]
                        self.current_msg_id = -1
                return
                
            raw_packet, addr, msg_id = result
            self.last_chunk_time = time.time()  # Update vremenske za timeout
            self.process_packet(raw_packet, msg_id)
            
        except socket.timeout:
            # Timeout za recvfrom - nema paketa na mreži
            # Proveri timeout za trenutnu poruku
            if time.time() - self.last_chunk_time > self.chunk_timeout:
                if self.current_msg_id != -1 and self.current_msg_id in self._assembly_buffer:
                    # Timeout - odustani od ove poruke
                    del self._assembly_buffer[self.current_msg_id]
                    self.current_msg_id = -1
        except BlockingIOError:
            pass

    def process_packet(self, packet: bytes, msg_id: int):
        try:
            parts = packet.rsplit(b";;", 3)
            if len(parts) < 4: return

            raw_data = parts[0]
            data_type_val = int.from_bytes(parts[1], byteorder='big', signed=True)
            chunk_idx     = int.from_bytes(parts[2], byteorder='big')
            total_chunks  = int.from_bytes(parts[3], byteorder='big')
            
            # VAŽNO: Sender šalje (total_chunks - 1), tako da dodajemo 1
            actual_total_chunks = total_chunks + 1 if total_chunks > 0 else 1

            data_type = DATA_TYPES(data_type_val)

            if total_chunks == 0:
                # Single chunk poruka
                self.handle_completed_message(raw_data, data_type)
            else:
                # Multi-chunk poruka
                self._assemble_multi_chunk(raw_data, data_type, chunk_idx, actual_total_chunks, msg_id)

        except Exception as e:
            pass # Ignorišemo greške pri parsiranju u produkciji da ne spamujemo konzolu

    def _assemble_multi_chunk(self, data, data_type, idx, total, msg_id):
        """
        Sklapa multi-chunk poruku. 'total' je već actual_total_chunks (tj. pravi broj chunk-ova)
        """
        # 1. AKO STIGNE NOVI ID PORUKE:
        if msg_id > self.current_msg_id:
            # Forsiramo sklapanje PRETHODNE poruke (ako imamo nešto od nje)
            if self.current_msg_id != -1 and self.current_msg_id in self._assembly_buffer:
                self._force_assemble(self.current_msg_id)
            
            # Resetujemo stanje za NOVU poruku
            self.current_msg_id = msg_id
            self.expected_type = data_type
            self._assembly_buffer[msg_id] = { "total": total, "chunks": {} }

        # 2. PUNIMO BAFER TRENUTNE PORUKE (ignorišemo stare zaostale pakete)
        if msg_id == self.current_msg_id:
            self._assembly_buffer[msg_id]["chunks"][idx] = data
            
            # 3. AKO SMO IMALI SREĆE DA STIGNU SVI PAKETI PRE SLEDEĆEG ID-a:
            if len(self._assembly_buffer[msg_id]["chunks"]) == self._assembly_buffer[msg_id]["total"]:
                self._force_assemble(msg_id)

    def _force_assemble(self, msg_id):
        if msg_id not in self._assembly_buffer:
            return
            
        buffer_info = self._assembly_buffer[msg_id]
        total = buffer_info["total"]
        chunks_dict = buffer_info["chunks"]
        
        # Provera da li su svi chunk-ovi stigli
        if len(chunks_dict) < total:
            print(f"[WARN] Nedostaju chunk-ovi za msg_id {msg_id}: {len(chunks_dict)}/{total}")
            del self._assembly_buffer[msg_id]
            return
        
        # 1. Provera Header-a (Chunk 0)
        if 0 in chunks_dict:
            self.cached_chunk_0 = chunks_dict[0]
        elif self.cached_chunk_0 is not None:
            chunks_dict[0] = self.cached_chunk_0
        else:
            print(f"[WARN] Nema chunk 0 za msg_id {msg_id}")
            del self._assembly_buffer[msg_id]
            return

        # 2. LINEARNO SKLAPANJE
        ordered_chunks = []
        for i in range(total):
            if i in chunks_dict:
                ordered_chunks.append(chunks_dict[i])
            else:
                print(f"[WARN] Fali chunk {i}/{total} za msg_id {msg_id}")
                # Ako fali chunk, ne sklapaj - JPEG će biti oštećen
                del self._assembly_buffer[msg_id]
                return
                
        full_data = b"".join(ordered_chunks)
        self.handle_completed_message(full_data, self.expected_type)
        del self._assembly_buffer[msg_id]

    def handle_completed_message(self, raw_data: bytes, data_type: DATA_TYPES):
        result = None
        if data_type == DATA_TYPES.IMAGE:
            if not isinstance(raw_data, (bytes, bytearray)):
                return None
            nparr = np.frombuffer(raw_data, np.uint8)
            if nparr.size == 0:
                return None
            result = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif data_type == DATA_TYPES.BOOLEAN:
            result = struct.unpack('?', raw_data)[0]
        elif data_type == DATA_TYPES.INTEGER:
            result = struct.unpack('>i', raw_data)[0]
        elif data_type == DATA_TYPES.FLOAT:
            result = struct.unpack('>d', raw_data)[0]
        elif data_type == DATA_TYPES.STRING:
            result = raw_data.decode('utf-8')
        
        # Spremi poslednju poruku
        self._last_received_data = result
        self._last_received_type = data_type
    
    def recv(self):
        """
        Procesira jedan paket i vraća (data, data_type) ako je poruka kompletna,
        ili (None, None) ako nema nove poruke.
        
        Korisnik poziva ovu metodu u while petlji.
        """
        self.tick()
        
        # Ako imamo novu poruku, vrati je i resetuj slot
        if self._last_received_data is not None:
            data = self._last_received_data
            data_type = self._last_received_type
            self._last_received_data = None
            self._last_received_type = None
            return (data, data_type)
        
        return (None, None)
UDP_PORT:int = 9990
UDP_BROADCAST_ADDRESS:str = "255.255.255.255"

# Manji chunk = manja šansa za gubitak (UDP MTU je ~1500 bajtova, ali imamo overhead)
MAX_CHUNK_SIZE = 1024  # Bio 500, sada 1024 za bolju balansiranost0
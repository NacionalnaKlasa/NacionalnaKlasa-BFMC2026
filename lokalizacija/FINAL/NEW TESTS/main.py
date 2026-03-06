import pygame
import math
import threading
from tcpLib import PCServer
from localization import LocalizationModule
from PC_withTCP import BoschCar, server_init, run
TRACK_IMAGE_PATH = r".\NEW TESTS\staza_smanjena.png"
GRAPH_PATH = r".\NEW TESTS\staza_graf.graphml"
TIMEOUT_THRESHOLD = 0.5

auto = BoschCar()
server, server_thread = server_init(port=65432)

run(auto, TRACK_IMAGE_PATH, GRAPH_PATH, TIMEOUT_THRESHOLD, server, server_thread)




import Logger.Color as Color
import sys

class Logger_Base:

	LOGGER_BASE_INITIALIZED = False

	LOG_LEVELS = {
		0: "INFO",
		1: "WARNING",
		2: "ERROR"
	}

	REV_LOG_LEVELS = {}

	INFO_COLOR = Color.RESET
	WARNING_COLOR = Color.YELLOW
	ERROR_COLOR = Color.RED

	Log_file_path = "./logs/"
	Log_file_name_prefix = "logger-"
	Log_file_name_sufix = ".txt"
	Log_file_name = None
	Log_file_descriptor = None

	Descriptors = [sys.stdout]

	@staticmethod
	def __init__():
		if not Logger_Base.LOGGER_BASE_INITIALIZED:
			Logger_Base.LOGGER_BASE_INITIALIZED = True
			Logger_Base.REV_LOG_LEVELS = {v: k for k, v in Logger_Base.LOG_LEVELS.items()}

	@staticmethod
	def log(prefix, msg, sufix):
		for desc in Logger_Base.Descriptors:
			if desc != sys.stdout:
				desc.write(msg + "\n")
			else:
				desc.write(prefix + msg + sufix + "\n")

	@staticmethod
	def loge(msg):
		Logger_Base.log(Logger_Base.ERROR_COLOR, "[ERROR] " + msg, Color.RESET)

	@staticmethod
	def logw(msg):
		Logger_Base.log(Logger_Base.WARNING_COLOR, "[WARNING] " + msg, Color.RESET)

	@staticmethod
	def logi(msg):
		Logger_Base.log(Logger_Base.INFO_COLOR, "[INFO] " + msg, Color.RESET)
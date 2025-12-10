import Logger.Color as Color

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

	@staticmethod
	def __init__():
		if not Logger_Base.LOGGER_BASE_INITIALIZED:
			Logger_Base.LOGGER_BASE_INITIALIZED = True
			Logger_Base.REV_LOG_LEVELS = {v: k for k, v in Logger_Base.LOG_LEVELS.items()}

	@staticmethod
	def loge(msg):
		print(Logger_Base.ERROR_COLOR + "[ERROR] " + msg + Color.RESET)

	@staticmethod
	def logw(msg):
		print(Logger_Base.WARNING_COLOR + "[WARNING] " + msg + Color.RESET)

	@staticmethod
	def logi(msg):
		print(Logger_Base.INFO_COLOR + "[INFO] " + msg + Color.RESET)
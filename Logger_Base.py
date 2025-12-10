
class Logger_Base:

	LOGGER_BASE_INITIALIZED = False

	LOG_LEVELS = {
		0: "INFO",
		1: "WARNING",
		2: "ERROR"
	}

	REV_LOG_LEVELS = {}

	@staticmethod
	def __init__():
		if not Logger_Base.LOGGER_BASE_INITIALIZED:
			Logger_Base.LOGGER_BASE_INITIALIZED = True
			Logger_Base.REV_LOG_LEVELS = {v: k for k, v in Logger_Base.LOG_LEVELS.items()}

	@staticmethod
	def loge(msg):
		print("[ERROR] " + msg)

	@staticmethod
	def logw(msg):
		print("[WARNING] " + msg)

	@staticmethod
	def logi(msg):
		print("[INFO] " + msg)
import threading

import os
import sys
from datetime import datetime
from pathlib import Path

from Logger.Logger_Base import Logger_Base
from Logger.Queue import Queue

class Logger(Logger_Base):

	QUEUE_INFO = Queue()
	QUEUE_WARNING = Queue()
	QUEUE_ERROR = Queue()

	Logger_Thread = None
	Logger_Thread_Stop = True

	__Logger_condition = threading.Condition()

	@staticmethod
	def __init__():
		if Logger.Logger_Thread == None:
			Logger_Base().__init__()
			Logger.Logger_Thread = threading.Thread(target=Logger.loop) 

			Logger.Logger_Thread_Stop = False
			Logger.Logger_Thread.start()

			if os.path.isdir(Logger_Base.Logger_Base_log_file_path):
				Logger.logi(f"The directory '{Logger_Base.Logger_Base_log_file_path}' exists.")
			else:
				Logger.logw(f"The directory '{Logger_Base.Logger_Base_log_file_path}' does not exist.")
				Logger.logi("Creating directory \"logs\"")
				os.makedirs(Path(Logger_Base.Logger_Base_log_file_path), exist_ok=True) 

			Logger_Base.Logger_Base_log_file_name = Logger_Base.Logger_Base_log_file_path + Logger_Base.Logger_Base_log_file_name_prefix + datetime.now().strftime("%Y-%m-%d_%H-%M-%S" + Logger_Base.Logger_Base_log_file_name_sufix)
			Logger_Base.Logger_Base_log_file = open(Logger_Base.Logger_Base_log_file_name, "wt")
			
			Logger_Base.Logger_descriptors.append(Logger_Base.Logger_Base_log_file)

	@staticmethod
	def stop():
		if Logger.Logger_Thread is not None:
			Logger.Logger_Thread_Stop = True
			with Logger.__Logger_condition:
				Logger.__Logger_condition.notify_all()
			Logger.Logger_Thread.join()

			Logger_Base.Logger_Base_log_file.close()			

	@staticmethod
	def loop():
		with Logger.__Logger_condition:
			while Logger.Logger_Thread_Stop == False:
				
				if len(Logger.QUEUE_ERROR):
					Logger_Base.loge(Logger.QUEUE_ERROR.pop())
					continue

				if len(Logger.QUEUE_WARNING):
					Logger_Base.logw(Logger.QUEUE_WARNING.pop())
					continue

				if len(Logger.QUEUE_INFO):
					Logger_Base.logi(Logger.QUEUE_INFO.pop())
					continue
				
				if len(Logger.QUEUE_INFO) == 0 and \
						len(Logger.QUEUE_WARNING) == 0 and \
						len(Logger.QUEUE_ERROR) == 0:
					
					Logger.__Logger_condition.wait(timeout=3)

	@staticmethod
	def __log(msg, log_level):
		ret_val = False
		if log_level == 0:
			ret_val = Logger.logi(msg)

		elif log_level == 1:
			ret_val = Logger.logw(msg)

		elif log_level == 2:
			ret_val = Logger.loge(msg)

		else:
			ret_val = False
		
		return ret_val
	
	@staticmethod
	def log(msg, log_level):
		if isinstance(log_level, bool):
			return False

		if not isinstance(log_level, (int, str)):
			return False

		if isinstance(log_level, str):
			log_level = Logger.REV_LOG_LEVELS.get(log_level)

		if log_level is None or log_level not in Logger.LOG_LEVELS:
			return False
		
		return Logger.__log(msg, log_level)
		
	@staticmethod
	def logi(msg):
		ret_val = Logger.QUEUE_INFO.append(msg)
		with Logger.__Logger_condition:
			Logger.__Logger_condition.notify_all()

		return ret_val

	@staticmethod
	def logw(msg):
		ret_val = Logger.QUEUE_WARNING.append(msg)
		with Logger.__Logger_condition:
			Logger.__Logger_condition.notify_all()

		return ret_val

	@staticmethod
	def loge(msg):
		ret_val = Logger.QUEUE_ERROR.append(msg)
		with Logger.__Logger_condition:
			Logger.__Logger_condition.notify_all()

		return ret_val

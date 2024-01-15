import os, sys
import re
import time
import logging
from typing import Final
from logging.handlers import TimedRotatingFileHandler
    
class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False):
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc)
        self.suffix_re = re.compile(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}[.]log$")

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dir_name, base_name = os.path.split(self.baseFilename)
        file_name, ext_name = base_name.split('.')
        dfn = self.rotation_filename(os.path.join(dir_name, '.'.join([file_name, time.strftime(self.suffix, timeTuple), ext_name])))
        if os.path.exists(dfn):
            os.remove(dfn)
        self.rotate(self.baseFilename, dfn)
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        if not self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow: 
                    addend = -3600
                else:
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt

    def getFilesToDelete(self):
        dir_name, base_name = os.path.split(self.baseFilename)
        file_names = os.listdir(dir_name)
        if not file_names:
            return []
        files_to_delete = []
        for file_name in file_names:
            if self.suffix_re.search(file_name):
                files_to_delete.append(file_name)
        if len(files_to_delete) <= self.backupCount or not files_to_delete:
            return []
        files_to_delete = sorted(files_to_delete)
        for i in range(self.backupCount):
            files_to_delete.pop()
        return [os.path.join(dir_name, file_name) for file_name in files_to_delete]

class JHLogger:
    LOG_DIR: Final = './logs'
    FILE_NAME: Final = os.path.join(LOG_DIR, 'LOG.log')
    logger = logging.getLogger('JHLogger')
    logger.setLevel(logging.DEBUG)
    
    @staticmethod
    def getLogger(file_interval: int, backup_num: int, s_level: int) -> None:
        """
        CRITICAL = 5
        ERROR = 4
        WARNING = 3
        INFO = 2
        DEBUG = 1
        """
        ### Check Logs Directory
        JHLogger.checkLogPath()
        ### Set Handler
        file_handler = CustomTimedRotatingFileHandler(
            JHLogger.FILE_NAME, 
            when='M', 
            interval=file_interval, 
            backupCount=backup_num,
            )
        file_handler.suffix = "%Y-%m-%d_%H-%M-%S"
        file_handler.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler()
        if s_level == 5:
            stream_level = logging.CRITICAL
        elif s_level == 4:
            stream_level = logging.ERROR
        elif s_level == 3:
            stream_level = logging.WARNING
        elif s_level == 2:
            stream_level = logging.INFO
        else:
            stream_level = logging.DEBUG
        stream_handler.setLevel(stream_level)
        ### Add Formatter
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] - %(message)s')
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)
        ### Add Handler
        JHLogger.logger.addHandler(file_handler)
        JHLogger.logger.addHandler(stream_handler)
        return JHLogger.logger
        
    @staticmethod
    def checkLogPath() -> None:
        if not os.path.exists(JHLogger.LOG_DIR):
            os.mkdir(JHLogger.LOG_DIR)
            
    @staticmethod
    def getLevel() -> int:
        level = 5
        try:
            input_value = sys.argv[1]
            if input_value == 'v':
                level = 1
            elif input_value == 'e':
                level = 4
        except IndexError:
            pass
        return level
            

if __name__ ==  '__main__':
    logger = JHLogger.getLogger(1, 3, JHLogger.getLevel())
    
    while True:
        try:
            logger.debug('Debug 메시지')
            logger.info('Info 메시지')
            logger.warning('Warning 메시지')
            logger.error('Error 메시지')
            logger.critical('Critical 메시지')
            time.sleep(1)
        except KeyboardInterrupt:
            break
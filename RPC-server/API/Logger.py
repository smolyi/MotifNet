__author__ = 'Ilan Smoly'

import logging

class Logger:
    """
    This class will provide the interface for a logger.

    Author
    ------
        Ilan Smoly

    Parameters
    ----------
        name : String
            The name of this logger.
        log_file_path : String
            The name of the log file.
        lock : Lock
            A lock to synchronize multi threaded apps.
        level : Int
            The logging level.

    """

    def __init__(self, name, log_file_path, lock = None, level = None): 
        self.lock = lock

        #create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        #create file handler and set level to debug
        fh = logging.FileHandler(log_file_path)
        fh.setLevel(logging.DEBUG)
        #create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        #create formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        #add formatter to ch
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        #add handlers to logger
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        #self.logger.removeHandler(sys.stderr)
        if level:self.setLogLevel(level)

    def __getstate__(self):
        _dict = {}
        _dict["fh"] = None
        return dict

    def __setstate__(self,_dict):
        _dict["fh"] = None
        self.__dict__.update(_dict)   # update attributes

    def setLogLevel(self, level):
        """
        This method will set the logging level.

        Parameters
        ----------
            level : int
                The logging level.
        """
        if level == 1:
            self.logger.setLevel(logging.DEBUG)
        elif level == 2:
            self.logger.setLevel(logging.INFO)
        elif level == 3:
            self.logger.setLevel(logging.WARNING)
        elif level == 4:
            self.logger.setLevel(logging.ERROR)
        elif level == 5:
            self.logger.setLevel(logging.CRITICAL)

    def log(self, level, msg):
        """
        This method will add a log message.

        Parameters
        ----------
            level : int
                The level for this message.
            msg : String
                The message.
        """
        if self.lock: self.lock.acquire()
        if level == 1:
            self.logger.debug(msg)
        elif level == 2:
            self.logger.info(msg)
        elif level == 3:
            self.logger.warning(msg)
        elif level == 4:
            self.logger.error(msg)
        elif level == 5:
            self.logger.critical(msg)
        if self.lock: self.lock.release()


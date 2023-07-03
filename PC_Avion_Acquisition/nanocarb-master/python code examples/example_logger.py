# /usr/bin/env python3
# -*- Coding: UTF-8 -*-


import logging
import pathlib

import os
import sys

# logmodule : used to get well formatted UDP messages
# require installation of github.com/rhawiz/python-udp-handler
# pip install git+https://github.com/rhawiz/python-udp-handler.git
from logmodule import get_logger

main_logger = None

# Custom Format introducing line header and color into log :)
class ConsoleFormatter(logging.Formatter):

    green = "\x1b[32;21m"
    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)s] %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
    
# Custom Format introducing line header only 
class FileFormatter(logging.Formatter):

    def format(self, record):
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)s] %(message)s")
        return formatter.format(record)
    

# main class
def setup_logger():
    """
    Sets up a logger object
    :param logger_name: Name of the logger
    :return:
    """
    global main_logger
    
    if main_logger == None :
        main_logger = get_logger("./logger.conf")

        main_logger.setLevel(logging.DEBUG)

        # Console handler : outputs to the console
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(ConsoleFormatter())

        # File handler : outputs to a log file
        fh = logging.FileHandler('./cru_calendar.log')
        fh.setLevel(logging.DEBUG)
        fh_formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)s] %(message)s')
        fh.setFormatter(FileFormatter())

        # Add the handlers to the logger
        main_logger.addHandler(fh)
        main_logger.addHandler(ch)

    return main_logger

import logging
import os

loggers = {}

def get_loglevel(loglevel: str):
    match loglevel:
        case "DEBUG":
            loglevel = logging.DEBUG
        case "INFO":
            loglevel = logging.INFO
        case "WARNING":
            loglevel = logging.WARNING
        case "ERROR":
            loglevel = logging.ERROR
        case "CRITICAL":
            loglevel = logging.CRITICAL
        case _:
            loglevel = logging.INFO

    return loglevel


def init_logger(name: str) -> logging.Logger:
    if loggers.get(name):
        return loggers[name]
    
    logger = logging.getLogger(name)
    loglevel = get_loglevel(os.environ.get("LOGLEVEL"))

    formatter = logging.Formatter(
        fmt=f"({name}) %(asctime)s %(module)s %(levelname)s: %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )
    
    for handler in logger.handlers:
        logger.removeHandler(handler)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(f"{name}.log")
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    logger.setLevel(loglevel)
    
    loggers[name] = logger

    return logger

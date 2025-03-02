import logging
import os

loggers = {}

logging_dir = str(os.environ.get("LOG_DIR", "logs"))
is_log_to_file = bool(os.environ.get("LOG_TO_FILE", "false").lower() == "true")

is_logging_to_file_configured = False


def configure_logging_to_file():
    config_value = os.environ.get("LOG_TO_FILE")
    if is_log_to_file:
        print(f"Logging to file is enabled" f"(LOG_TO_FILE is set to '{config_value}')")
        if logging_dir:
            print(f"Logging files directory: '{logging_dir}'")
            if not os.path.exists(logging_dir):
                os.makedirs(logging_dir, exist_ok=True)
    else:
        print(f"Logging to file is disabled" f"(LOG_TO_FILE is set to '{config_value}')")



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
    global is_logging_to_file_configured
    if not is_logging_to_file_configured:
        configure_logging_to_file()
        is_logging_to_file_configured = True

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
    logger.addHandler(stream_handler)

    if is_log_to_file:
        file_handler = logging.FileHandler(f"{logging_dir}/{name}.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.setLevel(loglevel)

    loggers[name] = logger

    return logger

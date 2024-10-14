import logging

class LoggingFormatter(logging.Formatter):
    def __init__(self) -> None:
        super().__init__()

        self.colours = {
            "WHITE": "\x1b[15m",
            "BLACK": "\x1b[30m",
            "RED": "\x1b[31m",
            "GREEN": "\x1b[32m",
            "YELLOW": "\x1b[33m",
            "BLUE": "\x1b[34m",
            "PURPLE": "\x1b[35m",
            "GRAY": "\x1b[38m",
        }

        self.styles = {
            "RESET": "\x1b[0m",
            "BOLD": "\x1b[1m",
        }

        self.levels = {
            logging.DEBUG: self.colours["GRAY"] + self.styles["BOLD"],
            logging.INFO: self.colours["BLUE"] + self.styles["BOLD"],
            logging.WARNING: self.colours["YELLOW"] + self.styles["BOLD"],
            logging.ERROR: self.colours["RED"],
            logging.CRITICAL: self.colours["RED"] + self.styles["BOLD"],
        }

    def format(self, record) -> str:
        message = "[GRAY][BOLD]{asctime}[RESET] [LEVEL_COLOUR]{levelname:<8}[RESET] [PURPLE][BOLD]{name}[RESET] [WHITE]{message}"
        for name, after in (self.colours | self.styles).items():
            message = message.replace(f"[{name}]", after)
        message = message.replace("[LEVEL_COLOUR]", self.levels[record.levelno])
        formatter = logging.Formatter(message, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)

class BotLogger:
    logger = logging.getLogger("dnd_spawner_bot")
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(LoggingFormatter())

    logger.addHandler(console_handler)

    @classmethod
    def get_logger(cls) -> logging.Logger:
        return cls.logger

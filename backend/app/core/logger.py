import logging
import sys
from typing import Optional
from colorama import Fore, Style, init

# init colorama once
init(autoreset=True)


class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.INFO: Fore.MAGENTA,      # purple
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT,
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, "")

        # color level name
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"

        # color message
        record.msg = f"{color}{record.getMessage()}{Style.RESET_ALL}"
        record.args = ()  # prevent double formatting

        return super().format(record)



class AppLogger:
    _configured = False

    @classmethod
    def configure(
        cls,
        level: int = logging.INFO,
        log_file: Optional[str] = None,
    ) -> None:
        if cls._configured:
            return

        handlers = []

        # Console
        console = logging.StreamHandler(sys.stdout)
        handlers.append(console)

        # Optional file (no colors)
        if log_file:
            handlers.append(logging.FileHandler(log_file))

        formatter = ColorFormatter(
            "%(levelname)-8s:     %(message)s",
        )

        for h in handlers:
            h.setFormatter(formatter)

        logging.basicConfig(
            level=level,
            handlers=handlers,
            force=True,
        )

        cls._configured = True

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)

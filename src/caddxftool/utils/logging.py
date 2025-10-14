from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    use_rich: bool = True,
) -> None:
    """
    配置根日志记录器。
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    handlers: list[logging.Handler] = []

    if use_rich:
        try:
            from rich.logging import RichHandler

            handlers.append(
                RichHandler(
                    rich_tracebacks=True,
                    show_path=False,
                    markup=True,
                )
            )
        except ImportError:
            handlers.append(logging.StreamHandler())
    else:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        handlers=handlers,
        force=True,
    )

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
            )
        )
        logging.getLogger().addHandler(file_handler)

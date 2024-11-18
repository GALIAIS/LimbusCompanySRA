import sys
import traceback
import uuid
from datetime import datetime
from pathlib import Path

from loguru import logger


class LoggerConfig:
    """日志配置类"""

    def __init__(self):
        if getattr(sys, 'frozen', False):
            self.file_dir = Path(sys.argv[0]).resolve().parent.parent
        else:
            self.file_dir = Path(__file__).resolve().parent.parent

        self.log_dirs = {
            "log": self.file_dir / 'log',
            "error": self.file_dir / 'log' / 'error',
            "structured": self.file_dir / 'log' / 'structured'
        }
        for path in self.log_dirs.values():
            path.mkdir(parents=True, exist_ok=True)

        self.configure_logger()

    def configure_logger(self):
        """配置 loguru 日志"""

        logger.remove()

        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<cyan>PID:{process}</cyan> | <cyan>Thread:{thread.name}</cyan> | "
            "<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )

        timestamp = datetime.now().strftime('%Y-%m-%d')

        self.add_file_logger("log", log_format, timestamp, "DEBUG", "00:00", "7 days")
        self.add_file_logger("error", log_format, timestamp, "WARNING", "10 MB", "30 days", "error")
        self.add_file_logger("structured", log_format, timestamp, "DEBUG", "5 MB", "15 days", "structured", True)

        logger.add(sys.stdout, format=log_format, level="TRACE", colorize=True, enqueue=True)

        self.configure_log_levels()

        sys.excepthook = self.log_exception

    def add_file_logger(self, log_type, log_format, timestamp, level, rotation, retention, sub_dir=None,
                        serialize=False):
        """为日志文件添加配置"""
        log_dir = self.log_dirs[log_type] if not sub_dir else self.log_dirs[sub_dir]
        logger.add(
            log_dir / f"{log_type}_{timestamp}.log",
            rotation=rotation,
            retention=retention,
            level=level,
            format=log_format,
            serialize=serialize,
            enqueue=True
        )

    def configure_log_levels(self):
        """配置日志级别和图标"""
        log_levels = {
            "TRACE": {"color": "<light-blue>", "icon": "🔍"},
            "DEBUG": {"color": "<blue>", "icon": "🐞"},
            "INFO": {"color": "<green>", "icon": "📄"},
            "SUCCESS": {"color": "<bold><green>", "icon": "✅"},
            "WARNING": {"color": "<yellow>", "icon": "⚠️"},
            "ERROR": {"color": "<red>", "icon": "❌"},
            "CRITICAL": {"color": "<bold><magenta>", "icon": "‼️"}
        }

        for level, config in log_levels.items():
            logger.level(level, color=config["color"], icon=config["icon"])

    def log_exception(self, exc_type, exc_value, exc_traceback):
        """异常捕获，输出详细的错误日志"""
        if not issubclass(exc_type, KeyboardInterrupt):
            tb_str = ''.join(traceback.format_tb(exc_traceback))
            logger.error(f"Uncaught exception: {exc_type.__name__}: {exc_value}\n{tb_str}")

    def add_request_id(self):
        """为每个日志记录添加唯一的请求ID"""
        request_id = str(uuid.uuid4())
        logger.contextualize(request_id=request_id)

    def log_with_request_id(self, message, level="INFO"):
        """添加请求 ID 后的日志记录方法"""
        self.add_request_id()
        logger.log(level, message)

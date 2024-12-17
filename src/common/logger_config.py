import sys
import traceback
import uuid
from datetime import datetime
from pathlib import Path
from loguru import logger
from filelock import FileLock


class LoggerConfig:
    """增强版日志配置类"""

    def __init__(self):
        if getattr(sys, 'frozen', False):
            self.file_dir = Path(sys.argv[0]).resolve().parent
        else:
            self.file_dir = Path(__file__).resolve().parent.parent

        self.log_dirs = {
            "log": self.file_dir / 'log',
            "error": self.file_dir / 'log' / 'error',
            "structured": self.file_dir / 'log' / 'structured',
            "json": self.file_dir / 'log' / 'json'
        }
        for path in self.log_dirs.values():
            path.mkdir(parents=True, exist_ok=True)

        self.log_lock = FileLock(self.file_dir / 'log.lock')
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

        with self.log_lock:
            # 添加多种日志文件
            self.add_file_logger("log", log_format, timestamp, "DEBUG", "1 day", "7 days", compression="zip")
            self.add_file_logger("error", log_format, timestamp, "WARNING", "10 MB", "30 days", compression="zip")
            self.add_file_logger("structured", log_format, timestamp, "DEBUG", "5 MB", "15 days", "structured", True)
            self.add_file_logger("json", "{message}", timestamp, "DEBUG", "5 MB", "15 days", serialize=True)

        # 输出到终端
        logger.add(sys.stdout, format=log_format, level="DEBUG", colorize=True, enqueue=True)

        self.configure_log_levels()
        sys.excepthook = self.log_exception

    def add_file_logger(self, log_type, log_format, timestamp, level, rotation, retention, sub_dir=None,
                        serialize=False, compression=None):
        """添加文件日志"""
        log_dir = self.log_dirs[log_type] if not sub_dir else self.log_dirs[sub_dir]
        log_file = log_dir / f"{log_type}_{timestamp}.log"

        try:
            logger.add(
                str(log_file),
                rotation=rotation,
                retention=retention,
                level=level,
                format=log_format,
                serialize=serialize,
                enqueue=True,
                compression=compression
            )
        except Exception as e:
            print(f"Failed to add logger: {e}")

    def configure_log_levels(self):
        """设置日志级别和样式"""
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
        """全局异常捕获"""
        if not issubclass(exc_type, KeyboardInterrupt):
            tb_str = ''.join(traceback.format_tb(exc_traceback))
            logger.critical(f"Uncaught exception: {exc_type.__name__}: {exc_value}\n{tb_str}")

    def add_request_id(self):
        """为每个日志记录添加唯一的请求ID"""
        request_id = str(uuid.uuid4())
        logger.contextualize(request_id=request_id)

    def log_with_request_id(self, message, level="INFO"):
        """添加请求 ID 后的日志记录方法"""
        self.add_request_id()
        logger.log(level, message)

    def change_log_level(self, level):
        """动态修改日志级别"""
        logger.remove()
        logger.add(sys.stdout, level=level, colorize=True, enqueue=True)
        logger.info(f"Log level changed to {level}")

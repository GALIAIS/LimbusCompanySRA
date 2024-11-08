import os
import sys
from pathlib import Path
import threading
import time
from loguru import logger

sys.path.append(str(Path(__file__).resolve().parent))

from src.common.utils import *
from src.script.Mirror_Dungeon import Mirror_Wuthering
from src.common.logger_config import LoggerConfig

mw = Mirror_Wuthering()


def main():
    """主函数"""
    logger_config = LoggerConfig()
    logger.info('日志初始化完成')

    mdw = Mirror_Wuthering()

    img_thread = threading.Thread(target=imgsrc_update_thread, name="IMG更新线程", daemon=True)
    bbox_thread = threading.Thread(target=bboxes_update_thread, name="BBoxes更新线程", daemon=True)
    mirror_wuthering = threading.Thread(target=mdw.run, name="Mirror Dungeon")

    img_thread.start()
    bbox_thread.start()
    mirror_wuthering.start()


if __name__ == "__main__":
    main()
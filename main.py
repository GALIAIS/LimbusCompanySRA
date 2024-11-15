# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path
import threading
import time
from multiprocessing import Process, Event
from PySide6.QtCore import QThread, Signal
from loguru import logger

sys.path.append(str(Path(__file__).resolve().parent))

from src.common.utils import *
from src.script.Mirror_Dungeon import Mirror_Wuthering
from src.common.logger_config import LoggerConfig

logger_config = LoggerConfig()
mw = Mirror_Wuthering()

stop_flag = Event()


def run_automation_task():
    logger.info("任务启动")

    mdw = Mirror_Wuthering()
    img_thread = threading.Thread(target=imgsrc_update_thread, name="IMG更新线程", daemon=True)
    bbox_thread = threading.Thread(target=bboxes_update_thread, name="BBoxes更新线程", daemon=True)
    mirror_wuthering = threading.Thread(target=mdw.run, name="Mirror Dungeon", daemon=True)

    img_thread.start()
    bbox_thread.start()
    mirror_wuthering.start()

    while not stop_flag.is_set():
        time.sleep(0.5)

    logger.info("正在停止任务")
    img_thread.join()
    bbox_thread.join()
    mirror_wuthering.join()
    logger.info("任务已停止")


class AutomationProcessManager:
    def __init__(self):
        self.process = None
        self.restart_attempts = 3
        self.current_attempt = 0

    def start(self):
        if self.process and self.process.is_alive():
            logger.warning("任务已在运行，无法重复启动")
            return

        stop_flag.clear()
        self.process = Process(target=self._run_with_restart)
        self.process.start()
        logger.info("任务已启动")

    def _run_with_restart(self):
        while self.current_attempt < self.restart_attempts:
            try:
                logger.info(f"第 {self.current_attempt + 1} 次尝试运行任务")
                run_automation_task()
                break
            except Exception as e:
                self.current_attempt += 1
                logger.error(f"任务异常退出: {e}")
                if self.current_attempt < self.restart_attempts:
                    logger.info("等待 5 秒后重启任务...")
                    time.sleep(5)
                else:
                    logger.error("任务多次重启失败")
                    break

    def stop(self):
        if self.process and self.process.is_alive():
            stop_flag.set()
            self.process.join(timeout=3)
            if self.process.is_alive():
                self.process.terminate()
                self.process.join()
            logger.info("任务已停止")
        else:
            logger.warning("没有正在运行的任务")
        self.current_attempt = 0

    def is_running(self):
        return self.process and self.process.is_alive()

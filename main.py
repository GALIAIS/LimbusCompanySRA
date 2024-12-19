# -*- coding: utf-8 -*-
import sys
from multiprocessing import Process, Event, Queue
from threading import Thread
import threading
import time
from pathlib import Path

if getattr(sys, 'frozen', False):
    sys.path.append(str(Path(sys.argv[0]).resolve().parent))
else:
    sys.path.append(str(Path(__file__).resolve().parent))

from src.common.actions import run
from src.app.Interface.start_interface import *
from src.common.logger_config import LoggerConfig

logger_config = LoggerConfig()
logging.disable(logging.DEBUG)

stop_flag = Event()


def run_automation_task():
    """自动化任务主入口，启动多个线程并监控其状态"""
    logger.info("任务启动")

    threads = [
        Thread(target=imgsrc_update_thread, name="IMG更新线程", daemon=True),
        Thread(target=bboxes_update_thread, name="BBoxes更新线程", daemon=True),
        Thread(target=run, name="LBCSRA", daemon=True)
    ]

    try:
        for thread in threads:
            try:
                thread.start()
                logger.info(f"{thread.name} 已启动")
            except Exception as e:
                logger.error(f"线程 {thread.name} 启动失败: {e}")
                stop_flag.set()
                raise e

        while not stop_flag.is_set():
            for thread in threads:
                if not thread.is_alive():
                    logger.warning(f"线程 {thread.name} 意外停止")
                    stop_flag.set()
                    break
            time.sleep(1)
    except Exception as e:
        logger.error(f"主循环运行时发生异常: {e}", exc_info=True)
    finally:
        logger.info("正在停止所有线程...")
        stop_flag.set()
        for thread in threads:
            thread.join(timeout=3)
            if thread.is_alive():
                logger.warning(f"线程 {thread.name} 未能正常退出，尝试强制停止")
        logger.info("任务已完全停止")


class AutomationProcessManager:

    def __init__(self):
        self.process = None
        self.restart_attempts = 3
        self.current_attempt = 0

    def start(self):
        """启动任务进程"""
        if self.process and self.process.is_alive():
            logger.warning("任务已在运行，无法重复启动")
            return

        stop_flag.clear()
        self.process = Process(target=self._run_with_restart)
        self.process.start()

        if is_process_running("PaddleOCR-json.exe"):
            kill_process("PaddleOCR-json.exe")
        logger.info("任务已启动")

    def _run_with_restart(self):
        """带有重启机制的任务运行方法"""
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
                    logger.error("任务多次重启失败，停止尝试")
                    break

    def stop(self):
        """停止任务进程"""
        if self.process and self.process.is_alive():
            stop_flag.set()
            self.process.join(timeout=3)
            if self.process.is_alive():
                logger.warning("任务未能正常退出，尝试强制终止")
                self.process.terminate()
                self.process.join()
            logger.info("任务已停止")
        else:
            logger.warning("没有正在运行的任务")

        if is_process_running("PaddleOCR-json.exe"):
            kill_process("PaddleOCR-json.exe")

        self.current_attempt = 0

    def is_running(self):
        """检查任务是否正在运行"""
        try:
            if self.process is None:
                return False
            if self.process.is_alive():
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"检查任务是否在运行时发生异常: {e}")
            return False


ap = AutomationProcessManager()

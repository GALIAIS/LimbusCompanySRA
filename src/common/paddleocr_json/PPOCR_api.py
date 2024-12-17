# 调用 PaddleOCR-json.exe 的 Python Api
# 项目主页：
# https://github.com/hiroi-sora/PaddleOCR-json

import os
import socket  # 套接字
import atexit  # 退出处理
import subprocess  # 进程，管道
import re  # regex
from json import loads as jsonLoads, dumps as jsonDumps
from sys import platform as sysPlatform  # popen静默模式
from base64 import b64encode  # base64 编码


class PPOCR_base:
    """PPOCR 调用基类，定义通用方法"""

    def __init__(self):
        self.__ENABLE_CLIPBOARD = False
        self.__runningMode = None

    def isClipboardEnabled(self) -> bool:
        return self.__ENABLE_CLIPBOARD

    def getRunningMode(self) -> str:
        return self.__runningMode

    def run(self, imgPath: str):
        """对一张本地图片进行文字识别。\n
        `exePath`: 图片路径。\n
        `return`:  {"code": 识别码, "data": 内容列表或错误信息字符串}\n"""
        writeDict = {"image_path": imgPath}
        return self.runDict(writeDict)

    def runClipboard(self):
        """立刻对剪贴板第一位的图片进行文字识别。\n
        `return`:  {"code": 识别码, "data": 内容列表或错误信息字符串}\n"""
        if self.__ENABLE_CLIPBOARD:
            return self.run("clipboard")
        else:
            raise Exception("剪贴板功能不存在或已禁用。")

    def runBase64(self, imageBase64: str):
        """对一张编码为base64字符串的图片进行文字识别。\n
        `imageBase64`: 图片base64字符串。\n
        `return`:  {"code": 识别码, "data": 内容列表或错误信息字符串}\n"""
        writeDict = {"image_base64": imageBase64}
        return self.runDict(writeDict)

    def runBytes(self, imageBytes):
        """对一张图片的字节流信息进行文字识别。\n
        `imageBytes`: 图片字节流。\n
        `return`:  {"code": 识别码, "data": 内容列表或错误信息字符串}\n"""
        imageBase64 = b64encode(imageBytes).decode("utf-8")
        return self.runBase64(imageBase64)

    def exit(self):
        """关闭引擎子进程/连接"""
        raise NotImplementedError("子类必须实现此方法")

    @staticmethod
    def printResult(res: dict):
        """用于调试，格式化打印识别结果。\n
        `res`: OCR识别结果。"""

        if res["code"] == 100:
            index = 1
            for line in res["data"]:
                print(
                    f"{index}-置信度：{round(line['score'], 2)}，文本：{line['text']}",
                    end="\\n\n" if line.get("end", "") == "\n" else "\n",
                )
                index += 1
        elif res["code"] == 100:
            print("图片中未识别出文字。")
        else:
            print(f"图片识别失败。错误码：{res['code']}，错误信息：{res['data']}")


class PPOCR_pipe(PPOCR_base):
    """调用OCR（管道模式）"""

    def __init__(self, exePath: str, modelsPath: str = None, argument: dict = None):
        """初始化识别器（管道模式）。\n
        `exePath`: 识别器`PaddleOCR_json.exe`的路径。\n
        `modelsPath`: 识别库`models`文件夹的路径。若为None则默认识别库与识别器在同一目录下。\n
        `argument`: 启动参数，字典`{"键":值}`。参数说明见 https://github.com/hiroi-sora/PaddleOCR-json
        """
        super().__init__()
        self.__runningMode = "local"

        exePath = os.path.abspath(exePath)
        cwd = os.path.abspath(os.path.join(exePath, os.pardir))  # 获取exe父文件夹
        cmds = [exePath]
        if modelsPath is not None:
            if os.path.exists(modelsPath) and os.path.isdir(modelsPath):
                cmds += ["--models_path", os.path.abspath(modelsPath)]
            else:
                raise Exception(
                    f"Input modelsPath doesn't exits or isn't a directory. modelsPath: [{modelsPath}]"
                )
        if isinstance(argument, dict):
            for key, value in argument.items():
                if isinstance(value, bool):
                    cmds += [f"--{key}={value}"]
                elif isinstance(value, str):
                    cmds += [f"--{key}", value]
                else:
                    cmds += [f"--{key}", str(value)]
        self.ret = None
        startupinfo = None
        if "win32" in str(sysPlatform).lower():
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags = (
                    subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
            )
            startupinfo.wShowWindow = subprocess.SW_HIDE
        self.ret = subprocess.Popen(
            cmds,
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            startupinfo=startupinfo,
        )
        # 启动子进程
        while True:
            if not self.ret.poll() is None:
                raise Exception(f"OCR init fail.")
            initStr = self.ret.stdout.readline().decode("utf-8", errors="ignore")
            if "OCR init completed." in initStr:
                break
            elif "OCR clipboard enbaled." in initStr:
                self.__ENABLE_CLIPBOARD = True
        atexit.register(self.exit)

    def runDict(self, writeDict: dict):
        """传入指令字典，发送给引擎进程。\n
        `writeDict`: 指令字典。\n
        `return`:  {"code": 识别码, "data": 内容列表或错误信息字符串}\n"""
        if not self.ret:
            return {"code": 901, "data": f"引擎实例不存在。"}
        if not self.ret.poll() is None:
            return {"code": 902, "data": f"子进程已崩溃。"}
        writeStr = jsonDumps(writeDict, ensure_ascii=True, indent=None) + "\n"
        try:
            self.ret.stdin.write(writeStr.encode("utf-8"))
            self.ret.stdin.flush()
        except Exception as e:
            return {
                "code": 902,
                "data": f"向识别器进程传入指令失败，疑似子进程已崩溃。{e}",
            }
        try:
            getStr = self.ret.stdout.readline().decode("utf-8", errors="ignore")
        except Exception as e:
            return {"code": 903, "data": f"读取识别器进程输出值失败。异常信息：[{e}]"}
        try:
            return jsonLoads(getStr)
        except Exception as e:
            return {
                "code": 904,
                "data": f"识别器输出值反序列化JSON失败。异常信息：[{e}]。原始内容：[{getStr}]",
            }

    def exit(self):
        """关闭引擎子进程"""
        if hasattr(self, "ret"):
            if self.ret:
                try:
                    self.ret.kill()
                    self.ret.wait()
                except Exception as e:
                    print(f"[Error] ret.kill() {e}")
        self.ret = None
        atexit.unregister(self.exit)

    def __del__(self):
        self.exit()


class PPOCR_socket(PPOCR_base):
    """调用OCR（套接字模式）"""

    def __init__(self, exePath: str, modelsPath: str = None, argument: dict = None):
        """初始化识别器（套接字模式）。\n
        `exePath`: 识别器`PaddleOCR_json.exe`的路径，可以是本地路径或远程地址 `remote://ip:port`。\n
        `modelsPath`: 识别库`models`文件夹的路径。若为None则默认识别库与识别器在同一目录下。仅在本地模式下有效。\n
        `argument`: 启动参数，字典`{"键":值}`。参数说明见 https://github.com/hiroi-sora/PaddleOCR-json。仅在本地模式下有效。
        """
        super().__init__()

        if not argument:
            argument = {}
        if "port" not in argument:
            argument["port"] = 0
        if "addr" not in argument:
            argument["addr"] = "loopback"

        self.__runningMode = self.__configureExePath(exePath)

        if self.__runningMode == "local":
            super().__init__()
            self.__runningMode = "local"
            pipe_instance = PPOCR_pipe(self.exePath, modelsPath, argument)
            self.__ENABLE_CLIPBOARD = pipe_instance.isClipboardEnabled()
            initStr = pipe_instance.ret.stdout.readline().decode("utf-8", errors="ignore")
            if not pipe_instance.ret.poll() is None:
                raise Exception(f"Socket init fail.")
            if "Socket init completed. " in initStr:
                splits = initStr.split(":")
                self.ip = splits[0].split("Socket init completed. ")[1]
                self.port = int(splits[1])
                pipe_instance.ret.stdout.close()
                print(f"套接字服务器初始化成功。{self.ip}:{self.port}")
                return

        elif self.__runningMode == "remote":
            self.__ENABLE_CLIPBOARD = False
            testServer = self.runDict({})
            if testServer["code"] in [902, 903, 904]:
                raise Exception(f"Socket connection fail.")
            print(f"套接字服务器连接成功。{self.ip}:{self.port}")
            return

        self.exit()
        raise Exception(f"Socket init fail.")

    def runDict(self, writeDict: dict):
        """传入指令字典，发送给引擎进程。\n
        `writeDict`: 指令字典。\n
        `return`:  {"code": 识别码, "data": 内容列表或错误信息字符串}\n"""

        # 通信
        writeStr = jsonDumps(writeDict, ensure_ascii=True, indent=None) + "\n"
        try:
            # 创建TCP连接
            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientSocket.connect((self.ip, self.port))
            # 发送数据
            clientSocket.sendall(writeStr.encode())
            # 发送完所有数据，关闭我方套接字，之后只能从服务器读取数据
            clientSocket.shutdown(socket.SHUT_WR)
            # 接收数据
            resData = b""
            while True:
                chunk = clientSocket.recv(1024)
                if not chunk:
                    break
                resData += chunk
            getStr = resData.decode()
        except ConnectionRefusedError:
            return {"code": 902, "data": "连接被拒绝"}
        except TimeoutError:
            return {"code": 903, "data": "连接超时"}
        except Exception as e:
            return {"code": 904, "data": f"网络错误：{e}"}
        finally:
            clientSocket.close()
        try:
            return jsonLoads(getStr)
        except Exception as e:
            return {
                "code": 905,
                "data": f"识别器输出值反序列化JSON失败。异常信息：[{e}]。原始内容：[{getStr}]",
            }

    def exit(self):
        """关闭引擎子进程"""
        if hasattr(self, "ret"):
            if self.__runningMode == "local":
                if not self.ret:
                    return
                try:
                    self.ret.kill()
                    self.ret.wait()
                except Exception as e:
                    print(f"[Error] ret.kill() {e}")
            self.ret = None

        self.ip = None
        self.port = None
        atexit.unregister(self.exit)
        print("###  PPOCR引擎子进程关闭！")

    def __del__(self):
        self.exit()

    def __configureExePath(self, exePath: str) -> str | None:
        """处理识别器路径，自动区分本地路径和远程路径"""
        pattern = r"remote://(.*):(\d+)"
        match = re.search(pattern, exePath)
        try:
            if match:  # 远程模式
                self.ip = match.group(1)
                self.port = int(match.group(2))
                if self.ip == "any":
                    self.ip = "0.0.0.0"
                elif self.ip == "loopback":
                    self.ip = "127.0.0.1"
                return "remote"
            else:
                self.exePath = exePath
                return "local"
        except:
            return None


def GetOcrApi(
        exePath: str, modelsPath: str = None, argument: dict = None, ipcMode: str = "pipe"
):
    """获取识别器API对象。\n
    `exePath`: 识别器`PaddleOCR_json.exe`的路径，可以是本地路径或远程地址 `remote://ip:port`。\n
    `modelsPath`: 识别库`models`文件夹的路径。若为None则默认识别库与识别器在同一目录下。仅在本地模式下有效。\n
    `argument`: 启动参数，字典`{"键":值}`。参数说明见 https://github.com/hiroi-sora/PaddleOCR-json。仅在本地模式下有效。\n
    `ipcMode`: 进程通信模式，可选值为套接字模式`socket` 或 管道模式`pipe`。用法上完全一致。
    """
    if ipcMode == "socket":
        return PPOCR_socket(exePath, modelsPath, argument)
    elif ipcMode == "pipe":
        return PPOCR_pipe(exePath, modelsPath, argument)
    else:
        raise Exception(
            f'ipcMode可选值为 套接字模式"socket" 或 管道模式"pipe" ，不允许{ipcMode}。'
        )

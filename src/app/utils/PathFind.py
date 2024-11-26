import os
import re
import sys
import winreg
from typing import Optional


def find_python(self, directory: str) -> Optional[str]:
    for root, _, files in os.walk(directory):
        for file in files:
            if re.match(r"^python(\.exe)?$", file, re.IGNORECASE):
                potential_path = os.path.join(root, file)
                if sys.platform == "win32" and os.access(potential_path, os.X_OK):
                    return potential_path
                elif sys.platform != "win32" and os.access(potential_path, os.X_OK):
                    return potential_path
    return None


def find_pip(self, directory: str) -> Optional[str]:
    for root, _, files in os.walk(directory):
        for file in files:
            if re.match(r"^pip(\.exe)?$", file, re.IGNORECASE):
                potential_path = os.path.join(root, file)
                if sys.platform == "win32" and os.access(potential_path, os.X_OK):
                    return potential_path
                elif sys.platform != "win32" and os.access(potential_path, os.X_OK):
                    return potential_path
    return None


def find_model(self, directory: str) -> Optional[str]:
    for root, _, files in os.walk(directory):
        for file in files:
            if re.match(r"^LBC(\.plan)?$", file, re.IGNORECASE):
                potential_path = os.path.join(root, file)
                if sys.platform == "win32" and os.access(potential_path, os.X_OK):
                    return potential_path
                elif sys.platform != "win32" and os.access(potential_path, os.X_OK):
                    return potential_path
    return None


def find_limbus(self, directory: str) -> Optional[str]:
    for root, _, files in os.walk(directory):
        for file in files:
            if re.match(r"^LimbusCompany(\.exe)?$", file, re.IGNORECASE):
                potential_path = os.path.join(root, file)
                if sys.platform == "win32" and os.access(potential_path, os.X_OK):
                    return potential_path
                elif sys.platform != "win32" and os.access(potential_path, os.X_OK):
                    return potential_path
    return None


def get_installed_steam_games():
    games = {}

    reg_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
    ]

    for hive, reg_key_path in reg_paths:
        try:
            reg_key = winreg.OpenKey(hive, reg_key_path)

            for i in range(0, winreg.QueryInfoKey(reg_key)[0]):
                sub_key_name = winreg.EnumKey(reg_key, i)

                if sub_key_name.startswith("Steam App "):
                    app_id = sub_key_name.split(" ")[-1]
                    sub_key = winreg.OpenKey(reg_key, sub_key_name)

                    try:
                        install_location, _ = winreg.QueryValueEx(sub_key, "InstallLocation")
                        games[app_id] = install_location
                    except FileNotFoundError:
                        pass

                    winreg.CloseKey(sub_key)

            winreg.CloseKey(reg_key)

        except FileNotFoundError:
            pass
        except PermissionError:
            pass
        except Exception:
            pass

    return games

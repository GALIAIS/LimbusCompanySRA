import argparse
import json
import os
import sys
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union, Callable, Dict, List

# import cerberus
import jsonschema
import toml
import yaml
from cryptography.fernet import Fernet, InvalidToken
from loguru import logger
from marshmallow import Schema, ValidationError as MarshmallowValidationError
from pydantic import BaseModel, ValidationError
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

if getattr(sys, 'frozen', False):
    config_path = Path(sys.argv[0]).resolve().parents[2]
else:
    config_path = Path(__file__).resolve().parents[2]

DEFAULT_JSON_SCHEMA = {
    "type": "object",
    "properties": {},
}

DEFAULT_CERBERUS_SCHEMA = {}


class ValidationPlugin:
    """校验器插件基类"""

    def validate(self, data: dict) -> bool:
        """校验数据

        Args:
            data: 待校验的数据

        Returns:
            校验是否通过
        """
        raise NotImplementedError

    def get_error_message(self) -> str:
        """获取错误信息"""
        raise NotImplementedError


class FileHandler(FileSystemEventHandler):
    """文件处理类，支持 YAML 和 JSON 文件，并负责文件夹的自动创建和文件监听"""

    def __init__(self, file_path: str, backup=False, encryption_key: Optional[bytes] = None,
                 validators: Optional[Dict[str, ValidationPlugin]] = None,
                 max_backups: int = 5, backup_interval: int = 60):
        self.file_path = Path(file_path)
        self.backup = backup
        self.encryption_key = encryption_key
        self.validators = validators or {}
        self._ensure_directory()

        self.max_backups = max_backups
        self.backup_interval = backup_interval
        self.last_backup_time = datetime.min

        self.observer = Observer()
        self.observer.schedule(self, str(self.file_path.parent), recursive=False)
        self.observer.start()

    def set_file_path(self, file_path: str):
        """设置新文件路径并确保目录存在"""
        try:
            self.file_path = Path(file_path)
            self._ensure_directory()
            logger.info(f"文件路径已更新为: {self.file_path}")
        except Exception as e:
            logger.error(f"设置文件路径失败：{e}")
            raise

    def _ensure_directory(self):
        """确保文件夹路径存在"""
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.error(f"创建文件夹失败：{e}")
            raise

    def on_modified(self, event):
        """监听文件修改事件"""
        if not event.is_directory and event.src_path == str(self.file_path):
            # logger.info(f"检测到配置文件修改: {self.file_path}")
            self.load()

    def load(self, enable_validation=False) -> Union[dict, list]:
        """加载数据，根据文件扩展名支持 YAML 和 JSON，并进行校验"""
        try:
            if not self.file_path.exists():
                logger.warning(f"文件不存在：{self.file_path}")
                return {}

            with open(self.file_path, 'rb' if self.encryption_key else 'r',
                      encoding=None if self.encryption_key else 'utf-8') as file:
                data = file.read()

                if self.encryption_key:
                    try:
                        cipher_suite = Fernet(self.encryption_key)
                        decrypted_data = cipher_suite.decrypt(data)
                        data = decrypted_data.decode('utf-8')
                    except InvalidToken as e:
                        logger.error(f"解密文件时出错：{e}")
                        raise ValueError("解密失败，请检查密钥或文件内容是否正确")

                if self.file_path.suffix == ".json":
                    loaded_data = json.loads(data)
                elif self.file_path.suffix in [".yaml", ".yml"]:
                    loaded_data = yaml.safe_load(data)
                else:
                    logger.error(f"不支持的文件格式：{self.file_path.suffix}")
                    return {}

                # 执行校验
                if enable_validation:
                    for validator_name, validator in self.validators.items():
                        if not validator.validate(loaded_data):
                            logger.error(
                                f"{validator_name} 校验失败：{validator.get_error_message()}")
                            return {}

                # logger.info(f"配置已加载：{self.file_path}")
                return loaded_data or {}

        except (yaml.YAMLError, json.JSONDecodeError) as e:
            logger.error(f"文件解析失败：{e}")
            return {}
        except Exception as e:
            logger.error(f"加载文件时出错：{e}")
            raise

    def trigger_backup(self):
        """手动触发备份"""
        self._create_backup()
        logger.info("手动触发备份完成")

    def save(self, data: Union[dict, list]):
        """保存数据，并可选创建备份"""
        try:
            self._ensure_directory()
            if self.backup:
                self._create_backup()

            if self.file_path.suffix == ".json":
                file_content = json.dumps(data, ensure_ascii=False, indent=4)
            elif self.file_path.suffix in [".yaml", ".yml"]:
                file_content = yaml.dump(data, allow_unicode=True, default_flow_style=False, indent=4)
            else:
                raise ValueError(f"不支持的文件格式：{self.file_path.suffix}")

            if self.encryption_key:
                cipher_suite = Fernet(self.encryption_key)
                file_content = cipher_suite.encrypt(file_content.encode('utf-8'))
                with open(self.file_path, 'wb') as file:
                    file.write(file_content)
            else:
                with open(self.file_path, 'w', encoding='utf-8') as file:
                    file.write(file_content)

            # logger.info(f"配置已保存到：{self.file_path}")
        except Exception as e:
            logger.error(f"保存文件失败：{e}")
            raise

    def _create_backup(self):
        """创建备份文件"""
        try:
            if self.file_path.exists():
                now = datetime.now()
                if (now - self.last_backup_time).total_seconds() >= self.backup_interval:
                    timestamp = now.strftime("%Y%m%d%H%M%S")

                    file_extension = self.file_path.suffix.lstrip('.')
                    backup_dir = self.file_path.parent / "backups" / self.file_path.stem / file_extension
                    backup_dir.mkdir(parents=True, exist_ok=True)

                    backups = sorted(backup_dir.glob(f"{self.file_path.stem}_*.{self.file_path.suffix}"),
                                     key=os.path.getmtime, reverse=True)

                    if len(backups) >= self.max_backups:
                        for backup in backups[self.max_backups:]:
                            backup.unlink()
                            logger.info(f"删除旧的备份文件：{backup}")

                    backup_path = backup_dir / f"{self.file_path.stem}_{timestamp}{self.file_path.suffix}"
                    self.file_path.replace(backup_path)
                    logger.info(f"备份创建于：{backup_path}")

                    self.last_backup_time = now

        except OSError as e:
            logger.error(f"创建备份失败：{e}")
            raise


class ConfigData:
    """配置数据管理类"""

    def __init__(self, initial_data: Optional[Union[dict, list]] = None):
        self.data = initial_data or {}
        self.on_changed_callbacks = []
        self.descriptions: Dict[str, str] = {}
        self.validators: Dict[str, Callable[[Any], bool]] = {}
        self.history: Dict[str, List[Any]] = {}

    def get(self, key: str, default: Any = None) -> Any:
        """获取嵌套配置项"""
        keys = key.split('.')
        value = self.data
        for k in keys:
            if isinstance(value, (dict, list)):
                try:
                    value = value.get(k, default) if isinstance(value, dict) else default
                except (TypeError, AttributeError):
                    try:
                        k_int = int(k)
                        value = value[k_int] if 0 <= k_int < len(value) else default
                    except (ValueError, IndexError):
                        return default
            else:
                return default
        return value

    def set(self, key: str, value: Any, description: Optional[str] = None):
        """设置嵌套配置项"""
        old_value = self.get(key)
        self._save_history(key, old_value)
        keys = key.split('.')
        data = self.data
        for k in keys[:-1]:
            try:
                if k not in data:
                    data[k] = {}
                elif not isinstance(data[k], (dict, list)):
                    data[k] = {}
                data = data[k]
            except (TypeError, AttributeError):
                try:
                    k_int = int(k)
                    if not (0 <= k_int < len(data)):
                        raise IndexError
                    data = data[k_int]
                except (ValueError, IndexError):
                    raise KeyError(f"Invalid key path: {key}")

        if key in self.validators:
            if not self.validators[key](value):
                raise ValueError(f"配置项 {key} 的值 {value} 未通过校验")

        try:
            data[keys[-1]] = deepcopy(value)
        except (TypeError, AttributeError):
            try:
                k_int = int(keys[-1])
                if not (0 <= k_int < len(data)):
                    raise IndexError
                data[k_int] = deepcopy(value)
            except (ValueError, IndexError):
                raise KeyError(f"Invalid key path: {key}")

        self._notify_change(key, value)
        if description:
            self.descriptions[key] = description

    def _save_history(self, key: str, value: Any):
        """保存配置项的历史记录"""
        if key not in self.history:
            self.history[key] = []
        self.history[key].append(value)

    def get_history(self, key: str) -> List[Any]:
        """获取配置项的历史记录"""
        return self.history.get(key, [])

    def update(self, new_data: Union[dict, list]):
        """递归更新配置项"""

        def recursive_update(d, u):
            if isinstance(u, dict):
                for k, v in u.items():
                    if isinstance(v, dict) and isinstance(d.get(k), dict):
                        recursive_update(d[k], v)
                    else:
                        if k in self.validators:
                            if not self.validators[k](v):
                                raise ValueError(f"配置项 {k} 的值 {v} 未通过校验")

                        d[k] = deepcopy(v)
                        self._notify_change(k, v)
            elif isinstance(u, list):
                for i, v in enumerate(u):
                    if isinstance(v, (dict, list)) and i < len(d) and isinstance(d[i], type(v)):
                        recursive_update(d[i], v)
                    else:
                        d[i] = deepcopy(v)
                        self._notify_change(str(i), v)

        recursive_update(self.data, new_data)

    def reset(self):
        """重置配置数据"""
        self.data.clear()
        self._notify_change(None, None)

    def get_data(self) -> Union[dict, list]:
        """获取完整数据"""
        return deepcopy(self.data)

    def delete(self, key: str):
        """删除配置项"""
        keys = key.split('.')
        data = self.data
        for k in keys[:-1]:
            if isinstance(data, dict):
                if k not in data:
                    return
                data = data[k]
            elif isinstance(data, list):
                try:
                    k_int = int(k)
                    if not (0 <= k_int < len(data)):
                        return
                    data = data[k_int]
                except ValueError:
                    return
            else:
                return

        if isinstance(data, dict):
            if keys[-1] in data:
                del data[keys[-1]]
                self._notify_change(key, None)
        elif isinstance(data, list):
            try:
                k_int = int(keys[-1])
                if 0 <= k_int < len(data):
                    del data[k_int]
                    self._notify_change(key, None)
            except ValueError:
                pass

    def exists(self, key: str) -> bool:
        """检查配置项是否存在"""
        return self.get(key) is not None

    def on_changed(self, callback: Callable[[str, Any], None]):
        """注册配置变更回调函数"""
        self.on_changed_callbacks.append(callback)

    def _notify_change(self, key: str, value: Any):
        """通知配置变更"""
        for callback in self.on_changed_callbacks:
            callback(key, value)

    def get_description(self, key: str) -> Optional[str]:
        """获取配置项描述"""
        return self.descriptions.get(key)

    def add_validator(self, key: str, validator: Callable[[Any], bool]):
        """添加自定义校验器"""
        self.validators[key] = validator


class ConfigManager:
    """配置管理类，协调 FileHandler 和 ConfigData"""

    def __init__(self, file_path: str, backup=False, encryption_key: Optional[bytes] = None,
                 validators: Optional[Dict[str, ValidationPlugin]] = None,
                 auto_save: bool = False, validation_hook: Optional[Callable[[Union[dict, list]], None]] = None,
                 max_backups: int = 5, backup_interval: int = 60, user_roles: Optional[List[str]] = None,
                 version_history_limit: int = 10, default_values: Optional[Union[dict, list]] = None):
        self.config_change_callbacks: List[Callable[[str, Any], None]] = []
        self.role_permissions: Dict[str, List[str]] = {}
        self.file_handler = FileHandler(file_path, backup=backup, encryption_key=encryption_key,
                                        validators=validators,
                                        max_backups=max_backups, backup_interval=backup_interval)
        self.config_data = ConfigData(self.file_handler.load())
        self.auto_save = auto_save
        self.validation_hook = validation_hook
        self.user_roles = user_roles or []
        self.version_history: List[Union[dict, list]] = []
        self.version_history_limit = version_history_limit
        self.default_values = default_values or {}

        self._parse_args()

    def _parse_args(self):
        """解析命令行参数"""
        parser = argparse.ArgumentParser()
        parser.add_argument('--set', action='append', nargs=2, metavar=('key', 'value'),
                            help='设置配置项，格式为 key=value')
        args, _ = parser.parse_known_args()

        if args.set:
            for key, value in args.set:
                try:
                    self.set(key, yaml.safe_load(value))
                except Exception as e:
                    logger.error(f"设置命令行参数 {key}={value} 时出错：{e}")

    def load(self):
        """重新加载配置"""
        self.config_data = ConfigData(self.file_handler.load())
        logger.info("配置已重新加载")

    def save(self):
        """保存当前配置"""
        self.version_history.append(self.config_data.get_data())
        if len(self.version_history) > self.version_history_limit:
            self.version_history.pop(0)
        self.file_handler.save(self.config_data.get_data())

    def get(self, key: str, default: Any = False) -> Any:
        """外部接口获取配置项，优先从环境变量获取"""
        env_var = f"APP_{key.upper().replace('.', '_')}"
        return os.environ.get(env_var) or self.config_data.get(key) or self.default_values.get(key, default)

    def set(self, key: str, value: Any, save: bool = True, description: Optional[str] = None,
            allowed_roles: Optional[List[str]] = None):
        """外部接口设置配置项，支持权限控制"""
        if allowed_roles:
            self.role_permissions[key] = allowed_roles
        if allowed_roles and not any(role in self.user_roles for role in allowed_roles):
            raise PermissionError(f"用户没有权限修改配置项：{key}")
        self.config_data.set(key, value, description)
        if save or (save is None and self.auto_save):
            self.save()

    def update(self, new_data: Union[dict, list], save: bool = True):
        """外部接口批量更新配置项"""
        self.config_data.update(new_data)
        if save or (save is None and self.auto_save):
            self.save()

    def reset(self, save: bool = True):
        """重置配置并可选立即保存"""
        self.config_data.reset()
        if save or (save is None and self.auto_save):
            self.save()

    def set_config_file(self, file_path: str, load_immediately: bool = True):
        """切换配置文件并重新加载（可选）"""
        self.file_handler.set_file_path(file_path)
        if load_immediately:
            self.load()

    def delete(self, key: str, save: bool = True):
        """删除配置项"""
        self.config_data.delete(key)
        if save or (save is None and self.auto_save):
            self.save()

    def exists(self, key: str) -> bool:
        """检查配置项是否存在"""
        return self.config_data.exists(key)

    def validate(self):
        """手动触发配置文件校验"""
        self.file_handler.load(enable_validation=True)

    def apply_validation_hook(self):
        """应用自定义校验钩子"""
        if self.validation_hook:
            self.validation_hook(self.config_data.get_data())

    def on_config_changed(self, callback: Callable[[str, Any], None]):
        """注册配置变更回调函数"""
        self.config_change_callbacks.append(callback)

    def _notify_config_change(self, key: str, value: Any):
        """通知配置变更"""
        for callback in self.config_change_callbacks:
            callback(key, value)

    def rollback(self, version: int):
        """回滚到指定版本"""
        if 0 <= version < len(self.version_history):
            self.config_data = ConfigData(self.version_history[version])
            self.save()
        else:
            raise ValueError(f"无效的版本号：{version}")

    def trigger_backup(self):
        """手动触发配置备份"""
        self.file_handler.trigger_backup()

    def export(self, file_path: str, file_format: str = 'yaml'):
        """导出配置到文件"""
        data = self.config_data.get_data()
        if file_format == 'yaml':
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False, indent=4)
        elif file_format == 'json':
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        elif file_format == 'toml':
            with open(file_path, 'w', encoding='utf-8') as f:
                toml.dump(data, f)
        else:
            raise ValueError(f"不支持的文件格式：{file_format}")

    def import_from_file(self, file_path: str, file_format: str = 'yaml'):
        """从文件导入配置"""
        if file_format == 'yaml':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        elif file_format == 'json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            raise ValueError(f"不支持的文件格式：{file_format}")
        self.config_data = ConfigData(data)
        self.save()

    def get_description(self, key: str) -> Optional[str]:
        """获取配置项描述"""
        return self.config_data.get_description(key)

    def add_validator(self, key: str, validator: Callable[[Any], bool]):
        """添加自定义校验器"""
        self.config_data.add_validator(key, validator)


class LengthValidator:
    def __init__(self, min_length: int = 0, max_length: int = 255):
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value: str) -> bool:
        return self.min_length <= len(value) <= self.max_length

    def get_error_message(self) -> str:
        return f"长度必须在 {self.min_length} 到 {self.max_length} 之间"


# class PydanticConfig(BaseModel):
#     pass  # 根据需要定义字段
#
#
# class MarshmallowConfig(Schema):
#     pass  # 根据需要定义字段
#
#
# class JSONSchemaValidator(ValidationPlugin):
#     """JSON Schema 校验器"""
#
#     def __init__(self, schema: dict):
#         self.schema = schema
#         self.error = None
#
#     def validate(self, data: dict) -> bool:
#         """使用 JSON Schema 校验数据"""
#         try:
#             jsonschema.validate(instance=data, schema=self.schema)
#             return True
#         except jsonschema.exceptions.ValidationError as e:
#             self.error = str(e)
#             return False
#
#     def get_error_message(self) -> str:
#         """获取 JSON Schema 校验错误信息"""
#         return self.error
#
#
# class CerberusValidator(ValidationPlugin):
#     """Cerberus 校验器"""
#
#     def __init__(self, schema: dict):
#         self.schema = schema
#         self.validator = cerberus.Validator(self.schema)
#
#     def validate(self, data: dict) -> bool:
#         """使用 Cerberus 校验数据"""
#         return self.validator.validate(data)
#
#     def get_error_message(self) -> str:
#         """获取 Cerberus 校验错误信息"""
#         return str(self.validator.errors)
#
#
# class PydanticValidator(ValidationPlugin):
#     """Pydantic 校验器"""
#
#     def __init__(self, model: type[BaseModel]):
#         self.model = model
#         self.error = None
#
#     def validate(self, data: dict) -> bool:
#         """使用 Pydantic 模型校验数据"""
#         try:
#             self.model.parse_obj(data)
#             return True
#         except ValidationError as e:
#             self.error = str(e)
#             return False
#
#     def get_error_message(self) -> str:
#         """获取 Pydantic 校验错误信息"""
#         return self.error
#
#
# class MarshmallowValidator(ValidationPlugin):
#     """Marshmallow 校验器"""
#
#     def __init__(self, schema: type[Schema]):
#         self.schema = schema
#         self.error = None
#
#     def validate(self, data: dict) -> bool:
#         """使用 Marshmallow Schema 校验数据"""
#         try:
#             self.schema().load(data)
#             return True
#         except MarshmallowValidationError as e:
#             self.error = str(e)
#             return False
#
#     def get_error_message(self) -> str:
#         """获取 Marshmallow 校验错误信息"""
#         return self.error
#
#
# json_schema_validator = JSONSchemaValidator(schema={
#     "type": "object",
#     "properties": {
#         "app": {
#             "type": "object",
#             "properties": {
#                 "theme": {"type": "string", "enum": ["Light", "Dark"]},
#                 "language": {"type": "string"},
#             },
#             "required": ["theme", "language"],
#         },
#     },
#     "required": ["app"],
# })

cfgm = ConfigManager(f"{config_path}/config/default.yaml")

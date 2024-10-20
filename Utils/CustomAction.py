# -*- This file is used to execute custom actions defined in the custom_command.txt file. -*-

import ast
import os

from Utils.GameOperate import *
from typing import Callable, List, Dict
from UI.Notification import NotificationManager




class ActionExecutor:
    def __init__(self, custom_command_path: str, hwnd: str = None):
        self.hwnd = hwnd
        self.custom_command_path = custom_command_path
        self.function_map = {
            '按下': press_key,
            '释放': release_key,
            '按下鼠标': mouse_down,
            '释放鼠标': mouse_up,
            '等待': delay,
            '随机移动': random_move,
            '随机转向': random_veer,
            'ctrl技能': killer_ctrl,
            '技能': killer_skill,
            '点击技能': killer_skillclick,
        }
        self.nested_function_map = {
            '随机移动时间': self.get_random_movetime,
            '随机转向时间': self.get_random_veertime,
            '随机移动方向': self.get_random_move_direction,
            '随机转向方向': self.get_random_veer_direction,
        }
        self.custom_names: Dict[str, str] = {}
        self.character_actions: Dict[str, List[str]] = {}  # 用于存储指定角色对应的动作
        self.current_character = None  # 用于记录指定角色名称
        self.current_character_match = None  # 用于记录指定角色名称的匹配结果
        self.common_actions = []  # 用于存储通用动作
        self.last_modified_time = None
        self.file_content = []

    def load_file(self):
        # 检测文件修改时间
        try:
            current_modified_time = os.path.getmtime(self.custom_command_path)
            if self.last_modified_time is None or current_modified_time != self.last_modified_time:
                # 清空之前的记录
                self.custom_names.clear()
                self.character_actions.clear()
                self.common_actions.clear()

                with open(self.custom_command_path, 'r', encoding='utf-8') as file:
                    self.file_content = file.readlines()

                # 保存新的修改时间
                self.last_modified_time = current_modified_time

                # 解析文件内容
                for line in self.file_content:
                    self.parse_line(line)
        except FileNotFoundError:
            print("文件不存在")
            self.file_content = []

    @staticmethod
    def get_random_movetime(*args):
        return random_movetime(*args)

    @staticmethod
    def get_random_veertime(*args):
        return random_veertime(*args)

    @staticmethod
    def get_random_move_direction(*args):
        return random_movement(*args)

    @staticmethod
    def get_random_veer_direction(*args):
        return random_direction(*args)

    @staticmethod
    def parse_arguments(args_str: List[str]) -> List:
        def safe_eval(arg):
            try:
                return ast.literal_eval(arg)
            except (ValueError, SyntaxError):
                return arg

        args = [safe_eval(arg) for arg in args_str]

        # 检查是否有字典参数
        for i, arg in enumerate(args):
            if isinstance(arg, str) and arg.startswith('{') and arg.endswith('}'):
                try:
                    args[i] = ast.literal_eval(arg)
                except (ValueError, SyntaxError):
                    pass

        # 类型检查和转换
        for i, arg in enumerate(args):
            if isinstance(arg, str):
                if arg.isdigit():
                    args[i] = int(arg)
                elif arg.replace('.', '', 1).isdigit():
                    args[i] = float(arg)

        return args

    def parse_line(self, line: str):
        line = line.strip()
        if not line:  # 处理空行
            return None
        if line.startswith('#'):  # 处理注释行
            return None
        if line.startswith('指定'):
            killer_names = line.split('->')[1].strip()
            self.current_character = killer_names  # 记录指定角色名称
            self.character_actions[self.current_character] = []  # 初始化指定角色的动作列表
            return None
        elif self.current_character:
            self.character_actions[self.current_character].append(line)  # 将动作添加到指定角色的动作列表
            return None
        else:
            self.common_actions.append(line)  # 将动作添加到通用动作列表
            return None

    def parse_action_commands(self, line: str):
        if not line.strip():  # 检查是否为空行
            return None, None
        if line.startswith('#'):  # 处理注释行
            return None, None
        first_equal_index = line.find('=')
        if first_equal_index == -1:
            first_left_bracket_index = line.find('(')
            if first_left_bracket_index == -1:
                raise ValueError(f"缺少左括号'(': {line}")
            else:
                command = line[:first_left_bracket_index].strip()
                first_right_bracket_index = line.find(')', first_left_bracket_index)
                if first_right_bracket_index == -1:
                    raise ValueError(f"未闭合的括号: {line}")
                args_str = line[first_left_bracket_index + 1:first_right_bracket_index].split()
        else:
            custom_name = line[:first_equal_index].strip()
            command_str = line[first_equal_index + 1:].strip()
            first_left_bracket_index = command_str.find('(')
            if first_left_bracket_index == -1:
                raise ValueError(f"命令格式错误: {line}-{command_str}")
            command = command_str[:first_left_bracket_index].strip()
            first_right_bracket_index = command_str.find(')', first_left_bracket_index)
            if first_right_bracket_index == -1:
                raise ValueError(f"未闭合的括号: {command_str}")
            args_str = command_str[first_left_bracket_index + 1:first_right_bracket_index].split()
            if command in self.nested_function_map:
                func = self.nested_function_map[command]
                args = self.parse_arguments(args_str)
                result = func(*args)
                self.custom_names[custom_name] = result
                return None, None
            else:
                raise ValueError(f"未识别的命令: {command}")

        args = self.parse_arguments(args_str)
        for i, arg in enumerate(args):
            if isinstance(arg, str) and arg in self.nested_function_map:
                if i + 1 < len(args) and isinstance(args[i + 1], dict):
                    nested_result = self.nested_function_map[arg](args[i + 1])
                else:
                    nested_result = self.nested_function_map[arg]()
                args = [nested_result]
                break

        if command in self.function_map:
            func = self.function_map[command]
            if self.hwnd is not None and callable(func) and self._is_function_need_hwnd(func):
                args = [self.hwnd] + args
            new_args = []
            for arg in args:
                if arg in self.custom_names:
                    new_args.append(self.custom_names[arg])
                else:
                    new_args.append(arg)
            args = new_args
            return func, args
        else:
            raise ValueError(f"未识别的命令: {command}")

    def _is_function_need_hwnd(self, func: Callable):
        return "hwnd" in self._get_function_params(func)

    @staticmethod
    def _get_function_params(func: Callable):
        return func.__code__.co_varnames[:func.__code__.co_argcount]

    def execute_action_sequence(self, killer_name: str = None):
        self.load_file()

        # 判断是否使用 execute_killer_actions
        if killer_name is not None and any(killer_name in key for key in self.character_actions):
            self.execute_killer_actions(killer_name)
            self.current_character_match = True
        else:
            self.current_character_match = False
            # print(self.common_actions)
            try:
                for action_line in self.common_actions:
                    try:
                        func, args = self.parse_action_commands(action_line)
                        if callable(func) and isinstance(args, list):
                            func(*args)
                    except ValueError as e:
                        print(e)
                        continue
                    except Exception as e:
                        print(f"执行动作时发生错误: {e}")
            except RuntimeError:
                manager.sMessageBox("不应在运行时改变内容！", "error")

    def execute_killer_actions(self, killer_name: str):
        try:
            for key in self.character_actions:
                if killer_name in key:
                    # print(self.character_actions[key])
                    for action_line in self.character_actions[key]:
                        try:
                            func, args = self.parse_action_commands(action_line)
                            if callable(func) and isinstance(args, list):
                                func(*args)
                        except ValueError as e:
                            print(e)
                            continue
                        except Exception as e:
                            print(f"执行动作时发生错误: {e}")
        except RuntimeError:
            manager.sMessageBox("不应在运行时改变内容！", "error")


manager = NotificationManager()

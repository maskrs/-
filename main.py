# -*- mode: python ; coding: utf-8 -*-

import atexit
import copy
import ctypes
import functools
import json
import os.path
import random
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
import pyautogui as py
import tkinter as tk
import pyperclip
import pytesseract
import re
import requests
import win32api
import win32con
import win32gui
import keyboard
import logging
import sentry_sdk
import win32print
import pictures_rc  # 导入资源文件

from sentry_sdk.integrations.logging import LoggingIntegration
from simpleaudio._simpleaudio import SimpleaudioError
from win32api import GetSystemMetrics

from simpleaudio import WaveObject
from configparser import ConfigParser
from operator import eq, gt, ge, ne
from PyQt5.QtCore import QTranslator, QLocale, Qt, QCoreApplication, QThread, pyqtSignal, QRegExp, QEvent, \
    pyqtSlot, QObject
from PyQt5.QtGui import QIcon, QPalette, QSyntaxHighlighter, QTextCharFormat, QFont, QColor, QMovie, QTextCursor
from PyQt5.QtWidgets import *
from typing import Callable, Optional

from UI.DBDAutoScriptUI import Ui_MainWindow
from UI.selec_killerUI import Ui_Dialog
from UI.AdvancedParameterUI import Ui_AdvancedWindow
from UI.CustomSelectUI import Ui_Custom_select
from UI.ShowLog import Ui_ShowLogDialog
from UI.DebugTool import Ui_DebugDialog
from UI.CustomCommandUI import Ui_CustomCommand
from UI.AutoComplete import CodeTextEdit
from UI.SettingsUI import Ui_SettingDialog
from UI.CrashReportUI import Ui_CrashReportDialog
from UI.Notification import NotificationManager

from Utils.GameOperate import (random_direction, random_movement, random_move, random_veer, killer_ctrl,
                               killer_skill, killer_skillclick)
from Utils.background_operation import key_down, key_up, screenshot
from Utils.CustomAction import ActionExecutor
from Utils.Client2ScreenOperate import MouseController


class DbdWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.trans = QTranslator()
        self.setupUi(self)
        self.setWindowIcon(QIcon(":mainwindow/picture/dbdwindow.png"))

        self.initUI()
        self.init_signals()

    def initUI(self):
        self.start_gif = GifButton(self.pb_start, ':start/picture/circled-play.gif')
        self.stop_gif = GifButton(self.pb_stop, ':stop/picture/shutdown.gif')
        self.setting_gif = GifButton(self.pb_setting, ':setting/picture/settings.gif')
        self.select_gif = GifButton(self.pb_select_cfg, ':mainwindow/picture/choose.gif')

    def init_signals(self):
        #  初始化信号和槽连接
        self.pb_select_cfg.clicked.connect(self.pb_select_cfg_click)
        self.pb_start.clicked.connect(begin)
        self.pb_stop.clicked.connect(kill)
        self.pb_setting.clicked.connect(self.pb_setting_click)
        self.rb_chinese.clicked.connect(self.rb_chinese_change)
        self.rb_english.clicked.connect(self.rb_english_change)
        self.cb_bvinit.clicked.connect(self.cb_bvinit_click)

    @staticmethod
    def pb_setting_click():
        settingsWindowUi.show()

    @staticmethod
    def pb_select_cfg_click():
        selectWindowUi.retranslateUi(selectWindowUi)
        selectWindowUi.show()
        selectWindowUi.adjustSize()

    def rb_chinese_change(self):
        # 默认的中文包，不要新建
        self.trans.load('zh_CN')
        _app = QApplication.instance()
        _app.installTranslator(self.trans)
        self.retranslateUi(self)
        self.adjustSize()
        save_cfg()

    def rb_english_change(self):
        # 导入语言包，english是翻译的.qm文件
        self.trans.load(":trans/picture/transEN.qm")
        _app = QApplication.instance()
        _app.installTranslator(self.trans)
        self.retranslateUi(self)
        self.adjustSize()
        save_cfg()

    def cb_bvinit_click(self):
        """重置二值化校准开关"""
        keys_to_update = [
            '匹配大厅二值化阈值',
            '准备房间二值化阈值',
            '结算页二值化阈值',
            '结算页每日祭礼二值化阈值',
            '段位重置二值化阈值',
            '主页面每日祭礼二值化阈值',
            '主页面二值化阈值',
            '断线检测二值化阈值',
            '新内容二值化阈值',
        ]
        if self.cb_bvinit.isChecked():
            # 遍历键列表并更新字典中的值
            for key in keys_to_update:
                current_value = self_defined_args[key]
                current_value[2] = 0  # 更新第三个元素
                self_defined_args[key] = current_value  # 将更新后的数组重新赋值给字典中对应的键
        else:
            # 遍历键列表并更新字典中的值
            for key in keys_to_update:
                current_value = self_defined_args[key]
                current_value[2] = 1  # 更新第三个元素
                self_defined_args[key] = current_value  # 将更新后的数组重新赋值给字典中对应的键

        # 将更新后的键值对写回文件
        with open(SDAGRS_PATH, 'w', encoding='utf-8') as f:
            json.dump(self_defined_args, f, indent=4, ensure_ascii=False)

    def closeEvent(self, event):
        # 在主窗口关闭时关闭所有通知
        manager.closeAllNotifications()
        event.accept()


class SelectWindow(QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(":select/picture/choose.png"))

        self.initUI()
        self.init_signals()

    def initUI(self):
        self.pb_save.setIcon(QIcon(":mainwindow/picture/confirm.gif"))
        self.pb_all.setIcon(QIcon(":mainwindow/picture/all.gif"))
        self.pb_invert.setIcon(QIcon(":mainwindow/picture/Invert.gif"))
        self.pb_custom_select.setIcon(QIcon(":mainwindow/picture/edit.gif"))

        self.save_gif = GifButton(self.pb_save, ':mainwindow/picture/confirm.gif')
        self.all_gif = GifButton(self.pb_all, ':mainwindow/picture/all.gif')
        self.invert_gif = GifButton(self.pb_invert, ':mainwindow/picture/Invert.gif')
        self.custom_select_gif = GifButton(self.pb_custom_select, ':mainwindow/picture/edit.gif')

    def init_signals(self):
        self.pb_all.clicked.connect(self.pb_select_all_click)
        self.pb_invert.clicked.connect(self.pb_invert_click)
        self.pb_save.clicked.connect(self.pb_save_click)
        self.pb_custom_select.clicked.connect(self.pb_custom_select_click)

    def pb_select_all_click(self):
        """全选点击槽"""
        # 获取self.select_ui中所有以cb_开头的属性
        checkboxes = [getattr(self, attr) for attr in dir(self) if
                      attr.startswith('cb_') and callable(getattr(self, attr).setChecked)]

        # 遍历复选框列表，设置每个复选框为选中状态
        for checkbox in checkboxes:
            checkbox.setChecked(True)

    def pb_invert_click(self):
        """反选点击槽"""
        # 获取self.select_ui中所有以cb_开头的复选框
        checkboxes = [getattr(self, attr) for attr in dir(self) if
                      attr.startswith('cb_') and isinstance(getattr(self, attr), QCheckBox)]

        # 遍历复选框列表，并切换每个复选框的状态
        for checkbox in checkboxes:
            checkbox.toggle()

    @staticmethod
    def pb_custom_select_click():
        customSelectWindowUi.loading_settings()
        customSelectWindowUi.show()

    @staticmethod
    def pb_save_click():
        manager.sMessageBox('已保存配置！', 'info')
        save_cfg()


class CustomCommandHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.error_format = QTextCharFormat()
        self.error_format.setForeground(QColor(255, 46, 46))
        self.error_format.setFontWeight(QFont.Bold)
        self.error_format.setUnderlineColor(Qt.red)
        self.error_format.setUnderlineStyle(QTextCharFormat.SingleUnderline)

        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#e4a24a"))

        self.function_format = QTextCharFormat()
        self.function_format.setForeground(QColor("#69b2ed"))

        self.variable_format = QTextCharFormat()
        self.variable_format.setForeground(QColor("#bf74af"))

        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#5aa66a"))
        self.comment_format.setFontItalic(True)

        self.keywords = [
            "按下", "释放", "按下鼠标", "释放鼠标", "等待", "随机移动", "随机转向", "ctrl技能", "技能", "点击技能",
            "指定",
            "随机移动方向", "随机转向方向"
        ]
        self.functions = [
            "随机移动时间", "随机转向时间"
        ]

        self.declared_variables = set()

    def highlightBlock(self, text):

        # 高亮注释行
        self.highlight_comments(text)

        # 高亮关键字
        self.highlight_keywords(text)

        # 高亮函数
        self.highlight_functions(text)

        # 识别和高亮变量声明
        self.highlight_variable_declarations(text)

        # 高亮变量引用
        self.highlight_variable_references(text)

        # 检查括号匹配
        self.check_parentheses_matching(text)

        # 检查中文符号匹配
        self.check_chinese_symbols_matching(text)

        # 检查括号内参数
        self.check_command_arguments(text)

    def highlight_comments(self, text):
        pattern = QRegExp(r"#.*")
        index = pattern.indexIn(text)
        if index >= 0:
            length = pattern.matchedLength()
            self.setFormat(index, length, self.comment_format)

    def highlight_keywords(self, text):
        for keyword in self.keywords:
            pattern = QRegExp(r"\b" + keyword + r"\b")
            index = pattern.indexIn(text)
            while index >= 0:
                length = pattern.matchedLength()
                self.setFormat(index, length, self.keyword_format)
                index = pattern.indexIn(text, index + length)

    def highlight_functions(self, text):
        for function in self.functions:
            pattern = QRegExp(r"\b" + function + r"\b")
            index = pattern.indexIn(text)
            while index >= 0:
                length = pattern.matchedLength()
                self.setFormat(index, length, self.function_format)
                index = pattern.indexIn(text, index + length)

    def highlight_variable_declarations(self, text):
        pattern = QRegExp(r"\b(\w+)\s*=\s*")
        index = pattern.indexIn(text)
        while index >= 0:
            variable_name = pattern.cap(1)
            self.declared_variables.add(variable_name)
            self.setFormat(pattern.pos(1), len(variable_name), self.variable_format)
            index = pattern.indexIn(text, index + pattern.matchedLength())

    def highlight_variable_references(self, text):
        pattern = QRegExp(r"\b(\w+)\b")
        index = pattern.indexIn(text)
        while index >= 0:
            variable_name = pattern.cap(1)
            if variable_name in self.declared_variables:
                self.setFormat(pattern.pos(1), len(variable_name), self.variable_format)
            index = pattern.indexIn(text, index + pattern.matchedLength())

    def check_parentheses_matching(self, text):
        stack = []
        for i, char in enumerate(text):
            if char == '(':
                stack.append(i)
            elif char == ')':
                if stack:
                    stack.pop()
                else:
                    self.setFormat(i, 1, self.error_format)
        for index in stack:
            self.setFormat(index, 1, self.error_format)

    def check_command_arguments(self, text):
        required_arguments = {
            "按下": r"\s\(.+\)",
            "释放": r"\s\(.+\)",
            "等待": r"\s\(.+\)",
            "随机移动": r"\s\(.+\)",
            "随机转向": r"\s\(.+\)",
        }
        for command, argument_pattern in required_arguments.items():
            pattern = QRegExp(r"\b" + command + r"\b" + argument_pattern)
            index = pattern.indexIn(text)
            if index == -1:
                pattern = QRegExp(r"\b" + command + r"\b\s*\(\s*\)")
                index = pattern.indexIn(text)
                if index != -1:
                    length = pattern.matchedLength()
                    self.setFormat(index + len(command), length - 2, self.error_format)

    def check_chinese_symbols_matching(self, text):
        chinese_symbols = {
            '（': '（', '）': '）', '【': '【', '】': '】', '《': '《', '》': '》', '“': '“', '”': '”', '‘': '‘', '’': '’',
            '〔': '〔', '〕': '〕', '〖': '〖', '〗': '〗', '；': '；', '：': '：', '〈': '〉', '，': '，', '。': '。',
            '、': '、', '？': '？', '！': '！', '·': '·', '……': '……', '——': '——',
        }
        stack = []
        for i, char in enumerate(text):
            if char in chinese_symbols:
                stack.append((i, char))
            elif char in chinese_symbols.values():
                if stack and stack[-1][1] == next(k for k, v in chinese_symbols.items() if v == char):
                    stack.pop()
                else:
                    self.setFormat(i, 1, self.error_format)
        for index, _ in stack:
            self.setFormat(index, 1, self.error_format)


class CustomCommand(QWidget, Ui_CustomCommand):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.completer = QCompleter(self)
        self.matchWords_list = ["按下 ($CURSOR$)", "释放 ($CURSOR$)", "按下鼠标 ($CURSOR$)", "释放鼠标 ($CURSOR$)",
                                "等待 ($CURSOR$)", "随机移动 ($CURSOR$)", "随机转向 ($CURSOR$)", "ctrl技能 ($CURSOR$)",
                                "技能 ($CURSOR$)", "点击技能 ($CURSOR$)", "指定 -> $CURSOR$", "随机移动时间 ($CURSOR$)",
                                "随机转向时间 ($CURSOR$)", "随机移动方向 ($CURSOR$)", "随机转向方向 ($CURSOR$)"]

        self.init_UI()
        self.init_signals()
        self.loading_commands()

        self.highlighter = CustomCommandHighlighter(self.pe_edit.document())

    def init_UI(self):
        self.setWindowIcon(QIcon(":customcommand/picture/edit-100.png"))
        self.label.setOpenExternalLinks(True)
        self.pe_edit = CodeTextEdit({}, self.matchWords_list, self)
        self.pe_edit.setCompleter(self.completer)
        self.gridLayout.addWidget(self.pe_edit)

        self.pe_edit.setLineWrapMode(QTextEdit.NoWrap)
        self.pe_edit.setStyleSheet("font-size: 13px;")

        self.pb_test.setIcon(QIcon(":mainwindow/picture/test.gif"))
        self.pb_save.setIcon(QIcon(":mainwindow/picture/save.gif"))

        self.test_gif = GifButton(self.pb_test, ':mainwindow/picture/test.gif')
        self.save_gif = GifButton(self.pb_save, ':mainwindow/picture/save.gif')

    def init_signals(self):
        self.pb_save.clicked.connect(self.pb_save_click)
        self.pb_test.clicked.connect(self.pb_test_click)

    def loading_commands(self):
        """加载自定义命令"""
        try:
            with open(CUSTOM_COMMAND_PATH, 'r', encoding='utf-8') as f:
                self.pe_edit.setPlainText(f.read())
        except FileNotFoundError:
            pass

    def pb_save_click(self):
        """保存自定义动作"""
        save_cfg()
        with open(CUSTOM_COMMAND_PATH, 'w', encoding='utf-8') as f:
            f.write(self.pe_edit.toPlainText())
        manager.sMessageBox("保存成功！", 'info')

    def pb_test_click(self):
        """测试自定义动作"""
        test_killer_name = None if self.le_test.text() == '' else self.le_test.text()
        if hwnd == 0:
            manager.sMessageBox('未检测到游戏窗口', 'error')
            return
        win32gui.SetForegroundWindow(hwnd)
        custom_command.execute_action_sequence(test_killer_name)
        manager.sMessageBox('测试结束！', 'info')


class AdvancedParameter(QDialog, Ui_AdvancedWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(":advanced/picture/advanced.png"))
        # 控件到设置键的反向映射
        self.reverse_mapping = {
            self.te_killer_message: '赛后发送消息',
            self.te_human_message: '人类发送消息',
            self.le_start_key: '开始快捷键',
            self.le_stop_key: '停止快捷键',
            self.le_pause_key: '暂停快捷键',
            self.le_firstx: '第一个角色坐标',
            self.le_search_name: '搜索输入框坐标',
            self.le_skill_allocation: '装备配置按钮坐标',
            self.le_allocation1: '装备配置1的坐标',
            self.le_allocation2: '装备配置2的坐标',
            self.le_allocation3: '装备配置3的坐标',
            self.le_play_area: '匹配阶段的识别范围',
            self.le_play_keywords: '匹配大厅识别关键字',
            self.le_playxy: '开始游戏按钮的坐标',
            self.le_play_binaryzation: '匹配大厅二值化阈值',
            self.le_ready_area: '准备阶段的识别范围',
            self.le_ready_keywords: '准备大厅识别关键字',
            self.le_readyxy: '准备就绪按钮的坐标',
            self.le_ready_binaryzation: '准备房间二值化阈值',
            self.le_over_area: '结算页的识别范围',
            self.le_over_keywords: '结算页识别关键字',
            self.le_over_continuexy: '结算页继续按钮坐标',
            self.le_over_binaryzation: '结算页二值化阈值',
            self.le_orites_area: '结算页每日祭礼的识别范围',
            self.le_orites_keywords: '结算页每日祭礼识别关键字',
            self.le_overritesxy: '结算页祭礼完成坐标',
            self.le_overrite_binaryzation: '结算页每日祭礼二值化阈值',
            self.le_season_reset: '段位重置的识别范围',
            self.le_sr_keywords: '段位重置识别关键字',
            self.le_seasonresetxy: '段位重置按钮的坐标',
            self.le_seasonreset_binaryzation: '段位重置二值化阈值',
            self.le_dr_main: '主界面的每日祭礼识别范围',
            self.le_drm_keywords: '主页面每日祭礼识别关键字',
            self.le_main_ritesxy: '主页面祭礼关闭坐标',
            self.le_mainrite_binaryzation: '主页面每日祭礼二值化阈值',
            self.le_mainjudge: '主页面的识别范围',
            self.le_mainjudge_keywords: '主页面识别关键字',
            self.le_main_startxy: '主页面开始坐标',
            self.le_main_binaryzation: '主页面二值化阈值',
            self.le_dccheck: '断线检测的识别范围',
            self.le_dccheck_keywords: '断线检测识别关键字',
            self.le_discheck_binaryzation: '断线检测二值化阈值',
            self.le_dcwords: '断线确认关键字',
            self.le_news: '新内容的识别范围',
            self.le_news_binaryzation: '新内容二值化阈值',
            self.le_new_keywords: '新内容识别关键字',
            self.le_newsxy: '新内容关闭坐标',
            self.le_main_humanxy: '主页面逃生者坐标',
            self.le_main_killerxy: '主页面杀手坐标',
            self.le_rolexy: '角色选择按钮坐标',
            self.le_evrewards: 'event_rewards',
        }

        self.load_settings()
        self.initUI()
        self.init_signals()

    def initUI(self):
        self.pb_save.setIcon(QIcon(":mainwindow/picture/save.gif"))
        self.pb_next.setIcon(QIcon(":mainwindow/picture/next.gif"))
        self.pb_previous.setIcon(QIcon(":mainwindow/picture/previous.gif"))
        self.pb_reset.setIcon(QIcon(":advanced/picture/reset.gif"))

        self.save_gif = GifButton(self.pb_save, ":mainwindow/picture/save.gif")
        self.next_gif = GifButton(self.pb_next, ":mainwindow/picture/next.gif")
        self.previous_gif = GifButton(self.pb_previous, ":mainwindow/picture/previous.gif")
        self.reset_gif = GifButton(self.pb_reset, ":advanced/picture/reset.gif")

    def init_signals(self):
        """初始化信号和槽连接"""

        self.pb_next.clicked.connect(self.pb_next_click)
        self.pb_previous.clicked.connect(self.pb_prev_click)
        self.pb_save.clicked.connect(self.pb_save_click)
        self.pb_reset.clicked.connect(self.pb_reset_click)

    def load_settings(self):
        """初始化加载设置文件内容"""
        # 定义控件映射字典，键是 self_defined_args 中的键，值是控件的属性和方法
        widget_mapping = {
            '赛后发送消息': (self.te_killer_message, 'setText'),
            '人类发送消息': (self.te_human_message, 'setText'),
            '开始快捷键': (self.le_start_key, 'setText'),
            '停止快捷键': (self.le_stop_key, 'setText'),
            '暂停快捷键': (self.le_pause_key, 'setText'),
            '第一个角色坐标': (self.le_firstx, 'setText'),
            '装备配置按钮坐标': (self.le_skill_allocation, 'setText'),
            '装备配置1的坐标': (self.le_allocation1, 'setText'),
            '装备配置2的坐标': (self.le_allocation2, 'setText'),
            '装备配置3的坐标': (self.le_allocation3, 'setText'),
            '搜索输入框坐标': (self.le_search_name, 'setText'),
            '匹配阶段的识别范围': (self.le_play_area, 'setText'),
            '匹配大厅识别关键字': (self.le_play_keywords, 'setText'),
            '开始游戏按钮的坐标': (self.le_playxy, 'setText'),
            '匹配大厅二值化阈值': (self.le_play_binaryzation, 'setText'),
            '准备阶段的识别范围': (self.le_ready_area, 'setText'),
            '准备大厅识别关键字': (self.le_ready_keywords, 'setText'),
            '准备就绪按钮的坐标': (self.le_readyxy, 'setText'),
            '准备房间二值化阈值': (self.le_ready_binaryzation, 'setText'),
            '结算页的识别范围': (self.le_over_area, 'setText'),
            '结算页二值化阈值': (self.le_over_binaryzation, 'setText'),
            '结算页识别关键字': (self.le_over_keywords, 'setText'),
            '结算页继续按钮坐标': (self.le_over_continuexy, 'setText'),
            '结算页每日祭礼的识别范围': (self.le_orites_area, 'setText'),
            '结算页每日祭礼二值化阈值': (self.le_overrite_binaryzation, 'setText'),
            '结算页每日祭礼识别关键字': (self.le_orites_keywords, 'setText'),
            '结算页祭礼完成坐标': (self.le_overritesxy, 'setText'),
            '段位重置的识别范围': (self.le_season_reset, 'setText'),
            '段位重置识别关键字': (self.le_sr_keywords, 'setText'),
            '段位重置按钮的坐标': (self.le_seasonresetxy, 'setText'),
            '段位重置二值化阈值': (self.le_seasonreset_binaryzation, 'setText'),
            '主界面的每日祭礼识别范围': (self.le_dr_main, 'setText'),
            '主页面每日祭礼识别关键字': (self.le_drm_keywords, 'setText'),
            '主页面每日祭礼二值化阈值': (self.le_mainrite_binaryzation, 'setText'),
            '主页面祭礼关闭坐标': (self.le_main_ritesxy, 'setText'),
            '主页面的识别范围': (self.le_mainjudge, 'setText'),
            '主页面识别关键字': (self.le_mainjudge_keywords, 'setText'),
            '主页面开始坐标': (self.le_main_startxy, 'setText'),
            '主页面二值化阈值': (self.le_main_binaryzation, 'setText'),
            '断线检测的识别范围': (self.le_dccheck, 'setText'),
            '断线检测识别关键字': (self.le_dccheck_keywords, 'setText'),
            '断线检测二值化阈值': (self.le_discheck_binaryzation, 'setText'),
            '断线确认关键字': (self.le_dcwords, 'setText'),
            '新内容的识别范围': (self.le_news, 'setText'),
            '新内容识别关键字': (self.le_new_keywords, 'setText'),
            '新内容二值化阈值': (self.le_news_binaryzation, 'setText'),
            '新内容关闭坐标': (self.le_newsxy, 'setText'),
            '主页面逃生者坐标': (self.le_main_humanxy, 'setText'),
            '主页面杀手坐标': (self.le_main_killerxy, 'setText'),
            '角色选择按钮坐标': (self.le_rolexy, 'setText'),
            'event_rewards': (self.le_evrewards, 'setText'),
        }

        # 读取self_defined_args内容
        try:
            with open(SDAGRS_PATH, mode='r', encoding='utf-8') as f:
                # 读取文件中的所有内容，并将其转换为一个字典
                existing_args = json.load(f)
                # 更新 self_defined_args 字典
                self_defined_args.update(existing_args)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # 如果文件不存在或内容不是有效的 JSON，您可以根据需要处理这个异常
            print(f"读取SDargs.json文件异常: {e}")

        # 遍历映射字典
        for key, (widget, method) in widget_mapping.items():
            # 确保 key 存在于 self_defined_args 中
            if key in self_defined_args:
                # 获取对应的控件和方法名
                ctrl = getattr(widget, method)
                # 检查值的类型，如果是列表，则转换为字符串
                arg = ', '.join(map(str, self_defined_args[key])) if isinstance(self_defined_args[key], list) else \
                    self_defined_args[key]
                # 调用控件的方法，传入转换后的参数
                ctrl(arg)
                # print(f"\nUpdated {key} to {arg}")
            else:
                QMessageBox.warning(self, "错误", "键值不在参数文件中")

    def pb_next_click(self):
        index = self.stackedWidget.currentIndex()
        if index >= 5:
            pass
        else:
            index = index + 1
        self.stackedWidget.setCurrentIndex(index)

    def pb_prev_click(self):
        index = self.stackedWidget.currentIndex()
        if index <= 0:
            pass
        else:
            index = index - 1
        self.stackedWidget.setCurrentIndex(index)

    def pb_reset_click(self):
        # 重置为初始值
        with open(SDAGRS_PATH, 'w', encoding='utf-8') as f:
            json.dump(self_defined_args_original, f, indent=4, ensure_ascii=False)
        manager.sMessageBox("重置成功！", 'info')
        self.load_settings()

    def pb_save_click(self):
        self.update_settings()
        # 将更新后的键值对写回文件
        with open(SDAGRS_PATH, 'w', encoding='utf-8') as f:
            json.dump(self_defined_args, f, indent=4, ensure_ascii=False)
        self.retranslateUi(self)
        manager.sMessageBox("保存成功！", 'info')

    def update_settings(self):
        """获取更改后的数值"""

        for widget, setting_key in self.reverse_mapping.items():
            if isinstance(widget, QLineEdit):
                settings_value = widget.text().split(',')
                try:
                    # 检查当前值的类型
                    if isinstance(self_defined_args[setting_key][0], int):
                        # 期望新值为整数
                        settings_value = [int(item.strip()) for item in settings_value]
                    elif isinstance(self_defined_args[setting_key][0], str):
                        # 期望新值为字符串列表，这里假设以逗号分隔
                        settings_value = [item.strip() for item in settings_value]
                except ValueError:
                    # 如果转换失败，返回原始文本值
                    settings_value = widget.text()
                except IndexError:
                    pass
                # 更新 self_defined_args 字典
                self_defined_args[setting_key] = settings_value

                # print(f'获取更改后的值：{self_defined_args}')


class Custom_select(QWidget, Ui_Custom_select):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(":edit/picture/edit.png"))

        self.initUI()
        self.init_signals()

    def initUI(self):
        self.pb_save.setIcon(QIcon(":mainwindow/picture/save.gif"))

        self.save_gif = GifButton(self.pb_save, ":mainwindow/picture/save.gif")

    def init_signals(self):
        self.pb_save.clicked.connect(self.pb_save_click)

    def pb_save_click(self):
        try:
            with open(CUSTOM_KILLER_PATH, 'w', encoding="utf-8") as f:
                f.write(self.pt_search.toPlainText())
            manager.sMessageBox("已保存配置！", 'info')
        except FileNotFoundError:
            manager.sMessageBox(f"{CUSTOM_KILLER_PATH}文件不存在！", "error")
        except Exception as e:
            manager.sMessageBox(f"保存文件时出错:{e}", "error")

    def loading_settings(self):
        try:
            with open(CUSTOM_KILLER_PATH, 'r', encoding="utf-8") as f:
                self.pt_search.setPlainText(f.read())
        except FileNotFoundError:
            manager.sMessageBox(f"{CUSTOM_KILLER_PATH}文件不存在！", "error")
        except Exception as e:
            manager.sMessageBox(f"读取文件时出错:{e}", "error")


class Settings(QDialog, Ui_SettingDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(":setting/picture/设置-32.png"))

        self.initUI()
        self.init_signals()

    def initUI(self):
        self.advanced_gif = GifButton(self.pb_advanced, ":advanced/picture/gears.gif")
        self.log_gif = GifButton(self.pb_showlog, ":log/picture/paper.gif")
        self.tool_gif = GifButton(self.pb_debug_tool, ":debug/picture/tool.gif")
        self.custom_gif = GifButton(self.pb_customcommand, ":customcommand/picture/create.gif")
        self.coordinate_gif = GifButton(self.pb_coordinate_transformation, ":setting/picture/refresh.gif")
        self.chat_gif = GifButton(self.pb_qqchat, ":setting/picture/comments.gif")
        self.help_gif = GifButton(self.pb_help, ":setting/picture/document.gif")
        self.crash_gif = GifButton(self.pb_crashreport, ":setting/picture/crash.gif")

    def init_signals(self):
        self.pb_qqchat.clicked.connect(self.pb_qqchat_click)
        self.pb_advanced.clicked.connect(self.pb_advanced_click)
        self.pb_showlog.clicked.connect(self.pb_showlog_click)
        self.pb_debug_tool.clicked.connect(self.pb_debug_tool_click)
        self.pb_coordinate_transformation.clicked.connect(self.pb_coordinate_transformation_click)
        self.pb_help.clicked.connect(self.pb_help_click)
        self.pb_customcommand.clicked.connect(self.pb_customcommand_click)
        self.pb_crashreport.clicked.connect(self.pb_crashreport_click)

    def pb_qqchat_click(self):
        webbrowser.open("https://pd.qq.com/s/942n1n6dc")

    @staticmethod
    def pb_advanced_click():
        advancedParameterWindowUi.retranslateUi(advancedParameterWindowUi)
        advancedParameterWindowUi.load_settings()
        advancedParameterWindowUi.show()

    @staticmethod
    def pb_debug_tool_click():
        debugWindowUi.retranslateUi(debugWindowUi)
        debugWindowUi.show()

    @staticmethod
    def pb_showlog_click():
        showLogWindowUi.retranslateUi(showLogWindowUi)
        showLogWindowUi.loading_settings()
        showLogWindowUi.show()

    @staticmethod
    def pb_help_click():
        webbrowser.open("https://x06w8gh3wwh.feishu.cn/wiki/JKjhwJBNFi6pj5kBoB1cS7HGnkU?from=from_copylink")

    @staticmethod
    def pb_customcommand_click():
        """编写自定义命令窗口"""
        customCommandWindowUi.show()

    @staticmethod
    def pb_coordinate_transformation_click():
        title = "警告"
        message = "此功能用于向下兼容分辨率，例如720p，请谨慎使用。\n是否继续？"
        confirm = win32api.MessageBox(0, message, title, win32con.MB_YESNO | win32con.MB_ICONWARNING)
        if confirm != 6:  # 点击确认
            return
        screen_width, screen_height, zoom_factor = get_screen_size()

        if cfg.getboolean("UPDATE", "rb_chinese"):
            lang = 'chinese'
        elif cfg.getboolean("UPDATE", "rb_english"):
            lang = 'english'
        else:
            lang = 'chinese'
        if screen_width == 1920 and screen_height == 1080 and zoom_factor == 1.0:
            if lang == "chinese":
                message = f"当前的屏幕分辨率为{screen_width}x{screen_height}，缩放为{int(zoom_factor * 100)}%，无需进行坐标转换。"
            else:
                message = (f"The current screen resolution is {screen_width}*{screen_height},\n"
                           f" and the zoom is {int(zoom_factor * 100)}%. No coordinate transf-\normation is required.")
            manager.sMessageBox(message, 'info')
            return
        else:
            if lang == "chinese":
                message = f"当前的屏幕分辨率为{screen_width}x{screen_height}，缩放为{int(zoom_factor * 100)}%。是否确定进行坐标转换？\n" \
                          f"请注意：如果你进行过参数修改，建议先备份SDargs.json文件。"
            else:
                message = (f"The current screen resolution is {screen_width}*{screen_height}, "
                           f"and the zoom is {int(zoom_factor * 100)}%. Do you want to perform coordinate transformation?\n"
                           f"Please note: If you have made any parameter modifications, \nit is recommended to backup SDargs.json file.")
        title = "坐标转换处理" if lang == "chinese" else "Coordinate Transformation"
        confirm = win32api.MessageBox(0, message, title, win32con.MB_YESNO | win32con.MB_ICONQUESTION)

        if eq(confirm, 6):  # 点击确认
            if self_defined_args['坐标转换开关'] == 1:
                manager.sMessageBox("你已进行过坐标转换，请勿重复进行！", 'error')
                return
            self_defined_args['坐标转换开关'] = 1
            # 找到包含"坐标"和"识别范围"的键
            keys_to_transform = [key for key in self_defined_args if '坐标' in key or '识别范围' in key]

            # 对这些键的值进行坐标转换
            for key in keys_to_transform:
                value = self_defined_args[key]
                # 假设所有的值都是列表形式的坐标或范围
                if isinstance(value, list) and len(value) > 1:  # 确保列表至少有两个元素
                    # 初始化一个空列表来存储转换后的坐标对
                    transformed_value = []
                    for i in range(0, len(value), 2):  # 步长为2，每次处理一对坐标
                        # 在访问 value[i + 1] 之前检查索引是否越界
                        if i + 1 < len(value):
                            original_x = value[i]
                            original_y = value[i + 1]
                            # 转换坐标对
                            new_x, new_y = coordinate_transformation(original_x, original_y)
                            # 将转换后的坐标对添加到列表中
                            transformed_value.extend([new_x, new_y])  # 使用 extend 来添加两个元素
                        else:
                            # 如果列表长度为奇数，处理最后一个元素
                            original_x = value[i]
                            new_x = coordinate_transformation(original_x, None)[0]
                            transformed_value.append(new_x)

                    # 更新self_defined_args中的值
                    self_defined_args[key] = transformed_value

            # 将更新后的键值对写回文件
            with open(SDAGRS_PATH, 'w', encoding='utf-8') as f:
                json.dump(self_defined_args, f, indent=4, ensure_ascii=False)

            message = "坐标转换已完成！" if lang == "chinese" else "Coordinate transformation is complete!"
            manager.sMessageBox(message, 'info')

    @staticmethod
    def pb_crashreport_click():
        crashReportWindowUi.loading_settings()
        crashReportWindowUi.show()


class ShowLog(QDialog, Ui_ShowLogDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(":log/picture/log.png"))

    def loading_settings(self):
        try:
            with open(LOG_PATH, 'r', encoding="utf-8") as f:
                self.te_showlog.setPlainText(f.read())
                print(f.read())
        except FileNotFoundError:
            manager.sMessageBox("\"debug_data.log\"文件不存在！", "error")
        except Exception as e:
            manager.sMessageBox(f"读取文件时出错:{e}", "error")


class DebugTool(QDialog, Ui_DebugDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(":debug/picture/tool.png"))

        self.initUI()
        self.init_signals()

    def initUI(self):
        self.pb_test.setIcon(QIcon(":mainwindow/picture/test.gif"))

        self.test_gif = GifButton(self.pb_test, ":mainwindow/picture/test.gif")

    def init_signals(self):
        self.pb_selection_region.clicked.connect(self.pb_selection_region_click)
        self.pb_test.clicked.connect(self.pb_test_click)

    def pb_selection_region_click(self):
        self.root = tk.Tk()
        self.selector = BoxSelector(self.root)
        self.root.mainloop()

    def pb_test_click(self):
        # 获取坐标和关键字
        if hwnd == 0:
            manager.sMessageBox('游戏未启动！', 'error')
            return
        coord_xy = self.le_coord.text()
        if not coord_xy:
            manager.sMessageBox("请先框选区域！", 'warning')
            return
        else:
            coordinates = [int(coord) for coord in coord_xy.split(",")]
            self.start_x, self.start_y, self.end_x, self.end_y = coordinates

        key_words = self.le_keywords.text().split(",")
        # print(key_words)
        if not key_words or all(not item.strip() for item in key_words):
            manager.sMessageBox("请输入关键字！", 'warning')
            return

        self.pe_result.clear()
        self.pe_result.appendPlainText(f"开始测试...\n- - - - - - - - -\n")
        self.pb_test.setDisabled(True)
        self.pb_selection_region.setDisabled(True)
        self.pb_test.setText("测试中")
        for sum_number in range(130, 20, -10):
            ocr_result = img_ocr(self.start_x, self.start_y, self.end_x, self.end_y,
                                 sum_number)
            if any(keyword in ocr_result for keyword in key_words):
                self.pe_result.appendPlainText(
                    f"识别成功！\nOCR内容为：{ocr_result}\n二值化值为：{sum_number}\n")
                break
            else:
                self.pe_result.appendPlainText(
                    f"未识别···\nOCR内容为：{ocr_result}\n二值化值为：{sum_number}\n")
            self.pe_result.ensureCursorVisible()
            # 添加延迟
            time.sleep(0.1)  # 等待0.1秒
            # 处理事件队列
            QCoreApplication.processEvents()
        self.pe_result.appendPlainText(f"- - - - - - - - -\n测试完成！")
        manager.sMessageBox('测试完成！', 'info')
        self.pb_test.setEnabled(True)
        self.pb_selection_region.setEnabled(True)
        self.pb_test.setText("测 试")


class CrashReport(QDialog, Ui_CrashReportDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(":mainwindow/picture/report.png"))

        self.init_signals()

    def init_signals(self):
        self.tb_save.clicked.connect(self.tb_save_click)

    def loading_settings(self):
        self.le_pivkey.setText(cfg["PIV"]["PIV_KEY"])

    def tb_save_click(self):
        piv_key = self.le_pivkey.text()
        if len(piv_key) < 20:
            manager.sMessageBox("无效的身份识别码！", "error")
            self.le_pivkey.clear()
            return
        else:
            manager.sMessageBox("认证成功！请重启软件。", "info")
            self.close()

        cfg["PIV"]["PIV_KEY"] = piv_key
        with open(CFG_PATH, 'w', encoding='utf-8') as configfile:
            cfg.write(configfile)

        cfg.read(CFG_PATH, encoding='utf-8')


class BoxSelector:
    def __init__(self, master):
        self.master = master
        master.overrideredirect(True)  # 移除窗口边框
        # 设置窗口置顶
        master.wm_attributes('-topmost', 1)
        # 获取屏幕宽度和高度，并移动窗口到屏幕左上角
        width = master.winfo_screenwidth()
        height = master.winfo_screenheight()
        master.geometry(f"{width}x{height}+0+0")
        # 设置窗口背景透明，如果不支持，将使用白色背景
        try:
            master.wm_attributes('-alpha', 0.3)
        except tk.TclError:
            master.configure(background='white')

        self.canvas = tk.Canvas(master, cursor="cross", bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind('<ButtonPress-1>', self.on_button_press)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_button_release)
        master.bind('<Button-3>', self.on_right_click)

        # 初始化坐标变量
        self.start_x = self.start_y = self.end_x = self.end_y = None
        self.rect_id = None

    def on_button_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        bright_red = "#FF0000"  # 鲜红色
        self.rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y,
                                                    outline=bright_red, width=2)

    def on_drag(self, event):
        if self.rect_id is not None:
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        if self.rect_id is not None:
            self.end_x, self.end_y = event.x, event.y
            self.master.destroy()  # 用户完成选框后退出窗口

        self.start_x, self.start_y = MControl.screen_to_client(self.start_x, self.start_y)
        self.end_x, self.end_y = MControl.screen_to_client(self.end_x, self.end_y)
        debugWindowUi.le_coord.setText(f"{self.start_x}, {self.start_y}, {self.end_x}, {self.end_y}")

    def on_right_click(self, event):
        # 清除 canvas 上的所有内容
        self.canvas.delete("all")
        # 重置起始和结束坐标
        self.start_x = self.start_y = self.end_x = self.end_y = None
        # 重置 rect_id
        self.rect_id = None
        self.master.destroy()


class CustomSelectKiller:
    def __init__(self):
        self.select_killer_lst = []
        self.match_select_killer_lst = []
        self.killer_name_array = []

    def select_killer_name_cn(self):
        """获取选取的杀手名称"""
        # 随版本更改
        # 此处append内容需与游戏中的名称一致
        # 创建一个字典，将配置项和对应的杀手名称进行映射
        killer_mapping_cn = {
            "cb_jiage": "设陷者",
            "cb_dingdang": "幽灵",
            "cb_dianjv": "农场主",
            "cb_hushi": "护士",
            "cb_tuzi": "女猎手",
            "cb_maishu": "迈克尔·迈尔斯",
            "cb_linainai": "妖巫",
            "cb_laoyang": "医生",
            "cb_babu": "食人魔",
            "cb_fulaidi": "梦魇",
            "cb_zhuzhu": "门徒",
            "cb_xiaochou": "小丑",
            "cb_lingmei": "怨灵",
            "cb_juntuan": "军团",
            "cb_wenyi": "瘟疫",
            "cb_guimian": "鬼面",
            "cb_mowang": "魔王",
            "cb_guiwushi": "鬼武士",
            "cb_qiangshou": "死亡枪手",
            "cb_sanjiaotou": "处刑者",
            "cb_kumo": "枯萎者",
            "cb_liantiying": "连体婴",
            "cb_gege": "骗术师",
            "cb_zhuizhui": "NEMESIS",
            "cb_dingzitou": "地狱修士",
            "cb_niaojie": "艺术家",
            "cb_zhenzi": "贞子",
            "cb_yingmo": "影魔",
            "cb_weishu": "操纵者",
            "cb_eqishi": "恶骑士",
            "cb_baigu": "白骨商人",
            "cb_jidian": "奇点",
            "cb_yixing": "异形",
            "cb_qiaji": "好孩子",
            "cb_ewu": "未知恶物",
            "cb_wuyao": "巫妖",
            "cb_degula": "黑暗之主"
        }
        # 遍历配置项，根据配置项添加对应的杀手名称到列表中
        for key, value in killer_mapping_cn.items():
            if cfg.getboolean("CUSSEC", key):
                self.select_killer_lst.append(value)

        if cfg.getboolean("SEKI", "usefile"):
            with open(CUSTOM_KILLER_PATH, "r", encoding='UTF-8') as search_file:
                self.select_killer_lst = search_file.readlines()
                self.select_killer_lst = [c.strip() for c in self.select_killer_lst]

    def select_killer_name_en(self):
        """获取选取的杀手名称"""
        # 随版本更改
        # 此处append内容需与游戏中的名称一致，去掉"THE"
        # 创建一个字典，将配置项和对应的杀手名称进行映射
        killer_mapping_en = {
            "cb_jiage": "TRAPPER",
            "cb_dingdang": "WRAITH",
            "cb_dianjv": "HILLBILLY",
            "cb_hushi": "NURSE",
            "cb_tuzi": "HUNTRESS",
            "cb_maishu": "SHAPE",
            "cb_linainai": "HAG",
            "cb_laoyang": "DOCTOR",
            "cb_babu": "CANNIBAL",
            "cb_fulaidi": "NIGHTMARE",
            "cb_zhuzhu": "PIG",
            "cb_xiaochou": "CLOWN",
            "cb_lingmei": "SPIRIT",
            "cb_juntuan": "LEGION",
            "cb_wenyi": "PLAGUE",
            "cb_guimian": "GHOST FACE",
            "cb_mowang": "DEMOGORGON",
            "cb_guiwushi": "ONI",
            "cb_qiangshou": "DEATHSLINGER",
            "cb_sanjiaotou": "EXECUTIONER",
            "cb_kumo": "BLIGHT",
            "cb_liantiying": "TWINS",
            "cb_gege": "TRICKSTER",
            "cb_zhuizhui": "NEMESIS",
            "cb_dingzitou": "CENOBITE",
            "cb_niaojie": "ARTIST",
            "cb_zhenzi": "ONRYO",
            "cb_yingmo": "DREDGE",
            "cb_weishu": "MASTERMIND",
            "cb_eqishi": "KNIGHT",
            "cb_baigu": "SKULL MERCHANT",
            "cb_jidian": "SINGULARITY",
            "cb_yixing": "XENOMORPH",
            "cb_qiaji": "GOOD GUY",
            "cb_ewu": "UNKNOWN",
            "cb_wuyao": "LICH",
            "cb_degula": "DARK LORD"
        }
        # 遍历配置项，根据配置项添加对应的杀手名称到列表中
        for key, value in killer_mapping_en.items():
            if cfg.getboolean("CUSSEC", key):
                self.select_killer_lst.append(value)

        if cfg.getboolean("SEKI", "usefile"):
            with open(CUSTOM_KILLER_PATH, "r", encoding='UTF-8') as search_file:
                self.select_killer_lst = search_file.readlines()
                self.select_killer_lst = [c.strip() for c in self.select_killer_lst]

    # def match_select_killer_name(self):
    #     """匹配选取的杀手名称在用户杀手列表中的位置"""
    #     if cfg.getboolean("SEKI", "usefile"):
    #         with open(CUSTOM_KILLER_PATH, "r", encoding='UTF-8') as search_file:
    #             self.select_killer_lst = search_file.readlines()
    #             self.select_killer_lst = [c.strip() for c in self.select_killer_lst]
    #         for i in self.select_killer_lst:
    #             self.match_select_killer_lst.append(self.killer_name_array.index(i) + 1)
    #     else:
    #         for i in self.select_killer_lst:
    #             self.match_select_killer_lst.append(self.killer_name_array.index(i) + 1)
    #
    # def read_search_killer_name(self):
    #     """读取检索文件"""
    #     with open(self.SEARCH_PATH, "r", encoding='UTF-8') as search_file:
    #         self.killer_name_array = search_file.readlines()
    #         self.killer_name_array = [c.strip() for c in self.killer_name_array]


class LogThread(QThread):
    new_data_signal = pyqtSignal(str)

    def __init__(self, log_file_path, parent=None):
        super().__init__(parent)
        self.log_file_path = log_file_path
        self.running = True

    def run(self):
        with open(self.log_file_path, 'r', encoding='utf-8') as file:
            file.seek(0, 2)  # Move to the end of the file
            while self.running:
                if not (line := file.readline()):
                    time.sleep(0.5)
                    continue
                self.new_data_signal.emit(line)

    def stop(self):
        self.running = False


class LogView(QMainWindow):
    start_thread_signal = pyqtSignal()
    ui_init_signal = pyqtSignal()

    def __init__(self, log_file_path):
        super().__init__()
        self.log_file_path = log_file_path

        self.ui_init_signal.connect(self.initUI)
        self.start_thread_signal.connect(self.start_log_reading)

    def initUI(self):
        game_window = MControl.get_window_rect()
        self.setGeometry(game_window.right - 210, game_window.top, 200, 175)
        self.setWindowOpacity(0.75)
        self.setWindowFlags(
            Qt.Tool |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.WindowDoesNotAcceptFocus |
            Qt.WindowTransparentForInput
        )
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.textEdit = QTextEdit(self)
        self.textEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        palette = QPalette(self.textEdit.palette())
        palette.setColor(QPalette.Base, Qt.white)  # 设置背景颜色为白色
        self.textEdit.setPalette(palette)
        self.textEdit.setAutoFillBackground(True)
        self.textEdit.setStyleSheet(f'background-color: rgba(255, 255, 255, 100); color: blue; font-size: 12px;')
        self.textEdit.setReadOnly(True)
        self.textEdit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.textEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.textEdit)
        central_widget = QWidget()
        central_widget.setLayout(layout)
        central_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCentralWidget(central_widget)

    def insert_text(self, line):
        cursor = self.textEdit.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(line)
        self.textEdit.ensureCursorVisible()

    def load_initial_log_content(self):
        with open(self.log_file_path, 'r', encoding='utf-8') as file:
            self.textEdit.append(file.read())

    def start_log_thread(self):
        self.start_thread_signal.emit()

    def start_log_reading(self):
        self.thread = LogThread(self.log_file_path, self)
        self.thread.new_data_signal.connect(self.insert_text)
        self.textEdit.clear()
        self.load_initial_log_content()
        self.show()
        self.thread.start()


class InputChinese:
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.codes_list = []

    def vkey_to_scan_code(self, key_code):
        return self.user32.MapVirtualKeyA(key_code, 0)

    def key_down(self, key_code, ext=False):
        ext_flg = 1 if ext else 0
        scan_code = self.vkey_to_scan_code(key_code)
        self.user32.keybd_event(key_code, scan_code, 0, 0)

    def key_up(self, key_code, ext=False):
        ext_flg = 1 if ext else 0
        scan_code = self.vkey_to_scan_code(key_code)
        self.user32.keybd_event(key_code, scan_code, 2, 0)

    def num_key_press(self, digit):
        key_code = {
            '0': 0x60, '1': 0x61, '2': 0x62, '3': 0x63,
            '4': 0x64, '5': 0x65, '6': 0x66, '7': 0x67,
            '8': 0x68, '9': 0x69, '+': 0x6B
        }.get(digit)

        if key_code is None:
            raise ValueError(f"Invalid digit: {digit}")
        self.key_down(key_code)
        self.key_up(key_code)

    def type_alt_code(self, code):
        try:
            self.key_down(0xA4)  # 模拟Alt键按下
            for digit in str(code):
                self.num_key_press(digit)  # 模拟数字小键盘按键
                time.sleep(0.001)  # 按键间隔
        finally:
            self.key_up(0xA4)  # 模拟Alt键释放

    def str_to_codes(self, string, encode):
        for char in string:
            char_bytes = char.encode(encode)
            self.codes_list.append(int.from_bytes(char_bytes, 'big'))

    def press_codes_with_alt(self, string, encode):
        self.str_to_codes(string, encode)
        for code in self.codes_list:
            self.type_alt_code(code)
        self.codes_list.clear()


class GifButton(QObject):
    def __init__(self, button, gif_path):
        super().__init__()
        self.button = button
        self.default_icon = QIcon(gif_path)
        self.movie = QMovie(gif_path)
        self.movie.setCacheMode(QMovie.CacheAll)
        self.movie.frameChanged.connect(self.updateIcon)
        self.button.installEventFilter(self)

    @pyqtSlot(int)
    def updateIcon(self, frame):
        self.button.setIcon(QIcon(self.movie.currentPixmap()))

    def eventFilter(self, obj, event):
        if obj == self.button:
            if event.type() == QEvent.Enter:
                self.movie.start()
                self.button.setIcon(QIcon(self.movie.currentPixmap()))
            elif event.type() == QEvent.Leave:
                self.movie.stop()
                self.button.setIcon(self.default_icon)
        return super().eventFilter(obj, event)


class Stage:
    def __init__(self):
        self.stage_name = ""
        self.entry_time = None  # 进入阶段的时间
        self.long_stay_switch = False
        self.log_recorded = False  # 是否记录日志

    def enter_stage(self, stage_name):
        """进入阶段时调用，记录进入时间"""
        self.stage_name = stage_name
        self.entry_time = time.time()
        self.long_stay_switch = False

    def check_stay_time(self, time_threshold: float):
        """检查是否长时间停留

        :param time_threshold: 阶段停留时间阈值，单位为秒
        """
        if self.entry_time:
            current_time = time.time()
            stay_duration = current_time - self.entry_time
            if stay_duration > time_threshold and not self.log_recorded:
                self.long_stay_switch = True
                self.log_recorded = True
                MControl.moveclick(10, 10)
                log.info(f"在'{self.stage_name}'阶段停留时间过长，触发BV循环")

    def exit_stage(self):
        """离开阶段时，重置开关"""
        self.entry_time = None  # 重置进入时间
        if self.long_stay_switch:
            log.info(f"成功！BV循环已关闭。")
        self.long_stay_switch = False
        self.log_recorded = False


def begin():
    """start the script"""
    global begin_state
    if not begin_state:
        open(LOG_PATH, 'w').close()
        save_cfg()
        if start_check():
            manager.sMessageBox("脚本已启动！正在运行中···", 'info')
            screen_age()
            move_window(hwnd, 0, 0)
            begin_state = True
            try:
                # 播放WAV文件
                play_str.play()
            except SimpleaudioError:
                pass
            event.clear()
            begingame = threading.Thread(target=afk, daemon=True)
            begingame.start()
            # 如果开启提醒，则开启线程
            if cfg.getboolean("CPCI", "rb_survivor") and cfg.getboolean("CPCI", "cb_survivor_do"):
                tip.start()
            # 开启日志显示窗口
            log_view.ui_init_signal.emit()
            log_view.start_log_thread()
    else:
        pass


def kill():
    """stop the script"""
    global begin_state
    if begin_state:
        try:
            # 播放WAV文件
            play_end.play()
        except SimpleaudioError:
            pass
        begin_state = False
        event.set()
        log.info(f"结束脚本····\n")
        manager.sMessageBox("脚本已停止！", 'info')
        log_view.thread.stop()
        # 等待线程安全退出
        log_view.thread.wait()
        log_view.close()


def initialize():
    """ 配置初始化 """
    # 检查配置文件是否存在，如果不存在则创建一个空文件
    if not os.path.exists(CFG_PATH):
        with open(CFG_PATH, 'w', encoding='UTF-8') as configfile:
            configfile.write("")
    # 生成配置字典
    settings_dict = {
        "CPCI": {
            "rb_survivor": False,
            "cb_survivor_do": False,
            "rb_killer": False,
            "cb_killer_do": False,
            "rb_fixed_mode": False,
            "rb_random_mode": False
        },
        "SEKI": {
            "usefile": False,
            "search_fix": False,
            "autoselect": False,
            "rb_pz1": False,
            "rb_pz2": False,
            "rb_pz3": False,
        },
        "CUCOM": {
            "cb_customcommand": False,
        },
        "UPDATE": {
            "cb_autocheck": True,
            "rb_chinese": True,
            "rb_english": False
        },
        "CUSSEC": {
            key: False for key in cussec_keys
        },
        "PIV": {
            "PIV_KEY": ""
        }
    }
    for section, options in settings_dict.items():
        if section not in cfg:
            cfg[section] = {}
        for option, value in options.items():
            if option not in cfg[section]:
                cfg[section][option] = str(value)
    with open(CFG_PATH, 'w') as configfile:
        cfg.write(configfile)

    # 检查自定义配置文件是否存在，如果不存在则创建一个空字典
    if not os.path.exists(SDAGRS_PATH):
        existing_args = {}
    else:
        # 文件存在，读取并加载现有内容
        with open(SDAGRS_PATH, 'r', encoding='utf-8') as f:
            existing_args = json.load(f)

    # 更新或添加新的键值对
    for key, value in self_defined_args.items():
        if key not in existing_args:
            existing_args[key] = value

    # 将更新后的键值对写回文件
    with open(SDAGRS_PATH, 'w', encoding='utf-8') as f:
        json.dump(existing_args, f, indent=4, ensure_ascii=False)

    # 检查自定义杀手文件是否存在，如果不存在则创建一个空文件
    if not os.path.exists(CUSTOM_KILLER_PATH):
        with open(CUSTOM_KILLER_PATH, 'w', encoding='UTF-8') as custom_file:
            custom_file.write("")

    # 检查自定义动作文件是否存在，如果不存在则创建一个空文件
    if not os.path.exists(CUSTOM_COMMAND_PATH):
        with open(CUSTOM_COMMAND_PATH, 'w', encoding='UTF-8') as custom_command_file:
            custom_command_file.write("")


def save_cfg():
    """ 保存配置文件 """
    for section, options in ui_components.items():
        if section not in cfg:
            cfg[section] = {}
        for option_name, ui_control in options.items():
            if option_name == "PIV_KEY":
                continue
            cfg[section][option_name] = str(ui_control.isChecked())
    with open(CFG_PATH, 'w', encoding='utf-8') as configfile:
        cfg.write(configfile)

    cfg.read(CFG_PATH, encoding='utf-8')


def read_cfg():
    """读取配置文件"""
    for section, keys in ui_components.items():
        if section == "PIV":
            continue
        for key, ui_control in keys.items():
            value = cfg.getboolean(section, key)
            ui_control.setChecked(value)
    if cfg.getboolean("CPCI", "rb_survivor"):
        dbdWindowUi.cb_survivor_do.setEnabled(True)
        dbdWindowUi.rb_fixed_mode.setDisabled(True)
        dbdWindowUi.rb_random_mode.setDisabled(True)
        dbdWindowUi.cb_killer_do.setDisabled(True)
        dbdWindowUi.pb_select_cfg.setDisabled(True)
    if cfg.getboolean("CPCI", "rb_killer"):
        dbdWindowUi.cb_survivor_do.setDisabled(True)
    if not cfg.getboolean("SEKI", "autoselect"):
        selectWindowUi.rb_pz1.setDisabled(True)
        selectWindowUi.rb_pz2.setDisabled(True)
        selectWindowUi.rb_pz3.setDisabled(True)

    # 读取self_defined_args内容
    try:
        with open(SDAGRS_PATH, mode='r', encoding='utf-8') as f:
            # 读取文件中的所有内容，并将其转换为一个字典
            existing_args = json.load(f)
            # 更新 self_defined_args 字典
            self_defined_args.update(existing_args)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        win32api.MessageBox(f"读取SDargs.json文件异常: {e}", "错误", win32con.MB_OK | win32con.MB_ICONWARNING)


def authorization(authorization_now: str):
    """check the authorization"""
    html_str = requests.get('https://gitee.com/kioley/DBD_AFK_TOOL').content.decode()
    authorization_new = re.search('title>(.*?)<', html_str, re.S).group(1)[21:]
    if ne(authorization_now, authorization_new):
        if cfg.getboolean("UPDATE", "rb_chinese"):
            win32api.MessageBox(0, "授权已过期", "授权失败", win32con.MB_OK | win32con.MB_ICONERROR)
            sys.exit(0)
        elif cfg.getboolean("UPDATE", "rb_english"):
            win32api.MessageBox(0, "Authorization expired", "Authorization failed",
                                win32con.MB_OK | win32con.MB_ICONERROR)
            sys.exit(0)


def check_update(ver_now: str):
    """check the update"""
    html_str = requests.get('https://gitee.com/kioley/DBD_AFK_TOOL').content.decode()
    ver_new = re.search('title>(.*?)<', html_str, re.S).group(1)[13:19]
    if cfg.getboolean("UPDATE", "rb_chinese"):
        lang = 'chinese'
    elif cfg.getboolean("UPDATE", "rb_english"):
        lang = 'english'
    else:
        lang = 'chinese'
    if ne(ver_now, ver_new):
        message = "检查到新版本，是否更新？" if lang == "chinese" else "Check the new version. Is it updated?"
        title = "检查更新" if lang == "chinese" else "Check for updates"
        confirm = win32api.MessageBox(0, message, title, win32con.MB_YESNO | win32con.MB_ICONQUESTION)
        if eq(confirm, 6):  # 打开
            webbrowser.open("https://pd.qq.com/s/942n1n6dc")
            subprocess.call("update.exe")
            sys.exit()


def check_ocr():
    """check if not ocr installed"""
    if cfg.getboolean("UPDATE", "rb_chinese"):
        lang = 'chinese'
    elif cfg.getboolean("UPDATE", "rb_english"):
        lang = 'english'
    else:
        lang = 'chinese'
    if not os.path.exists(CHECK_PATH):
        message = "未检查到运行环境，请进行初始化。" if lang == "chinese" else \
            "The running environment is not detected. Please initialize it."
        title = "检查环境" if lang == "chinese" else "Check the environment"
        confirm = win32api.MessageBox(0, message, title, win32con.MB_YESNO | win32con.MB_ICONQUESTION)
        if eq(confirm, 6):  # 打开
            subprocess.call("initialize.exe")
        else:
            sys.exit()


def notice(notice_now: str):
    """take a message"""
    html_str = requests.get('https://gitee.com/kioley/test-git').content.decode()
    notice_new = re.search('title>(.*?)<', html_str, re.S).group(1)[0:8]
    notice = re.search('title>(.*?)<', html_str, re.S).group(1)[9:]
    if ne(notice_now, notice_new):
        win32api.MessageBox(0, notice, "通知", win32con.MB_OK | win32con.MB_ICONINFORMATION)


def close_logger():
    """关闭日志记录器"""
    for handler in logging.root.handlers:
        if isinstance(handler, logging.FileHandler):
            handler.close()


def get_screen_size():
    """获取屏幕分辨率"""
    hDC = win32gui.GetDC(0)
    # 横向分辨率
    real_screen_width = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
    # 纵向分辨率
    real_screen_height = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
    screen_width = GetSystemMetrics(0)
    # screen_height = GetSystemMetrics(1)
    screen_scale_rate = round(real_screen_width / screen_width, 2)
    return real_screen_width, real_screen_height, screen_scale_rate


def screen_age():
    screen_size_width, screen_size_height, zoom_factor = get_screen_size()
    log.info(f"系统分辨率为：{screen_size_width}*{screen_size_height}，缩放为：{int(zoom_factor * 100)}%\n"
             f"\n---当前版本: {settingsWindowUi.lb_version.text().strip()}---\n")


def coordinate_transformation(original_x: int, original_y: Optional[int] = None) -> tuple:
    """坐标转换
    :param original_x: 原始坐标x
    :param original_y: 原始坐标y"""

    screen_size_width, screen_size_height, zoom_factor = get_screen_size()
    # 计算转换后的坐标
    new_x = round(original_x * screen_size_width / 1920)
    if original_y is not None:
        new_y = round(original_y * screen_size_height / 1080)
    else:
        new_y = None
    # print(f"转换后的坐标为：{new_x}, {new_y}")
    return new_x, new_y


def is_edcs_only(content: str):
    pattern = re.compile(r'^[A-Za-z0-9\s,.?!\"*/+\'()-]+$')
    return bool(pattern.match(content))


def auto_message() -> None:
    """对局结束后的自动留言"""
    py.press('enter')
    input_str = self_defined_args['赛后发送消息']
    if is_edcs_only(input_str):
        py.typewrite(input_str)
    else:
        input_cn.press_codes_with_alt(input_str, 'gbk')
    py.press('enter')
    time.sleep(0.5)


def hall_tip():
    """Child thread, survivor hall tip"""
    while True:
        if readyhall():
            for _ in range(3):
                if event.is_set():
                    return
                py.press('space')
                py.hotkey('ctrl', 'a')
                py.press('delete')
                input_str = self_defined_args['人类发送消息']
                if is_edcs_only(input_str):
                    py.typewrite(input_str)
                else:
                    input_cn = InputChinese()
                    input_cn.press_codes_with_alt(input_str, 'gbk')
                py.press('enter')
                time.sleep(15)


def autospace():
    """Child thread, auto press space"""
    while not stop_space:
        if not pause_event.is_set():
            pause_event.wait()
        else:
            key_down(hwnd, 'space')
            time.sleep(5)
            key_up(hwnd, 'space')


def move_window(hwnd, target_x, target_y):
    """
    使用win32api移动指定窗口到新的位置。
    :param hwnd: 窗口的句柄
    :param target_x: 新的x坐标位置
    :param target_y: 新的y坐标位置
    """
    try:
        # 移动窗口到新的位置
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, target_x, target_y, 0, 0, win32con.SWP_NOSIZE)
    except Exception as e:
        log.warning(f"移动窗口到新的位置失败：{e}")
        manager.sMessageBox(f"尝试以管理员权限运行脚本。", 'error')


def change_skill_allocation():
    if cfg.getboolean("SEKI", "autoselect"):
        MControl.moveclick(self_defined_args['装备配置按钮坐标'][0], self_defined_args['装备配置按钮坐标'][1], 1)
        if cfg.getboolean("SEKI", "rb_pz1"):
            MControl.moveclick(self_defined_args['装备配置1的坐标'][0], self_defined_args['装备配置1的坐标'][1], 1)
        if cfg.getboolean("SEKI", "rb_pz2"):
            MControl.moveclick(self_defined_args['装备配置2的坐标'][0], self_defined_args['装备配置2的坐标'][1], 1)
        if cfg.getboolean("SEKI", "rb_pz3"):
            MControl.moveclick(self_defined_args['装备配置3的坐标'][0], self_defined_args['装备配置3的坐标'][1], 1)


def action():
    """游戏内角色的动作行为"""
    rb_survivor = cfg.getboolean("CPCI", "rb_survivor")
    rb_fixed_mode = cfg.getboolean("CPCI", "rb_fixed_mode")
    rb_random_mode = cfg.getboolean("CPCI", "rb_random_mode")
    rb_killer = cfg.getboolean("CPCI", "rb_killer")
    while not stop_action:
        if not pause_event.is_set():
            pause_event.wait()
        else:
            if rb_survivor:
                survivor_action()
            elif rb_fixed_mode and rb_killer:
                killer_fixed_act()
            elif rb_random_mode and rb_killer:
                killer_action()


def listen_key():
    """快捷键监听"""

    def pause():
        global pause

        if not pause:
            try:
                # 播放WAV文件
                play_pau.play()
            except SimpleaudioError:
                pass
            log.info(f"脚本已暂停")
            pause = True
            pause_event.clear()
        elif pause:
            try:
                # 播放WAV文件
                play_res.play()
            except SimpleaudioError:
                pass
            log.info(f"脚本已恢复")
            pause = False
            pause_event.set()
        try:
            win32gui.SetForegroundWindow(hwnd)
        except Exception as ex:
            print(f"An error occurred: {ex}")

    try:
        keyboard.add_hotkey(self_defined_args['开始快捷键'][0], begin)
        keyboard.add_hotkey(self_defined_args['暂停快捷键'][0], pause)
        keyboard.add_hotkey(self_defined_args['停止快捷键'][0], kill)
        # 保持程序运行，监听键盘事件
        keyboard.wait()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # 清理，移除监听
        keyboard.remove_all_hotkeys()


def ocr_range_inspection(identification_key: str,
                         ocr_func: Callable,
                         capture_range: str,
                         min_sum_name: str,
                         name: str) -> Callable:
    """装饰器工厂，生成OCR识别函数，根据阈值范围和关键字进行识别
    :param identification_key: 关键字列表名称，str
    :param ocr_func: 图像识别函数，Callable
    :param capture_range: 自定义参数的名称，str
    :param min_sum_name: 最小阈值的名称，str
    :param name: 图片命名，str
    :return: Callable
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper():
            # x1 = self_defined_args[capture_range][0]
            # y1 = self_defined_args[capture_range][1]
            # x2 = self_defined_args[capture_range][2]
            # y2 = self_defined_args[capture_range][3]
            x1, y1, x2, y2 = self_defined_args[capture_range]
            threshold = self_defined_args[min_sum_name][0]
            threshold_high = self_defined_args[min_sum_name][1]
            keywords = self_defined_args[identification_key]
            if name == 'disconnect' and dbdWindowUi.cb_debug.isChecked():
                # 调试模式直接返回
                return False

            # 调用img_ocr函数，传入坐标和二值化阈值
            ocr_result = ocr_func(x1, y1, x2, y2, sum=threshold)
            if dbdWindowUi.cb_detailed_log.isChecked():
                log.debug(f"{name}.OCR 识别内容为：{ocr_result}")

            if any(keyword in ocr_result for keyword in keywords):

                if dbdWindowUi.cb_bvinit.isChecked() and self_defined_args[min_sum_name][2] == 0:
                    # if min_sum_name != '断线检测二值化阈值':
                    self_defined_args[min_sum_name][2] = 1
                    # 将更新后的键值对写回文件
                    with open(SDAGRS_PATH, 'w', encoding='utf-8') as f:
                        json.dump(self_defined_args, f, indent=4, ensure_ascii=False)

                return True
            elif ((dbdWindowUi.cb_bvinit.isChecked() and self_defined_args[min_sum_name][2] == 0) or
                  stage_monitor.long_stay_switch is True):

                new_threshold = threshold - 10  # 递减一个步长作为新的阈值
                if new_threshold < 30:  # 确保不低于停止值
                    new_threshold = threshold_high
                self_defined_args[min_sum_name][0] = new_threshold
                if dbdWindowUi.cb_detailed_log.isChecked():
                    log.debug(f"BV循环中···{name}的二值化阈值当前为：{new_threshold}")

            return False

        return wrapper

    return decorator


def img_ocr(x1, y1, x2, y2, sum=128) -> str:
    """OCR识别图像，返回字符串
    :return: string"""
    if hwnd == 0:
        manager.sMessageBox('未检测到游戏窗口！', 'warning')
        return ""
    result = ""
    image = screenshot(hwnd)
    if image is None:
        manager.sMessageBox('无效的截图区域，游戏或已崩溃！', 'error')
        log.warning(f"截图失败，无效的截图区域！")
        kill()
        return result

    screen_x1, screen_y1 = MControl.client_to_screen(x1, y1)
    screen_x2, screen_y2 = MControl.client_to_screen(x2, y2)

    # 按区域裁剪
    cropped_pixmap = image.crop((screen_x1, screen_y1, screen_x2, screen_y2))
    # 转换为灰度图
    grayscale_image = cropped_pixmap.convert('L')
    # 二值化
    binary_image = grayscale_image.point(lambda x: 255 if x > sum else 0, '1')

    custom_config = r'--oem 3 --psm 6'  # ocr识别模式
    # 判断中英文切换模型
    if cfg.getboolean("UPDATE", "rb_chinese"):
        lan = "chi_sim"
    elif cfg.getboolean("UPDATE", "rb_english"):
        lan = "eng"
    else:
        lan = "chi_sim+eng"  # 默认简体中文+英文

    try:
        # 创建一个临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_path = temp_file.name
            # 将二值化后的图像保存到临时文件
            binary_image.save(temp_path, format='JPEG')
            try:
                # 使用Tesseract OCR引擎识别图像中的文本
                result_unprocessed = pytesseract.image_to_string(temp_path, config=custom_config, lang=lan)
                if result_unprocessed:
                    result = "".join(result_unprocessed.split())
            except pytesseract.TesseractError:
                result = ""
    finally:
        # 确保临时文件被删除，防止内存泄露和磁盘空间占用
        os.unlink(temp_path)

    return result


@ocr_range_inspection('匹配大厅识别关键字',
                      img_ocr, '匹配阶段的识别范围', '匹配大厅二值化阈值', "play")
def starthall() -> bool:
    """check the start  hall
    :return: bool"""
    pass


@ocr_range_inspection('准备大厅识别关键字',
                      img_ocr, '准备阶段的识别范围', '准备房间二值化阈值', "ready")
def readyhall() -> bool:
    """check the  ready hall
    :return: bool"""
    pass


# @ocr_range_inspection('准备取消按钮识别关键字',
#                       img_ocr, '开始游戏、准备就绪按钮的识别范围', '准备取消按钮二值化阈值', "cancel")
# def readycancle() -> bool:
#     """检查游戏准备后的取消，消失就进入对局加载
#     :return: bool"""
#     pass


@ocr_range_inspection('结算页识别关键字',
                      img_ocr, '结算页的识别范围', '结算页二值化阈值', "gameover")
def gameover() -> bool:
    """检查对局结束
    :return: bool"""
    pass


@ocr_range_inspection('结算页每日祭礼识别关键字',
                      img_ocr, '结算页每日祭礼的识别范围', '结算页每日祭礼二值化阈值', "rites")
def rites() -> bool:
    """check rites complete
    :return:bool"""
    pass


# @ocr_range_inspection((130, 80, -10), ["每日祭礼", "DAILY RITUALS"])
# 检测活动奖励  #####未完成
# def event_rewards() -> bool:
#     """check the event rewards
#     :return: bool"""


@ocr_range_inspection('段位重置识别关键字',
                      img_ocr, '段位重置的识别范围', '段位重置二值化阈值', "reset")
def season_reset() -> bool:
    """check the season reset
    :return: bool"""
    pass


@ocr_range_inspection('主页面每日祭礼识别关键字',
                      img_ocr, '主界面的每日祭礼识别范围', '主页面每日祭礼二值化阈值', "daily_ritual_main")
def daily_ritual_main() -> bool:
    """check the daily task after serious disconnect -->[main]
    :return: bool
    """
    pass


@ocr_range_inspection('主页面识别关键字',
                      img_ocr, '主页面的识别范围', '主页面二值化阈值', "start")
def mainjudge() -> bool:
    """after serious disconnect.
    check the game whether return the main menu.
    :return: bool
    """
    pass


@ocr_range_inspection('断线检测识别关键字',
                      img_ocr, '断线检测的识别范围', '断线检测二值化阈值', "disconnect")
def disconnect_check() -> bool:
    """After disconnect check the connection status
    :return: bool"""
    pass


@ocr_range_inspection('新内容识别关键字',
                      img_ocr, '新内容的识别范围', '新内容二值化阈值', "news")
def news() -> bool:
    """断线重连后的新闻
    :return: bool"""
    pass


def disconnect_confirm(sum=120) -> None:
    """After disconnection click confirm button. not need process."""

    # 定义局部函数，用于获取按钮坐标
    def get_coordinates(result, target_string):
        for item in result:
            if target_string in item:
                target = result.index(item)
                # 确保不会越界，并且结果确实是数字
                if target + 2 < len(result) and result[target + 1].isdigit() and result[target + 2].isdigit():
                    confirmX, confirmY = int(result[target + 1]), int(result[target + 2])
                    return confirmX, confirmY
        return None, None

    # print(f"disconnect_confirm识别中···\n")
    result = ""
    disconnect_check_colorXY = self_defined_args['断线检测的识别范围']

    image = screenshot(hwnd)
    if image is None:
        manager.sMessageBox('无效的截图区域，游戏或已崩溃！', 'error')
        log.warning(f"截图失败，无效的截图区域！")
        kill()
        return

    screen_x1, screen_y1 = MControl.client_to_screen(disconnect_check_colorXY[0], disconnect_check_colorXY[1])
    screen_x2, screen_y2 = MControl.client_to_screen(disconnect_check_colorXY[2], disconnect_check_colorXY[3])
    # 按区域裁剪

    # 裁剪图像
    cropped = image.crop((screen_x1, screen_y1, screen_x2, screen_y2))

    # 转为灰度图像
    grayscale_image = cropped.convert('L')

    # 二值化
    binary_image = grayscale_image.point(lambda x: 0 if x < sum else 255, '1')

    custom_config = r'--oem 3 --psm 6'

    # 判断中英文切换模型
    if cfg.getboolean("UPDATE", "rb_chinese"):
        lan = "chi_sim"
    elif cfg.getboolean("UPDATE", "rb_english"):
        lan = "eng"
    else:
        lan = "chi_sim+eng"  # 默认简体中文+英文

    try:
        # 创建一个临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_path = temp_file.name
            # 将二值化后的图像保存到临时文件
            binary_image.save(temp_path, format='JPEG')
            try:
                # 使用Tesseract OCR引擎识别图像中的文本
                result_unprocessed = pytesseract.image_to_boxes(binary_image, config=custom_config, lang=lan)

                # 检查是否有识别结果
                if result_unprocessed:
                    result = result_unprocessed.split(' ')
            except pytesseract.TesseractError:
                return
    finally:
        # 确保临时文件被删除，防止内存泄露和磁盘空间占用
        os.unlink(temp_path)

    if dbdWindowUi.cb_detailed_log.isChecked():
        log.debug(f"断线确认识别内容为：{result}\n")

    # 定义需要查找的字符串列表
    target_strings = self_defined_args["断线确认关键字"]

    # 遍历目标字符串列表
    for target_string in target_strings:
        confirmx, confirmy = get_coordinates(result, target_string)
        if confirmx is not None and confirmy is not None:
            # print(f"disconnect_confirm已识别···")
            # 调用moveclick函数
            # print(f"关键字：{target_string},坐标：({confirmx}, {confirmy})")
            MControl.moveclick(disconnect_check_colorXY[0] + confirmx, disconnect_check_colorXY[3] - confirmy,
                               1, 1)
            # 找到了坐标，跳出循环
            break


def reconnect() -> bool:
    """Determine whether the peer is disconnected and return to the matching hall
    :return: bool -->TRUE
    """
    global stop_space, stop_action
    log.info(f"检测到游戏断线，进入重连···")
    time.sleep(1)
    stop_space = True  # 自动空格线程标志符
    stop_action = True  # 动作线程标志符
    if disconnect_check():
        for sum in range(130, 80, -10):
            disconnect_confirm(sum)
            if not disconnect_check():
                break

    # 检测以判断断线情况
    if starthall() or readyhall():  # 小退
        log.info(f"重连完成···类型：错误代码")
        return True
    elif gameover():  # 意味着不在大厅
        MControl.moveclick(self_defined_args['结算页继续按钮坐标'][0], self_defined_args['结算页继续按钮坐标'][1])
        log.info(f"重连完成···类型：错误代码")
        return True
    else:  # 大退

        main_quit = False
        stage_mointor = Stage()
        stage_mointor.enter_stage('大退重连')
        while not main_quit:
            if event.is_set():
                return True
            if not pause_event.is_set():
                pause_event.wait()
            if disconnect_check():
                for sum in range(130, 80, -10):
                    disconnect_confirm(sum)
                    if not disconnect_check():
                        break
            time.sleep(1)
            MControl.moveclick(10, 10, click_delay=1)  # 登录界面“按空格以继续”
            # 活动奖励 -> None
            # 判断新闻
            if news():
                MControl.moveclick(self_defined_args['新内容关闭坐标'][0], self_defined_args['新内容关闭坐标'][1],
                                   click_delay=1)
                log.info(f"重连---关闭新闻···")
            # 判断每日祭礼
            if daily_ritual_main():
                MControl.moveclick(self_defined_args['主页面祭礼关闭坐标'][0],
                                   self_defined_args['主页面祭礼关闭坐标'][1],
                                   click_delay=1)
                log.info(f"重连---关闭每日祭礼···")
            # 判断段位重置
            if season_reset():
                MControl.moveclick(self_defined_args['段位重置按钮的坐标'][0],
                                   self_defined_args['段位重置按钮的坐标'][1],
                                   click_delay=1)
                log.info(f"重连---关闭段位重置···")
            # 是否重进主页面判断
            if mainjudge():
                log.info(f"重连---正在返回匹配大厅···")
                MControl.moveclick(self_defined_args['主页面开始坐标'][0], self_defined_args['主页面开始坐标'][1],
                                   1)  # 点击开始
                # 通过阵营选择判断返回大厅
                if cfg.getboolean("CPCI", "rb_survivor"):
                    MControl.moveclick(self_defined_args['主页面逃生者坐标'][0],
                                       self_defined_args['主页面逃生者坐标'][1], 1)
                elif cfg.getboolean("CPCI", "rb_killer"):
                    MControl.moveclick(self_defined_args['主页面杀手坐标'][0], self_defined_args['主页面杀手坐标'][1],
                                       1)
                main_quit = True
            stage_mointor.check_stay_time(300)
            if gameover():  # 特殊情况处理
                MControl.moveclick(self_defined_args['结算页继续按钮坐标'][0],
                                   self_defined_args['结算页继续按钮坐标'][1])
                MControl.moveclick(10, 10, 1, 3)  # 避免遮挡
                main_quit = True
            if starthall() or readyhall():
                main_quit = True
        log.info(f"重连完成···类型：断线")
        stage_mointor.exit_stage()
        return True


def survivor_action() -> None:
    """survivor`s action"""

    # 执行自定义命令
    if cfg.getboolean("CUCOM", "cb_customcommand"):
        custom_command.execute_action_sequence("逃生者")
        return

    key_down(hwnd, 'w')
    key_down(hwnd, 'lshift')
    act_direction = random_direction()
    for i in range(10):
        key_down(hwnd, act_direction)
        time.sleep(0.05)
        key_up(hwnd, act_direction)
        time.sleep(0.7)
    py.mouseDown(button='left')
    time.sleep(2)
    py.mouseUp(button='left')
    key_up(hwnd, 'lshift')
    key_up(hwnd, 'w')


def killer_action() -> None:
    """killer integral action"""
    # 随版本更改，适配不同的屠夫
    ctrl_lst_cn = ["医生", "梦魇", "小丑", "魔王", "连体婴", "影魔", "白骨商人", "好孩子", "未知恶物", "巫妖"]
    need_lst_cn = ["门徒", "魔王", "死亡枪手", "骗术师", "NEMESIS", "地狱修士", "艺术家", "影魔", "奇点", "操纵者",
                   "好孩子", "未知恶物", "巫妖", "黑暗之主"]
    ctrl_lst_en = ["DOCTOR", "NIGHTMARE", "CLOWN", "DEMOGORGON", "TWINS", "DREDGE", "SKULL MERCHANT", "GOOD GUY",
                   "UNKNOWN", "LICH"]
    need_lst_en = ["PIG", "DEMOGORGON", "DEATHSLINGER", "TRICKSTER", "NEMESIS",
                   "CENOBITE", "ARTIST", "DREDGE", "SINGULARITY", "MASTERMIND", "GOOD GUY", "UNKNOWN",
                   "LICH", "DARK LORD"]
    ctrl_lst = []
    need_lst = []
    if cfg.getboolean("UPDATE", "rb_chinese"):
        ctrl_lst = ctrl_lst_cn
        need_lst = need_lst_cn
    elif cfg.getboolean("UPDATE", "rb_english"):
        ctrl_lst = ctrl_lst_en
        need_lst = need_lst_en
    # 防止下标越界
    killer_num = len(custom_select.select_killer_lst)
    if ge(index - 1, 0):  # index == character_num_index 更改名称
        killer_num = index - 1
    else:
        killer_num -= 1

    try:
        # 执行自定义命令
        if cfg.getboolean("CUCOM", "cb_customcommand"):
            custom_command.execute_action_sequence(custom_select.select_killer_lst[killer_num])
            if custom_command.common_actions or custom_command.current_character_match:
                return
    except IndexError:
        print(f"下标越界···{killer_num}")

    try:
        key_down(hwnd, 'w')
        if eq(custom_select.select_killer_lst[killer_num], "枯萎者") or eq(
                custom_select.select_killer_lst[killer_num], "BLIGHT"):
            key_up(hwnd, 'w')
            act_move = random_movement()
            key_down(hwnd, act_move)
            act_direction = random_direction()
            py.mouseDown(button='right')
            py.mouseUp(button='right')
            time.sleep(0.7)
            key_down(hwnd, act_direction)
            time.sleep(0.3)
            key_up(hwnd, act_direction)
            key_up(hwnd, act_move)
        elif eq(custom_select.select_killer_lst[killer_num], "怨灵") or eq(
                custom_select.select_killer_lst[killer_num], "SPIRIT"):
            key_up(hwnd, 'w')
            act_move = random_movement()
            key_down(hwnd, act_move)
            act_direction = random_direction()
            py.mouseDown(button='right')
            time.sleep(3)
            key_down(hwnd, act_direction)
            time.sleep(0.3)
            key_up(hwnd, act_direction)
            time.sleep(5)
            key_up(hwnd, act_move)
            py.mouseUp(button='right')
        elif custom_select.select_killer_lst[killer_num] in need_lst:
            act_direction = random_direction()
            for i in range(5):
                key_down(hwnd, act_direction)
                time.sleep(0.05)
                key_up(hwnd, act_direction)
                time.sleep(0.7)
            killer_skillclick(hwnd)
            if custom_select.select_killer_lst[killer_num] in ctrl_lst:
                killer_ctrl(hwnd)
        else:
            act_direction = random_direction()
            for i in range(5):
                key_down(hwnd, act_direction)
                time.sleep(0.05)
                key_up(hwnd, act_direction)
                time.sleep(0.7)
            killer_skill(hwnd)
            if custom_select.select_killer_lst[killer_num] in ctrl_lst:
                killer_ctrl(hwnd)
        key_up(hwnd, 'w')

    except IndexError:
        print(f"下标越界···{killer_num}")


def killer_fixed_act() -> None:
    """main blood"""
    # 防止下标越界
    killer_num = len(custom_select.select_killer_lst)
    if ge(index - 1, 0):  # index == character_num_index 更改名称
        killer_num = index - 1
    else:
        killer_num -= 1

    try:
        # 执行自定义命令
        if cfg.getboolean("CUCOM", "cb_customcommand"):
            custom_command.execute_action_sequence(custom_select.select_killer_lst[killer_num])
            if custom_command.common_actions or custom_command.current_character_match:
                return
    except IndexError:
        print(f"下标越界···{killer_num}")

    key_down(hwnd, 'w')
    killer_ctrl(hwnd)
    for i in range(4):
        move_time = round(random.uniform(1.5, 5.0), 3)
        random_move(hwnd, move_time)
        veertime = round(random.uniform(0.285, 0.6), 3)
        random_veer(hwnd, veertime)
        py.mouseDown(button='right')
        time.sleep(4)
        py.mouseUp(button='right')
        time.sleep(0.3)
    py.mouseDown()
    time.sleep(2)
    py.mouseUp()
    key_up(hwnd, 'w')


def character_selection() -> None:
    """自选特定的角色轮换"""
    global index
    log.info(f"执行角色选择···当前的角色为-->{custom_select.select_killer_lst[index]}")
    MControl.moveclick(10, 10, 0.5)
    MControl.moveclick(self_defined_args['角色选择按钮坐标'][0], self_defined_args['角色选择按钮坐标'][1], 1)
    MControl.moveclick(self_defined_args['搜索输入框坐标'][0], self_defined_args['搜索输入框坐标'][1], 1)
    input_str = custom_select.select_killer_lst[index]
    if event.is_set():
        return
    if not pause_event.is_set():
        pause_event.wait()
    if cfg.getboolean("SEKI", "search_fix"):
        pyperclip.copy(input_str)
        py.hotkey('ctrl', 'v')
    else:
        if is_edcs_only(input_str):
            py.typewrite(input_str)
        else:
            input_cn.press_codes_with_alt(input_str, 'gbk')

    MControl.moveclick(self_defined_args['第一个角色坐标'][0], self_defined_args['第一个角色坐标'][1], 1, times=2,
                       interval=1)
    MControl.moveclick(self_defined_args['角色选择按钮坐标'][0], self_defined_args['角色选择按钮坐标'][1], 1, times=2,
                       interval=1)

    if index < len(custom_select.select_killer_lst):
        index += 1
        if index == len(custom_select.select_killer_lst):
            index = 0


def start_check() -> bool:
    """启动脚本前的检查"""

    global hwnd, MControl
    hwnd = win32gui.FindWindow(None, u"DeadByDaylight  ")
    MControl = MouseController(hwnd)
    if cfg.getboolean("UPDATE", "rb_chinese"):
        custom_select.select_killer_name_cn()
        lang = "chinese"
    elif cfg.getboolean("UPDATE", "rb_english"):
        custom_select.select_killer_name_en()
        lang = "english"
    else:
        lang = "chinese"

    # 判断游戏是否运行
    if eq(hwnd, 0):
        message = "未检测到游戏窗口，请先启动游戏！" if lang == "chinese" else \
            "The game window was not detected. Please start the game first!"
        manager.sMessageBox(message, "warning")
        return False
    else:
        real_screen_width, real_screen_height, screen_scale_rate = get_screen_size()
        left, top, right, bottom = win32gui.GetClientRect(hwnd)
        # 计算窗口的宽度和高度
        width = right - left
        height = bottom - top
        if real_screen_width >= 1920 and real_screen_height >= 1080 and width != 1920 and height != 1080:
            message = f"请将游戏窗口调整为<1920×1080> 分辨率，当前分辨率为<{width}×{height}>" if lang == "chinese" else \
                f"Please adjust the game window to <1920×1080> resolution, current resolution is <{width}×{height}>"
            manager.sMessageBox(message, "warning", 5000)
            return False

    # 判断阵营选择
    if not dbdWindowUi.rb_killer.isChecked() and not dbdWindowUi.rb_survivor.isChecked():
        message = "请选择阵营！" if lang == "chinese" else "Please select the camp!"
        manager.sMessageBox(message, "warning")
        return False

    # 判断行为模式选择
    if (not dbdWindowUi.rb_fixed_mode.isChecked() and not dbdWindowUi.rb_random_mode.isChecked()
            and dbdWindowUi.rb_killer.isChecked()):
        message = "请选择行为模式！" if lang == "chinese" else "Please select the mode!"
        manager.sMessageBox(message, "warning")
        return False

    # 判断角色选择是否规范
    if (not custom_select.select_killer_lst and cfg.getboolean("CPCI", "rb_killer")
            and not cfg.getboolean("SEKI", "usefile")):
        message = "至少选择一个屠夫！" if lang == "chinese" else "Choose at least one killer!"
        manager.sMessageBox(message, "warning")
        return False

    # 使用外部文件时的判断
    if eq(os.path.getsize(CUSTOM_KILLER_PATH), 0) and cfg.getboolean("SEKI", "usefile"):
        message = "外部文件至少写入一个屠夫！" if lang == "chinese" else "External files are written to at least one killer!"
        manager.sMessageBox(message, "warning")
        return False

    MControl.moveclick(10, 10)
    log.info(f"启动脚本····\n")
    return True


def afk() -> None:
    """挂机主体函数"""
    global stop_space, stop_action, index
    list_number = len(custom_select.select_killer_lst)
    circulate_number = 0
    win32gui.SetForegroundWindow(hwnd)
    while True:
        reconnection = False
        circulate_number += 1
        '''
        匹配
        '''
        matching = False
        stage_monitor.enter_stage('匹配')
        while not matching:
            if event.is_set():
                break
            if not pause_event.is_set():
                pause_event.wait()

            # 判断条件是否成立
            if starthall():
                stage_monitor.exit_stage()
                log.info(f"第{circulate_number}次脚本循环---进入匹配大厅···")
                if cfg.getboolean("CPCI", "rb_killer"):
                    if eq(list_number, 1):
                        character_selection()
                        list_number = 0
                    elif gt(list_number, 1):
                        character_selection()
                    if circulate_number <= len(custom_select.select_killer_lst):
                        change_skill_allocation()
                elif cfg.getboolean("CPCI", "rb_survivor"):
                    time.sleep(1)

                while not matching:
                    if event.is_set():
                        break
                    if not pause_event.is_set():
                        pause_event.wait()
                    MControl.moveclick(self_defined_args['开始游戏按钮的坐标'][0],
                                       self_defined_args['开始游戏按钮的坐标'][1], 1)
                    MControl.moveclick(20, 689, 1, 5)  # 商城上空白
                    if not starthall():
                        matching = True
                        log.info(f"第{circulate_number}次脚本循环---开始匹配!")
            elif disconnect_check():
                reconnection = reconnect()
                matching = True
                stage_monitor.exit_stage()

            stage_monitor.check_stay_time(600)

        # 重连返回值的判断
        if reconnection:
            continue

        '''
        准备加载
        '''
        # ready_load = False  # debug:False -->True
        # while not ready_load:
        #     if event.is_set():
        #         break
        #     if not pause_event.is_set():
        #         pause_event.wait()
        #     if not readycancle():
        #         ready_load = True

        '''
        准备
        '''
        ready_room = dbdWindowUi.cb_debug.isChecked()
        stage_monitor.enter_stage('准备')
        if ready_room:
            stage_monitor.exit_stage()
        while not ready_room:
            if event.is_set():
                break
            if not pause_event.is_set():
                pause_event.wait()

            if readyhall():
                stage_monitor.exit_stage()
                log.info(f"第{circulate_number}次脚本循环---进入准备大厅···")
                MControl.moveclick(10, 10, 1)
                MControl.moveclick(self_defined_args['准备就绪按钮的坐标'][0],
                                   self_defined_args['准备就绪按钮的坐标'][1], 1)
                MControl.moveclick(20, 689, 1, 3)  # 商城上空白
                if not readyhall():
                    ready_room = True
                    log.info(f"第{circulate_number}次脚本循环---准备完成!")
            elif disconnect_check():
                reconnection = reconnect()
                ready_room = True
                stage_monitor.exit_stage()
            stage_monitor.check_stay_time(600)
        # 重连返回值判断
        if reconnection:
            continue

        '''
        游戏载入
        '''

        # game_load = False
        # while not game_load:
        #     if event.is_set():
        #         break
        #     if not pause_event.is_set():
        #         pause_event.wait()
        #     if not readycancle():
        #         game_load = True
        #         time.sleep(5)

        '''
        局内与局后
        '''
        auto_space = threading.Thread(target=autospace, daemon=True)
        auto_action = threading.Thread(target=action, daemon=True)
        stop_space = False  # 自动空格线程标志符
        stop_action = False  # 动作线程标志符
        auto_space.start()
        auto_action.start()
        game = False
        log.info(f"第{circulate_number}次脚本循环---进入对局···")
        stage_monitor.enter_stage('结算')
        while not game:
            if event.is_set():
                break
            if not pause_event.is_set():
                pause_event.wait()

            # 判断段位重置
            if season_reset():
                MControl.moveclick(self_defined_args['段位重置按钮的坐标'][0],
                                   self_defined_args['段位重置按钮的坐标'][1], click_delay=1)
            # 祭礼完成
            if rites():
                MControl.moveclick(self_defined_args['结算页祭礼完成坐标'][0],
                                   self_defined_args['结算页祭礼完成坐标'][1], 0.5, 1)
                MControl.moveclick(self_defined_args['结算页祭礼完成坐标'][2],
                                   self_defined_args['结算页祭礼完成坐标'][3])

            if gameover():
                stage_monitor.exit_stage()
                log.info(f"第{circulate_number}次脚本循环---游戏结束···")
                stop_space = True  # 自动空格线程标志符
                stop_action = True  # 动作线程标志符
                MControl.moveclick(10, 10, 1, 1)
                # 删除动作线程的输入字符
                py.press('enter')
                py.hotkey('ctrl', 'a')
                py.press('delete')
                # 判断是否开启留言
                if (cfg.getboolean("CPCI", "cb_killer_do")
                        and cfg.getboolean("CPCI", "rb_killer")):
                    auto_message()
                MControl.moveclick(self_defined_args['结算页继续按钮坐标'][0],
                                   self_defined_args['结算页继续按钮坐标'][1], 0.5, 1)  # return hall
                MControl.moveclick(10, 10, 1, 3)  # 避免遮挡
                if not gameover():
                    game = True
                    log.info(f"第{circulate_number}次脚本循环---正在返回匹配大厅···\n")
                elif disconnect_check():
                    reconnection = reconnect()
                    game = True
            else:
                if disconnect_check():
                    reconnection = reconnect()
                    game = True
                    stage_monitor.exit_stage()
            stage_monitor.check_stay_time(900)

        # 重连返回值判断
        if reconnection:
            continue

        if event.is_set():
            stop_space = True  # 自动空格线程标志符
            stop_action = True  # 动作线程标志符
            index = 0  # 列表的下标归零
            custom_select.select_killer_lst.clear()
            return


def resource_path(relative_path):
    try:
        # PyInstaller创建的临时文件夹
        base_path = sys._MEIPASS
    except Exception:
        # 如果不是通过PyInstaller运行，则使用当前工作目录
        base_path = os.path.join(BASE_DIR, "picture")

    return os.path.join(base_path, relative_path)


def sentry_ignore_error():
    """获取sentry的过滤列表"""
    html_str = requests.get('https://gitee.com/kioley/sentryig').content.decode()
    ignore_error = re.search('title>(.*?)<', html_str, re.S).group(1)[9:]
    ignore_error_list = [item.strip() for item in ignore_error.split(',')]
    return ignore_error_list


def sentry_init(dsn1: str, dsn2: str):
    html_str = requests.get('https://gitee.com/kioley/sentryit').content.decode()
    sentry_dsn_check = re.search('title>(.*?)<', html_str, re.S).group(1)[9:]
    if sentry_dsn_check == '1':
        dsn = dsn1
    else:
        dsn = dsn2

    PivKey = cfg['PIV']['PIV_KEY']
    user_context = {
        'id': PivKey,
        'version': settingsWindowUi.lb_version.text().strip()
    }

    sentry_sdk.init(
        dsn=dsn,
        integrations=[LoggingIntegration()],
        send_default_pii=True,
        ignore_errors=sentry_ignore_error(),
    )

    with sentry_sdk.configure_scope() as scope:
        scope.set_user(user_context)


def is_admin():
    if (BASE_DIR.startswith("C:") or BASE_DIR.startswith("c:")) and not ctypes.windll.shell32.IsUserAnAdmin():
        win32api.MessageBox(0, "请以管理员身份运行程序!", "提示", win32con.MB_OK | win32con.MB_ICONWARNING)
        sys.exit()


def global_exception(exctype, value, traceback):
    logging.error("未捕获的异常", exc_info=(exctype, value, traceback))


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
    is_admin()
    CHECK_PATH = os.path.join(BASE_DIR, "tesseract-ocr")
    OCR_PATH = os.path.join(BASE_DIR, "tesseract-ocr", "tesseract.exe")
    TESSDATA_PREFIX = os.path.join(BASE_DIR, "tesseract-ocr", "tessdata")
    CFG_PATH = os.path.join(BASE_DIR, "cfg.cfg")
    CUSTOM_KILLER_PATH = os.path.join(BASE_DIR, "custom_killer.txt")
    SDAGRS_PATH = os.path.join(BASE_DIR, "SDargs.json")
    LOG_PATH = os.path.join(BASE_DIR, "debug_data.log")
    CUSTOM_COMMAND_PATH = os.path.join(BASE_DIR, "custom_command.txt")

    os.environ['OCR'] = OCR_PATH
    os.environ['TESSDATA_PREFIX'] = TESSDATA_PREFIX
    os.environ['NO_PROXY'] = 'gitee.com'

    hwnd = win32gui.FindWindow(None, u"DeadByDaylight  ")
    py.FAILSAFE = False

    # 自定义参数
    self_defined_args = {'赛后发送消息': 'DBD-AFK League',
                         '人类发送消息': 'AFK',
                         '开始快捷键': ['alt+home'],
                         '暂停快捷键': ['f9'],
                         '停止快捷键': ['alt+end'],
                         '角色选择按钮坐标': [139, 93],
                         '第一个角色坐标': [366, 402],
                         '搜索输入框坐标': [666, 254],
                         '装备配置按钮坐标': [140, 200],
                         '装备配置1的坐标': [900, 60],
                         '装备配置2的坐标': [950, 60],
                         '装备配置3的坐标': [1000, 60],
                         '匹配阶段的识别范围': [1446, 771, 1920, 1080],
                         '匹配大厅二值化阈值': [120, 130, 1],
                         '匹配大厅识别关键字': ["开始游戏", "PLAY"],
                         '开始游戏按钮的坐标': [1742, 931],
                         '准备阶段的识别范围': [1446, 771, 1920, 1080],
                         '准备房间二值化阈值': [120, 130, 1],
                         '准备大厅识别关键字': ["准备就绪", "READY"],
                         '准备就绪按钮的坐标': [1742, 931],
                         '结算页的识别范围': [56, 46, 370, 172],
                         '结算页二值化阈值': [70, 130, 1],
                         '结算页识别关键字': ["比赛", "得分", "你的", "MATCH", "SCORE"],
                         '结算页继续按钮坐标': [1761, 1009],
                         '结算页每日祭礼的识别范围': [106, 267, 430, 339],
                         '结算页每日祭礼二值化阈值': [120, 130, 1],
                         '结算页每日祭礼识别关键字': ["每日", "DAILY RITUALS"],
                         '结算页祭礼完成坐标': [396, 718, 140, 880],
                         '段位重置的识别范围': [192, 194, 426, 291],
                         '段位重置二值化阈值': [120, 130, 1],
                         '段位重置识别关键字': ["重置", "RESET"],
                         '段位重置按钮的坐标': [1468, 843],
                         '断线检测的识别范围': [457, 530, 1488, 796],
                         '断线检测二值化阈值': [110, 130, 1],
                         '断线检测识别关键字': ["好的", "关闭", "CLOSE", "继续", "CONTINUE"],
                         '断线确认关键字': ["好", "关", "继", "K", "C"],
                         '主界面的每日祭礼识别范围': [441, 255, 666, 343],
                         '主页面每日祭礼二值化阈值': [120, 130, 1],
                         '主页面每日祭礼识别关键字': ["每日", "DAILY RITUALS"],
                         '主页面祭礼关闭坐标': [545, 880],
                         '主页面的识别范围': [203, 78, 365, 135],
                         '主页面二值化阈值': [120, 130, 1],
                         '主页面识别关键字': ["开始", "PLAY"],
                         '主页面开始坐标': [320, 100],
                         '主页面逃生者坐标': [339, 320],
                         '主页面杀手坐标': [328, 224],
                         '新内容的识别范围': [548, 4, 1476, 256],
                         '新内容二值化阈值': [120, 130, 1],
                         '新内容识别关键字': ["新内容", "NEW CONTENT"],
                         '新内容关闭坐标': [1413, 992],
                         '坐标转换开关': 0,
                         'event_rewards': ["-"],  # 未完成的事件奖励,留空即可
                         }
    self_defined_args_original = copy.deepcopy(self_defined_args)

    # UI设置
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    dbdWindowUi = DbdWindow()
    selectWindowUi = SelectWindow()
    customSelectWindowUi = Custom_select()
    customCommandWindowUi = CustomCommand()
    advancedParameterWindowUi = AdvancedParameter()
    settingsWindowUi = Settings()
    showLogWindowUi = ShowLog()
    debugWindowUi = DebugTool()
    crashReportWindowUi = CrashReport()

    # 配置文件参数
    cpci_keys = [
        "rb_survivor",
        "cb_survivor_do",
        "rb_killer",
        "cb_killer_do",
        "rb_fixed_mode",
        "rb_random_mode"
    ]
    cpci_dict = {key: getattr(dbdWindowUi, key) for key in cpci_keys}

    seki_keys = [
        "usefile",
        "search_fix",
        "autoselect",
        "rb_pz1",
        "rb_pz2",
        "rb_pz3",
    ]
    seki_dict = {key: getattr(selectWindowUi, key) for key in seki_keys}

    cucom_keys = [
        "cb_customcommand"
    ]
    cucom_dict = {key: getattr(customCommandWindowUi, key) for key in cucom_keys}

    update_keys = [
        "cb_autocheck",
        "rb_chinese",
        "rb_english"
    ]
    update_dict = {key: getattr(dbdWindowUi, key) for key in update_keys}

    # 提取 CUSSEC 部分的配置 [# 随版本更改]
    cussec_keys = [
        "cb_" + key for key in [
            "jiage", "dingdang", "dianjv", "hushi", "tuzi", "maishu", "linainai", "laoyang",
            "babu", "fulaidi", "zhuzhu", "xiaochou", "lingmei", "juntuan", "wenyi", "guimian",
            "mowang", "guiwushi", "qiangshou", "sanjiaotou", "kumo", "liantiying", "gege",
            "zhuizhui", "dingzitou", "niaojie", "zhenzi", "yingmo", "weishu", "eqishi",
            "baigu", "jidian", "yixing", "qiaji", "ewu", "wuyao", "degula"
        ]
    ]
    cussec_dict = {key: getattr(selectWindowUi, key) for key in cussec_keys}

    piv_key = [
        "PIV_KEY"
    ]
    piv_dict = {"PIV_KEY": ''}

    # 合并所有部分到最终的 ui_components
    ui_components = {
        "CPCI": cpci_dict,
        "SEKI": seki_dict,
        "CUCOM": cucom_dict,
        "UPDATE": update_dict,
        "CUSSEC": cussec_dict,
        "PIV": piv_dict
    }
    cfg = ConfigParser()  # 配置文件
    cfg.read(CFG_PATH, encoding='utf-8')

    initialize()  # 初始化cfg
    read_cfg()

    sentry_init(
        "https://cedb96910714cd07d682f1fead495553@o4507677044506624.ingest.de.sentry.io/4507677065347152",
        "https://c4ccce3bbe650bd9b3c897084d11c2d2@o4507677203038208.ingest.de.sentry.io/4507677302259792")  # 崩溃报告

    play_str = WaveObject.from_wave_file(resource_path("start.wav"))
    play_pau = WaveObject.from_wave_file(resource_path("pause.wav"))
    play_res = WaveObject.from_wave_file(resource_path("resume.wav"))
    play_end = WaveObject.from_wave_file(resource_path("close.wav"))

    # 配置日志格式
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    file_handler = logging.FileHandler(LOG_PATH, encoding='utf-8')  # 配置文件处理器，将日志写入文件
    file_handler.setLevel(logging.DEBUG)  # 设置处理器的日志级别
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)
    log = logging.getLogger(__name__)  # 获取日志记录器对象
    log.setLevel(logging.DEBUG)  # 设置记录器的日志级别
    log.addHandler(file_handler)
    atexit.register(close_logger)  # 程序退出时关闭日志
    sys.excepthook = global_exception  # 全局未捕获异常捕获

    # 实例声明
    input_cn = InputChinese()
    MControl = MouseController(hwnd)
    manager = NotificationManager()
    custom_command = ActionExecutor(CUSTOM_COMMAND_PATH, hwnd)
    log_view = LogView(LOG_PATH)

    if QLocale.system().language() != QLocale.Chinese or cfg.getboolean("UPDATE", "rb_english"):
        dbdWindowUi.rb_english_change()
    custom_select = CustomSelectKiller()
    stage_monitor = Stage()
    screen = QApplication.primaryScreen()
    begin_state = False  # 开始状态
    index = 0  # 列表的下标
    # 动作标志
    pause = False  # 监听暂停标志
    stop_thread = False  # 检查tip标志
    stop_space = False  # 自动空格标志
    stop_action = False  # 执行动作标志
    # 创建子线程
    event = threading.Event()
    event.set()
    pause_event = threading.Event()
    pause_event.set()
    hotkey = threading.Thread(target=listen_key, daemon=True)
    tip = threading.Thread(target=hall_tip, daemon=True)
    pytesseract.pytesseract.tesseract_cmd = OCR_PATH  # 配置OCR路径
    notice('test gic')  # 通知消息
    authorization('~x&amp;mBGbIneqSS(')  # 授权验证
    hotkey.start()  # 热键监听
    check_ocr()  # 检查初始化
    if cfg.getboolean("UPDATE", "cb_autocheck"):  # 检查更新
        check_update('V5.2.6')
    dbdWindowUi.show()
    sys.exit(app.exec_())

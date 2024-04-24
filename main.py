# -*- mode: python ; coding: utf-8 -*-
import atexit
import functools
import glob
import json
import os.path
import random
import subprocess
import sys
import threading
import time
import webbrowser
import pyautogui as py
import tkinter as tk
import pytesseract
import re
import requests
import win32api
import win32con
import win32gui
import keyboard
import logging
from configparser import ConfigParser
from operator import lt, eq, gt, ge, ne, floordiv, mod
from PIL import Image
from PyQt5.QtCore import QTranslator, QLocale, Qt, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from configobj import ConfigObj
from DBDAutoScriptUI import Ui_MainWindow
from selec_killerUI import Ui_Dialog
from AdvancedParameterUI import Ui_AdvancedWindow
from TipForm import Ui_TipForm
from ShowLog import Ui_ShowLogDialog
from DebugTool import Ui_DebugDialog
from keyboard_operation import key_down, key_up
from simpleaudio import WaveObject
from typing import Callable


def begin():
    global begin_state
    cfg.read(CFG_PATH, encoding='utf-8')
    if not begin_state:
        open(LOG_PATH, 'w').close()
        save_cfg()
        if start_check():
            screen_age()
            begin_state = True
            # 播放WAV文件
            play_str.play()
            event.clear()
            begingame = threading.Thread(target=afk, daemon=True)
            begingame.start()
            # 如果开启提醒，则开启线程
            if cfg.getboolean("CPCI", "rb_survivor") and cfg.getboolean("CPCI", "cb_survivor_do"):
                tip.start()
    else:
        pass


def kill():
    global begin_state
    # 播放WAV文件
    play_end.play()
    del_jpg()
    begin_state = False
    event.set()
    log.info(f"结束脚本····\n")


def del_jpg():
    # 获取当前目录下所有的.jpg文件
    jpg_files = glob.glob('*.jpg')
    # 遍历文件列表并尝试删除每个文件
    for file in jpg_files:
        try:
            # 尝试删除文件
            os.remove(file)
            # print(f"成功删除文件: {file}")
        except OSError as e:
            # 如果文件正在被其他进程使用，通常会抛出PermissionError
            print(f"退出时删除文件时出错: {file} - {e.strerror}\n")


class DbdWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.main_ui = Ui_MainWindow()
        self.trans = QTranslator()
        self.main_ui.setupUi(self)
        self.setWindowIcon(QIcon("picture\\dbdwindow.png"))

        self.init_signals()

    def init_signals(self):
        #  初始化信号和槽连接
        self.main_ui.pb_select_cfg.clicked.connect(self.pb_select_cfg_click)
        self.main_ui.pb_search.clicked.connect(self.pb_search_click)
        self.main_ui.pb_start.clicked.connect(begin)
        self.main_ui.pb_stop.clicked.connect(kill)
        self.main_ui.pb_github.clicked.connect(self.github)
        self.main_ui.rb_chinese.clicked.connect(self.rb_chinese_change)
        self.main_ui.rb_english.clicked.connect(self.rb_english_change)
        self.main_ui.pb_help.clicked.connect(self.pb_help_click)
        self.main_ui.cb_bvinit.clicked.connect(self.cb_bvinit_click)
        self.main_ui.pb_advanced.clicked.connect(self.pb_advanced_click)
        self.main_ui.pb_showlog.clicked.connect(self.pb_showlog_click)
        self.main_ui.pb_debug_tool.clicked.connect(self.pb_debug_tool_click)


    @staticmethod
    def pb_search_click():
        tf_widget.tipform_ui.retranslateUi(tf_widget)
        tf_widget.loading_settings()
        tf_widget.show()

    @staticmethod
    def pb_help_click():
        webbrowser.open("https://x06w8gh3wwh.feishu.cn/wiki/JKjhwJBNFi6pj5kBoB1cS7HGnkU?from=from_copylink")

    @staticmethod
    def github():
        webbrowser.open("https://github.com/maskrs/DBD_AFK_TOOL")

    def pb_select_cfg_click(self):
        sel_dialog.select_ui.retranslateUi(sel_dialog)
        sel_dialog.exec_()

    @staticmethod
    def pb_advanced_click():
        adv_dialog.advanced_ui.retranslateUi(adv_dialog)
        adv_dialog.exec_()

    @staticmethod
    def pb_debug_tool_click():
        debug_dialog.debugtool_ui.retranslateUi(debug_dialog)
        debug_dialog.exec_()

    def rb_chinese_change(self):
        # 默认的中文包，不要新建
        self.trans.load('zh_CN')
        _app = QApplication.instance()
        _app.installTranslator(self.trans)
        self.main_ui.retranslateUi(self)
        self.main_ui.lb_message.show()
        save_cfg()
        cfg.read(CFG_PATH, encoding='utf-8')

    def rb_english_change(self):
        # 导入语言包，english是翻译的.qm文件
        self.trans.load(TRANSLATE_PATH)
        _app = QApplication.instance()
        _app.installTranslator(self.trans)
        self.main_ui.retranslateUi(self)
        self.main_ui.lb_message.show()
        save_cfg()
        cfg.read(CFG_PATH, encoding='utf-8')

    def cb_bvinit_click(self):
        """重置二值化校准开关"""
        keys_to_update = [
            '匹配大厅二值化阈值',
            '准备房间二值化阈值',
            '结算页二值化阈值',
            '结算页每日祭礼二值化阈值',
            '段位重置二值化阈值',
            '主页面每日祭礼二值化阈值',
            '主页面开始按钮二值化阈值',
            '断线检测二值化阈值',
            '新内容二值化阈值',
            '准备取消按钮二值化阈值'
        ]
        if self.main_ui.cb_bvinit.isChecked():
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

    @staticmethod
    def pb_showlog_click():
        shl_dialog.showlog_ui.retranslateUi(shl_dialog)
        shl_dialog.loading_settings()
        shl_dialog.exec_()




class SelectWindow(QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.select_ui = Ui_Dialog()
        self.select_ui.setupUi(self)
        self.setWindowIcon(QIcon("picture\\choose.png"))
        self.select_ui.pb_all.clicked.connect(self.pb_select_all_click)
        self.select_ui.pb_invert.clicked.connect(self.pb_invert_click)
        self.select_ui.pb_save.clicked.connect(self.pb_save_click)


    def pb_select_all_click(self):
        """全选点击槽"""
        # 获取self.select_ui中所有以cb_开头的属性
        checkboxes = [getattr(self.select_ui, attr) for attr in dir(self.select_ui) if
                      attr.startswith('cb_') and callable(getattr(self.select_ui, attr).setChecked)]

        # 遍历复选框列表，设置每个复选框为选中状态
        for checkbox in checkboxes:
            checkbox.setChecked(True)


    def pb_invert_click(self):
        """反选点击槽"""
        # 获取self.select_ui中所有以cb_开头的复选框
        checkboxes = [getattr(self.select_ui, attr) for attr in dir(self.select_ui) if
                      attr.startswith('cb_') and isinstance(getattr(self.select_ui, attr), QCheckBox)]

        # 遍历复选框列表，并切换每个复选框的状态
        for checkbox in checkboxes:
            checkbox.toggle()


    @staticmethod
    def pb_save_click():
        save_cfg()
        cfg.read(CFG_PATH, encoding='utf-8')




class AdvancedParameter(QDialog, Ui_AdvancedWindow):
    def __init__(self):
        super().__init__()
        self.advanced_ui = Ui_AdvancedWindow()
        self.advanced_ui.setupUi(self)
        self.setWindowIcon(QIcon("picture\\advanced.png"))
        # 控件到设置键的反向映射
        self.reverse_mapping = {
            self.advanced_ui.sb_maxenter: '最大换行次数',
            self.advanced_ui.te_killer_message: '赛后发送消息',
            self.advanced_ui.te_human_message: '人类发送消息',
            self.advanced_ui.le_tuzixy: '女猎手所在位置的坐标',
            self.advanced_ui.le_firstx: '角色第一行横坐标',
            self.advanced_ui.le_firsty: '角色第一行纵坐标',
            self.advanced_ui.te_lastx: '最后七个角色横坐标',
            self.advanced_ui.te_lasty: '最后七个角色纵坐标',
            self.advanced_ui.sb_backfirst: '角色回滚滚轮到最顶端的次数',
            self.advanced_ui.le_play_area: '开始游戏、准备就绪按钮的识别范围',
            self.advanced_ui.le_play_keywords: '匹配大厅识别关键字',
            self.advanced_ui.le_ready_keywords: '准备大厅识别关键字',
            self.advanced_ui.le_over_area: '结算页的识别范围',
            self.advanced_ui.le_over_keywords: '结算页识别关键字',
            self.advanced_ui.le_orites_area: '结算页每日祭礼的识别范围',
            self.advanced_ui.le_orites_keywords: '结算页每日祭礼识别关键字',
            self.advanced_ui.le_season_reset: '段位重置的识别范围',
            self.advanced_ui.le_sr_keywords: '段位重置识别关键字',
            self.advanced_ui.le_dr_main: '主界面的每日祭礼识别范围',
            self.advanced_ui.le_drm_keywords: '主页面每日祭礼识别关键字',
            self.advanced_ui.le_mainjudge: '主页面的识别范围',
            self.advanced_ui.le_mainjudge_keywords: '主页面识别关键字',
            self.advanced_ui.le_dccheck: '断线检测的识别范围',
            self.advanced_ui.le_dccheck_keywords: '断线检测识别关键字',
            self.advanced_ui.le_news: '新内容的识别范围',
            self.advanced_ui.le_new_keywords: '新内容识别关键字',
            self.advanced_ui.le_evrewards: 'event_rewards',
            self.advanced_ui.le_playxy: '开始游戏和准备就绪按钮的坐标',
            self.advanced_ui.le_seasonresetxy: '段位重置按钮的坐标',
            self.advanced_ui.le_overritesxy: '结算页祭礼完成坐标',
            self.advanced_ui.le_over_continuexy: '结算页继续按钮坐标',
            self.advanced_ui.le_newsxy: '主页面新闻关闭坐标',
            self.advanced_ui.le_main_ritesxy: '主页面祭礼关闭坐标',
            self.advanced_ui.le_main_startxy: '主页面开始坐标',
            self.advanced_ui.le_main_humanxy: '主页面逃生者坐标',
            self.advanced_ui.le_main_killerxy: '主页面杀手坐标',
            self.advanced_ui.le_rolexy: '匹配大厅的角色按钮坐标',
        }
        self.load_settings()

        self.init_signals()


    def init_signals(self):
        """初始化信号和槽连接"""

        # 为控件连接信号和槽
        for widget, setting_key in self.reverse_mapping.items():
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(self.update_settings)
            elif isinstance(widget, QSpinBox):
                widget.valueChanged.connect(self.update_settings)
            elif isinstance(widget, QTextEdit):
                widget.textChanged.connect(self.update_settings)

        self.advanced_ui.pb_next.clicked.connect(self.pb_next_click)
        self.advanced_ui.pb_previous.clicked.connect(self.pb_prev_click)
        self.advanced_ui.pb_save.clicked.connect(self.pb_save_click)

    def load_settings(self):
        """初始化加载设置文件内容"""
        # 定义控件映射字典，键是 self_defined_args 中的键，值是控件的属性和方法
        widget_mapping = {
            '最大换行次数': (self.advanced_ui.sb_maxenter, 'setValue'),
            '赛后发送消息': (self.advanced_ui.te_killer_message, 'setText'),
            '人类发送消息': (self.advanced_ui.te_human_message, 'setText'),
            '女猎手所在位置的坐标': (self.advanced_ui.le_tuzixy, 'setText'),
            '角色第一行横坐标': (self.advanced_ui.le_firstx, 'setText'),
            '角色第一行纵坐标': (self.advanced_ui.le_firsty, 'setText'),
            '最后七个角色横坐标': (self.advanced_ui.te_lastx, 'setText'),
            '最后七个角色纵坐标': (self.advanced_ui.te_lasty, 'setText'),
            '角色回滚滚轮到最顶端的次数': (self.advanced_ui.sb_backfirst, 'setValue'),
            '开始游戏、准备就绪按钮的识别范围': (self.advanced_ui.le_play_area, 'setText'),
            '匹配大厅识别关键字': (self.advanced_ui.le_play_keywords, 'setText'),
            '准备大厅识别关键字': (self.advanced_ui.le_ready_keywords, 'setText'),
            '结算页的识别范围': (self.advanced_ui.le_over_area, 'setText'),
            '结算页识别关键字': (self.advanced_ui.le_over_keywords, 'setText'),
            '结算页每日祭礼的识别范围': (self.advanced_ui.le_orites_area, 'setText'),
            '结算页每日祭礼识别关键字': (self.advanced_ui.le_orites_keywords, 'setText'),
            '段位重置的识别范围': (self.advanced_ui.le_season_reset, 'setText'),
            '段位重置识别关键字': (self.advanced_ui.le_sr_keywords, 'setText'),
            '主界面的每日祭礼识别范围': (self.advanced_ui.le_dr_main, 'setText'),
            '主页面每日祭礼识别关键字': (self.advanced_ui.le_drm_keywords, 'setText'),
            '主页面的识别范围': (self.advanced_ui.le_mainjudge, 'setText'),
            '主页面识别关键字': (self.advanced_ui.le_mainjudge_keywords, 'setText'),
            '断线检测的识别范围': (self.advanced_ui.le_dccheck, 'setText'),
            '断线检测识别关键字': (self.advanced_ui.le_dccheck_keywords, 'setText'),
            '新内容的识别范围': (self.advanced_ui.le_news, 'setText'),
            '新内容识别关键字': (self.advanced_ui.le_new_keywords, 'setText'),
            'event_rewards': (self.advanced_ui.le_evrewards, 'setText'),
            '开始游戏和准备就绪按钮的坐标': (self.advanced_ui.le_playxy, 'setText'),
            '段位重置按钮的坐标': (self.advanced_ui.le_seasonresetxy, 'setText'),
            '结算页祭礼完成坐标': (self.advanced_ui.le_overritesxy, 'setText'),
            '结算页继续按钮坐标': (self.advanced_ui.le_over_continuexy, 'setText'),
            '主页面新闻关闭坐标': (self.advanced_ui.le_newsxy, 'setText'),
            '主页面祭礼关闭坐标': (self.advanced_ui.le_main_ritesxy, 'setText'),
            '主页面开始坐标': (self.advanced_ui.le_main_startxy, 'setText'),
            '主页面逃生者坐标': (self.advanced_ui.le_main_humanxy, 'setText'),
            '主页面杀手坐标': (self.advanced_ui.le_main_killerxy, 'setText'),
            '匹配大厅的角色按钮坐标': (self.advanced_ui.le_rolexy, 'setText'),
        }

        # 遍历映射字典
        for key, (widget, method) in widget_mapping.items():
            # 确保 key 存在于 self_defined_args 中
            if key in self_defined_args:
                # 获取对应的控件和方法名
                ctrl = getattr(widget, method)
                # 检查值的类型，如果是列表，则转换为字符串
                arg = ', '.join(map(str, self_defined_args[key])) if isinstance(self_defined_args[key], list) else (
                    self_defined_args)[key]
                # 调用控件的方法，传入转换后的参数
                ctrl(arg)
            else:
                QMessageBox.warning(self, "错误", "键值不在参数文件中")

    def pb_next_click(self):
        index = self.advanced_ui.stackedWidget.currentIndex()
        if index >= 3:
            pass
        else:
            index = index + 1
        self.advanced_ui.stackedWidget.setCurrentIndex(index)

    def pb_prev_click(self):
        index = self.advanced_ui.stackedWidget.currentIndex()
        if index <= 0:
            pass
        else:
            index = index - 1
        self.advanced_ui.stackedWidget.setCurrentIndex(index)

    @staticmethod
    def pb_save_click():
        # 将更新后的键值对写回文件
        with open(SDAGRS_PATH, 'w', encoding='utf-8') as f:
            json.dump(self_defined_args, f, indent=4, ensure_ascii=False)
        win32api.MessageBox(0, "保存成功", "提醒", win32con.MB_ICONASTERISK)

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
            elif isinstance(widget, QSpinBox):
                settings_value = widget.value()
            elif isinstance(widget, QTextEdit):
                settings_value = widget.toPlainText()

            if setting_key in ['最大换行次数', '角色回滚滚轮到最顶端的次数']:
                self_defined_args[setting_key] = int(settings_value)
            elif setting_key in ['赛后发送消息', '人类发送消息']:
                self_defined_args[setting_key] = settings_value
            else:
                self_defined_args[setting_key] = settings_value

            # print(self_defined_args)




class TipForm(QWidget, Ui_TipForm):
    def __init__(self):
        super().__init__()
        self.tipform_ui = Ui_TipForm()
        self.tipform_ui.setupUi(self)
        self.setWindowIcon(QIcon("picture\\edit.png"))

        self.init_signals()

    def init_signals(self):
        self.tipform_ui.pb_save.clicked.connect(self.pb_save_click)

    def wrkn_file(self):
        """中英文相互映射写入文件"""
        # 创建两个字典，一个用于中文到英文的映射，另一个用于英文到中文的映射
        # 随版本更改
        cn_to_en_map = {
            "设陷者": "TRAPPER",
            "幽灵": "WRAITH",
            "农场主": "HILLBILLY",
            "护士": "NURSE",
            "女猎手": "HUNTRESS",
            "迈克尔.迈尔斯": "SHAPE",
            "妖巫": "HAG",
            "医生": "DOCTOR",
            "食人魔": "CANNIBAL",
            "梦魇": "NIGHTMARE",
            "门徒": "PIG",
            "小丑": "CLOWN",
            "怨灵": "SPIRIT",
            "军团": "LEGION",
            "瘟疫": "PLAGUE",
            "鬼面": "GHOSTFACE",
            "魔王": "DEMOGORGON",
            "鬼武士": "ONI",
            "死亡枪手": "DEATHSLINGER",
            "处刑者": "EXECUTIONER",
            "枯萎者": "BLIGHT",
            "连体婴": "TWINS",
            "骗术师": "TRICKSTER",
            "NEMESIS": "NEMESIS",
            "地狱修士": "CENOBITE",
            "艺术家": "ARTIST",
            "贞子": "ONRYO",
            "影魔": "DREDGE",
            "操纵者": "MASTERMIND",
            "恶骑士": "KNIGHT",
            "白骨商人": "SKULLMERCHANT",
            "奇点": "SINGULARITY",
            "异形": "XENOMORPH",
            "好孩子": "GOODGUY",
            "未知恶物": "UNKNOWN"
        }

        en_to_cn_map = {v: k for k, v in cn_to_en_map.items()}

        with open(SEARCH_PATH_CN, 'w') as cn_file, open(SEARCH_PATH_EN, 'w') as en_file:
            # 将文件内容截断为空
            cn_file.truncate()
            en_file.truncate()

        killer_names = self.tipform_ui.pt_search.toPlainText().splitlines()
        # 遍历 killer_name_array
        for killer_name in killer_names:
            # 检查 killer_name 是否在字典的键中
            if killer_name in cn_to_en_map:
                # killer_name 是中文，将其写入中文文件并转换为英文写入英文文件
                with open(SEARCH_PATH_CN, 'a', encoding='UTF-8') as cn_file:
                    cn_file.write(killer_name + '\n')
                with open(SEARCH_PATH_EN, 'a', encoding='UTF-8') as en_file:
                    en_file.write(cn_to_en_map[killer_name] + '\n')
            elif killer_name in en_to_cn_map:
                # killer_name 是英文，将其写入英文文件并转换为中文写入中文文件
                with open(SEARCH_PATH_EN, 'a', encoding='UTF-8') as en_file:
                    en_file.write(killer_name + '\n')
                with open(SEARCH_PATH_CN, 'a', encoding='UTF-8') as cn_file:
                    cn_file.write(en_to_cn_map[killer_name] + '\n')

    def pb_save_click(self):
        try:
            if cfg.getboolean("UPDATE", "rb_chinese"):
                SEARCH_PATH = SEARCH_PATH_CN
            elif cfg.getboolean("UPDATE", "rb_english"):
                SEARCH_PATH = SEARCH_PATH_EN
            with open(SEARCH_PATH, 'w', encoding="utf-8") as f:
                f.write(self.tipform_ui.pt_search.toPlainText())
        except FileNotFoundError:
            win32api.MessageBox(0, f"{SEARCH_PATH}文件不存在", "错误", win32con.MB_ICONERROR, win32con.MB_OK)
        except Exception as e:
            win32api.MessageBox(0, f"读取文件时出错:{e}", "警告  ", win32con.MB_ICONWARNING, win32con.MB_OK)
        self.wrkn_file()

    def loading_settings(self):
        try:
            if cfg.getboolean("UPDATE", "rb_chinese"):
                SEARCH_PATH = SEARCH_PATH_CN
            elif cfg.getboolean("UPDATE", "rb_english"):
                SEARCH_PATH = SEARCH_PATH_EN
            with open(SEARCH_PATH, 'r', encoding="utf-8") as f:
                self.tipform_ui.pt_search.setPlainText(f.read())
        except FileNotFoundError:
            win32api.MessageBox(0, f"{SEARCH_PATH}文件不存在", "错误", win32con.MB_ICONERROR, win32con.MB_OK)
        except Exception as e:
            win32api.MessageBox(0, f"读取文件时出错:{e}", "警告  ", win32con.MB_ICONWARNING, win32con.MB_OK)




class ShowLog(QDialog, Ui_ShowLogDialog):
    def __init__(self):
        super().__init__()
        self.showlog_ui = Ui_ShowLogDialog()
        self.showlog_ui.setupUi(self)
        self.setWindowIcon(QIcon("picture\\log.png"))

    def loading_settings(self):
        try:
            with open(LOG_PATH, 'r', encoding="utf-8") as f:
                self.showlog_ui.te_showlog.setPlainText(f.read())
                print(f.read())
        except FileNotFoundError:
            win32api.MessageBox(0, "\"debug_data.log\"文件不存在", "错误", win32con.MB_ICONERROR, win32con.MB_OK)
        except Exception as e:
            win32api.MessageBox(0, f"读取文件时出错:{e}", "警告  ", win32con.MB_ICONWARNING, win32con.MB_OK)




class DebugTool(QDialog, Ui_DebugDialog):
    def __init__(self):
        super().__init__()
        self.debugtool_ui = Ui_DebugDialog()
        self.debugtool_ui.setupUi(self)
        self.setWindowIcon(QIcon("picture\\tool.png"))

        self.init_signals()

    def init_signals(self):
        self.debugtool_ui.pb_selection_region.clicked.connect(self.pb_selection_region_click)
        self.debugtool_ui.pb_test.clicked.connect(self.pb_test_click)

    def pb_selection_region_click(self):
        self.root = tk.Tk()
        self.selector = BoxSelector(self.root)
        self.root.mainloop()

    def pb_test_click(self):
        coord_xy = debug_dialog.debugtool_ui.le_coord.text()
        if not coord_xy:
            debug_dialog.debugtool_ui.lb_result.setText("请先框选区域！")
            return

        key_words = self.debugtool_ui.le_keywords.text().split(",")
        # print(key_words)
        if not key_words or all(not item.strip() for item in key_words):
            debug_dialog.debugtool_ui.lb_result.setText("请输入关键字！")
            return

        for sum_number in range(130, 20, -10):
            debug_dialog.debugtool_ui.pb_test.setDisabled(True)
            debug_dialog.debugtool_ui.pb_test.setText("测试中")
            ocr_result = img_ocr(self.selector.start_x, self.selector.start_y, self.selector.end_x, self.selector.end_y,
                                 "debug_test", sum_number)
            if any(keyword in ocr_result for keyword in key_words):
                debug_dialog.debugtool_ui.lb_result.setText(f"识别成功！\n二值化值为：{sum_number}")
                break
            else:
                debug_dialog.debugtool_ui.lb_result.setText(f"未识别···\n二值化值为：{sum_number}")

            # 添加延迟
            time.sleep(0.1)  # 等待0.1秒
            # 处理事件队列
            QCoreApplication.processEvents()

        debug_dialog.debugtool_ui.pb_test.setEnabled(True)
        debug_dialog.debugtool_ui.pb_test.setText("测 试")
        del_jpg()




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
            print(f"Selected Box: From {(self.start_x, self.start_y)} to {(self.end_x, self.end_y)}")
            self.master.destroy()  # 用户完成选框后退出程序

        debug_dialog.debugtool_ui.le_coord.setText(f"{self.start_x},{self.start_y},{self.end_x},{self.end_y}")

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
        if cfg.getboolean("UPDATE", "rb_chinese"):
            self.SEARCH_PATH = SEARCH_PATH_CN
        elif cfg.getboolean("UPDATE", "rb_english"):
            self.SEARCH_PATH = SEARCH_PATH_EN

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
            "cb_maishu": "迈克尔.迈尔斯",
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
            "cb_ewu": "未知恶物"
        }
        # 遍历配置项，根据配置项添加对应的杀手名称到列表中
        for key, value in killer_mapping_cn.items():
            if cfg.getboolean("CUSSEC", key):
                self.select_killer_lst.append(value)

    def select_killer_name_en(self):
        """获取选取的杀手名称"""
        # 随版本更改
        # 此处append内容需与self_defined_parameter['all_killer_name_EN']中的值一致
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
            "cb_guimian": "GHOSTFACE",
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
            "cb_baigu": "SKULLMERCHANT",
            "cb_jidian": "SINGULARITY",
            "cb_yixing": "XENOMORPH",
            "cb_qiaji": "GOOD GUY",
            "cb_ewu": "UNKNOWN"
        }
        # 遍历配置项，根据配置项添加对应的杀手名称到列表中
        for key, value in killer_mapping_en.items():
            if cfg.getboolean("CUSSEC", key):
                self.select_killer_lst.append(value)

    def match_select_killer_name(self):
        """匹配选取的杀手名称在用户杀手列表中的位置"""
        if cfg.getboolean("SEKI", "cb_usefile"):
            with open(CUSTOM_KILLER_PATH, "r", encoding='UTF-8') as search_file:
                self.select_killer_lst = search_file.readlines()
                self.select_killer_lst = [c.strip() for c in self.select_killer_lst]
            for i in self.select_killer_lst:
                self.match_select_killer_lst.append(self.killer_name_array.index(i) + 1)
        else:
            for i in self.select_killer_lst:
                self.match_select_killer_lst.append(self.killer_name_array.index(i) + 1)

    def read_search_killer_name(self):
        """读取检索文件"""
        with open(self.SEARCH_PATH, "r", encoding='UTF-8') as search_file:
            self.killer_name_array = search_file.readlines()
            self.killer_name_array = [c.strip() for c in self.killer_name_array]




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
            "cb_usefile": False,
        },
        "UPDATE": {
            "cb_autocheck": True,
            "rb_chinese": True,
            "rb_english": False
        },
        "CUSSEC": {
            key: False for key in cussec_keys
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

    # 检查自定义文件是否存在，如果不存在则创建一个空字典
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


def save_cfg():
    """ 保存配置文件 """
    for section, options in ui_components.items():
        if section not in settings:
            settings[section] = {}
        for option_name, ui_control in options.items():
            settings[section][option_name] = ui_control.isChecked()
    settings.write()


def read_cfg():
    """读取配置文件"""
    for section, keys in ui_components.items():
        for key, ui_control in keys.items():
            value = cfg.getboolean(section, key)
            ui_control.setChecked(value)
    if cfg.getboolean("CPCI", "rb_survivor"):
        dbd_window.main_ui.cb_survivor_do.setEnabled(True)
        dbd_window.main_ui.rb_fixed_mode.setDisabled(True)
        dbd_window.main_ui.rb_random_mode.setDisabled(True)
        dbd_window.main_ui.pb_select_cfg.setDisabled(True)
        dbd_window.main_ui.pb_search.setDisabled(True)
    # if cfg.getboolean("CPCI", "rb_killer"):
    #     dbd_window.main_ui.cb_killer_do.setEnabled(True)

    # 读取self_defined_args内容
    try:
        with open(SDAGRS_PATH, mode='r', encoding='utf-8') as f:
            # 读取文件中的所有内容，并将其转换为一个字典
            existing_args = json.load(f)
            # 更新 self_defined_args 字典
            self_defined_args.update(existing_args)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # 如果文件不存在或内容不是有效的 JSON，您可以根据需要处理这个异常
        log.error(f"读取SDargs.json文件异常: {e}")


def authorization():
    """check the authorization"""
    authorization_now = '~x&amp;mBGbIneqSS('
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


def check_update():
    """check the update"""
    ver_now = 'V5.1.9'
    html_str = requests.get('https://gitee.com/kioley/DBD_AFK_TOOL').content.decode()
    ver_new = re.search('title>(.*?)<', html_str, re.S).group(1)[13:19]
    if ne(ver_now, ver_new):
        if cfg.getboolean("UPDATE", "rb_chinese"):
            confirm = win32api.MessageBox(0,
                                          f"检查到新版本，是否更新？",
                                          "检查更新", win32con.MB_YESNO | win32con.MB_ICONQUESTION)
            if eq(confirm, 6):  # 打开
                webbrowser.open("https://github.com/maskrs/DBD_AFK_TOOL/releases")
                subprocess.call("update.exe")
                sys.exit()
        elif cfg.getboolean("UPDATE", "rb_english"):
            confirm = win32api.MessageBox(0,
                                          f"Check the new version. Is it updated?",
                                          "Check for updates", win32con.MB_YESNO | win32con.MB_ICONQUESTION)
            if eq(confirm, 6):  # 打开
                webbrowser.open("https://github.com/maskrs/DBD_AFK_TOOL/releases")
                subprocess.call("update.exe")
                sys.exit()


def check_ocr():
    """check if not ocr installed"""
    if not os.path.exists(CHECK_PATH):
        if cfg.getboolean("UPDATE", "rb_chinese"):
            confirm = win32api.MessageBox(0, "未检查到运行环境，是否进行初始化？", "检查环境",
                                          win32con.MB_YESNO | win32con.MB_ICONQUESTION)
            if eq(confirm, 6):  # 打开
                subprocess.call("initialize.exe")
            else:
                sys.exit()
        elif cfg.getboolean("UPDATE", "rb_english"):
            confirm = win32api.MessageBox(0, "The running environment is not detected. Do you want to initialize it?",
                                          "Check the environment", win32con.MB_YESNO | win32con.MB_ICONQUESTION)
            if eq(confirm, 6):  # 打开
                subprocess.call("initialize.exe")
            else:
                sys.exit()


def notice():
    """take a message"""
    notice_now = 'test git'
    html_str = requests.get('https://gitee.com/kioley/test-git').content.decode()
    notice_new = re.search('title>(.*?)<', html_str, re.S).group(1)[0:8]
    notice = re.search('title>(.*?)<', html_str, re.S).group(1)[9:]
    if ne(notice_now, notice_new):
        win32api.MessageBox(0, notice, "通知", win32con.MB_OK | win32con.MB_ICONINFORMATION)


def close_logger():
    for handler in logging.root.handlers:
        if isinstance(handler, logging.FileHandler):
            handler.close()


def screen_age():
    def get_screen_size():
        """获取缩放后的分辨率"""
        w = win32api.GetSystemMetrics(0)
        h = win32api.GetSystemMetrics(1)
        return w, h

    screen_size = get_screen_size()
    log.info(f"系统分辨率为：{screen_size}\n")


def hall_tip():
    """Child thread, survivor hall tip"""
    while True:
        if readyhall():
            py.press('enter')
            py.typewrite(self_defined_args['人类发送消息'])
            py.press('enter')
            time.sleep(20)
        else:
            time.sleep(1)


def autospace():
    """Child thread, auto press space"""
    while not stop_space:
        if not pause:
            key_down(hwnd, 'space')
            time.sleep(7)


def action():
    cfg.read(CFG_PATH, encoding='utf-8')
    time.sleep(1)
    rb_survivor = cfg.getboolean("CPCI", "rb_survivor")
    rb_fixed_mode = cfg.getboolean("CPCI", "rb_fixed_mode")
    rb_random_mode = cfg.getboolean("CPCI", "rb_random_mode")
    rb_killer = cfg.getboolean("CPCI", "rb_killer")
    while not stop_action:
        if not pause:
            if rb_survivor:
                survivor_action()
            elif rb_fixed_mode and rb_killer:
                killer_fixed_act()
            elif rb_random_mode and rb_killer:
                killer_action()


def listen_key():
    """Hotkey  setting, monitored keyboard input"""

    # 定义快捷键组合
    hotkeys = [
        'alt+end',
        'f9',
        'alt+home'
    ]

    def pause():
        global pause

        if not pause:
            # 播放WAV文件
            play_pau.play()
            pause = True
            pause_event.clear()
        elif pause:
            # 播放WAV文件
            play_res.play()
            pause = False
            pause_event.set()
        try:
            # 置顶
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
            # 取消置顶
            win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
        except Exception as ex:
            print(f"An error occurred: {ex}")

    try:
        keyboard.add_hotkey(hotkeys[0], kill)
        keyboard.add_hotkey(hotkeys[1], pause)
        keyboard.add_hotkey(hotkeys[2], begin)
        # 保持程序运行，监听键盘事件
        keyboard.wait()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # 清理，移除监听
        keyboard.unhook_all_hotkeys()


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
            x1, y1, x2, y2 = self_defined_args[capture_range]
            threshold = self_defined_args[min_sum_name][0]
            threshold_high = self_defined_args[min_sum_name][1]
            keywords = self_defined_args[identification_key]

            # 调用img_ocr函数，传入固定坐标和阈值
            ocr_result = ocr_func(x1, y1, x2, y2, ocrname=name, sum=threshold)
            if dbd_window.main_ui.cb_debug.isChecked():
                log.info(f"DEBUG -{name}.OCR result is:{ocr_result}")

            if any(keyword in ocr_result for keyword in keywords):

                if dbd_window.main_ui.cb_bvinit.isChecked() and self_defined_args[min_sum_name][2] == 0:
                    if min_sum_name != '断线检测二值化阈值':
                        self_defined_args[min_sum_name][2] = 1
                        # 将更新后的键值对写回文件
                        with open(SDAGRS_PATH, 'w', encoding='utf-8') as f:
                            json.dump(self_defined_args, f, indent=4, ensure_ascii=False)

                return True
            elif dbd_window.main_ui.cb_bvinit.isChecked() and self_defined_args[min_sum_name][2] == 0:

                new_threshold = threshold - 10  # 递减一个步长作为新的阈值
                if new_threshold < 30:  # 确保不低于停止值
                    new_threshold = threshold_high
                self_defined_args[min_sum_name][0] = new_threshold

            return False

        return wrapper

    return decorator


def img_ocr(x1, y1, x2, y2, ocrname, sum=128) -> str:
    """OCR识别图像，返回字符串
    :return: string"""
    result = " "
    ocrXY = [x1, y1, x2, y2]
    image = screen.grabWindow(0).toImage()
    # 生成唯一的文件名
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"image_{timestamp}_{ocrname}.jpg"
    image.save(filename)
    time.sleep(1)
    try:
        # 打开图像文件并裁剪、二值化
        with Image.open(filename) as img:
            cropped = img.crop((ocrXY[0], ocrXY[1], ocrXY[2], ocrXY[3]))
            grayscale_image = cropped.convert('L')
            binary_image = grayscale_image.point(lambda x: 0 if x < sum else 255, '1')
            binary_image.save(filename)  # 保存二值化后的图像到相同的文件
    except FileNotFoundError as e:
        print(f"{e}:image file not found - {filename}\n")
        return result
    except OSError as f:
        print(f"{f}:image file is truncated - {filename}\n")
        return result

    custom_config = r'--oem 3 --psm 6'
    # 判断中英文切换模型
    lan = "chi_sim+eng"  # 默认简体中文+英文
    if cfg.getboolean("UPDATE", "rb_chinese"):
        lan = "chi_sim"
    elif cfg.getboolean("UPDATE", "rb_english"):
        lan = "eng"
    try:
        with Image.open(filename) as ocr_image:
            # 使用Tesseract OCR引擎识别图像中的文本
            result = pytesseract.image_to_string(ocr_image, config=custom_config, lang=lan)
            result = "".join(result.split())
    except FileNotFoundError as e:
        print(f"{e}:image file not found - {filename}\n")
        return result
    except OSError as f:
        print(f"{f}:image file is truncated - {filename}\n")
        return result

    if os.path.exists(filename):
        try:
            os.remove(filename)  # 尝试删除文件
        except Exception as e:
            print(f"ocr检索删除文件时出错: {filename} - {e}\n")
    return result


@ocr_range_inspection('匹配大厅识别关键字',
                      img_ocr, '开始游戏、准备就绪按钮的识别范围', '匹配大厅二值化阈值', "play")
def starthall() -> bool:
    """check the start  hall
    :return: bool"""
    pass


@ocr_range_inspection('准备大厅识别关键字',
                      img_ocr, '开始游戏、准备就绪按钮的识别范围', '准备房间二值化阈值', "ready")
def readyhall() -> bool:
    """check the  ready hall
    :return: bool"""
    pass


@ocr_range_inspection('准备取消按钮识别关键字',
                      img_ocr, '开始游戏、准备就绪按钮的识别范围', '准备取消按钮二值化阈值', "cancel")
def readycancle() -> bool:
    """检查游戏准备后的取消，消失就进入对局加载
    :return: bool"""
    pass


@ocr_range_inspection('结算页识别关键字',
                      img_ocr, '结算页的识别范围', '结算页二值化阈值', "gameover")
def gameover() -> bool:
    """检查对局后的继续
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
# eventXY = Coord(1864, 455, 1920, 491)
# eventXY.processed_coord()
# eventXY.area_check()


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
                      img_ocr, '主页面的识别范围', '主页面开始按钮二值化阈值', "start")
def mainjudge() -> bool:
    """after serious disconnect.
    check the game whether return the main menu. -->[quit button]
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
        if target_string in result:
            target = result.index(target_string)
            # 确保不会越界，并且结果确实是数字
            if target + 2 < len(result) and result[target + 1].isdigit() and result[target + 2].isdigit():
                confirmX, confirmY = int(result[target + 1]), int(result[target + 2])
                return confirmX, confirmY
        return None, None

    # log.info(f"disconnect_confirm识别中···\n")

    disconnect_check_colorXY = self_defined_args['断线检测的识别范围']

    screen = QApplication.primaryScreen()
    image = screen.grabWindow(0).toImage()

    # 生成唯一的文件名
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"image_{timestamp}.jpg"
    image.save(filename)
    time.sleep(1)
    try:
        # 打开图像文件并裁剪、二值化
        with Image.open(filename) as img:
            cropped = img.crop((disconnect_check_colorXY[0], disconnect_check_colorXY[1],
                                disconnect_check_colorXY[2], disconnect_check_colorXY[3]))
            grayscale_image = cropped.convert('L')
            binary_image = grayscale_image.point(lambda x: 0 if x < sum else 255, '1')
            binary_image.save(filename)  # 保存二值化后的图像到相同的文件
    except FileNotFoundError as e:
        print(f"{e}:image file not found - {filename}\n")
        return None
    except OSError as f:
        print(f"{f}:image file is truncated - {filename}\n")
        return None

    custom_config = r'--oem 3 --psm 6'
    # 判断中英文切换模型
    lan = "chi_sim+eng"  # 默认简体中文+英文
    if cfg.getboolean("UPDATE", "rb_chinese"):
        lan = "chi_sim"
    elif cfg.getboolean("UPDATE", "rb_english"):
        lan = "eng"
    try:
        with Image.open(filename) as ocr_image:
            # 使用Tesseract OCR引擎识别图像中的文本
            result = pytesseract.image_to_boxes(ocr_image, config=custom_config, lang=lan)
            result = result.split(' ')
    except FileNotFoundError as e:
        print(f"{e}:image file not found - {filename}\n")
        return None
    except OSError as f:
        print(f"{f}:image file is truncated - {filename}\n")
        return None

    # log.info(f"识别内容为：{result}\n")

    # 定义需要查找的字符串列表
    target_strings = ["好", "关", "继", "K", "C"]

    # 初始化坐标
    # confirmX, confirmY = None, None

    # 遍历目标字符串列表
    for target_string in target_strings:
        confirmx, confirmy = get_coordinates(result, target_string)
        if confirmx is not None and confirmy is not None:
            # log.info(f"disconnect_confirm已识别···")
            # 调用moveclick函数
            moveclick(disconnect_check_colorXY[0] + confirmx, disconnect_check_colorXY[3] - confirmy,
                      1, 1)
            # 找到了坐标，跳出循环
            break

    # 如果没有找到坐标，则可以根据需要添加处理逻辑
    # if confirmX is None or confirmY is None:
    #     log.info("disconnect_confirm未识别···\n")

    if os.path.exists(filename):
        try:
            os.remove(filename)  # 尝试删除文件
        except Exception as e:
            print(f"ocr检索删除文件时出错: {filename} - {e}\n")
    else:
        print(f"ocr检索删除文件时出错: 文件不存在 - {filename}\n")


def moveclick(x, y, delay: float = 0, click_delay: float = 0) -> None:
    """mouse move to a true place and click """
    py.moveTo(x, y)
    time.sleep(delay)
    py.click()
    time.sleep(click_delay)


def auto_message() -> None:
    """对局结束后的自动留言"""
    py.press('enter')
    py.typewrite(self_defined_args['赛后发送消息'])
    py.press('enter')
    time.sleep(0.5)


def reconnect() -> bool:
    """Determine whether the peer is disconnected and return to the matching hall
    :return: bool -->TRUE
    """
    global stop_space, stop_action
    log.info(f"游戏断线，进入重连···")
    time.sleep(2)
    stop_space = True  # 自动空格线程标志符
    stop_action = True  # 动作线程标志符
    while disconnect_check():
        for sum in range(130, 80, -10):
            disconnect_confirm(sum)
            if not disconnect_check():
                break

    # 检测血点，判断断线情况
    if starthall() or readyhall():  # 小退
        log.info(f"重连完成···错误代码")
        return True
    elif gameover():  # 意味着不在大厅
        moveclick(self_defined_args['结算页继续按钮坐标'][0], self_defined_args['结算页继续按钮坐标'][1])
        log.info(f"重连完成···错误代码")
        return True
    else:  # 大退

        main_quit = False
        while not main_quit:
            if event.is_set():
                return True
            if not pause_event.is_set():
                pause_event.wait()
            while disconnect_check():
                for sum in range(130, 80, -10):
                    disconnect_confirm(sum)
                    if not disconnect_check():
                        break
            time.sleep(1)
            moveclick(10, 10, click_delay=1)  # 错误
            #### 活动奖励
            if news():
                moveclick(self_defined_args['主页面新闻关闭坐标'][0], self_defined_args['主页面新闻关闭坐标'][1],
                          click_delay=1)  # 新闻点击

            # 判断每日祭礼
            if daily_ritual_main():
                moveclick(self_defined_args['主页面祭礼关闭坐标'][0], self_defined_args['主页面祭礼关闭坐标'][1],
                          click_delay=1)
            # 判断段位重置
            if season_reset():
                moveclick(self_defined_args['段位重置按钮的坐标'][0], self_defined_args['段位重置按钮的坐标'][1],
                          click_delay=1)
            # 是否重进主页面判断
            if mainjudge():
                moveclick(self_defined_args['主页面开始坐标'][0], self_defined_args['主页面开始坐标'][1],
                          click_delay=1)  # 点击开始
                # 通过阵营选择判断返回大厅
                if cfg.getboolean("CPCI", "rb_survivor"):
                    moveclick(self_defined_args['主页面逃生者坐标'][0], self_defined_args['主页面逃生者坐标'][1])
                elif cfg.getboolean("CPCI", "rb_killer"):
                    moveclick(self_defined_args['主页面杀手坐标'][0], self_defined_args['主页面杀手坐标'][1])
                main_quit = True
            if gameover():
                moveclick(self_defined_args['结算页继续按钮坐标'][0], self_defined_args['结算页继续按钮坐标'][1])
                moveclick(10, 10)  # 避免遮挡
                main_quit = True
        log.info(f"重连完成···断线")
        return True


def random_movement() -> str:
    """通过随机数取得移动的方向
    :return: str
    """
    rn = random.randint(1, 6)
    if lt(rn, 2) or ge(rn, 5):
        return 'w'
    elif eq(rn, 2):
        return 'd'
    elif eq(rn, 3):
        return 'a'
    else:
        return 's'


def random_direction() -> str:
    """随机旋转方向
    :return: str
    """
    rn = random.randint(1, 2)
    if eq(rn, 1):
        return 'q'
    else:
        return 'e'


def random_movetime() -> float:
    """get the character random move time in the game
    :return: float"""
    rn = round(random.uniform(1.1, 2.0), 3)  # 0.5 1.5
    return rn


def random_veertime() -> float:
    """get the character random veer time
    :return: float"""
    rn = round(random.uniform(0.275, 0.4), 3)  # 0.6
    return rn


def random_move(move_time) -> None:
    """行走动作"""
    act_move = random_movement()
    key_down(hwnd, act_move)
    time.sleep(move_time)
    key_up(hwnd, act_move)


def random_veer(veer_time) -> None:
    """旋转动作"""
    act_direction = random_direction()
    key_down(hwnd, act_direction)
    time.sleep(veer_time)
    key_up(hwnd, act_direction)


def survivor_action() -> None:
    """survivor`s action"""
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


def killer_ctrl() -> None:
    key_down(hwnd, 'lcontrol')
    time.sleep(4.3)
    key_up(hwnd, 'lcontrol')


def killer_skillclick() -> None:
    py.mouseDown(button='right')
    time.sleep(3)
    py.mouseDown()
    py.mouseUp()
    py.mouseUp(button='right')
    time.sleep(2)
    key_down(hwnd, 'lcontrol')
    key_up(hwnd, 'lcontrol')


def killer_skill() -> None:
    py.mouseDown(button='right')
    time.sleep(3)
    key_down(hwnd, 'lcontrol')
    key_up(hwnd, 'lcontrol')
    py.mouseUp(button='right')


def killer_action() -> None:
    """killer integral action"""
    ctrl_lst_cn = ["医生", "梦魇", "小丑", "魔王", "连体婴", "影魔", "白骨商人", "好孩子", "未知恶物"]
    need_lst_cn = ["门徒", "魔王", "死亡枪手", "骗术师", "NEMESIS", "地狱修士", "艺术家", "影魔", "奇点", "操纵者",
                   "好孩子", "未知恶物"]
    ctrl_lst_en = ["DOCTOR", "NIGHTMARE", "CLOWN", "DEMOGORGON", "TWINS", "DREDGE", "SKULL MERCHANT", "GOODGUY",
                   "UNKNOWN"]
    need_lst_en = ["PIG", "DEMOGORGON", "DEATHSLINGER", "TRICKSTER", "NEMESIS",
                   "CENOBITE", "ARTIST", "DREDGE", "SINGULARITY", "MASTERMIND", "GOODGUY", "UNKNOWN"]
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
    if ge(character_num_b - 1, 0):
        killer_num = character_num_b - 1
    else:
        killer_num -= 1
    key_down(hwnd, 'w')
    if eq(custom_select.select_killer_lst[killer_num], "枯萎者") or eq(
            custom_select.select_killer_lst[killer_num], "BLIGHT"):
        key_up(hwnd, 'w')
        for i in range(5):
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
    elif custom_select.select_killer_lst[killer_num] in need_lst:
        act_direction = random_direction()
        for i in range(5):
            key_down(hwnd, act_direction)
            time.sleep(0.05)
            key_up(hwnd, act_direction)
            time.sleep(0.7)
        killer_skillclick()
        if custom_select.select_killer_lst[killer_num] in ctrl_lst:
            killer_ctrl()
    else:
        act_direction = random_direction()
        for i in range(5):
            key_down(hwnd, act_direction)
            time.sleep(0.05)
            key_up(hwnd, act_direction)
            time.sleep(0.7)
        killer_skill()
        if custom_select.select_killer_lst[killer_num] in ctrl_lst:
            killer_ctrl()
    key_up(hwnd, 'w')


def killer_fixed_act() -> None:
    """main blood"""
    key_down(hwnd, 'w')
    killer_ctrl()
    for i in range(4):
        move_time = round(random.uniform(1.5, 5.0), 3)
        random_move(move_time)
        veertime = round(random.uniform(0.285, 0.6), 3)
        random_veer(veertime)
        py.mouseDown(button='right')
        time.sleep(4)
        py.mouseUp(button='right')
        time.sleep(0.3)
    py.mouseDown()
    time.sleep(2)
    py.mouseUp()
    key_up(hwnd, 'w')


def back_first() -> None:
    """click back the first character"""
    for i in range(self_defined_args['角色回滚滚轮到最顶端的次数']):
        py.moveTo(self_defined_args['女猎手所在位置的坐标'][0], self_defined_args['女猎手所在位置的坐标'][1])
        py.sleep(0.5)
        py.scroll(1)
    moveclick(self_defined_args['角色第一行横坐标'][0], self_defined_args['角色第一行纵坐标'][0], 1.5)


def character_selection() -> None:
    """自选特定的角色轮转"""
    global character_num_b, circle, frequency, judge, character_num
    # 角色选择的参数
    ghX = self_defined_args['角色第一行横坐标']
    ghY = self_defined_args['角色第一行纵坐标']
    glX = self_defined_args['最后七个角色横坐标']
    glY = self_defined_args['最后七个角色纵坐标']
    if eq(judge, 0):
        custom_select.read_search_killer_name()
        custom_select.match_select_killer_name()
        character_num = custom_select.match_select_killer_lst
        judge = 1
    py.sleep(1)
    moveclick(10, 10, 1, 1)
    time.sleep(1)
    moveclick(self_defined_args['匹配大厅的角色按钮坐标'][0], self_defined_args['匹配大厅的角色按钮坐标'][1], 1,
              1)  # 角色按钮
    timey = floordiv(character_num[character_num_b], 4)  # 取整
    timex = mod(character_num[character_num_b], 4)  # 取余
    time.sleep(0.5)
    back_first()
    if lt(timey, self_defined_args['最大换行次数'] + 1):  # 最大的换行次数+1
        if eq(timex, 0):
            timey -= 1
            timex = 4
        if gt(timey, 0):
            while True:
                moveclick(self_defined_args['女猎手所在位置的坐标'][0], self_defined_args['女猎手所在位置的坐标'][1],
                          1, 1)
                frequency += 1
                if eq(frequency, timey):
                    frequency = 0
                    break
        moveclick(ghX[timex - 1], ghY[timex - 1], 1.5)
    elif gt(timey, self_defined_args['最大换行次数']):  # 最大换行次数
        time.sleep(1.5)
        while True:
            moveclick(self_defined_args['女猎手所在位置的坐标'][0], self_defined_args['女猎手所在位置的坐标'][1],
                      1, 1)
            frequency += 1
            if eq(frequency, timey):
                frequency = 0
                break
        if eq(timey, (self_defined_args['最大换行次数'] + 1)) and eq(timex, 0):  # 第一个判断最大换行次数加一
            moveclick(ghX[3], ghY[3], 1.5)
        else:
            final_number = character_num[character_num_b] - (self_defined_args['最大换行次数'] + 1) * 4  # (最大换行+1)*4
            # 最后两行的序数，减1为数组序数。再减1为下标
            if gt(final_number, 1):
                final_number -= 2
                moveclick(glX[final_number], glY[final_number], 1.5)
    if lt(circle, len(character_num)):
        circle += 1
        character_num_b += 1
        if eq(character_num_b, len(character_num)):
            circle = 0
            character_num_b = 0


def start_check() -> bool:
    hwnd = win32gui.FindWindow(None, u"DeadByDaylight  ")
    if cfg.getboolean("UPDATE", "rb_chinese"):
        custom_select.select_killer_name_cn()
    elif cfg.getboolean("UPDATE", "rb_english"):
        custom_select.select_killer_name_en()
    # 判断游戏是否运行
    if eq(hwnd, 0) and cfg.getboolean("UPDATE", "rb_chinese"):
        win32api.MessageBox(hwnd, "未检测到游戏窗口，请先启动游戏。", "提示",
                            win32con.MB_OK | win32con.MB_ICONWARNING)
        return False
    elif eq(hwnd, 0) and cfg.getboolean("UPDATE", "rb_english"):
        win32api.MessageBox(hwnd, "The game window was not detected. Please start the game first.", "Prompt",
                            win32con.MB_OK | win32con.MB_ICONWARNING)
        return False
    # 判断角色选择是否规范
    if (not custom_select.select_killer_lst and cfg.getboolean("CPCI", "rb_killer")
            and not cfg.getboolean("SEKI", "cb_usefile")):
        if cfg.getboolean("UPDATE", "rb_chinese"):
            win32api.MessageBox(hwnd, "至少选择一个屠夫。", "提示", win32con.MB_OK | win32con.MB_ICONASTERISK)
            return False
        elif cfg.getboolean("UPDATE", "rb_english"):
            win32api.MessageBox(hwnd, "Choose at least one killer.", "Tip",
                                win32con.MB_OK | win32con.MB_ICONASTERISK)
            return False
    # 使用外部文件时的判断
    if eq(os.path.getsize(CUSTOM_KILLER_PATH), 0) and cfg.getboolean("SEKI", "cb_usefile"):
        if cfg.getboolean("UPDATE", "rb_chinese"):
            win32api.MessageBox(hwnd, "外部文件至少写入一个屠夫。", "提示", win32con.MB_OK | win32con.MB_ICONASTERISK)
            return False
        elif cfg.getboolean("UPDATE", "rb_english"):
            win32api.MessageBox(hwnd, "External files are written to at least one killer.", "Tip",
                                win32con.MB_OK | win32con.MB_ICONASTERISK)
            return False
    moveclick(10, 10)
    log.info(f"启动脚本····\n")
    return True


def afk() -> None:
    """挂机主体函数"""
    global stop_space, stop_action, character_num_b, judge
    list_number = len(custom_select.select_killer_lst)
    circulate_number = 0
    # 置顶
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
    # 取消置顶
    win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)

    while True:
        reconnection = False
        circulate_number += 1
        '''
        匹配
        '''
        matching = False
        while not matching:
            if event.is_set():
                break
            if not pause_event.is_set():
                pause_event.wait()

            # 判断条件是否成立
            if starthall():
                log.info(f"第{circulate_number}次脚本循环---进入匹配大厅···")
                if cfg.getboolean("CPCI", "rb_killer"):
                    time.sleep(1)
                    if eq(list_number, 1):
                        list_number = 0
                        time.sleep(1)
                    elif gt(list_number, 1):
                        character_selection()
                        time.sleep(1)
                elif cfg.getboolean("CPCI", "rb_survivor"):
                    time.sleep(1)
                while not matching:
                    if event.is_set():
                        break
                    if not pause_event.is_set():
                        pause_event.wait()

                    moveclick(self_defined_args['开始游戏和准备就绪按钮的坐标'][0],
                              self_defined_args['开始游戏和准备就绪按钮的坐标'][1], 1, 0.5)  # 处理坐标，开始匹配
                    moveclick(20, 689, 1.5)  # 商城上空白
                    if not starthall():
                        matching = True

            elif disconnect_check():
                reconnection = reconnect()
                matching = True


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
        ready_room = False  # debug:False -->True
        while not ready_room:
            if event.is_set():
                break
            if not pause_event.is_set():
                pause_event.wait()

            if readyhall():
                log.info(f"第{circulate_number}次脚本循环---进入准备大厅···")
                time.sleep(1)
                moveclick(10, 10, 1, 1)
                moveclick(self_defined_args['开始游戏和准备就绪按钮的坐标'][0],
                          self_defined_args['开始游戏和准备就绪按钮的坐标'][1], 2, 0.5)
                moveclick(20, 689)  # 商城上空白
                if not readyhall():
                    ready_room = True
            elif disconnect_check():
                reconnection = reconnect()
                ready_room = True
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
        while not game:
            if event.is_set():
                break
            if not pause_event.is_set():
                pause_event.wait()

            if gameover():
                log.info(f"第{circulate_number}次脚本循环---游戏结束···\n")
                stop_space = True  # 自动空格线程标志符
                stop_action = True  # 动作线程标志符
                moveclick(10, 10, 0.5, 2)
                # 判断段位重置
                if season_reset():
                    moveclick(self_defined_args['段位重置按钮的坐标'][0],
                              self_defined_args['段位重置按钮的坐标'][1], click_delay=1)
                # 祭礼完成
                if rites():
                    moveclick(self_defined_args['结算页祭礼完成坐标'][0],
                              self_defined_args['结算页祭礼完成坐标'][1], 0.5, 1)
                    moveclick(self_defined_args['结算页祭礼完成坐标'][2], self_defined_args['结算页祭礼完成坐标'][3])
                time.sleep(3)

                # 删除动作线程的输入字符
                py.press('enter')
                py.hotkey('ctrl', 'a')
                py.press('delete')
                # 判断是否开启留言
                if (cfg.getboolean("CPCI", "cb_killer_do")
                        and cfg.getboolean("CPCI", "rb_killer")):
                    auto_message()
                moveclick(self_defined_args['结算页继续按钮坐标'][0],
                          self_defined_args['结算页继续按钮坐标'][1], 0.5, 1)  # return hall
                moveclick(10, 10)  # 避免遮挡
                if not gameover():
                    game = True
                elif disconnect_check():
                    reconnection = reconnect()
                    game = True
            else:
                if disconnect_check():
                    reconnection = reconnect()
                    game = True

        # 重连返回值判断
        if reconnection:
            continue

        if event.is_set():
            stop_space = True  # 自动空格线程标志符
            stop_action = True  # 动作线程标志符
            character_num_b = 0  # 列表的下标归零
            judge = 0
            custom_select.select_killer_lst.clear()
            custom_select.match_select_killer_lst.clear()
            return


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
    CHECK_PATH = os.path.join(BASE_DIR, "tesseract-ocr")
    OCR_PATH = os.path.join(BASE_DIR, "tesseract-ocr\\tesseract.exe")
    TESSDATA_PREFIX = os.path.join(BASE_DIR, "tesseract-ocr\\tessdata")
    os.environ['OCR'] = OCR_PATH
    os.environ['TESSDATA_PREFIX'] = TESSDATA_PREFIX
    os.environ['NO_PROXY'] = 'gitee.com'
    CFG_PATH = os.path.join(BASE_DIR, "cfg.cfg")
    SEARCH_PATH_CN = os.path.join(BASE_DIR, "searchfile_cn.txt")
    SEARCH_PATH_EN = os.path.join(BASE_DIR, "searchfile_en.txt")
    CUSTOM_KILLER_PATH = os.path.join(BASE_DIR, "custom_killer.txt")
    SDAGRS_PATH = os.path.join(BASE_DIR, "SDargs.json")
    TRANSLATE_PATH = os.path.join(BASE_DIR, "picture\\transEN.qm")
    LOG_PATH = os.path.join(BASE_DIR, "debug_data.log")
    play_str = WaveObject.from_wave_file(os.path.join(BASE_DIR, "picture\\start.wav"))
    play_pau = WaveObject.from_wave_file(os.path.join(BASE_DIR, "picture\\pause.wav"))
    play_res = WaveObject.from_wave_file(os.path.join(BASE_DIR, "picture\\resume.wav"))
    play_end = WaveObject.from_wave_file(os.path.join(BASE_DIR, "picture\\close.wav"))
    hwnd = win32gui.FindWindow(None, u"DeadByDaylight  ")

    # 自定义参数
    self_defined_args = {'赛后发送消息': 'DBD-AFK League',
                         '人类发送消息': 'AFK',
                         '最大换行次数': 6,
                         '女猎手所在位置的坐标': [404, 536],
                         '角色第一行横坐标': [405, 548, 703, 854],
                         '角色第一行纵坐标': [314, 323, 318, 302],
                         '最后七个角色横坐标': [549, 709, 858, 384, 556, 715, 882],
                         '最后七个角色纵坐标': [517, 528, 523, 753, 741, 749, 750],
                         '角色回滚滚轮到最顶端的次数': 3,
                         '开始游戏、准备就绪按钮的识别范围': [1446, 771, 1920, 1080],
                         '匹配大厅识别关键字': ["开始游戏", "PLAY"],
                         '准备大厅识别关键字': ["准备就绪", "READY"],
                         '准备取消按钮识别关键字': ["取消", "CANCEL"],
                         '结算页的识别范围': [56, 46, 370, 172],
                         '结算页识别关键字': ["比赛", "得分", "你的", "MATCH", "SCORE"],
                         '结算页每日祭礼的识别范围': [106, 267, 430, 339],
                         '结算页每日祭礼识别关键字': ["每日", "DAILY RITUALS"],
                         '段位重置的识别范围': [192, 194, 426, 291],
                         '段位重置识别关键字': ["重置", "RESET"],
                         '主界面的每日祭礼识别范围': [441, 255, 666, 343],
                         '主页面每日祭礼识别关键字': ["每日", "DAILY RITUALS"],
                         '主页面的识别范围': [187, 50, 317, 159],
                         '主页面识别关键字': ["开始", "PLAY"],
                         '断线检测的识别范围': [299, 614, 1796, 800],
                         '断线检测识别关键字': ["好的", "关闭", "OK", "CLOSE", "继续", "CONTINUE"],
                         '新内容的识别范围': [548, 4, 1476, 256],
                         '新内容识别关键字': ["新内容", "NEW CONTENT"],
                         'event_rewards': ["-"],  # 未完成的事件奖励,留空即可
                         '开始游戏和准备就绪按钮的坐标': [1742, 931],
                         '段位重置按钮的坐标': [1468, 843],
                         '结算页祭礼完成坐标': [396, 718, 140, 880],
                         '结算页继续按钮坐标': [1761, 1009],
                         '主页面新闻关闭坐标': [1413, 992],
                         '主页面祭礼关闭坐标': [545, 880],
                         '主页面开始坐标': [320, 100],
                         '主页面逃生者坐标': [339, 320],
                         '主页面杀手坐标': [328, 224],
                         '匹配大厅的角色按钮坐标': [141, 109],
                         '匹配大厅二值化阈值': [120, 130, 1],
                         '准备房间二值化阈值': [120, 130, 1],
                         '结算页二值化阈值': [80, 130, 1],
                         '结算页每日祭礼二值化阈值': [120, 130, 1],
                         '段位重置二值化阈值': [120, 130, 1],
                         '主页面每日祭礼二值化阈值': [130, 130, 1],
                         '主页面开始按钮二值化阈值': [130, 130, 1],
                         '断线检测二值化阈值': [120, 130, 1],
                         '新内容二值化阈值': [130, 130, 1],
                         '准备取消按钮二值化阈值': [70, 130, 1]
                         }

    # UI设置
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    dbd_window = DbdWindow()
    sel_dialog = SelectWindow()
    adv_dialog = AdvancedParameter()
    tf_widget = TipForm()
    shl_dialog = ShowLog()
    debug_dialog = DebugTool()

    # 配置文件参数
    cpci_keys = [
        "rb_survivor",
        "cb_survivor_do",
        "rb_killer",
        "cb_killer_do",
        "rb_fixed_mode",
        "rb_random_mode"
    ]
    cpci_dict = {key: getattr(dbd_window.main_ui, key) for key in cpci_keys}

    seki_keys = [
        "cb_usefile"
    ]
    seki_dict = {key: getattr(sel_dialog.select_ui, key) for key in seki_keys}

    update_keys = [
        "cb_autocheck",
        "rb_chinese",
        "rb_english"
    ]
    update_dict = {key: getattr(dbd_window.main_ui, key) for key in update_keys}

    # 提取 CUSSEC 部分的配置 [随版本更改]
    cussec_keys = [
        "cb_" + key for key in [
            "jiage", "dingdang", "dianjv", "hushi", "tuzi", "maishu", "linainai", "laoyang",
            "babu", "fulaidi", "zhuzhu", "xiaochou", "lingmei", "juntuan", "wenyi", "guimian",
            "mowang", "guiwushi", "qiangshou", "sanjiaotou", "kumo", "liantiying", "gege",
            "zhuizhui", "dingzitou", "niaojie", "zhenzi", "yingmo", "weishu", "eqishi",
            "baigu", "jidian", "yixing", "qiaji", "ewu"
        ]
    ]
    cussec_dict = {key: getattr(sel_dialog.select_ui, key) for key in cussec_keys}
    # 合并所有部分到最终的 ui_components
    ui_components = {
        "CPCI": cpci_dict,
        "SEKI": seki_dict,
        "UPDATE": update_dict,
        "CUSSEC": cussec_dict
    }

    # 配置日志格式
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    # 配置文件处理器，将日志写入文件
    file_handler = logging.FileHandler(LOG_PATH, encoding='utf-8')
    file_handler.setLevel(logging.INFO)  # 设置处理器的日志级别
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)
    # 获取日志记录器对象
    log = logging.getLogger(__name__)
    log.addHandler(file_handler)
    log.setLevel(logging.INFO)  # 设置记录器的日志级别
    atexit.register(close_logger)  # 程序退出时关闭日志
    atexit.register(del_jpg)  # 程序退出时删除图片
    cfg = ConfigParser()  # 配置文件
    cfg.read(CFG_PATH, encoding='utf-8')
    settings = ConfigObj(CFG_PATH, default_encoding='utf8')
    initialize()
    read_cfg()

    if QLocale.system().language() != QLocale.Chinese or cfg.getboolean("UPDATE", "rb_english"):
        dbd_window.rb_english_change()
    custom_select = CustomSelectKiller()
    screen = QApplication.primaryScreen()
    begin_state = False  # 开始状态
    character_num_b = 0  # 列表的下标
    character_num = []  # 列表，表示选择的角色序号
    circle = 0  # 选择的次数
    judge = 0
    frequency = 0  # 换行的次数
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
    notice()  # 通知消息
    authorization()  # 授权验证
    hotkey.start()  # 热键监听
    if cfg.getboolean("UPDATE", "cb_autocheck"):  # 检查更新
        check_update()
    check_ocr()  # 检查初始化
    dbd_window.show()
    sys.exit(app.exec_())

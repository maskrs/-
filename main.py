# -*- mode: python ; coding: utf-8 -*-
import functools
import glob
import os.path
import random
import subprocess
import sys
import threading
import time
import webbrowser
from configparser import ConfigParser
from operator import lt, eq, gt, ge, ne, floordiv, mod
import pyautogui as py
import pytesseract
import re
import requests
import win32api
import win32con
import win32gui
import keyboard
from PIL import Image
from PyQt5.QtCore import QTranslator, QLocale, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from configobj import ConfigObj
from DBDAutoScriptUI import Ui_MainWindow
from keyboard_operation import key_down, key_up
from selec_killerUI import Ui_Dialog
from simpleaudio import WaveObject
from functools import wraps
from typing import Callable, List


class Coord:
    def __init__(self, x1_coor, y1_coor, x2_coor=0, y2_coor=0):
        self.x1_coor = x1_coor
        self.y1_coor = y1_coor
        self.x2_coor = x2_coor
        self.y2_coor = y2_coor

    def processed_coord(self):
        # 获取缩放后的屏幕分辨率,并获得比例
        ScreenX = win32api.GetSystemMetrics(0)  # 屏幕分辨率 横向
        ScreenY = win32api.GetSystemMetrics(1)  # 屏幕分辨率 纵向
        factorX = ScreenX / 1920
        factory = ScreenY / 1080
        self.x1_coor = self.x1_coor * factorX
        self.y1_coor = self.y1_coor * factory
        self.x2_coor = self.x2_coor * factorX
        self.y2_coor = self.y2_coor * factory
        return self.x1_coor, self.y1_coor, self.x2_coor, self.y2_coor

    def area_check(self):
        self.x1_coor = int(self.x1_coor)
        self.y1_coor = int(self.y1_coor)
        self.x2_coor = int(self.x2_coor)
        self.y2_coor = int(self.y2_coor)
        return self.x1_coor, self.y1_coor, self.x2_coor, self.y2_coor


class Logger(object):
    def __init__(self, log_path="default.log"):
        import sys
        self.terminal = sys.stdout
        self.log = open(log_path, "wb", buffering=0)  # , encoding="utf-8"

    def print(self, *message):
        message = ",".join([str(it) for it in message])
        # self.terminal.write(str(message) + "\n")
        self.log.write(str(message).encode('utf-8') + b"\n")

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()


def begin():
    global begin_state
    cfg.read(CFG_PATH, encoding='utf-8')
    if not begin_state:
        begin_state = True
        open(LOG_PATH, 'w').close()
        save_cfg()
        if start_check():
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
            log.print(f"{now_time()}……//////退出时删除文件时出错: {file} - {e.strerror}")


class DbdWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.main_ui = Ui_MainWindow()
        self.sel_dialog = SelectWindow()
        self.trans = QTranslator()
        self.main_ui.setupUi(self)
        self.main_ui.pb_select_cfg.clicked.connect(self.pb_select_cfg_click)
        self.main_ui.pb_search.clicked.connect(self.pb_search_click)
        self.main_ui.pb_start.clicked.connect(begin)
        self.main_ui.pb_stop.clicked.connect(kill)
        self.main_ui.pb_github.clicked.connect(self.github)
        self.main_ui.rb_chinese.clicked.connect(self.rb_chinese_change)
        self.main_ui.rb_english.clicked.connect(self.rb_english_change)
        self.main_ui.pb_help.clicked.connect(self.pb_help_click)

    def pb_search_click(self):
        global stop_thread, checktip
        if not checktip.is_alive():
            stop_thread = False
            checktip = threading.Thread(target=check_tip)
            checktip.start()
        # 判断游戏是否运行
        hwnd = win32gui.FindWindow(None, u"DeadByDaylight  ")
        if eq(hwnd, 0) and cfg.getboolean("UPDATE", "rb_chinese"):
            win32api.MessageBox(hwnd, "未检测到游戏窗口，请先启动游戏。", "提示",
                                win32con.MB_OK | win32con.MB_ICONWARNING)
            sys.exit()
        elif eq(hwnd, 0) and cfg.getboolean("UPDATE", "rb_english"):
            win32api.MessageBox(hwnd, "The game window was not detected. Please start the game first.", "Prompt",
                                win32con.MB_OK | win32con.MB_ICONWARNING)
            sys.exit()
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
        notification.show()
        self.notification_hwnd = win32gui.FindWindow(None, "Transparent Notification")
        win32gui.SetWindowPos(self.notification_hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
        time.sleep(2)
        log.print(f"{now_time()}……//////开始检索。\n********************")
        moveclick(141, 109, 1, 1)  # 打开角色按钮
        back_first()
        thread = threading.Thread(target=self.run_search_and_close_notification)  # 无边框窗口通知
        thread.start()

    def pb_help_click(self):
        webbrowser.open("https://x06w8gh3wwh.feishu.cn/wiki/JKjhwJBNFi6pj5kBoB1cS7HGnkU?from=from_copylink")

    def run_search_and_close_notification(self):
        custom_select.search_killer_name(self_defined_parameter['killer_number'])
        win32gui.SetWindowPos(self.notification_hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
        notification.close()

    def github(self):
        webbrowser.open("https://github.com/maskrs/DBD_AFK_TOOL")

    def pb_select_cfg_click(self):
        self.sel_dialog.select_ui.retranslateUi(self)
        self.sel_dialog.exec()

    def rb_chinese_change(self):
        # 默认的中文包，不要新建
        self.trans.load('zh_CN')
        _app = QApplication.instance()
        _app.installTranslator(self.trans)
        self.main_ui.retranslateUi(self)
        self.main_ui.lb_message.show()
        save_cfg()
        cfg.read(CFG_PATH, encoding='utf-8')

        # settings.setValue("UPDATE/rb_chinese", dbd_window.main_ui.rb_chinese.isChecked())
        # settings.setValue("UPDATE/rb_english", dbd_window.main_ui.rb_english.isChecked())

    def rb_english_change(self):
        # 导入语言包，english是翻译的.qm文件
        self.trans.load(TRANSLATE_PATH)
        _app = QApplication.instance()
        _app.installTranslator(self.trans)
        self.main_ui.retranslateUi(self)
        self.main_ui.lb_message.show()
        save_cfg()
        cfg.read(CFG_PATH, encoding='utf-8')
        # settings.setValue("UPDATE/rb_chinese", dbd_window.main_ui.rb_chinese.isChecked())
        # settings.setValue("UPDATE/rb_english", dbd_window.main_ui.rb_english.isChecked())

    #
    # def cb_rotate_solo_click(self):
    #     self.main_ui.cb_rotate_order.setChecked(False)
    #     self.main_ui.cb_select_killer.setChecked(False)
    #
    # def cb_rotate_order_click(self):
    #     self.main_ui.cb_rotate_solo.setChecked(False)
    #     self.main_ui.cb_select_killer.setChecked(False)
    #
    # def cb_select_killer_click(self):
    #     self.main_ui.cb_rotate_solo.setChecked(False)
    #     self.main_ui.cb_rotate_order.setChecked(False)


class SelectWindow(QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.select_ui = Ui_Dialog()
        self.select_ui.setupUi(self)
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

    def pb_save_click(self):
        save_cfg()
        cfg.read(CFG_PATH, encoding='utf-8')


class TransparentNotification(QWidget):
    def __init__(self):
        super().__init__()
        cfg.read(CFG_PATH)
        self.setWindowTitle('Transparent Notification')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.X11BypassWindowManagerHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(800, 25, 250, 50)  # 设置窗口大小和位置
        if cfg.getboolean("UPDATE", "rb_chinese"):
            self.label = QLabel('检索中…', self)
        elif cfg.getboolean("UPDATE", "rb_english"):
            self.label = QLabel('SEARCHING…', self)
        self.label.setStyleSheet('color: pink; font-size: 22px; font-weight: bold; '
                                 'font-style: italic; text-align: center;'
                                 'background-color: rgba(192, 192, 192, 0);')
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(40, 5, 250, 45)  # 设置标签大小和位置


class CustomSelectKiller:
    def __init__(self):
        self.ocr_error = 0
        self.killer_name_array = []
        self.own_number = 0
        self.select_killer_lst = []
        self.match_select_killer_lst = []
        # 随版本更改
        if cfg.getboolean("UPDATE", "rb_chinese"):
            self.all_killer_name = self_defined_parameter['all_killer_name_CN']
            self.SEARCH_PATH = SEARCH_PATH_CN
            self.sign_1 = "未知恶物"
            self.sign_2 = "角色"
        elif cfg.getboolean("UPDATE", "rb_english"):
            self.all_killer_name = self_defined_parameter['all_killer_name_EN']
            self.SEARCH_PATH = SEARCH_PATH_EN
            self.sign_1 = "UNKNOWN"
            self.sign_2 = "CHARACTERS"
        # print(self.all_killer_name)  ##### debug

    def read_search_killer_name(self):
        with open(self.SEARCH_PATH, "r", encoding='UTF-8') as search_file:
            self.killer_name_array = search_file.readlines()
            self.killer_name_array = [c.strip() for c in self.killer_name_array]

    @staticmethod
    def keep_letters_only(input_string):
        """只保留字母字符"""
        cleaned_string = re.sub(r'[^a-zA-Z]', '', input_string)
        return cleaned_string

    def killer_name_ocr(self):
        found = False  # 设置一个标志
        find = False
        for sum_number in range(130, 60, -10):
            if cfg.getboolean("UPDATE", "rb_chinese"):  # user use chinese
                self.killer_name = img_ocr(390, 35, 744, 79, sum_number)
            elif cfg.getboolean("UPDATE", "rb_english"):
                self.killer_name = img_ocr(453, 35, 744, 79, sum_number)
                self.killer_name = self.keep_letters_only(self.killer_name)
            # print('当前检测内容：' + self.killer_name)  ##### debug
            if ge(len(self.killer_name), 2):
                for name in self.all_killer_name:
                    if self.killer_name in name:
                        # print(f"{name} 已匹配")  ##### debug
                        found = True  # 找到匹配，设置标志为True
                        break

            if found:  # 如果找到匹配，跳出最外层循环
                break

        if found:
            global stop_thread
            self.write_killer_name()
            if self.killer_name in self.sign_1:  # 随版本更改
                self.ocr_error = 1
                back_first()
                moveclick(387, 300, 1, 1)
                moveclick(141, 109, 1, 1)  # 关闭角色按钮
                id = win32gui.FindWindow(None, "DBD_AFK_TOOL")
                win32gui.SetWindowPos(id, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
                win32gui.SetWindowPos(id, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
                if cfg.getboolean("UPDATE", "rb_chinese"):
                    win32api.MessageBox(0, "角色检索已完成", "提醒", win32con.MB_ICONASTERISK)
                    stop_thread = True
                elif cfg.getboolean("UPDATE", "rb_english"):
                    win32api.MessageBox(0, "Character search completed", "Tips", win32con.MB_ICONASTERISK)
                    stop_thread = True

                # with open(SEARCH_PATH_CN, "w", encoding='UTF-8') as cn_file:
                #     cn_file.write("\n".join(self.killer_name_array))
                self.wrkn_file()
                self.killer_name_array.clear()

        else:
            for sum_number in range(180, 120, -10):
                if cfg.getboolean("UPDATE", "rb_chinese"):
                    self.ocr_notown = img_ocr(241, 46, 339, 90, sum_number)
                elif cfg.getboolean("UPDATE", "rb_english"):
                    self.ocr_notown = img_ocr(329, 36, 470, 84, sum_number)  # 320,36,463,83
                # print('\n当前notown：' + self.ocr_notown)  ##### debug
                if ge(len(self.ocr_notown), 2):
                    if self.ocr_notown in self.sign_2:
                        find = True
                        break
            if find:
                self.ocr_error = 1
                time.sleep(2)
                py.keyDown('esc')
                py.keyUp('esc')
                time.sleep(1)
                py.keyDown('esc')
                py.keyUp('esc')
                id = win32gui.FindWindow(None, "DBD_AFK_TOOL")
                win32gui.SetWindowPos(id, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
                win32gui.SetWindowPos(id, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
                if cfg.getboolean("UPDATE", "rb_chinese"):
                    win32api.MessageBox(0, "角色检索已完成", "提醒", win32con.MB_ICONASTERISK)
                    stop_thread = True
                elif cfg.getboolean("UPDATE", "rb_english"):
                    win32api.MessageBox(0, "Character search completed", "Tips", win32con.MB_ICONASTERISK)
                    stop_thread = True

                self.wrkn_file()
                self.killer_name_array.clear()
            else:
                back_first()
                moveclick(387, 300, 1, 1)
                moveclick(141, 109, 1, 1)  # 关闭角色按钮
                id = win32gui.FindWindow(None, "DBD_AFK_TOOL")
                win32gui.SetWindowPos(id, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
                win32gui.SetWindowPos(id, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
                if cfg.getboolean("UPDATE", "rb_chinese"):
                    win32api.MessageBox(0, "检索未完成，请检查以下：\n" + str(
                        self.killer_name_array) + "\n有错误或乱码请重新检索",
                                        "提醒", win32con.MB_ICONASTERISK)
                    stop_thread = True
                elif cfg.getboolean("UPDATE", "rb_english"):
                    win32api.MessageBox(0, "Search not completed, please check the following:\n" + str(
                        self.killer_name_array) + "\nIf there is an error or garbled code, please re-search", "Tips",
                                        win32con.MB_ICONASTERISK)
                    stop_thread = True

                self.wrkn_file()
                self.ocr_error = 1
                self.killer_name_array.clear()

    def write_killer_name(self):
        # 必须与self_defined_parameter['all_killer_name_CN/EN']中的值一致
        self.name_mapping = {
            '设陷者顽皮熊': '设陷者',
            '折士': '护士',
            '迈克尔.迈尔斯迈克尔·迈尔斯迈克尔\'迈尔斯': '迈克尔.迈尔斯',
            '妖巫妊巫': '妖巫',
            '食人广': '食人魔',
            '梦广梦硒梦麻梦厦': '梦魇',
            '小于小吾小王小各': '小丑',
            '影广影魔': '影魔',
            '贞子页子': '贞子'
        }
        for name, normalized_name in self.name_mapping.items():
            if self.killer_name in name:
                self.killer_name = normalized_name
                break
        log.print(f"{now_time()}……//////{self.killer_name}已匹配。\n********************")
        self.killer_name_array.append(self.killer_name)

    def wrkn_file(self):
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

        # 遍历 killer_name_array
        for killer_name in self.killer_name_array:
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

    def search_killer_name(self, ownnumber):
        self.ocr_error = 0
        choice_last_x = [546, 708, 847, 395, 551, 705, 855]
        choice_last_y = [497, 495, 486, 724, 717, 717, 710]
        change_x = 387
        change_y = 300
        changecount_x = 0
        changecount_y = 0
        count = 0
        n = 0
        self.own_number = ownnumber  # 拥有的角色数量
        result_integer = self.own_number // 4  # 取整
        result_remainder = self.own_number % 4  # 取余数

        if result_remainder == 0:
            result_integer = result_integer - 1
            result_remainder = 4

        timetypeone = result_integer
        timetypetwo = result_remainder
        # 随版本更新 最大值
        if result_integer >= 8:
            timetypeone = 7  # 最大值-1

        while True:
            if self.ocr_error == 1:
                break
            if count == timetypeone:
                moveclick(387, 530, 1, 1)
                self.killer_name_ocr()
                if self.ocr_error == 1:
                    break
                if result_integer > 5:
                    break
                change_x = 387
                change_y = 300
                change = Coord(change_x, change_y)
                change.processed_coord()
                change.area_check()
                for i in range(timetypetwo):
                    py.moveTo(change.x1_coor, change.y1_coor)
                    if n != 0:
                        time.sleep(1)
                        py.click()
                        time.sleep(1)
                        self.killer_name_ocr()
                        if self.ocr_error == 1:
                            break
                    n += 1
                    change_x += 200
                break
            while True:
                if self.ocr_error == 1:
                    break
                change = Coord(change_x, change_y)
                change.processed_coord()
                change.area_check()
                moveclick(change.x1_coor, change.y1_coor, 1, 1)
                self.killer_name_ocr()
                if self.ocr_error == 1:
                    break
                change_y = 300
                change_x += 158
                changecount_x += 1
                if changecount_x == 4:
                    break
            change_x = 387
            changecount_x = 0
            changecount_y += 1
            change_y += 225
            count += 1
            if changecount_y == 2:
                changecount_y = 0
            if self.ocr_error == 1:
                break
                ###
        if result_integer > 6:  # 最大值-2
            if result_integer <= 7:  # 最大值-1
                timetypetwo = timetypetwo - 1
            elif result_integer >= 8:  # 最大值
                timetypetwo += 3
            n = 0
            for i in range(timetypetwo):
                if self.ocr_error == 1:
                    break
                linex = choice_last_x[n]
                liney = choice_last_y[n]
                line = Coord(linex, liney)
                line.processed_coord()
                line.area_check()
                moveclick(line.x1_coor, line.y1_coor, 1, 1)
                self.killer_name_ocr()
                # if self.ocr_error == 1:
                #     break
                n += 1

    def select_killer_name_CN(self):
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

    def select_killer_name_EN(self):
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
        for i in self.select_killer_lst:
            self.match_select_killer_lst.append(self.killer_name_array.index(i) + 1)

    def debug_traverse(self):  # 遍历调试
        killer_name_array_len = len(self.killer_name_array)
        print(*self.killer_name_array, sep=",")
        for i in range(0, killer_name_array_len):
            print(self.killer_name_array[i])


def initialize():
    """ 配置初始化 """
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
        "UPDATE": {
            "cb_autocheck": True,
            "rb_chinese": True,
            "rb_english": False
        },
        "CUSSEC": {key: False for key in cussec_keys}
    }

    for section, options in settings_dict.items():
        if section not in cfg:
            cfg[section] = {}
        for option, value in options.items():
            if option not in cfg[section]:
                cfg[section][option] = str(value)
    with open(CFG_PATH, 'w') as configfile:
        cfg.write(configfile)


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
    if cfg.getboolean("CPCI", "rb_killer"):
        dbd_window.main_ui.cb_killer_do.setEnabled(True)
    # if cfg.getboolean("UPDATE", "rb_english"):
    #     dbd_window.main_ui.lb_message.hide()


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
    ver_now = 'V5.1.7'
    html_str = requests.get('https://gitee.com/kioley/DBD_AFK_TOOL').content.decode()
    ver_new = re.search('title>(.*?)<', html_str, re.S).group(1)[13:19]
    if ne(ver_now, ver_new):
        # confirm = pyautogui.confirm(text=text, title="检查更新", buttons=['OK', 'Cancel'])
        if cfg.getboolean("UPDATE", "rb_chinese"):
            confirm = win32api.MessageBox(0,
                                          "检查到新版本：{b}\n\n当前的使用版本是：{a}，推荐更新。".format(a=ver_now,
                                                                                                      b=ver_new)
                                          , "检查更新", win32con.MB_YESNO | win32con.MB_ICONQUESTION)
            if eq(confirm, 6):  # 打开
                webbrowser.open("https://github.com/maskrs/DBD_AFK_TOOL/releases")
                subprocess.call("update.exe")
                sys.exit()
        elif cfg.getboolean("UPDATE", "rb_english"):
            confirm = win32api.MessageBox(0,
                                          "New version detected: {b}\n\nThe current version is: {a}, recommended update.".format(
                                              a=ver_now, b=ver_new)
                                          , "Check for updates", win32con.MB_YESNO | win32con.MB_ICONQUESTION)
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
    notice_now = 'test giw'
    html_str = requests.get('https://gitee.com/kioley/test-git').content.decode()
    notice_new = re.search('title>(.*?)<', html_str, re.S).group(1)[0:8]
    notice = re.search('title>(.*?)<', html_str, re.S).group(1)[9:]
    if ne(notice_now, notice_new):
        win32api.MessageBox(0, notice, "通知", win32con.MB_OK | win32con.MB_ICONINFORMATION)


def screen_age():
    def get_screen_size():
        """获取缩放后的分辨率"""
        w = win32api.GetSystemMetrics(0)
        h = win32api.GetSystemMetrics(1)
        return w, h

    screen_size = get_screen_size()
    log.print(f"{now_time()}-----缩放后的分辨率为：{screen_size}\n")


def hall_tip():
    """Child thread, survivor hall tip"""
    while True:
        if readyhall():
            py.press('enter')
            py.press('delete', 3)
            py.write('AFK')
            py.press('enter')
            time.sleep(30)
        else:
            time.sleep(1)


def check_tip():
    """检测tip弹窗，置顶"""
    while not stop_thread:
        time.sleep(0.5)
        id = 0
        id1 = win32gui.FindWindow(None, u"提醒")
        id2 = win32gui.FindWindow(None, u"Tips")
        if ne(id1, 0):
            id = id1
        elif ne(id2, 0):
            id = id2
        if ne(id, 0):
            win32gui.SetWindowPos(id, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                  win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
            # win32gui.SetWindowPos(id, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
            #                       win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
    handle = win32gui.FindWindow(None, "DBD_AFK_TOOL")
    win32gui.SetWindowPos(handle, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                          win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
    win32gui.SetWindowPos(handle, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                          win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)


def autospace():
    """Child thread, auto press space"""
    while not stop_space:
        if not pause:
            key_down(hwnd, 'space')
            time.sleep(5)
        else:
            pass


def action():
    cfg.read(CFG_PATH, encoding='utf-8')
    time.sleep(1)
    while not stop_action:
        if not pause:
            if cfg.getboolean("CPCI", "rb_survivor"):
                survivor_action()
            elif (cfg.getboolean("CPCI", "rb_fixed_mode") and
                  cfg.getboolean("CPCI", "rb_killer")):
                killer_fixed_act()
            elif (cfg.getboolean("CPCI", "rb_random_mode") and
                  cfg.getboolean("CPCI", "rb_killer")):
                killer_action()
        else:
            pass


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
        except Exception as e:
            print(f"An error occurred: {e}")

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


def ocr_range_inspection(range_args: tuple, keywords: List[str],
                         ocr_func: Callable, x1: int, y1: int, x2: int, y2: int) -> Callable:
    def decorator(func):
        @functools.wraps(func)
        def wrapper():
            for threshold in range(*range_args):
                # 调用img_ocr函数，传入固定坐标和阈值
                ocr_result = ocr_func(x1, y1, x2, y2, sum=threshold)
                log.print(f"{now_time()}……//////识别内容为：\n{ocr_result}\n********************")
                if any(keyword in ocr_result for keyword in keywords):
                    log.print(f"{now_time()}……///{func.__name__}()识别函数已识别···")
                    return True
            log.print(f"{now_time()}……///{func.__name__}()识别函数未识别···")
            return False

        return wrapper

    return decorator


def img_ocr(x1, y1, x2, y2, sum=128):
    """OCR识别图像，返回字符串
    :return: string"""
    hwnd = win32gui.FindWindow(None, u"DeadByDaylight  ")
    ocrXY = Coord(x1, y1, x2, y2)
    ocrXY.processed_coord()
    ocrXY.area_check()
    image = screen.grabWindow(hwnd).toImage()

    # 生成唯一的文件名
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"image_{timestamp}.jpg"
    image.save(filename)

    # 打开图像文件并裁剪、二值化
    with Image.open(filename) as img:
        cropped = img.crop((ocrXY.x1_coor, ocrXY.y1_coor, ocrXY.x2_coor, ocrXY.y2_coor))
        grayscale_image = cropped.convert('L')
        binary_image = grayscale_image.point(lambda x: 0 if x < sum else 255, '1')
        binary_image.save(filename)  # 保存二值化后的图像到相同的文件

    custom_config = r'--oem 3 --psm 6'
    # 判断中英文切换模型
    lan = "chi_sim+eng"  # 默认简体中文+英文
    if cfg.getboolean("UPDATE", "rb_chinese"):
        lan = "chi_sim"
    elif cfg.getboolean("UPDATE", "rb_english"):
        lan = "eng"

    with Image.open(filename) as ocr_image:
        # 使用Tesseract OCR引擎识别图像中的文本
        result = pytesseract.image_to_string(ocr_image, config=custom_config, lang=lan)
        result = "".join(result.split())
    time.sleep(0.5)  # 确保文件关闭
    if os.path.exists(filename):
        try:
            os.remove(filename)  # 尝试删除文件
        except Exception as e:
            log.print(f"{now_time()}……//////ocr检索删除文件时出错: {filename} - {e}")
    else:
        log.print(f"{now_time()}……//////ocr检索删除文件时出错: 文件不存在 - {filename}")

    return result


@ocr_range_inspection((130, 80, -10), ["开始游戏", "PLAY"],
                      img_ocr, 1446, 771, 1920, 1080)
def starthall() -> bool:
    """check the start  hall
    :return: bool"""
    pass


@ocr_range_inspection((130, 80, -10), ["准备就绪", "READY"],
                      img_ocr, 1446, 771, 1920, 1080)
def readyhall() -> bool:
    """check the  ready hall
    :return: bool"""
    pass


@ocr_range_inspection((120, 50, -10), ["取消", "CANCEL"], img_ocr, 1446, 771, 1920, 1080)
def readycancle() -> bool:
    """检查游戏准备后的取消，消失就进入对局加载
    :return: bool"""
    pass


@ocr_range_inspection((130, 50, -10), ["比赛", "得分", "MATCH", "SCORE"],
                      img_ocr, 56, 46, 370, 172)
def gameover() -> bool:
    """检查对局后的继续
    :return: bool"""
    pass


# def starthall() -> bool:
#     """check the start  hall
#     :return: bool"""
#     log.print(f"{now_time()}……///starthall()识别函数识别中···")
#     for sum in range(130, 80, -10):
#         ocr = img_ocr(1446, 771, 1920, 1080, sum)
#         log.print(f"{now_time()}……//////识别内容为：\n{ocr}\n********************")
#         if "开始游戏" in ocr or "PLAY" in ocr:
#             log.print(f"{now_time()}……///starthall()识别函数已识别···")
#             return True
#     log.print(f"{now_time()}……///starthall()识别函数未识别···")
#     return False
#
#
# def readyhall() -> bool:
#     """check the  ready hall
#     :return: bool"""
#     log.print(f"{now_time()}……///readyhall()识别函数识别中···")
#     for sum in range(130, 80, -10):
#         ocr = img_ocr(1446, 771, 1920, 1080, sum)
#         log.print(f"{now_time()}……//////识别内容为：\n{ocr}\n********************")
#         if "准备就绪" in ocr or "READY" in ocr:
#             log.print(f"{now_time()}……///readyhall()识别函数已识别···")
#             return True
#     log.print(f"{now_time()}……///readyhall()识别函数未识别···")
#     return False
#
#
# def readycancle() -> bool:
#     """检查游戏准备后的取消，消失就进入对局加载
#     :return: bool"""
#     log.print(f"{now_time()}……///readycancle()识别函数识别中···")
#     for sum in range(120, 50, -10):
#         ocr = img_ocr(1446, 771, 1920, 1080, sum)
#         log.print(f"{now_time()}……//////识别内容为：\n{ocr}\n********************")
#         if "取消" in ocr or "CANCEL" in ocr:
#             log.print(f"{now_time()}……///readycancle()识别函数已识别···")
#             return True
#     log.print(f"{now_time()}……///readycancle()识别函数未识别···")
#     return False
#
#
# def gameover() -> bool:
#     """检查对局后的继续
#     :return: bool"""
#     log.print(f"{now_time()}……///gameover()识别函数识别中···")
#     for sum in range(130, 50, -10):
#         ocr = img_ocr(56, 46, 370, 172, sum)  # 70
#         log.print(f"{now_time()}……//////识别内容为：\n{ocr}\n********************")
#         # ocr2 = img_ocr(1745, 991, 1820, 1028, 30)
#         if "比赛" in ocr or "得分" in ocr or "MATCH" in ocr or "SCORE" in ocr:
#             log.print(f"{now_time()}……///gameover()识别函数已识别···")
#             return True
#     log.print(f"{now_time()}……///gameover()识别函数未识别···")
#     return False


def stage_judge():
    """判断游戏所处在的阶段"""

    log.print(f"{now_time()}……///脚本正在使用stage_judge()判断游戏所处阶段···")
    if starthall():
        stage = "匹配大厅"
        return stage
    elif readyhall():
        stage = "准备房间"
        return stage
    else:
        return None


def now_time():
    # 获得当前时间时间戳
    now = int(time.time())
    # 转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime


@ocr_range_inspection((130, 80, -10), ["每日祭礼", "DAILY RITUALS"],
                      img_ocr, 106, 267, 430, 339)
def rites() -> bool:
    """check rites complete
    :return:bool"""
    pass


# @ocr_range_inspection((130, 80, -10), ["每日祭礼", "DAILY RITUALS"])
# 检测活动奖励  #####未完成
def event_rewards() -> bool:
    """check the event rewards
    :return: bool"""
    eventXY = Coord(1864, 455, 1920, 491)
    eventXY.processed_coord()
    eventXY.area_check()


@ocr_range_inspection((130, 80, -10), ["重置", "RESET"], img_ocr, 192, 194, 426, 291)
def season_reset() -> bool:
    """check the season reset
    :return: bool"""
    pass


@ocr_range_inspection((130, 80, -10), ["每日祭礼", "DAILY RITUALS"],
                      img_ocr, 441, 255, 666, 343)
def daily_ritual_main() -> bool:
    """check the daily task after serious disconnect -->[main]
    :return: bool
    """
    pass


@ocr_range_inspection((130, 80, -10), ["商城", "STORE"], img_ocr, 77, 266, 400, 386)
def mainjudge() -> bool:
    """after serious disconnect.
    check the game whether return the main menu. -->[quit button]
    :return: bool
    """
    pass


@ocr_range_inspection((130, 80, -10), ["好的", "关闭", "OK", "CLOSE", "继续", "CONTINUE"],
                      img_ocr, 299, 614, 1796, 800)
def disconnect_check() -> bool:
    """After disconnect check the connection status
    :return: bool"""
    pass


@ocr_range_inspection((130, 80, -10), ["新内容", "NEW CONTENT"],
                      img_ocr, 548, 4, 1476, 256)
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

    log.print(f"{now_time()}……///disconnect_confirm()识别函数识别中···")

    disconnect_check_colorXY = Coord(299, 614, 1796, 800)
    disconnect_check_colorXY.processed_coord()
    disconnect_check_colorXY.area_check()
    screen = QApplication.primaryScreen()
    image = screen.grabWindow(hwnd).toImage()

    # 生成唯一的文件名
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"image_{timestamp}.jpg"
    image.save(filename)

    # 打开图像文件并裁剪、二值化
    with Image.open(filename) as img:
        cropped = img.crop((disconnect_check_colorXY.x1_coor, disconnect_check_colorXY.y1_coor,
                            disconnect_check_colorXY.x2_coor, disconnect_check_colorXY.y2_coor))
        grayscale_image = cropped.convert('L')
        binary_image = grayscale_image.point(lambda x: 0 if x < sum else 255, '1')
        binary_image.save(filename)  # 保存二值化后的图像到相同的文件

    custom_config = r'--oem 3 --psm 6'
    # 判断中英文切换模型
    lan = "chi_sim+eng"  # 默认简体中文+英文
    if cfg.getboolean("UPDATE", "rb_chinese"):
        lan = "chi_sim"
    elif cfg.getboolean("UPDATE", "rb_english"):
        lan = "eng"

    with Image.open(filename) as ocr_image:
        # 使用Tesseract OCR引擎识别图像中的文本
        result = pytesseract.image_to_boxes(ocr_image, config=custom_config, lang=lan)
        result = result.split(' ')

    log.print(f"{now_time()}……//////识别内容为：\n{result}\n********************")

    # 定义需要查找的字符串列表
    target_strings = ["好", "关", "继", "O", "C"]

    # 初始化坐标
    confirmX, confirmY = None, None

    # 遍历目标字符串列表
    for target_string in target_strings:
        confirmx, confirmy = get_coordinates(result, target_string)
        if confirmx is not None and confirmy is not None:
            log.print(f"{now_time()}……///disconnect_confirm()识别函数已识别···")
            # 调用moveclick函数
            moveclick(disconnect_check_colorXY.x1_coor + confirmx, disconnect_check_colorXY.y2_coor - confirmy,
                      1, 1)
            # 找到了坐标，跳出循环
            break

    # 如果没有找到坐标，则可以根据需要添加处理逻辑
    if confirmX is None or confirmY is None:
        log.print(f"{now_time()}……///disconnect_confirm()识别函数未识别···")

    if os.path.exists(filename):
        try:
            os.remove(filename)  # 尝试删除文件
        except Exception as e:
            log.print(f"{now_time()}……//////ocr检索删除文件时出错: {filename} - {e}")
    else:
        log.print(f"{now_time()}……//////ocr检索删除文件时出错: 文件不存在 - {filename}")


def moveclick(x, y, delay=0, click_delay=0) -> None:
    """mouse move to a true place and click """
    coorXY = Coord(x, y)
    coorXY.processed_coord()
    coorXY.area_check()
    py.moveTo(coorXY.x1_coor, coorXY.y1_coor)
    time.sleep(delay)
    py.click()
    time.sleep(click_delay)


def auto_message() -> None:
    """对局结束后的自动留言"""
    py.write(self_defined_parameter['message'])
    py.press('space')
    py.press('enter')
    time.sleep(0.5)


def reconnect() -> bool:
    """Determine whether the peer is disconnected and return to the matching hall
    :return: bool -->TRUE
    """
    global stop_space, stop_action
    log.print(f"{now_time()}……///正在进入重连···")
    time.sleep(2)
    stop_space = True  # 自动空格线程标志符
    stop_action = True  # 动作线程标志符
    # moveclick(586, 679, cli
    # moveclick(570, 710, click_delay=1)  # 错误代码2
    # moveclick(594, 721, click_delay=1)  # 错误代码3
    # moveclick(1334, 635, click_delay=1)  # 错误代码4
    # moveclick(1429, 640, click_delay=1)  # 错误代码5
    # moveclick(1389, 670, click_delay=1)  # 错误代码6
    # moveclick(563, 722, click_delay=1)  # 错误代码7
    while disconnect_check():
        for sum in range(130, 80, -10):
            disconnect_confirm(sum)
            if not disconnect_check():
                break

    # 检测血点，判断断线情况
    if starthall() or readyhall():  # 小退
        log.print(f"{now_time()}……///断线重连程度检测·····小退")
        return True
    elif gameover():  # 意味着不在大厅
        moveclick(1761, 1009)
        log.print(f"{now_time()}……///断线重连程度检测·····小退")
        return True
    else:  # 大退
        log.print(f"{now_time()}……///断线重连程度检测·····大退")

        main_quit = False
        while main_quit == False:
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
                moveclick(1413, 992, click_delay=1)  # 新闻点击

            # 判断每日祭礼
            if daily_ritual_main():
                moveclick(545, 880, click_delay=1)
            # 判断段位重置
            if season_reset():
                moveclick(1468, 843, click_delay=1)
            # 是否重进主页面判断
            if mainjudge():
                moveclick(320, 100, click_delay=1)  # 点击开始
                # 通过阵营选择判断返回大厅
                if cfg.getboolean("CPCI", "rb_survivor"):
                    moveclick(339, 320)
                elif cfg.getboolean("CPCI", "rb_killer"):
                    moveclick(328, 224)
                main_quit = True
            if gameover():
                moveclick(1761, 1009)
                moveclick(10, 10)  # 避免遮挡
                main_quit = True
        log.print(f"{now_time()}……///重连完成···")
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


# def random_veer_move():
#     act_move = random_movement()
#     key_down(hwnd, act_move)
#     time.sleep(random_movetime())
#     act_direction = random_direction()
#     key_down(hwnd, act_direction)
#     time.sleep(random_veertime())
#     key_up(hwnd, act_direction)
#     key_up(hwnd, act_move)

# def hurt():
#     """check survivor whether hurt
#     ":return: bool"""
#     hurtXY = Coord(106, 451, 150, 498)  # 102, 450, 159, 499
#     hurtXY.processed_coord()
#     hurtXY.area_check()
#     ret1, ret2 = hurtXY.find_color("9F1409-000000")
#     if gt(ret1, 0) and gt(ret2, 0):
#         return True
#     else:
#         return False
#
# def on_hook():
#     """check survivor whether on the hook
#     :return: bool"""
#     hookXY = Coord(106, 451, 150, 498)  # 189, 492, 325, 508
#     hookXY.processed_coord()
#     hookXY.area_check()
#     ret1, ret2 = hookXY.find_color("5F261E-000000")
#     if gt(ret1, 0) and gt(ret2, 0):
#         return True
#     else:
#         return False

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
        for i in range(10):
            key_down(hwnd, act_direction)
            time.sleep(0.05)
            key_up(hwnd, act_direction)
            time.sleep(0.7)
        killer_skillclick()
        if custom_select.select_killer_lst[killer_num] in ctrl_lst:
            killer_ctrl()
    else:
        act_direction = random_direction()
        for i in range(10):
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
        time.sleep(2)
        py.mouseUp(button='right')
        time.sleep(0.3)
    py.mouseDown()
    time.sleep(2)
    py.mouseUp()
    key_up(hwnd, 'w')


def back_first() -> None:
    """click back the first character"""
    wheelcoord = Coord(404, 536)
    wheelcoord.processed_coord()
    wheelcoord.area_check()
    # 回到最开始,需要几次就回滚几次
    py.moveTo(wheelcoord.x1_coor, wheelcoord.y1_coor)
    for i in range(3):  # 3
        py.sleep(0.5)
        py.scroll(1)
    moveclick(405, 314, 1.5)



def character_selection() -> None:
    """自选特定的角色轮转"""
    global character_num_b, circle, frequency, judge, character_num
    if eq(judge, 0):
        custom_select.read_search_killer_name()
        custom_select.match_select_killer_name()
        character_num = custom_select.match_select_killer_lst
        judge = 1
    py.sleep(1)
    moveclick(10, 10, 1, 1)
    time.sleep(1)
    moveclick(141, 109, 1, 1)  # 角色按钮
    timey = floordiv(character_num[character_num_b], 4)  # 取整
    timex = mod(character_num[character_num_b], 4)  # 取余
    time.sleep(0.5)
    wheelcoord = Coord(404, 536)  # 第五个坐标，提前处理
    wheelcoord.processed_coord()
    wheelcoord.area_check()
    back_first()
    if lt(timey, 7):  # 最大的换行次数+1
        if eq(timex, 0):
            timey -= 1
            timex = 4
        if gt(timey, 0):
            py.moveTo(wheelcoord.x1_coor, wheelcoord.y1_coor)
            time.sleep(1.5)
            while True:
                py.click()
                time.sleep(1.5)
                frequency += 1
                if eq(frequency, timey):
                    frequency = 0
                    break
        moveclick(ghX[timex - 1], ghY[timex - 1], 1.5)
    elif gt(timey, 6):  # 最大换行次数
        py.moveTo(wheelcoord.x1_coor, wheelcoord.y1_coor)
        time.sleep(1.5)
        while True:
            py.click()
            time.sleep(1.5)
            frequency += 1
            if eq(frequency, timey):
                frequency = 0
                break
        if eq(timey, 7) and eq(timex, 0):  # 第一个判断最大换行次数加一
            moveclick(ghX[3], ghY[3], 1.5)
        else:
            final_number = character_num[character_num_b] - 28  # (最大换行+1)*4
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
        custom_select.select_killer_name_CN()
    elif cfg.getboolean("UPDATE", "rb_english"):
        custom_select.select_killer_name_EN()
    # 判断游戏是否运行
    if eq(hwnd, 0) and cfg.getboolean("UPDATE", "rb_chinese"):
        win32api.MessageBox(hwnd, "未检测到游戏窗口，请先启动游戏。", "提示",
                            win32con.MB_OK | win32con.MB_ICONWARNING)
        return False
    elif eq(hwnd, 0) and cfg.getboolean("UPDATE", "rb_english"):
        win32api.MessageBox(hwnd, "The game window was not detected. Please start the game first.", "Prompt",
                            win32con.MB_OK | win32con.MB_ICONWARNING)
        return False
    if not custom_select.select_killer_lst and cfg.getboolean("CPCI", "rb_killer"):
        if cfg.getboolean("UPDATE", "rb_chinese"):
            win32api.MessageBox(hwnd, "至少选择一个屠夫。", "提示", win32con.MB_OK | win32con.MB_ICONASTERISK)
            return False
        elif cfg.getboolean("UPDATE", "rb_english"):
            win32api.MessageBox(hwnd, "Choose at least one killer.", "Tip",
                                win32con.MB_OK | win32con.MB_ICONASTERISK)
            return False
    moveclick(10, 10)
    log.print(f"{now_time()}---启动脚本····")
    return True


def afk() -> None:
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

            log.print(f"{now_time()}---第{circulate_number}次脚本循环---脚本处于匹配阶段···")
            # 判断条件是否成立
            if starthall():
                log.print(f"{now_time()}---第{circulate_number}次脚本循环---游戏处于匹配大厅···")
                # 判断游戏所处的阶段
                if eq(self_defined_parameter['stage_judge_switch'], 1):
                    match_stage = stage_judge()
                    if match_stage != "匹配大厅":
                        log.print(f"{now_time()}……///当前不处于匹配大厅，此功能生效···")
                        break

                if cfg.getboolean("CPCI", "rb_killer"):
                    time.sleep(1)
                    if eq(list_number, 1):
                        list_number = 0
                        time.sleep(1)
                    elif gt(list_number, 1):
                        character_selection()
                        print(custom_select.select_killer_lst, custom_select.match_select_killer_lst)
                elif cfg.getboolean("CPCI", "rb_survivor"):
                    time.sleep(1)
                # 进行准备
                while starthall():  # debug:True -->False
                    if event.is_set():
                        break
                    if not pause_event.is_set():
                        pause_event.wait()
                    moveclick(1742, 931, 1, 0.5)  # 处理坐标，开始匹配
                    log.print(f"{now_time()}---第{circulate_number}次脚本循环---处于匹配大厅，处理坐标，开始匹配···")
                    moveclick(20, 689, 1.5)  # 商城上空白
                    if disconnect_check():  # 断线检测
                        reconnection = reconnect()
                    else:
                        time.sleep(1.5)
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
        ready_load = False  # debug:False -->True
        log.print(f"{now_time()}---第{circulate_number}次脚本循环---脚本处于准备加载阶段···")
        # # 检测游戏所在阶段
        # if eq(self_defined_parameter['stage_judge_switch'], 1):
        #     if ne(match_stage, "匹配大厅"):
        #         ready_load = True
        while not ready_load:
            if event.is_set():
                break
            if not pause_event.is_set():
                pause_event.wait()
            if not readycancle():
                log.print(f"{now_time()}---第{circulate_number}次脚本循环---脚本准备加载阶段结束···")
                ready_load = True
            log.print(f"{now_time()}---第{circulate_number}次脚本循环---游戏正在准备加载中···")

        '''
        准备
        '''
        ready_room = False  # debug:False -->True
        log.print(f"{now_time()}---第{circulate_number}次脚本循环---脚本处于准备阶段···")
        while not ready_room:
            if event.is_set():
                break
            if not pause_event.is_set():
                pause_event.wait()
            # 判断游戏所处的阶段
            if eq(self_defined_parameter['stage_judge_switch'], 1):
                ready_stage = stage_judge()
                if ready_stage != "准备房间":
                    log.print(f"{now_time()}……///当前不处于准备房间，此功能生效···")
                    break
            if readyhall():
                log.print(f"{now_time()}---第{circulate_number}次脚本循环---游戏已进入准备大厅···")
                time.sleep(5)
                moveclick(10, 10, 2, 2)
                moveclick(1742, 931, 2, 0.5)
                log.print(f"{now_time()}---第{circulate_number}次脚本循环---准备按钮点击完成···")
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

        game_load = False
        log.print(f"{now_time()}---第{circulate_number}次脚本循环---脚本处于对局载入阶段···")
        # # 检测游戏所在阶段
        # if eq(self_defined_parameter['stage_judge_switch'], 1):
        #     if ne(ready_stage, "准备房间"):
        #         game_load = True
        while not game_load:
            if event.is_set():
                break
            if not pause_event.is_set():
                pause_event.wait()
            if not readycancle():
                log.print(f"{now_time()}---第{circulate_number}次脚本循环---游戏已进入准备加载阶段···")
                game_load = True
                time.sleep(5)
            log.print(f"{now_time()}---第{circulate_number}次脚本循环---游戏对局正在载入中···")

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
        log.print(f"{now_time()}---第{circulate_number}次脚本循环---脚本处于对局动作执行阶段···")
        action_time = 0
        while not game:
            if event.is_set():
                break
            if not pause_event.is_set():
                pause_event.wait()
            action_time += 1
            # 判断所处的游戏阶段
            if eq(self_defined_parameter['stage_judge_switch'], 1):
                end_stage = stage_judge()
                if end_stage == "匹配大厅" or end_stage == "准备房间":
                    stop_space = True  # 自动空格线程标志符
                    stop_action = True  # 动作线程标志符
                    log.print(f"{now_time()}……///当前不处于游戏结算界面，纠察系统生效···")
                    break

            if gameover():
                log.print(f"{now_time()}---第{circulate_number}次脚本循环---游戏对局已结束···")
                stop_space = True  # 自动空格线程标志符
                stop_action = True  # 动作线程标志符
                moveclick(10, 10, 0.5, 1)
                time.sleep(2)
                # 判断段位重置
                if season_reset():
                    moveclick(1468, 843, click_delay=1)
                # 祭礼完成
                if rites():
                    moveclick(396, 718, 0.5, 1)
                    moveclick(140, 880)
                time.sleep(5)

                # 删除动作线程的输入字符
                py.press('enter')
                py.hotkey('ctrl', 'a')
                py.press('delete')
                # 判断是否开启留言
                if (cfg.getboolean("CPCI", "cb_killer_do")
                        and cfg.getboolean("CPCI", "rb_killer")):
                    auto_message()
                moveclick(1761, 1009, 0.5, 1)  # return hall
                moveclick(10, 10)  # 避免遮挡
                if not gameover():
                    game = True
                elif disconnect_check():
                    reconnection = reconnect()
                    game = True
            else:
                log.print(
                    f"{now_time()}---第{circulate_number}次脚本循环---游戏处于对局阶段···动作循环已执行{action_time}次")
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
    # DBDAS_PATH = os.path.join(BASE_DIR, "DBDAutoScript")
    CHECK_PATH = os.path.join(BASE_DIR, "tesseract-ocr")
    OCR_PATH = os.path.join(BASE_DIR, "tesseract-ocr\\tesseract.exe")
    TESSDATA_PREFIX = os.path.join(BASE_DIR, "tesseract-ocr\\tessdata")
    os.environ['OCR'] = OCR_PATH
    os.environ['TESSDATA_PREFIX'] = TESSDATA_PREFIX
    os.environ['NO_PROXY'] = 'gitee.com'
    CFG_PATH = os.path.join(BASE_DIR, "cfg.cfg")
    SEARCH_PATH_CN = os.path.join(BASE_DIR, "searchfile_cn.txt")
    SEARCH_PATH_EN = os.path.join(BASE_DIR, "searchfile_en.txt")
    # SDPARAMETER_PATH = os.path.join(BASE_DIR, "SDparameter.json")
    TRANSLATE_PATH = os.path.join(BASE_DIR, "picture\\transEN.qm")
    LOG_PATH = os.path.join(BASE_DIR, "debug_data.log")
    hwnd = win32gui.FindWindow(None, u"DeadByDaylight  ")
    # 自定义参数
    self_defined_parameter = {'killer_number': 35, 'message': 'GG',
                              'all_killer_name_CN': ["设陷者顽皮熊", "幽灵", "农场主", "折士", "女猎手",
                                                     "迈克尔.迈尔斯迈克尔·迈尔斯迈克尔\'迈尔斯",
                                                     "妖巫妊巫", "医生",
                                                     "食人广", "梦广梦硒梦麻梦厦", "门徒", "小于小吾小王小各", "怨灵",
                                                     "军团", "瘟疫", "鬼面",
                                                     "魔王", "鬼武士",
                                                     "死亡枪手", "处刑者", "枯萎者", "连体婴", "骗术师", "NEMESIS",
                                                     "地狱修士", "艺术家",
                                                     "贞子页子", "影广影魔", "操纵者", "恶骑士", "白骨商人", "奇点",
                                                     "异形",
                                                     "好孩子", "未知恶物"],
                              'all_killer_name_EN': ["TRAPPER", "WRAITH", "HILLBILLY", "NURSE", "HUNTRESS", "SHAPE",
                                                     "HAG", "DOCTOR",
                                                     "CANNIBAL", "NIGHTMARE", "PIG", "CLOWN", "SPIRIT", "LEGION",
                                                     "PLAGUE", "GHOSTFACE", "DEMOGORGON", "ONI",
                                                     "DEATHSLINGER", "EXECUTIONER", "BLIGHT", "TWINS", "TRICKSTER",
                                                     "NEMESIS", "CENOBITE", "ARTIST", "ONRYO",
                                                     "DREDGE", "MASTERMIND", "KNIGHT", "SKULLMERCHANT", "SINGULARITY",
                                                     "XENOMORPH", "GOODGUY", "UNKNOWN"],
                              'stage_judge_switch': 0}  # 阶段判断开关
    # UI设置
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("picture\\dbdwindow.png"))
    dbd_window = DbdWindow()
    # -------------------------------------------------------------------- 配置文件参数
    cpci_keys = [
        "rb_survivor",
        "cb_survivor_do",
        "rb_killer",
        "cb_killer_do",
        "rb_fixed_mode",
        "rb_random_mode"
    ]
    cpci_dict = {key: getattr(dbd_window.main_ui, key) for key in cpci_keys}

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
    cussec_dict = {key: getattr(dbd_window.sel_dialog.select_ui, key) for key in cussec_keys}
    # 合并所有部分到最终的 ui_components
    ui_components = {
        "CPCI": cpci_dict,
        "UPDATE": update_dict,
        "CUSSEC": cussec_dict
    }
    # --------------------------------------------------------------------------------------------
    log = Logger(LOG_PATH)  # 日志
    cfg = ConfigParser()  # 配置文件
    cfg.read(CFG_PATH, encoding='utf-8')
    initialize()
    read_cfg()
    if QLocale.system().language() != QLocale.Chinese or cfg.getboolean("UPDATE", "rb_english"):
        dbd_window.rb_english_change()
    play_str = WaveObject.from_wave_file(os.path.join(BASE_DIR, "picture\\start.wav"))
    play_pau = WaveObject.from_wave_file(os.path.join(BASE_DIR, "picture\\pause.wav"))
    play_res = WaveObject.from_wave_file(os.path.join(BASE_DIR, "picture\\resume.wav"))
    play_end = WaveObject.from_wave_file(os.path.join(BASE_DIR, "picture\\close.wav"))
    custom_select = CustomSelectKiller()
    screen = QApplication.primaryScreen()
    # max_click = 0  # 最少点几次不会上升
    # front_times = 0  # 可上升部分的循环次数
    # behind_times = 0  # 不可上升后的循环次数
    # x, y = 548, 323  # 初始的坐标值[Second]
    begin_state = False  # 开始状态
    # 角色选择的参数
    ghX = [405, 548, 703, 854]
    ghY = [314, 323, 318, 302]
    glX = [549, 709, 858, 384, 556, 715, 882]
    glY = [517, 528, 523, 753, 741, 749, 750]
    character_num_b = 0  # 列表的下标
    character_num = []  # 列表，表示选择的角色序号
    judge = 0
    circle = 0  # 选择的次数
    frequency = 0  # 换行的次数
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
    checktip = threading.Thread(target=check_tip)
    settings = ConfigObj(CFG_PATH, default_encoding='utf8')
    pytesseract.pytesseract.tesseract_cmd = OCR_PATH  # 配置OCR路径

    notice()  # 通知消息
    authorization()  # 授权验证
    hotkey.start()  # 热键监听
    screen_age()
    if cfg.getboolean("UPDATE", "cb_autocheck"):  # 检查更新
        check_update()
    check_ocr()  # 检查初始化
    notification = TransparentNotification()
    dbd_window.show()
    sys.exit(app.exec_())

import os.path
import random
import subprocess
import time
import threading
import sys
import webbrowser
import pyautogui as py
import win32api
import requests, re
from configobj import ConfigObj
from configparser import ConfigParser
import win32gui
import jsonlines
import pytesseract
import psutil
import win32con
from PIL import Image
from keyboard_operation import key_down, key_up
from operator import lt, eq, gt, ge, ne, floordiv, mod
from pynput import keyboard
from win32api import MessageBox
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTranslator, QLocale, Qt
from DBDAutoScriptUI import Ui_MainWindow
from selec_killerUI import Ui_Dialog


class Coord:
    def __init__(self, x1_coor, y1_coor, x2_coor=0, y2_coor=0):
        self.x1_coor = x1_coor
        self.y1_coor = y1_coor
        self.x2_coor = x2_coor
        self.y2_coor = y2_coor

    def processed_coord(self):
        # 获取缩放后的屏幕分辨率,并获得比例
        factorX = ScreenX / 1920
        factory = ScreenY / 1080
        # processed_coordX = self.x * factorX
        # processed_coordY = self.y * factory
        self.x1_coor = self.x1_coor * factorX
        self.y1_coor = self.y1_coor * factory
        self.x2_coor = self.x2_coor * factorX
        self.y2_coor = self.y2_coor * factory

    def area_check(self):
        self.x1_coor = int(self.x1_coor)
        self.y1_coor = int(self.y1_coor)
        self.x2_coor = int(self.x2_coor)
        self.y2_coor = int(self.y2_coor)


class Logger(object):
    def __init__(self, log_path="default.log"):
        import sys
        self.terminal = sys.stdout
        self.log = open(log_path, "wb", buffering=0)  # , encoding="utf-8"

    def print(self, *message):
        message = ",".join([str(it) for it in message])
        self.terminal.write(str(message) + "\n")
        self.log.write(str(message).encode('utf-8') + b"\n")

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()


def begin():
    file = open(LOG_PATH, 'w').close()
    save_cfg()
    cfg.read(CFG_PATH, encoding='utf-8')
    # begin = multiprocessing.Process(target=AFK)
    # begin.daemon = True
    begingame.start()
    autospace.start()
    # 如果开启提醒，则开启线程
    if (eq(cfg.getboolean("CPCI", "rb_survivor"), True)
            and eq(cfg.getboolean("CPCI", "cb_survivor_do"), True)):
        tip.start()


def kill():
    log.close()
    psutil.Process(os.getpid()).kill()


class DbdWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.main_ui = Ui_MainWindow()
        self.sel_dialog = SelectWindow()
        self.trans = QTranslator()
        qss_style = '''
            QPushButton:hover {
                background-color: #EEF1F2;
                border: 1px solid #D0D3D4;
                border-radius: 5px;
            }
            QPushButton:pressed, QPushButton:checked {
                border: 1px solid #BEC9CA;
                background-color: #EDEEEF;
                border-radius: 5px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
            QCheckBox::indicator:unchecked {
                border-image: url(picture/checkbox_unchecked.png);
            }
            QCheckBox::indicator:checked{
                border-image: url(picture/checkbox_checked_border.png);
            }
            QCheckBox::indicator:unchecked:hover {
                border-image: url(picture/checkbox_hover.png);
            }
            QRadioButton::indicator {
                width: 15px;
                height: 15px;
            }
            QRadioButton::indicator:checked {
                border-image: url(picture/radiobutton_checked.png);
            }
            QRadioButton::indicator:unchecked {
                border-image: url(picture/radiobutton_unchecked.png);
            }
            QRadioButton::indicator:unchecked:hover {
            border-image: url(picture/radiobutton_hover_border.png);
            }
        '''
        # self.sel_dialog.setStyleSheet(qss_style)
        self.main_ui.setupUi(self)
        # self.main_ui.sb_input_count.setMaximum(30)
        self.main_ui.pb_select_cfg.clicked.connect(self.pb_select_cfg_click)
        # self.main_ui.cb_rotate_solo.clicked.connect(self.cb_rotate_solo_click)
        # self.main_ui.cb_rotate_order.clicked.connect(self.cb_rotate_order_click)
        # self.main_ui.cb_select_killer.clicked.connect(self.cb_select_killer_click)
        self.main_ui.pb_search.clicked.connect(self.pb_search_click)
        self.main_ui.pb_start.clicked.connect(begin)
        self.main_ui.pb_stop.clicked.connect(kill)
        self.main_ui.pb_github.clicked.connect(self.github)
        self.main_ui.rb_chinese.clicked.connect(self.rb_chinese_change)
        self.main_ui.rb_english.clicked.connect(self.rb_english_change)

    def pb_search_click(self):
        # lw.SetDict(0, "DbdKillerNames.txt")  # 设置字库
        # 判断游戏是否运行
        print(hwnd)
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
        moveclick(141, 109, 1, 1)  # 打开角色按钮
        back_first()
        custom_select.search_killer_name(self_defined_parameter['killer_number'])  # 随版本更改

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
        # settings.setValue("UPDATE/rb_chinese", dbd_window.main_ui.rb_chinese.isChecked())
        # settings.setValue("UPDATE/rb_english", dbd_window.main_ui.rb_english.isChecked())

    def rb_english_change(self):
        # 导入语言包，english是翻译的.qm文件
        self.trans.load(TRANSLATE_PATH)
        _app = QApplication.instance()
        _app.installTranslator(self.trans)
        self.main_ui.retranslateUi(self)
        self.main_ui.lb_message.hide()
        save_cfg()
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
        # 随版本更改
        self.select_ui.cb_jiage.setChecked(True)
        self.select_ui.cb_dingdang.setChecked(True)
        self.select_ui.cb_dianjv.setChecked(True)
        self.select_ui.cb_hushi.setChecked(True)
        self.select_ui.cb_tuzi.setChecked(True)
        self.select_ui.cb_maishu.setChecked(True)
        self.select_ui.cb_linainai.setChecked(True)
        self.select_ui.cb_laoyang.setChecked(True)
        self.select_ui.cb_babu.setChecked(True)
        self.select_ui.cb_fulaidi.setChecked(True)
        self.select_ui.cb_zhuzhu.setChecked(True)
        self.select_ui.cb_xiaochou.setChecked(True)
        self.select_ui.cb_lingmei.setChecked(True)
        self.select_ui.cb_juntuan.setChecked(True)
        self.select_ui.cb_wenyi.setChecked(True)
        self.select_ui.cb_guimian.setChecked(True)
        self.select_ui.cb_mowang.setChecked(True)
        self.select_ui.cb_guiwushi.setChecked(True)
        self.select_ui.cb_qiangshou.setChecked(True)
        self.select_ui.cb_sanjiaotou.setChecked(True)
        self.select_ui.cb_kumo.setChecked(True)
        self.select_ui.cb_liantiying.setChecked(True)
        self.select_ui.cb_gege.setChecked(True)
        self.select_ui.cb_zhuizhui.setChecked(True)
        self.select_ui.cb_dingzitou.setChecked(True)
        self.select_ui.cb_niaojie.setChecked(True)
        self.select_ui.cb_zhenzi.setChecked(True)
        self.select_ui.cb_yingmo.setChecked(True)
        self.select_ui.cb_weishu.setChecked(True)
        self.select_ui.cb_eqishi.setChecked(True)
        self.select_ui.cb_baigu.setChecked(True)
        self.select_ui.cb_jidian.setChecked(True)
        self.select_ui.cb_yixing.setChecked(True)
        self.select_ui.cb_qiaji.setChecked(True)

    def pb_invert_click(self):
        # 随版本更改
        self.select_ui.cb_jiage.toggle()
        self.select_ui.cb_dingdang.toggle()
        self.select_ui.cb_dianjv.toggle()
        self.select_ui.cb_hushi.toggle()
        self.select_ui.cb_tuzi.toggle()
        self.select_ui.cb_maishu.toggle()
        self.select_ui.cb_linainai.toggle()
        self.select_ui.cb_laoyang.toggle()
        self.select_ui.cb_babu.toggle()
        self.select_ui.cb_fulaidi.toggle()
        self.select_ui.cb_zhuzhu.toggle()
        self.select_ui.cb_xiaochou.toggle()
        self.select_ui.cb_lingmei.toggle()
        self.select_ui.cb_juntuan.toggle()
        self.select_ui.cb_wenyi.toggle()
        self.select_ui.cb_guimian.toggle()
        self.select_ui.cb_mowang.toggle()
        self.select_ui.cb_guiwushi.toggle()
        self.select_ui.cb_qiangshou.toggle()
        self.select_ui.cb_sanjiaotou.toggle()
        self.select_ui.cb_kumo.toggle()
        self.select_ui.cb_liantiying.toggle()
        self.select_ui.cb_gege.toggle()
        self.select_ui.cb_zhuizhui.toggle()
        self.select_ui.cb_dingzitou.toggle()
        self.select_ui.cb_niaojie.toggle()
        self.select_ui.cb_zhenzi.toggle()
        self.select_ui.cb_yingmo.toggle()
        self.select_ui.cb_weishu.toggle()
        self.select_ui.cb_eqishi.toggle()
        self.select_ui.cb_baigu.toggle()
        self.select_ui.cb_jidian.toggle()
        self.select_ui.cb_yixing.toggle()
        self.select_ui.cb_qiaji.toggle()

    def pb_save_click(self):
        save_cfg()
        cfg.read(CFG_PATH, encoding='utf-8')


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
            self.sign_1 = "好孩子"
            self.sign_2 = "商城"
        elif cfg.getboolean("UPDATE", "rb_english"):
            self.SEARCH_PATH = SEARCH_PATH_EN
            self.all_killer_name = self_defined_parameter['all_killer_name_EN']
            self.sign_1 = "GOOD GUY"
            self.sign_2 = "CHARACTERS"
        # print(self.all_killer_name)  # debug

    def read_search_killer_name(self):
        with open(self.SEARCH_PATH, "r", encoding='UTF-8') as search_file:
            self.killer_name_array = search_file.readlines()
            self.killer_name_array = [c.strip() for c in self.killer_name_array]

    def killer_name_ocr(self):
        killername = Coord(373, 0, 657, 160)
        killername.processed_coord()
        killername.area_check()
        self.killer_name = OCR(469, 53, 788, 99)
        self.killer_name = self.killer_name.strip()
        if self.killer_name in self.all_killer_name:
            self.write_killer_name()
            if self.killer_name == self.sign_1:  # 随版本更改
                self.ocr_error = 1
                back_first()
                moveclick(387, 300, 1, 1)
                moveclick(141, 109, 1, 1)  # 关闭角色按钮
                id = win32gui.FindWindow(None, u"DBD_AFK_TOOL")
                win32gui.SetWindowPos(id, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
                win32gui.SetWindowPos(id, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
                if cfg.getboolean("UPDATE", "rb_chinese"):
                    MessageBox(0, "角色检索已完成", "提醒", win32con.MB_ICONASTERISK)
                elif cfg.getboolean("UPDATE", "rb_english"):
                    MessageBox(0, "Character search completed", "Tips", win32con.MB_ICONASTERISK)
                with open(self.SEARCH_PATH, "w", encoding='UTF-8') as search_file:
                    search_file.write("\n".join(self.killer_name_array))
                self.killer_name_array.clear()
        else:
            killername = Coord(239, 0, 359, 196)
            killername.processed_coord()
            killername.area_check()
            self.ocr_notown = OCR(329, 36, 470, 84)
            self.ocr_notown = self.ocr_notown.strip()
            # print(self.ocr_notown)  # debug
            if self.ocr_notown == self.sign_2:
                self.ocr_error = 1
                time.sleep(2)
                py.keyDown('esc')
                py.keyUp('esc')
                time.sleep(1)
                py.keyDown('esc')
                py.keyUp('esc')
                id = win32gui.FindWindow(None, u"DBD_AFK_TOOL")
                win32gui.SetWindowPos(id, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
                win32gui.SetWindowPos(id, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
                if cfg.getboolean("UPDATE", "rb_chinese"):
                    MessageBox(0, "角色检索已完成", "提醒", win32con.MB_ICONASTERISK)
                elif cfg.getboolean("UPDATE", "rb_english"):
                    MessageBox(0, "Character search completed", "Tips", win32con.MB_ICONASTERISK)
                with open(self.SEARCH_PATH, "w", encoding='UTF-8') as search_file:
                    search_file.write("\n".join(self.killer_name_array))
                self.killer_name_array.clear()
            else:
                back_first()
                moveclick(387, 300, 1, 1)
                moveclick(141, 109, 1, 1)  # 关闭角色按钮
                id = win32gui.FindWindow(None, u"DBD_AFK_TOOL")
                win32gui.SetWindowPos(id, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
                win32gui.SetWindowPos(id, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
                if cfg.getboolean("UPDATE", "rb_chinese"):
                    MessageBox(0, "检索未完成，请检查以下：\n" + str(self.killer_name_array) + "\n有错误或乱码请重新检索",
                               "提醒", win32con.MB_ICONASTERISK)
                elif cfg.getboolean("UPDATE", "rb_english"):
                    MessageBox(0, "Search not completed, please check the following:\n" + str(
                        self.killer_name_array) + "\nIf there is an error or garbled code, please re-search", "Tips",
                               win32con.MB_ICONASTERISK)
                with open(self.SEARCH_PATH, "w") as search_file:
                    search_file.write("\n".join(self.killer_name_array))
                self.ocr_error = 1
                self.killer_name_array.clear()

    def write_killer_name(self):
        self.killer_name_array.append(self.killer_name)

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
                moveclick(line.x1_coor, line.y1_coor, 1, 1)
                self.killer_name_ocr()
                # if self.ocr_error == 1:
                #     break
                n += 1

    def select_killer_name_CN(self):
        # 随版本更改
        if cfg.getboolean("CUSSEC", "cb_jiage"):
            self.select_killer_lst.append("设陷者")
        if cfg.getboolean("CUSSEC", "cb_dingdang"):
            self.select_killer_lst.append("幽灵")
        if cfg.getboolean("CUSSEC", "cb_dianjv"):
            self.select_killer_lst.append("农场主")
        if cfg.getboolean("CUSSEC", "cb_hushi"):
            self.select_killer_lst.append("护士")
        if cfg.getboolean("CUSSEC", "cb_tuzi"):
            self.select_killer_lst.append("女猎手")
        if cfg.getboolean("CUSSEC", "cb_maishu"):
            self.select_killer_lst.append("迈克尔迈尔斯")
        if cfg.getboolean("CUSSEC", "cb_linainai"):
            self.select_killer_lst.append("妖巫")
        if cfg.getboolean("CUSSEC", "cb_laoyang"):
            self.select_killer_lst.append("医生")
        if cfg.getboolean("CUSSEC", "cb_babu"):
            self.select_killer_lst.append("食人魔")
        if cfg.getboolean("CUSSEC", "cb_fulaidi"):
            self.select_killer_lst.append("梦魇")
        if cfg.getboolean("CUSSEC", "cb_zhuzhu"):
            self.select_killer_lst.append("门徒")
        if cfg.getboolean("CUSSEC", "cb_xiaochou"):
            self.select_killer_lst.append("小丑")
        if cfg.getboolean("CUSSEC", "cb_lingmei"):
            self.select_killer_lst.append("怨灵")
        if cfg.getboolean("CUSSEC", "cb_juntuan"):
            self.select_killer_lst.append("军团")
        if cfg.getboolean("CUSSEC", "cb_wenyi"):
            self.select_killer_lst.append("瘟疫")
        if cfg.getboolean("CUSSEC", "cb_guimian"):
            self.select_killer_lst.append("鬼面")
        if cfg.getboolean("CUSSEC", "cb_mowang"):
            self.select_killer_lst.append("魔王")
        if cfg.getboolean("CUSSEC", "cb_guiwushi"):
            self.select_killer_lst.append("鬼武士")
        if cfg.getboolean("CUSSEC", "cb_qiangshou"):
            self.select_killer_lst.append("死亡枪手")
        if cfg.getboolean("CUSSEC", "cb_sanjiaotou"):
            self.select_killer_lst.append("处刑者")
        if cfg.getboolean("CUSSEC", "cb_kumo"):
            self.select_killer_lst.append("枯萎者")
        if cfg.getboolean("CUSSEC", "cb_liantiying"):
            self.select_killer_lst.append("连体婴")
        if cfg.getboolean("CUSSEC", "cb_gege"):
            self.select_killer_lst.append("骗术师")
        if cfg.getboolean("CUSSEC", "cb_zhuizhui"):
            self.select_killer_lst.append("NEMESIS")
        if cfg.getboolean("CUSSEC", "cb_dingzitou"):
            self.select_killer_lst.append("地狱修士")
        if cfg.getboolean("CUSSEC", "cb_niaojie"):
            self.select_killer_lst.append("艺术家")
        if cfg.getboolean("CUSSEC", "cb_zhenzi"):
            self.select_killer_lst.append("贞子")
        if cfg.getboolean("CUSSEC", "cb_yingmo"):
            self.select_killer_lst.append("影魔")
        if cfg.getboolean("CUSSEC", "cb_weishu"):
            self.select_killer_lst.append("操纵者")
        if cfg.getboolean("CUSSEC", "cb_eqishi"):
            self.select_killer_lst.append("恶骑士")
        if cfg.getboolean("CUSSEC", "cb_baigu"):
            self.select_killer_lst.append("白骨商人")
        if cfg.getboolean("CUSSEC", "cb_jidian"):
            self.select_killer_lst.append("奇点")
        if cfg.getboolean("CUSSEC", "cb_yixing"):
            self.select_killer_lst.append("异形")
        if cfg.getboolean("CUSSEC", "cb_qiaji"):
            self.select_killer_lst.append("好孩子")

    def select_killer_name_EN(self):
        # 随版本更改
        if cfg.getboolean("CUSSEC", "cb_jiage"):
            self.select_killer_lst.append("TRAPPER")
        if cfg.getboolean("CUSSEC", "cb_dingdang"):
            self.select_killer_lst.append("WRAITH")
        if cfg.getboolean("CUSSEC", "cb_dianjv"):
            self.select_killer_lst.append("HILLBILLY")
        if cfg.getboolean("CUSSEC", "cb_hushi"):
            self.select_killer_lst.append("NURSE")
        if cfg.getboolean("CUSSEC", "cb_tuzi"):
            self.select_killer_lst.append("HUNTRESS")
        if cfg.getboolean("CUSSEC", "cb_maishu"):
            self.select_killer_lst.append("SHAPE")
        if cfg.getboolean("CUSSEC", "cb_linainai"):
            self.select_killer_lst.append("HAG")
        if cfg.getboolean("CUSSEC", "cb_laoyang"):
            self.select_killer_lst.append("DOCTOR")
        if cfg.getboolean("CUSSEC", "cb_babu"):
            self.select_killer_lst.append("CANNIBAL")
        if cfg.getboolean("CUSSEC", "cb_fulaidi"):
            self.select_killer_lst.append("NIGHTMARE")
        if cfg.getboolean("CUSSEC", "cb_zhuzhu"):
            self.select_killer_lst.append("PIG")
        if cfg.getboolean("CUSSEC", "cb_xiaochou"):
            self.select_killer_lst.append("CLOWN")
        if cfg.getboolean("CUSSEC", "cb_lingmei"):
            self.select_killer_lst.append("SPIRIT")
        if cfg.getboolean("CUSSEC", "cb_juntuan"):
            self.select_killer_lst.append("LEGION")
        if cfg.getboolean("CUSSEC", "cb_wenyi"):
            self.select_killer_lst.append("PLAGUE")
        if cfg.getboolean("CUSSEC", "cb_guimian"):
            self.select_killer_lst.append("GHOST FACE")
        if cfg.getboolean("CUSSEC", "cb_mowang"):
            self.select_killer_lst.append("DEMOGORGON")
        if cfg.getboolean("CUSSEC", "cb_guiwushi"):
            self.select_killer_lst.append("ONI")
        if cfg.getboolean("CUSSEC", "cb_qiangshou"):
            self.select_killer_lst.append("DEATHSLINGER")
        if cfg.getboolean("CUSSEC", "cb_sanjiaotou"):
            self.select_killer_lst.append("EXECUTIONER")
        if cfg.getboolean("CUSSEC", "cb_kumo"):
            self.select_killer_lst.append("BLIGHT")
        if cfg.getboolean("CUSSEC", "cb_liantiying"):
            self.select_killer_lst.append("TWINS")
        if cfg.getboolean("CUSSEC", "cb_gege"):
            self.select_killer_lst.append("TRICKSTER")
        if cfg.getboolean("CUSSEC", "cb_zhuizhui"):
            self.select_killer_lst.append("NEMESIS")
        if cfg.getboolean("CUSSEC", "cb_dingzitou"):
            self.select_killer_lst.append("CENOBITE")
        if cfg.getboolean("CUSSEC", "cb_niaojie"):
            self.select_killer_lst.append("ARTIST")
        if cfg.getboolean("CUSSEC", "cb_zhenzi"):
            self.select_killer_lst.append("ONRY6")
        if cfg.getboolean("CUSSEC", "cb_yingmo"):
            self.select_killer_lst.append("DREDGE")
        if cfg.getboolean("CUSSEC", "cb_weishu"):
            self.select_killer_lst.append("MASTERMIND")
        if cfg.getboolean("CUSSEC", "cb_eqishi"):
            self.select_killer_lst.append("KNIGHT")
        if cfg.getboolean("CUSSEC", "cb_baigu"):
            self.select_killer_lst.append("SKULL MERCHANT")
        if cfg.getboolean("CUSSEC", "cb_jidian"):
            self.select_killer_lst.append("SINGULARITY")
        if cfg.getboolean("CUSSEC", "cb_yixing"):
            self.select_killer_lst.append("XENOMORPH")
        if cfg.getboolean("CUSSEC", "cb_qiaji"):
            self.select_killer_lst.append("GOOD GUY")

    def match_select_killer_name(self):
        for i in self.select_killer_lst:
            self.match_select_killer_lst.append(self.killer_name_array.index(i) + 1)

    def debug_traverse(self):  # 遍历调试
        killer_name_array_len = len(self.killer_name_array)
        print(*self.killer_name_array, sep=",")
        for i in range(0, killer_name_array_len):
            print(self.killer_name_array[i])


def initialize():
    """ 程序初始化 """
    global self_defined_parameter
    if not os.path.exists(CFG_PATH):
        with open(CFG_PATH, 'w', encoding='UTF-8') as configfile:
            configfile.write("")

        # 随版本更改
        settings["CPCI"] = {}
        settings["CPCI"]["rb_survivor"] = False
        settings["CPCI"]["cb_survivor_do"] = False
        settings["CPCI"]["rb_killer"] = False
        settings["CPCI"]["cb_killer_do"] = False
        settings["CPCI"]["rb_fixed_mode"] = False
        settings["CPCI"]["rb_random_mode"] = False
        settings["UPDATE"] = {}
        settings["UPDATE"]["cb_autocheck"] = True
        settings["UPDATE"]["rb_chinese"] = True
        settings["UPDATE"]["rb_english"] = False
        settings["CUSSEC"] = {}
        settings["CUSSEC"]["cb_jiage"] = False
        settings["CUSSEC"]["cb_dingdang"] = False
        settings["CUSSEC"]["cb_dianjv"] = False
        settings["CUSSEC"]["cb_hushi"] = False
        settings["CUSSEC"]["cb_tuzi"] = False
        settings["CUSSEC"]["cb_maishu"] = False
        settings["CUSSEC"]["cb_linainai"] = False
        settings["CUSSEC"]["cb_laoyang"] = False
        settings["CUSSEC"]["cb_babu"] = False
        settings["CUSSEC"]["cb_fulaidi"] = False
        settings["CUSSEC"]["cb_zhuzhu"] = False
        settings["CUSSEC"]["cb_xiaochou"] = False
        settings["CUSSEC"]["cb_lingmei"] = False
        settings["CUSSEC"]["cb_juntuan"] = False
        settings["CUSSEC"]["cb_wenyi"] = False
        settings["CUSSEC"]["cb_guimian"] = False
        settings["CUSSEC"]["cb_mowang"] = False
        settings["CUSSEC"]["cb_guiwushi"] = False
        settings["CUSSEC"]["cb_qiangshou"] = False
        settings["CUSSEC"]["cb_sanjiaotou"] = False
        settings["CUSSEC"]["cb_kumo"] = False
        settings["CUSSEC"]["cb_liantiying"] = False
        settings["CUSSEC"]["cb_gege"] = False
        settings["CUSSEC"]["cb_zhuizhui"] = False
        settings["CUSSEC"]["cb_dingzitou"] = False
        settings["CUSSEC"]["cb_niaojie"] = False
        settings["CUSSEC"]["cb_zhenzi"] = False
        settings["CUSSEC"]["cb_yingmo"] = False
        settings["CUSSEC"]["cb_weishu"] = False
        settings["CUSSEC"]["cb_eqishi"] = False
        settings["CUSSEC"]["cb_baigu"] = False
        settings["CUSSEC"]["cb_jidian"] = False
        settings["CUSSEC"]["cb_yixing"] = False
        settings["CUSSEC"]["cb_qiaji"] = False

        settings.write()

    if not os.path.exists(SDPARAMETER_PATH):
        with jsonlines.open(SDPARAMETER_PATH, mode='w') as writer:
            writer.write(self_defined_parameter)


def save_cfg():
    """ 保存配置文件 """
    # 随版本更改
    settings["CPCI"]["rb_survivor"] = dbd_window.main_ui.rb_survivor.isChecked()
    settings["CPCI"]["cb_survivor_do"] = dbd_window.main_ui.cb_survivor_do.isChecked()
    settings["CPCI"]["rb_killer"] = dbd_window.main_ui.rb_killer.isChecked()
    settings["CPCI"]["cb_killer_do"] = dbd_window.main_ui.cb_killer_do.isChecked()
    settings["CPCI"]["rb_fixed_mode"] = dbd_window.main_ui.rb_fixed_mode.isChecked()
    settings["CPCI"]["rb_random_mode"] = dbd_window.main_ui.rb_random_mode.isChecked()
    settings["UPDATE"]["cb_autocheck"] = dbd_window.main_ui.cb_autocheck.isChecked()
    settings["UPDATE"]["rb_chinese"] = dbd_window.main_ui.rb_chinese.isChecked()
    settings["UPDATE"]["rb_english"] = dbd_window.main_ui.rb_english.isChecked()
    settings["CUSSEC"]["cb_jiage"] = dbd_window.sel_dialog.select_ui.cb_jiage.isChecked()
    settings["CUSSEC"]["cb_dingdang"] = dbd_window.sel_dialog.select_ui.cb_dingdang.isChecked()
    settings["CUSSEC"]["cb_dianjv"] = dbd_window.sel_dialog.select_ui.cb_dianjv.isChecked()
    settings["CUSSEC"]["cb_hushi"] = dbd_window.sel_dialog.select_ui.cb_hushi.isChecked()
    settings["CUSSEC"]["cb_tuzi"] = dbd_window.sel_dialog.select_ui.cb_tuzi.isChecked()
    settings["CUSSEC"]["cb_maishu"] = dbd_window.sel_dialog.select_ui.cb_maishu.isChecked()
    settings["CUSSEC"]["cb_linainai"] = dbd_window.sel_dialog.select_ui.cb_linainai.isChecked()
    settings["CUSSEC"]["cb_laoyang"] = dbd_window.sel_dialog.select_ui.cb_laoyang.isChecked()
    settings["CUSSEC"]["cb_babu"] = dbd_window.sel_dialog.select_ui.cb_babu.isChecked()
    settings["CUSSEC"]["cb_fulaidi"] = dbd_window.sel_dialog.select_ui.cb_fulaidi.isChecked()
    settings["CUSSEC"]["cb_zhuzhu"] = dbd_window.sel_dialog.select_ui.cb_zhuzhu.isChecked()
    settings["CUSSEC"]["cb_xiaochou"] = dbd_window.sel_dialog.select_ui.cb_xiaochou.isChecked()
    settings["CUSSEC"]["cb_lingmei"] = dbd_window.sel_dialog.select_ui.cb_lingmei.isChecked()
    settings["CUSSEC"]["cb_juntuan"] = dbd_window.sel_dialog.select_ui.cb_juntuan.isChecked()
    settings["CUSSEC"]["cb_wenyi"] = dbd_window.sel_dialog.select_ui.cb_wenyi.isChecked()
    settings["CUSSEC"]["cb_guimian"] = dbd_window.sel_dialog.select_ui.cb_guimian.isChecked()
    settings["CUSSEC"]["cb_mowang"] = dbd_window.sel_dialog.select_ui.cb_mowang.isChecked()
    settings["CUSSEC"]["cb_guiwushi"] = dbd_window.sel_dialog.select_ui.cb_guiwushi.isChecked()
    settings["CUSSEC"]["cb_qiangshou"] = dbd_window.sel_dialog.select_ui.cb_qiangshou.isChecked()
    settings["CUSSEC"]["cb_sanjiaotou"] = dbd_window.sel_dialog.select_ui.cb_sanjiaotou.isChecked()
    settings["CUSSEC"]["cb_kumo"] = dbd_window.sel_dialog.select_ui.cb_kumo.isChecked()
    settings["CUSSEC"]["cb_liantiying"] = dbd_window.sel_dialog.select_ui.cb_liantiying.isChecked()
    settings["CUSSEC"]["cb_gege"] = dbd_window.sel_dialog.select_ui.cb_gege.isChecked()
    settings["CUSSEC"]["cb_zhuizhui"] = dbd_window.sel_dialog.select_ui.cb_zhuizhui.isChecked()
    settings["CUSSEC"]["cb_dingzitou"] = dbd_window.sel_dialog.select_ui.cb_dingzitou.isChecked()
    settings["CUSSEC"]["cb_niaojie"] = dbd_window.sel_dialog.select_ui.cb_niaojie.isChecked()
    settings["CUSSEC"]["cb_zhenzi"] = dbd_window.sel_dialog.select_ui.cb_zhenzi.isChecked()
    settings["CUSSEC"]["cb_yingmo"] = dbd_window.sel_dialog.select_ui.cb_yingmo.isChecked()
    settings["CUSSEC"]["cb_weishu"] = dbd_window.sel_dialog.select_ui.cb_weishu.isChecked()
    settings["CUSSEC"]["cb_eqishi"] = dbd_window.sel_dialog.select_ui.cb_eqishi.isChecked()
    settings["CUSSEC"]["cb_baigu"] = dbd_window.sel_dialog.select_ui.cb_baigu.isChecked()
    settings["CUSSEC"]["cb_jidian"] = dbd_window.sel_dialog.select_ui.cb_jidian.isChecked()
    settings["CUSSEC"]["cb_yixing"] = dbd_window.sel_dialog.select_ui.cb_yixing.isChecked()
    settings["CUSSEC"]["cb_qiaji"] = dbd_window.sel_dialog.select_ui.cb_qiaji.isChecked()
    settings.write()


def read_cfg():
    """读取配置文件"""
    global self_defined_parameter
    # 随版本更改
    dbd_window.main_ui.rb_survivor.setChecked(cfg.getboolean("CPCI", "rb_survivor"))
    dbd_window.main_ui.cb_survivor_do.setChecked(cfg.getboolean("CPCI", "cb_survivor_do"))
    dbd_window.main_ui.rb_killer.setChecked(cfg.getboolean("CPCI", "rb_killer"))
    dbd_window.main_ui.cb_killer_do.setChecked(cfg.getboolean("CPCI", "cb_killer_do"))
    dbd_window.main_ui.rb_fixed_mode.setChecked(cfg.getboolean("CPCI", "rb_fixed_mode"))
    dbd_window.main_ui.rb_random_mode.setChecked(cfg.getboolean("CPCI", "rb_random_mode"))
    dbd_window.main_ui.cb_autocheck.setChecked(cfg.getboolean("UPDATE", "cb_autocheck"))
    dbd_window.main_ui.rb_chinese.setChecked(cfg.getboolean("UPDATE", "rb_chinese"))
    dbd_window.main_ui.rb_english.setChecked(cfg.getboolean("UPDATE", "rb_english"))
    dbd_window.sel_dialog.select_ui.cb_jiage.setChecked(cfg.getboolean("CUSSEC", "cb_jiage"))
    dbd_window.sel_dialog.select_ui.cb_dingdang.setChecked(cfg.getboolean("CUSSEC", "cb_dingdang"))
    dbd_window.sel_dialog.select_ui.cb_dianjv.setChecked(cfg.getboolean("CUSSEC", "cb_dianjv"))
    dbd_window.sel_dialog.select_ui.cb_hushi.setChecked(cfg.getboolean("CUSSEC", "cb_hushi"))
    dbd_window.sel_dialog.select_ui.cb_tuzi.setChecked(cfg.getboolean("CUSSEC", "cb_tuzi"))
    dbd_window.sel_dialog.select_ui.cb_maishu.setChecked(cfg.getboolean("CUSSEC", "cb_maishu"))
    dbd_window.sel_dialog.select_ui.cb_linainai.setChecked(cfg.getboolean("CUSSEC", "cb_linainai"))
    dbd_window.sel_dialog.select_ui.cb_laoyang.setChecked(cfg.getboolean("CUSSEC", "cb_laoyang"))
    dbd_window.sel_dialog.select_ui.cb_babu.setChecked(cfg.getboolean("CUSSEC", "cb_babu"))
    dbd_window.sel_dialog.select_ui.cb_fulaidi.setChecked(cfg.getboolean("CUSSEC", "cb_fulaidi"))
    dbd_window.sel_dialog.select_ui.cb_zhuzhu.setChecked(cfg.getboolean("CUSSEC", "cb_zhuzhu"))
    dbd_window.sel_dialog.select_ui.cb_xiaochou.setChecked(cfg.getboolean("CUSSEC", "cb_xiaochou"))
    dbd_window.sel_dialog.select_ui.cb_lingmei.setChecked(cfg.getboolean("CUSSEC", "cb_lingmei"))
    dbd_window.sel_dialog.select_ui.cb_juntuan.setChecked(cfg.getboolean("CUSSEC", "cb_juntuan"))
    dbd_window.sel_dialog.select_ui.cb_wenyi.setChecked(cfg.getboolean("CUSSEC", "cb_wenyi"))
    dbd_window.sel_dialog.select_ui.cb_guimian.setChecked(cfg.getboolean("CUSSEC", "cb_guimian"))
    dbd_window.sel_dialog.select_ui.cb_mowang.setChecked(cfg.getboolean("CUSSEC", "cb_mowang"))
    dbd_window.sel_dialog.select_ui.cb_guiwushi.setChecked(cfg.getboolean("CUSSEC", "cb_guiwushi"))
    dbd_window.sel_dialog.select_ui.cb_qiangshou.setChecked(cfg.getboolean("CUSSEC", "cb_qiangshou"))
    dbd_window.sel_dialog.select_ui.cb_sanjiaotou.setChecked(cfg.getboolean("CUSSEC", "cb_sanjiaotou"))
    dbd_window.sel_dialog.select_ui.cb_kumo.setChecked(cfg.getboolean("CUSSEC", "cb_kumo"))
    dbd_window.sel_dialog.select_ui.cb_liantiying.setChecked(cfg.getboolean("CUSSEC", "cb_liantiying"))
    dbd_window.sel_dialog.select_ui.cb_gege.setChecked(cfg.getboolean("CUSSEC", "cb_gege"))
    dbd_window.sel_dialog.select_ui.cb_zhuizhui.setChecked(cfg.getboolean("CUSSEC", "cb_zhuizhui"))
    dbd_window.sel_dialog.select_ui.cb_dingzitou.setChecked(cfg.getboolean("CUSSEC", "cb_dingzitou"))
    dbd_window.sel_dialog.select_ui.cb_niaojie.setChecked(cfg.getboolean("CUSSEC", "cb_niaojie"))
    dbd_window.sel_dialog.select_ui.cb_zhenzi.setChecked(cfg.getboolean("CUSSEC", "cb_zhenzi"))
    dbd_window.sel_dialog.select_ui.cb_yingmo.setChecked(cfg.getboolean("CUSSEC", "cb_yingmo"))
    dbd_window.sel_dialog.select_ui.cb_weishu.setChecked(cfg.getboolean("CUSSEC", "cb_weishu"))
    dbd_window.sel_dialog.select_ui.cb_eqishi.setChecked(cfg.getboolean("CUSSEC", "cb_eqishi"))
    dbd_window.sel_dialog.select_ui.cb_baigu.setChecked(cfg.getboolean("CUSSEC", "cb_baigu"))
    dbd_window.sel_dialog.select_ui.cb_jidian.setChecked(cfg.getboolean("CUSSEC", "cb_jidian"))
    dbd_window.sel_dialog.select_ui.cb_yixing.setChecked(cfg.getboolean("CUSSEC", "cb_yixing"))
    if cfg.getboolean("CPCI", "rb_survivor"):
        dbd_window.main_ui.cb_survivor_do.setEnabled(True)
        dbd_window.main_ui.rb_fixed_mode.setDisabled(True)
        dbd_window.main_ui.rb_random_mode.setDisabled(True)
        # dbd_window.main_ui.rb_no_action.setDisabled(True)
        # dbd_window.main_ui.pb_research.setDisabled(True)
        dbd_window.main_ui.pb_select_cfg.setDisabled(True)
    if cfg.getboolean("CPCI", "rb_killer"):
        dbd_window.main_ui.cb_killer_do.setEnabled(True)
    # if settings.value("CPCI/rb_no_action") == "true":
    #     dbd_window.main_ui.pb_research.setDisabled(True)
    #     dbd_window.main_ui.pb_select_cfg.setDisabled(True)
    if cfg.getboolean("UPDATE", "rb_chinese"):
        dbd_window.main_ui.pb_search.setDisabled(True)
    if cfg.getboolean("UPDATE", "rb_english"):
        dbd_window.main_ui.lb_message.hide()

    with jsonlines.open(SDPARAMETER_PATH, mode='r') as reader:
        for temporary_dict in reader:
            self_defined_parameter.update(temporary_dict)


# # 检测左上角的角色按钮
# def character_button():
#     character_buttonXY = Coord(105, 73, 178, 149)
#     character_buttonXY.processed_coord()
#     character_buttonXY.area_check()
#     ret1, ret2 = character_buttonXY.find_color("7F7F7F-000000")
#     if gt(ret1, 0) and gt(ret2, 0):
#         return True
#     else:
#         return False

def authorization():
    """check the authorization"""
    authorization_now = '~x&amp;mBGbIneqSS('
    html_str = requests.get('https://gitee.com/kioley/DBD_AFK_TOOL').content.decode()
    authorization_new = re.search('title>(.*?)<', html_str, re.S).group(1)[21:]
    if ne(authorization_now, authorization_new):
        # confirm = pyautogui.confirm(text=text, title="检查更新", buttons=['OK', 'Cancel'])
        if cfg.getboolean("UPDATE", "rb_chinese"):
            win32api.MessageBox(0, "授权已过期", "授权失败", win32con.MB_OK | win32con.MB_ICONERROR)
            sys.exit(0)
        elif cfg.getboolean("UPDATE", "rb_english"):
            win32api.MessageBox(0, "Authorization expired", "Authorization failed",
                                win32con.MB_OK | win32con.MB_ICONERROR)
            sys.exit(0)


def check_update():
    """check the update"""
    ver_now = 'V5.1.4'
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
                # webbrowser.open("https://github.com/maskrs/DBD_AFK_TOOL/releases")
                subprocess.call("更新update.exe")
                sys.exit()
        elif cfg.getboolean("UPDATE", "rb_english"):
            confirm = win32api.MessageBox(0,
                                          "New version detected: {b}\n\nThe current version is: {a}, recommended update.".format(
                                              a=ver_now, b=ver_new)
                                          , "Check for updates", win32con.MB_YESNO | win32con.MB_ICONQUESTION)
            if eq(confirm, 6):  # 打开
                # webbrowser.open("https://github.com/maskrs/DBD_AFK_TOOL/releases")
                subprocess.call("更新update.exe")
                sys.exit()


def notice():
    """take a message"""
    notice_now = 'test git'
    html_str = requests.get('https://gitee.com/kioley/test-git').content.decode()
    notice_new = re.search('title>(.*?)<', html_str, re.S).group(1)[0:8]
    notice = re.search('title>(.*?)<', html_str, re.S).group(1)[9:]
    if ne(notice_now, notice_new):
        win32api.MessageBox(0, notice, "通知", win32con.MB_OK | win32con.MB_ICONINFORMATION)


def hall_tip():
    """Child thread, survivor hall tip"""
    while True:
        if eq(readyhall(), True):
            py.press('enter')
            py.press('delete', 3)
            py.write('AFK')
            py.press('enter')
            time.sleep(30)
        else:
            time.sleep(1)


def auto_space():
    """Child thread, auto press space"""
    hwnd1 = win32gui.FindWindow(None, u"DeadByDaylight  ")
    while True:
        key_down(hwnd1, 'space')
        time.sleep(2)
        key_up(hwnd1, 'space')
        py.press('backspace', 20)
        time.sleep(3)


def listen_key(pid):
    """Hotkey  setting, monitored keyboard input"""

    cmb1 = [{keyboard.Key.alt_l, keyboard.Key.end}, {keyboard.Key.alt_r, keyboard.Key.end}]
    cmb2 = [{keyboard.Key.alt_l, keyboard.KeyCode.from_char('p')},
            {keyboard.Key.alt_r, keyboard.KeyCode.from_char('p')}]
    cmb3 = [{keyboard.Key.alt_l, keyboard.Key.home}, {keyboard.Key.alt_r, keyboard.Key.home}]
    current = set()

    def execute():
        kill = psutil.Process(pid)

        # begingame._stop_event = threading.Event()
        def openexe():
            os.startfile(os.path.join(BASE_DIR, "DBD_AFK_TOOL.exe"))

        open_exe = threading.Thread(target=openexe, daemon=True)
        open_exe.start()
        time.sleep(1.5)
        kill.kill()

    def pause():
        pause = psutil.Process(pid)
        pause.suspend()

    def resume():
        resume = psutil.Process(pid)
        resume.resume()

    def on_press(key):
        if any([key in z for z in cmb1]) or any([key in z for z in cmb2]) or any([key in z for z in cmb3]):
            current.add(key)
            if any(all(k in current for k in z) for z in cmb1):
                execute()
            elif any(all(k in current for k in z) for z in cmb2):
                pause()
            elif any(all(k in current for k in z) for z in cmb3):
                begin()

    def on_release(key):
        if any([key in z for z in cmb1]) or any([key in z for z in cmb2]) or any([key in z for z in cmb3]):
            current.remove(key)

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


def OCR(x1, y1, x2, y2, sum=128):
    """OCR识别图像，返回字符串
    :return: string"""
    ocrXY = Coord(x1, y1, x2, y2)
    ocrXY.processed_coord()
    ocrXY.area_check()
    screen = QApplication.primaryScreen()
    image = screen.grabWindow(hwnd).toImage()
    # 裁剪图像
    image.save('image.jpg')
    img = Image.open("image.jpg")
    cropped = img.crop((ocrXY.x1_coor, ocrXY.y1_coor, ocrXY.x2_coor, ocrXY.y2_coor))
    cropped.save("image.jpg")
    # image = ImageGrab.grab(bbox=(ocrXY.x1_coor, ocrXY.y1_coor, ocrXY.x2_coor, ocrXY.y2_coor))
    image = Image.open('image.jpg')
    # 将图片转换为灰度图像
    grayscale_image = image.convert('L')
    # 对灰度图像进行二值化处理
    binary_image = grayscale_image.point(lambda x: 0 if x < sum else 255, '1')
    # 保存二值化后的图片
    binary_image.save('image.jpg')
    # 读取图像
    img = Image.open('image.jpg')
    custom_config = r'--oem 3 --psm 6'
    # 使用Tesseract OCR引擎识别图像中的文本
    result = pytesseract.image_to_string(img, config=custom_config, lang='chi_sim+eng')
    result = "".join(result.split())
    return result


def starthall():
    """check the start  hall
    :return: bool"""
    log.print(f"{now_time()}……///starthall()识别函数识别中···")
    for sum in range(80, 130, 10):
        ocr = OCR(1446, 771, 1920, 1080, sum)
        log.print(f"{now_time()}……识别内容为：\n********************\n{ocr}\n********************")
        if "开始游戏" in ocr or "PLAY" in ocr:
            log.print(f"{now_time()}……///starthall()识别函数已识别···")
            return True
    log.print(f"{now_time()}……///starthall()识别函数未识别···")
    return False


def readyhall():
    """check the  ready hall
    :return: bool"""
    log.print(f"{now_time()}……///readyhall()识别函数识别中···")
    for sum in range(80, 130, 10):
        ocr = OCR(1446, 771, 1920, 1080, sum)
        log.print(f"{now_time()}……识别内容为：\n********************\n{ocr}\n********************")
        if "准备就绪" in ocr or "READY" in ocr:
            log.print(f"{now_time()}……///readyhall()识别函数已识别···")
            return True
    log.print(f"{now_time()}……///readyhall()识别函数未识别···")
    return False


def readycancle():
    """检查游戏准备后的取消，消失就进入对局加载
    :return: bool"""
    log.print(f"{now_time()}……///readycancle()识别函数识别中···")
    for sum in range(50, 120, 10):
        ocr = OCR(1446, 771, 1920, 1080, sum)  # 80
        log.print(f"{now_time()}……识别内容为：\n********************\n{ocr}\n********************")
        if "取消" in ocr or "CANCEL" in ocr:
            log.print(f"{now_time()}……///readycancle()识别函数已识别···")
            return True
    log.print(f"{now_time()}……///readycancle()识别函数未识别···")
    return False


def map_name():
    """检查地图名字，以判断是否进入游戏，TRUE则开始动作"""
    ocr = OCR(65, 864, 492, 989)
    if ne(ocr, None):
        return True
    else:
        return False


def gameover():
    """检查对局后的继续
    :return: bool"""
    log.print(f"{now_time()}……///gameover()识别函数识别中···")
    for sum in range(20, 110, 10):
        ocr = OCR(1577, 932, 1820, 1028, sum)  # 70
        log.print(f"{now_time()}……识别内容为：\n********************\n{ocr}\n********************")
        # ocr2 = OCR(1745, 991, 1820, 1028, 30)
        if "继续" in ocr or "CONTINUE" in ocr:
            log.print(f"{now_time()}……///gameover()识别函数已识别···")
            return True
    log.print(f"{now_time()}……///gameover()识别函数未识别···")
    return False


def stage_judge():
    """判断游戏所处在的阶段"""
    global match_stage, ready_stage, end_stage
    stage_judge_value = starthall()
    if stage_judge_value:
        match_stage = "匹配大厅"

    stage_judge_value = readyhall()
    if stage_judge_value:
        ready_stage = "准备房间"

    stage_judge_value = gameover()
    if stage_judge_value:
        end_stage = "游戏结束"


def now_time():
    # 获得当前时间时间戳
    now = int(time.time())
    # 转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime


# def setting_button():
#     """check the setting button
#     :return: bool"""
#     setting_buttonXY = Coord(292, 978, 341, 1032)
#     setting_buttonXY.processed_coord()
#     setting_buttonXY.area_check()
#     ret1, ret2 = setting_buttonXY.find_color(self_defined_parameter['setting_button_color'], self_defined_parameter['setting_button_value'])
#     if gt(ret1, 0) and gt(ret2, 0):
#         return True
#     else:
#         return False

# def set_race():
#     """after race check setting button
#     :return: bool"""
#     set_raceXY = Coord(91, 985, 133, 1026)
#     set_raceXY.processed_coord()
#     set_raceXY.area_check()
#     ret1, ret2 = set_raceXY.find_color(self_defined_parameter['set_race_color'], self_defined_parameter['set_race_value'])
#     if gt(ret1, 0) and gt(ret2, 0):
#         return True
#     else:
#         return False


# def ready_red():
#     """check after clicking the 'start' button """
#     ready_redXY = Coord(1794, 983, 1850, 1037)
#     ready_redXY.processed_coord()
#     ready_redXY.area_check()
#     ret1, ret2 = ready_redXY.find_color(self_defined_parameter['ready_color'], self_defined_parameter['ready_value'])
#     if gt(ret1, 0) and gt(ret2, 0):
#         return True
#     else:
#         return False


# def segment_reset():
#     """check Segment Reset
#     :return: bool"""
#     segmentXY = Coord(369, 221, 416, 277)
#     segmentXY.processed_coord()
#     segmentXY.area_check()
#     ret1, ret2 = segmentXY.find_color(self_defined_parameter['segment_reset_color'], self_defined_parameter['segment_reset_value'])
#     if gt(ret1, 0) and gt(ret2, 0):
#         return True
#     else:
#         return False


def rites():
    """check rites complete
    :return:bool"""
    log.print(f"{now_time()}……///rites()识别函数识别中···")
    for sum in range(80, 130, 10):
        ocr = OCR(0, 126, 838, 982, sum)
        log.print(f"{now_time()}……识别内容为：\n********************\n{ocr}\n********************")
        if "每日祭礼" in ocr or "DAILY RITUALS" in ocr:
            log.print(f"{now_time()}……///rites()识别函数已识别···")
            return True
    log.print(f"{now_time()}……///rites()识别函数未识别···")
    return False


# 检测活动奖励  #####未完成
def event_rewards():
    """check the event rewards
    :return: bool"""
    eventXY = Coord(1864, 455, 1920, 491)
    eventXY.processed_coord()
    eventXY.area_check()


def daily_ritual_main():
    """check the daily task after serious disconnect -->[main]
    :return: bool
    """
    log.print(f"{now_time()}……///daily_ritual_main()识别函数识别中···")
    for sum in range(80, 130, 10):
        ocr = OCR(180, 74, 1017, 825, sum)
        log.print(f"{now_time()}……识别内容为：\n********************\n{ocr}\n********************")
        if "每日祭礼" in ocr or "DAILY RITUALS" in ocr:
            log.print(f"{now_time()}……///daily_ritual_main()识别函数已识别···")
            return True
    log.print(f"{now_time()}……///daily_ritual_main()识别函数未识别···")
    return False


def mainjudge():
    """after serious disconnect.
    check the game whether return the main menu. -->[quit button]
    :return: bool
    """
    log.print(f"{now_time()}……///mainjudge()识别函数识别中···")
    for sum in range(80, 130, 10):
        ocr = OCR(180, 74, 1017, 825, sum)
        log.print(f"{now_time()}……识别内容为：\n********************\n{ocr}\n********************")
        if "商城" in ocr or "STORE" in ocr:
            log.print(f"{now_time()}……///mainjudge()识别函数已识别···")
            return True
    log.print(f"{now_time()}……///mainjudge()识别函数未识别···")
    return False


def disconnect_check():
    """After disconnect check the connection status
    :return: bool"""
    log.print(f"{now_time()}……///断线重连检测···")
    for sum in range(80, 130, 10):
        ocr = OCR(299, 614, 1796, 862, sum)  # 110
        log.print(f"{now_time()}……识别内容为：\n********************\n{ocr}\n********************")
        if "好的" in ocr or "关闭" in ocr or "OK" in ocr or "CLOSE" in ocr:
            log.print(f"{now_time()}……///断线重连检测，已断线。")
            return True
    log.print(f"{now_time()}……///断线重连检测，未断线。")
    return False


def news():
    """断线重连后的新闻
    :return: bool"""
    log.print(f"{now_time()}……///news()识别函数识别中···")
    for sum in range(80, 130, 10):
        ocr = OCR(548, 4, 1476, 256, sum)
        log.print(f"{now_time()}……识别内容为：\n********************\n{ocr}\n********************")
        if "新内容" in ocr or "NEW CONTENT" in ocr:
            log.print(f"{now_time()}……///news()识别函数已识别···")
            return True
    log.print(f"{now_time()}……///news()识别函数未识别···")
    return False


def disconnect_confirm(sum=120):
    """After disconnection click confirm button. not need process.
    :return: int"""
    log.print(f"{now_time()}……///disconnect_confirm()识别函数识别中···")
    disconnect_check_colorXY = Coord(299, 614, 1796, 862)
    disconnect_check_colorXY.processed_coord()
    disconnect_check_colorXY.area_check()
    screen = QApplication.primaryScreen()
    image = screen.grabWindow(hwnd).toImage()
    # 裁剪图像
    image.save('image.jpg')
    img = Image.open("image.jpg")
    cropped = img.crop((disconnect_check_colorXY.x1_coor, disconnect_check_colorXY.y1_coor,
                        disconnect_check_colorXY.x2_coor, disconnect_check_colorXY.y2_coor))
    cropped.save("image.jpg")
    # image = ImageGrab.grab(bbox=(ocrXY.x1_coor, ocrXY.y1_coor, ocrXY.x2_coor, ocrXY.y2_coor))
    image = Image.open('image.jpg')
    # 将图片转换为灰度图像
    grayscale_image = image.convert('L')
    # 对灰度图像进行二值化处理
    binary_image = grayscale_image.point(lambda x: 0 if x < sum else 255, '1')  # 120
    # 保存二值化后的图片
    binary_image.save('image.jpg')
    # 读取图像
    img = Image.open('image.jpg')
    custom_config = r'--oem 3 --psm 6'
    # 使用Tesseract OCR引擎识别图像中的文本
    result = pytesseract.image_to_boxes(img, config=custom_config, lang='chi_sim+eng')
    result = result.split(' ')
    log.print(f"{now_time()}……识别内容为：\n********************\n{ocr}\n********************")
    if ne(len(result), 0):
        log.print(f"{now_time()}……///disconnect_confirm()识别函数已识别···")
        confirmX, confirmY = int(result[3]), int(result[4])
        moveclick(disconnect_check_colorXY.x1_coor + confirmX, disconnect_check_colorXY.y2_coor - confirmY,
                  1, 1)
    else:
        log.print(f"{now_time()}……///disconnect_confirm()识别函数未识别···")


# def skill_check():
#     """skill check in the game
#     :return: bool
#     """
#     skill_checkXY_1 = Coord(1606, 780, 1855, 1021)
#     skill_checkXY_2 = Coord(125, 948, 142, 967)
#     skill_checkXY_1.processed_coord()
#     skill_checkXY_1.area_check()
#     ret1, ret2 = skill_checkXY_1.find_color("4E235E-000000|6C5718-000000|083F10-000000")
#     skill_checkXY_2.processed_coord()
#     skill_checkXY_2.area_check()
#     ret3, ret4 = skill_checkXY_2.find_color("FEFEFE-000000")
#     if gt(ret1, 0) and gt(ret2, 0):
#         return True
#     elif gt(ret3, 0) and gt(ret4, 0):
#         return True
#     else:
#         return False


def moveclick(x, y, delay=0, click_delay=0):
    """mouse move to a true place and click """
    coorXY = Coord(x, y)
    coorXY.processed_coord()
    coorXY.area_check()
    py.moveTo(coorXY.x1_coor, coorXY.y1_coor)
    time.sleep(delay)
    py.click()
    time.sleep(click_delay)


def auto_message():
    """对局结束后的自动留言"""
    py.press('enter')
    py.write(self_defined_parameter['message'])
    py.press('space')
    py.press('enter')
    time.sleep(0.5)


def reconnect():
    """Determine whether the peer is disconnected and return to the matching hall
    :return: bool -->TRUE
    """
    log.print(f"{now_time()}……///正在进入重连···")
    time.sleep(2)
    # moveclick(586, 679, cli
    # moveclick(570, 710, click_delay=1)  # 错误代码2
    # moveclick(594, 721, click_delay=1)  # 错误代码3
    # moveclick(1334, 635, click_delay=1)  # 错误代码4
    # moveclick(1429, 640, click_delay=1)  # 错误代码5
    # moveclick(1389, 670, click_delay=1)  # 错误代码6
    # moveclick(563, 722, click_delay=1)  # 错误代码7
    while eq(disconnect_check(), True):
        for sum in range(80, 130, 10):
            disconnect_confirm(sum)
            if eq(disconnect_check(), False):
                break
    # 段位重置
    # if eq(segment_reset(), True):
    #     moveclick(1462, 841)
    # 检测血点，判断断线情况
    if eq(starthall(), True) or eq(readyhall(), True):  # 小退
        log.print(f"{now_time()}……///断线重连程度检测·····小退")
        return True
    elif eq(gameover(), True):  # 意味着不在大厅
        moveclick(1761, 1009)
        log.print(f"{now_time()}……///断线重连程度检测·····小退")
        return True
    else:  # 大退
        log.print(f"{now_time()}……///断线重连程度检测·····大退")
        main_quit = False
        while main_quit == False:
            while eq(disconnect_check(), True):
                for sum in range(80, 130, 10):
                    disconnect_confirm(sum)
                    if eq(disconnect_check(), False):
                        break
            time.sleep(1)
            # moveclick(1453, 628, click_delay=1)  # 错误
            #### 活动奖励
            if eq(news(), True):
                moveclick(1413, 992, click_delay=1)  # 新闻点击
            # moveclick(1430, 744, click_delay=1)  # 账号连接
            # moveclick(1631, 966, click_delay=1)  # 转生系统
            # if eq(blood_and_ceasma(), True):
            #     while eq(blood_and_ceasma(), True):
            #         moveclick(0, 0, 0.5, 1)
            #         moveclick(1761, 1009, 3, 1)
            #     return True
            # 判断每日祭礼
            if eq(daily_ritual_main(), True):
                moveclick(545, 880, click_delay=1)
            # 是否重进主页面判断
            if eq(mainjudge(), True):
                # 通过阵营选择判断返回大厅
                if eq(cfg.getboolean("CPCI", "rb_survivor"), True):
                    moveclick(143, 261)
                elif eq(cfg.getboolean("CPCI", "rb_killer"), True):
                    moveclick(135, 133)
                main_quit = True
        log.print(f"{now_time()}……///重连完成···")
        return True


def random_movement():
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


def random_direction():
    """随机旋转方向
    :return: str
    """
    rn = random.randint(1, 2)
    if eq(rn, 1):
        return 'q'
    else:
        return 'e'


def random_movetime():
    """get the character random move time in the game
    :return: float"""
    rn = round(random.uniform(1.1, 2.0), 3)  # 0.5 1.5
    return rn


def random_veertime():
    """get the character random veer time
    :return: float"""
    rn = round(random.uniform(0.275, 0.4), 3)  # 0.6
    return rn


def random_move(move_time):
    """行走动作"""
    act_move = random_movement()
    key_down(hwnd, act_move)
    time.sleep(move_time)
    key_up(hwnd, act_move)


def random_veer(veer_time):
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

def survivor_action():
    """survivor`s action"""
    key_down(hwnd, 'lshift')
    act_move = random_movement()
    key_down(hwnd, act_move)
    act_direction = random_direction()
    key_down(hwnd, act_direction)
    time.sleep(random_veertime())
    key_up(hwnd, act_direction)
    py.mouseDown(button='left')
    time.sleep(2)
    py.mouseUp(button='left')
    key_up(hwnd, act_move)
    key_up(hwnd, 'lshift')


# def killer_action_skill():
#     """killer`s skill action"""
#     random_number = random.sample(range(1, 6), 5)
#     act_direction = random_direction()
#     act_direction_judge = False
#     rn = random.randint(1, 1000)
#     if 1 <= rn <= 25:
#         act_move = random_movement()
#         key_down(hwnd, act_move)
#         key_down(hwnd, act_direction)
#         act_direction_judge = True
#     else:
#         act_move = random_movement()
#         key_down(hwnd, act_move)
#     time.sleep(0.2)
#     # 力量
#     ctrl_lst = ["医生", "梦魇", "小丑", "魔王", "连体婴", "影魔", "白骨商人"]
#     if custom_select.select_killer_lst[character_num_b - 1] in ctrl_lst:
#         if eq(random_number[0], 1) or eq(random_number[0], 2) or eq(random_number[0], 3):
#         # rn = random.randint(1, 200)
#         # if 100 < rn <= 175:
#             key_down(hwnd, 'lcontrol')
#             time.sleep(4.3)
#             key_up(hwnd, 'lcontrol')
#     if act_direction_judge:
#         key_up(hwnd, act_direction)
#     key_up(hwnd, act_move)
#     # 技能[右键左键]
#     need_lst = ["门徒", "魔王", "死亡枪手", "骗术师", "NEMESIS", "地狱修士", "艺术家", "影魔", "奇点", "操纵者"]
#     if custom_select.select_killer_lst[character_num_b - 1] in need_lst:
#         if eq(random_number[1], 2) or eq(random_number[1], 1) or eq(random_number[1], 3):
#         # rn = random.randint(1, 1000)
#         # if 1 <= rn <= 25:
#             act_move = random_movement()
#             key_down(hwnd, act_move)
#             veertime = round(random.uniform(0.3, 0.6), 3)
#             random_veer(veertime)
#         elif eq(random_number[2], 3):
#             act_move = random_movement()
#             key_down(hwnd, act_move)
#             random_veer(random_veertime())
#         if eq(random_number[3], 4) or eq(random_number[3], 3) or eq(random_number[3], 2):
#             py.mouseDown(button='right')
#             rn = random.randint(1, 10)
#             if rn >= 7:
#                 random_veer(random_veertime())
#             time.sleep(3.5)
#             py.mouseDown()
#             py.mouseUp()
#             py.mouseUp(button='right')
#             time.sleep(2.0)
#         random_veer(random_veertime())
#         rn = random.randint(1, 1000)
#         if 1 <= rn <= 850:
#             key_down(hwnd, 'lcontrol')
#             key_up(hwnd, 'lcontrol')
#             key_down(hwnd, 'lcontrol')
#             key_up(hwnd, 'lcontrol')
#         key_up(hwnd, act_move)
#     elif eq(custom_select.select_killer_lst[character_num_b - 1], "枯萎者"):
#         for i in range(5):
#             act_move = random_movement()
#             key_down(hwnd, act_move)
#             act_direction = random_direction()
#             py.mouseDown(button='right')
#             py.mouseUp(button='right')
#             time.sleep(0.7)
#             key_down(hwnd, act_direction)
#             time.sleep(0.3)
#             key_up(hwnd, act_direction)
#             key_up(hwnd, act_move)
#     else:
#         # 技能[右键]
#         for i in range(1):
#             move_time = round(random.uniform(1.5, 5.0), 3)
#             random_move(move_time)
#             veertime = round(random.uniform(0.285, 0.6), 3)
#             random_veer(veertime)
#         act_move_1 = random_movement()
#         act_move_2 = random_movement()
#         key_down(hwnd, act_move_1)
#         key_down(hwnd, act_move_2)
#         time.sleep(1.5)
#         py.mouseDown(button='right')
#         time.sleep(1)
#         key_down(hwnd, 'lcontrol')
#         key_up(hwnd, 'lcontrol')
#         py.mouseUp(button='right')
#         key_up(hwnd, act_move_1)
#         key_up(hwnd, act_move_2)
#         random_move(3)
def killer_ctrl():
    key_down(hwnd, 'lcontrol')
    time.sleep(4.3)
    key_up(hwnd, 'lcontrol')


def killer_skillclick():
    py.mouseDown(button='right')
    time.sleep(3)
    py.mouseDown()
    py.mouseUp()
    py.mouseUp(button='right')
    time.sleep(2)
    key_down(hwnd, 'lcontrol')
    key_up(hwnd, 'lcontrol')


def killer_skill():
    py.mouseDown(button='right')
    time.sleep(3)
    key_down(hwnd, 'lcontrol')
    key_up(hwnd, 'lcontrol')
    py.mouseUp(button='right')


def killer_action():
    """killer integral action"""
    ctrl_lst_cn = ["医生", "梦魇", "小丑", "魔王", "连体婴", "影魔", "白骨商人", "好孩子"]
    need_lst_cn = ["门徒", "魔王", "死亡枪手", "骗术师", "NEMESIS", "地狱修士", "艺术家", "影魔", "奇点", "操纵者",
                   "好孩子"]
    ctrl_lst_en = ["DOCTOR", "NIGHTMARE", "CLOWN", "DEMOGORGON", "TWINS", "DREDGE", "SKULL MERCHANT", "GOOD GUY"]
    need_lst_en = ["PIG", "DEMOGORGON", "DEATHSLINGER", "TRICKSTER", "NEMESIS",
                   "CENOBITE", "ARTIST", "DREDGE", "SINGULARITY", "MASTERMIND", "GOOD GUY"]
    ctrl_lst = []
    need_lst = []
    if cfg.getboolean("UPDATE", "rb_chinese"):
        ctrl_lst = ctrl_lst_cn
        need_lst = need_lst_cn
    elif cfg.getboolean("UPDATE", "rb_english"):
        ctrl_lst = ctrl_lst_en
        need_lst = need_lst_en
    if eq(custom_select.select_killer_lst[character_num_b - 1], "枯萎者") or eq(
            custom_select.select_killer_lst[character_num_b - 1], "BLIGHT"):
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
    elif custom_select.select_killer_lst[character_num_b - 1] in need_lst:
        random_number = random.randint(1, 1000)
        if gt(random_number, 400):
            # 移动
            key_down(hwnd, 'w')
            # 点按
            random_number = random.randint(1, 1000)
            if gt(random_number, 600):
                for i in range(3):
                    move = random_movement()
                    if ne(move, 'w'):
                        key_down(hwnd, move)
                        time.sleep(0.5)
                        key_up(hwnd, move)
            # 技能
            random_number = random.randint(1, 1000)
            if gt(random_number, 700):
                killer_skillclick()
            # 转向
            direction = random_direction()
            random_number = random.randint(1, 1000)
            if gt(random_number, 600):
                key_down(hwnd, direction)
                time.sleep(random_veertime())
                key_up(hwnd, direction)
            # ctrl
            random_number = random.randint(1, 1000)
            if gt(random_number, 700):
                killer_ctrl()
            time.sleep(5)
            key_up(hwnd, 'w')
        elif lt(random_number, 400):
            direction = random_direction()
            # 转向
            key_down(hwnd, direction)
            time.sleep(random_veertime())
            key_up(hwnd, direction)
            # 移动
            key_down(hwnd, 'w')
            # 点按
            random_number = random.randint(1, 1000)
            if gt(random_number, 600):
                for i in range(3):
                    move = random_movement()
                    if ne(move, 'w'):
                        key_down(hwnd, move)
                        time.sleep(0.5)
                        key_up(hwnd, move)
            # ctrl
            random_number = random.randint(1, 1000)
            if gt(random_number, 500):
                killer_ctrl()
            # 技能
            random_number = random.randint(1, 1000)
            if gt(random_number, 700):
                killer_skillclick()
            time.sleep(5)
            key_up(hwnd, 'w')
    else:
        random_number = random.randint(1, 1000)
        if gt(random_number, 400):
            # 移动
            key_down(hwnd, 'w')
            # 点按
            random_number = random.randint(1, 1000)
            if gt(random_number, 600):
                for i in range(3):
                    move = random_movement()
                    if ne(move, 'w'):
                        key_down(hwnd, move)
                        time.sleep(0.5)
                        key_up(hwnd, move)
            # 技能
            if ne(custom_select.select_killer_lst[character_num_b - 1], '设陷者'):
                random_number = random.randint(1, 1000)
                if gt(random_number, 700):
                    killer_skill()
            else:
                time.sleep(3)
            # 转向
            random_number = random.randint(1, 1000)
            if gt(random_number, 600):
                direction = random_direction()
                key_down(hwnd, direction)
                time.sleep(random_veertime())
                key_up(hwnd, direction)
                if custom_select.select_killer_lst[character_num_b - 1] in ctrl_lst:
                    # ctrl
                    killer_ctrl()
            time.sleep(5)
            key_up(hwnd, 'w')
        elif lt(random_number, 400):
            direction = random_direction()
            # 转向
            key_down(hwnd, direction)
            time.sleep(random_veertime())
            key_up(hwnd, direction)
            # 移动
            key_down(hwnd, 'w')
            # 点按
            random_number = random.randint(1, 1000)
            if gt(random_number, 600):
                for i in range(3):
                    move = random_movement()
                    if ne(move, 'w'):
                        key_down(hwnd, move)
                        time.sleep(0.5)
                        key_up(hwnd, move)
            # 技能
            if ne(custom_select.select_killer_lst[character_num_b - 1], '设陷者'):
                random_number = random.randint(1, 1000)
                if gt(random_number, 700):
                    if custom_select.select_killer_lst[character_num_b - 1] in ctrl_lst:
                        # ctrl
                        killer_ctrl()
                    killer_skill()
            else:
                time.sleep(3)
            time.sleep(5)
            key_up(hwnd, 'w')


def killer_fixed_act():
    """main blood"""
    for i in range(4):
        move_time = round(random.uniform(1.5, 5.0), 3)
        random_move(move_time)
        veertime = round(random.uniform(0.285, 0.6), 3)
        random_veer(veertime)
        rn = random.randint(1, 200)
        if gt(rn, 175):
            py.mouseDown()
            time.sleep(2)
            py.mouseUp()
            time.sleep(0.3)
    py.mouseDown()
    time.sleep(2)
    py.mouseUp()


def back_first():
    """click back the first character"""
    wheelcoord = Coord(404, 536)
    wheelcoord.processed_coord()
    # 回到最开始,需要几次就回滚几次
    py.moveTo(wheelcoord.x1_coor, wheelcoord.y1_coor)
    py.sleep(0.5)
    py.scroll(1)  # 1
    py.sleep(0.5)
    py.scroll(1)  # 2
    py.sleep(0.5)
    py.scroll(1)  # 3
    moveclick(405, 314, 1.5)


# def character_rotation():
#     '''全角色轮转和单行轮转'''
#     global click_times, max_click, front_times, behind_times, click_times, x, y, input_num
#
#     py.sleep(1)
#     moveclick(1, 1, 1, 1)
#     moveclick(141, 109, 1, 1)  # 角色按钮
#     if eq(click_times, input_num):  # num 为 用户输入的轮换值
#         max_click = 0
#         front_times = 0
#         behind_times = 0
#         click_times = 1
#         if ne(input_num, 4):  # 为4 则是单行轮转
#             back_first()
#         moveclick(405, 314, 1.5)
#     if eq(max_click, 6):  ## 最大的换行次数
#         if lt(behind_times, 3):
#             if eq(behind_times, 0):
#                 x, y = 548, 517  # 最后七个第一个
#             moveclick(x, y, 1.5)
#             x += 155
#             behind_times += 1
#             click_times += 1
#         elif lt(behind_times, 5):  ##最后剩几个就是几个
#             if eq(behind_times, 3):
#                 x, y = 384, 753  # 最后七个第四个
#             moveclick(x, y, 1.5)
#             x += 155
#             behind_times += 1
#             click_times += 1
#     else:
#         if eq(front_times, 0):
#             front_times += 1
#         elif lt(front_times, 4):
#             if eq(front_times, 1):
#                 x, y = 548, 323  # 第二个
#             moveclick(x, y, 1.5)
#             x += 155
#             front_times += 1
#             click_times += 1
#         elif gt(front_times, 3):
#             x, y = 404, 536  # 第五个
#             moveclick(x, y, 1.5)
#             front_times = 1
#             max_click += 1
#             click_times += 1


def character_selection():
    """自选特定的角色轮转"""
    global ghX, ghY, glX, glY, character_num, character_num_b, circle, frequency, judge
    if eq(judge, 0):
        custom_select.read_search_killer_name()
        custom_select.match_select_killer_name()
        character_num = custom_select.match_select_killer_lst
        judge = 1
    py.sleep(1)
    moveclick(10, 10, 1, 1)
    moveclick(141, 109, 1, 1)  # 角色按钮
    timey = floordiv(character_num[character_num_b], 4)  # 取整
    timex = mod(character_num[character_num_b], 4)  # 取余
    time.sleep(0.5)
    wheelcoord = Coord(404, 536)  # 第五个坐标，提前处理
    wheelcoord.processed_coord()
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
                final_number -= 2  # -->>
                moveclick(glX[final_number], glY[final_number], 1.5)
    if lt(circle, len(character_num)):
        circle += 1
        character_num_b += 1
        if eq(character_num_b, len(character_num)):
            circle = 0
            character_num_b = 0


def AFK():
    # hwnd = win32gui.FindWindow(None, u"DeadByDaylight  ")
    global hwnd, match_stage, ready_stage, end_stage, self_defined_parameter
    if cfg.getboolean("UPDATE", "rb_chinese"):
        custom_select.select_killer_name_CN()
    elif cfg.getboolean("UPDATE", "rb_english"):
        custom_select.select_killer_name_EN()
    list_number = len(custom_select.select_killer_lst)
    # 判断游戏是否运行
    if eq(hwnd, 0) and cfg.getboolean("UPDATE", "rb_chinese"):
        win32api.MessageBox(hwnd, "未检测到游戏窗口，请先启动游戏。", "提示",
                            win32con.MB_OK | win32con.MB_ICONWARNING)
        kill()
    elif eq(hwnd, 0) and cfg.getboolean("UPDATE", "rb_english"):
        win32api.MessageBox(hwnd, "The game window was not detected. Please start the game first.", "Prompt",
                            win32con.MB_OK | win32con.MB_ICONWARNING)
        kill()
    if not custom_select.select_killer_lst and eq(cfg.getboolean("CPCI", "rb_killer"), True):
        if cfg.getboolean("UPDATE", "rb_chinese"):
            win32api.MessageBox(hwnd, "未选择屠夫。", "提示", win32con.MB_OK | win32con.MB_ICONASTERISK)
            kill()
        elif cfg.getboolean("UPDATE", "rb_english"):
            win32api.MessageBox(hwnd, "No killer selected.", "Prompt",
                                win32con.MB_OK | win32con.MB_ICONASTERISK)
            kill()
    # 检查输入数值是否超过最大角色数量
    # if eq(settings.value("CPCI/rb_survivor"), True) and gt(dbd_window.main_ui.sb_input_count.value(), 32):
    #     win32api.MessageBox(hwnd, "超过角色最大数量。", "错误", win32con.MB_OK | win32con.MB_ICONERROR)
    #     sys.exit(0)
    # elif eq(settings.value("CPCI/rb_killer"), True) and gt(dbd_window.main_ui.sb_input_count.value(), 30):
    #     win32api.MessageBox(hwnd, "超过角色最大数量。", "错误", win32con.MB_OK | win32con.MB_ICONERROR)
    #     sys.exit(0)

    # 置顶
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
    # 取消置顶
    win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
    moveclick(10, 10)
    log.print(f"{now_time()}---启动脚本····")
    circulate_number = 0
    while True:
        reconnection = False
        circulate_number += 1
        '''
        匹配

        '''
        matching = False
        while not matching:
            log.print(f"{now_time()}---第{circulate_number}次脚本循环---脚本处于匹配阶段···")
            # 判断条件是否成立
            if eq(starthall(), True):
                log.print(f"{now_time()}---第{circulate_number}次脚本循环---游戏处于匹配大厅···")
                # 判断游戏所处的阶段
                if eq(self_defined_parameter['stage_judge_switch'], 1):
                    stage_judge()
                    if match_stage != "匹配大厅":
                        break

                """
                在这里判断选择的模式，并从前台提取数值。
                挂机模式 值 = 轮换 则再判断为哪种模式；如果值 = 固定 则等待time
                再判断插件是否为0，@@插件已废弃
                """
                # if eq(settings.value("CPCI/cb_rotate_solo"), True) and eq(settings.value("CPCI/rb_rotate_mode"), True):
                #     global input_num
                #     input_num = 4
                #     time.sleep(1)
                #     character_rotation()
                # elif eq(settings.value("CPCI/cb_rotate_order"), True) and eq(settings.value("CPCI/rb_rotate_mode"), True):
                #     time.sleep(1)
                #     character_rotation()
                # 自动选择屠夫的模式
                if eq(cfg.getboolean("CPCI", "rb_killer"), True):
                    time.sleep(1)
                    # if eq(settings.value("CPCI/rb_no_action"), True):
                    #     list_number = 0
                    if eq(list_number, 1):
                        character_selection()
                        list_number = 0
                    elif gt(list_number, 1):
                        character_selection()
                elif eq(cfg.getboolean("CPCI", "rb_survivor"), True):
                    time.sleep(1)
                # 进行准备
                while eq(starthall(), True):  # debug:False -->test
                    moveclick(1742, 931, 1, 0.5)  # 处理坐标，开始匹配
                    log.print(f"{now_time()}---第{circulate_number}次脚本循环---处于匹配大厅，处理坐标，开始匹配···")
                    moveclick(20, 689, 1.5)  # 商城上空白
                    if eq(disconnect_check(), True):  # 断线检测
                        reconnection = reconnect()
                    else:
                        time.sleep(1.5)
                matching = True
            elif eq(disconnect_check(), True):
                reconnection = reconnect()
                matching = True

        # 重连返回值的判断
        if eq(reconnection, True):
            continue
        '''
        准备加载
        '''
        ready_load = False  # debug:False -->test
        log.print(f"{now_time()}---第{circulate_number}次脚本循环---脚本处于准备加载阶段···")
        # 检测游戏所在阶段
        if eq(self_defined_parameter['stage_judge_switch'], 1):
            if ne(match_stage, "匹配大厅"):
                ready_load = True

        while not ready_load:
            if eq(readycancle(), False):
                log.print(f"{now_time()}---第{circulate_number}次脚本循环---脚本准备加载阶段结束···")
                ready_load = True
            log.print(f"{now_time()}---第{circulate_number}次脚本循环---游戏正在载入中···")

        # 重连返回值的判断
        if eq(reconnection, True):
            continue

        '''
        准备
        '''
        ready_room = False  # debug:False -->True
        log.print(f"{now_time()}---第{circulate_number}次脚本循环---脚本处于准备阶段···")
        while not ready_room:
            # 判断游戏所处的阶段
            if eq(self_defined_parameter['stage_judge_switch'], 1):
                stage_judge()
                if ready_stage != "准备房间":
                    break
            if eq(readyhall(), True):
                log.print(f"{now_time()}---第{circulate_number}次脚本循环---游戏已进入准备大厅···")
                time.sleep(5)
                moveclick(10, 10, 2, 2)
                moveclick(1742, 931, 2, 0.5)
                log.print(f"{now_time()}---第{circulate_number}次脚本循环---准备按钮点击完成···")
                moveclick(20, 689)  # 商城上空白
                if eq(readyhall(), False):
                    ready_room = True
            elif eq(disconnect_check(), True):
                reconnection = reconnect()
                ready_room = True
        # 重连返回值判断
        if eq(reconnection, True):
            continue

        '''
        载入
        '''

        game_load = False
        log.print(f"{now_time()}---第{circulate_number}次脚本循环---脚本处于对局载入阶段···")
        # 检测游戏所在阶段
        if eq(self_defined_parameter['stage_judge_switch'], 1):
            if ne(ready_stage, "准备房间"):
                game_load = True
        while not game_load:
            if eq(readycancle(), False):
                log.print(f"{now_time()}---第{circulate_number}次脚本循环---游戏已进入准备加载阶段···")
                game_load = True
                time.sleep(5)
            log.print(f"{now_time()}---第{circulate_number}次脚本循环---游戏正在载入中···")
        # 重连返回值判断
        if eq(reconnection, True):
            continue

        '''
        局内
        '''
        game = False
        # in_game = False
        log.print(f"{now_time()}---第{circulate_number}次脚本循环---脚本处于对局动作执行阶段···")
        action_time = 0
        while not game:
            action_time += 1
            if eq(gameover(), True):
                log.print(f"{now_time()}---第{circulate_number}次脚本循环---游戏对局已结束···")
                moveclick(10, 10, 0.5, 1)
                time.sleep(2)
                # 段位重置
                # if eq(segment_reset(), True):
                #     moveclick(1462, 841)
                # 祭礼完成
                if eq(rites(), True):
                    moveclick(396, 718, 0.5, 1)
                    moveclick(140, 880)
                time.sleep(5)
                # 判断所处的游戏阶段
                if eq(self_defined_parameter['stage_judge_switch'], 1):
                    stage_judge()
                    if end_stage != "游戏结束":
                        if match_stage == "匹配大厅" or ready_stage == "准备房间":
                            break
                        else:
                            continue
                # 判断是否开启
                if (eq(cfg.getboolean("CPCI", "cb_killer_do"), True)
                        and eq(cfg.getboolean("CPCI", "rb_killer"), True)):
                    auto_message()
                moveclick(1761, 1009, 0.5, 1)  # return hall
                moveclick(10, 10)
                if eq(gameover(), False):
                    game = True
                elif eq(disconnect_check(), True):
                    reconnection = reconnect()
                    game = True
            else:
                # if eq(in_game, False):
                #     if eq(map_name(), True):
                #         in_game = True
                # 从前台获取 阵营数据，再判断行为模式
                # if eq(in_game, True):
                log.print(
                    f"{now_time()}---第{circulate_number}次脚本循环---游戏处于对局阶段···动作循环已执行{action_time}次")
                if eq(cfg.getboolean("CPCI", "rb_survivor"), True):
                    survivor_action()
                elif eq(cfg.getboolean("CPCI", "rb_fixed_mode"), True):
                    killer_fixed_act()
                elif eq(cfg.getboolean("CPCI", "rb_random_mode"), True):
                    killer_action()
                time.sleep(1)
                if eq(disconnect_check(), True):
                    reconnection = reconnect()
                    game = True

        # 重连返回值判断
        if eq(reconnection, True):
            continue


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
    # DBDAS_PATH = os.path.join(BASE_DIR, "DBDAutoScript")
    OCR_PATH = os.path.join(BASE_DIR, "tesseract-ocr\\tesseract.exe")
    CFG_PATH = os.path.join(BASE_DIR, "cfg.cfg")
    SEARCH_PATH_CN = os.path.join(BASE_DIR, "searchfile_cn.txt")
    SEARCH_PATH_EN = os.path.join(BASE_DIR, "searchfile_en.txt")
    SDPARAMETER_PATH = os.path.join(BASE_DIR, "SDparameter.json")
    TRANSLATE_PATH = os.path.join(BASE_DIR, "picture\\transEN.qm")
    LOG_PATH = os.path.join(BASE_DIR, "debug_data.log")
    pytesseract.pytesseract.tesseract_cmd = OCR_PATH
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("picture\\dbdwindow.png"))
    dbd_window = DbdWindow()
    # 判断的颜色值。相似度，屠夫列表
    self_defined_parameter = {'killer_number': 34, 'message': 'GG',
                              'all_killer_name_CN': ["设陷者", "幽灵", "农场主", "护士", "女猎手", "迈克尔迈尔斯",
                                                     "妖巫", "医生",
                                                     "食人魔", "梦魇", "门徒", "小丑", "怨灵", "军团", "瘟疫", "鬼面",
                                                     "魔王", "鬼武士",
                                                     "死亡枪手", "处刑者", "枯萎者", "连体婴", "骗术师", "NEMESIS",
                                                     "地狱修士", "艺术家",
                                                     "贞子", "影魔", "操纵者", "恶骑士", "白骨商人", "奇点", "异形",
                                                     "好孩子"],
                              'all_killer_name_EN': ["TRAPPER", "WRAITH", "HILLBILLY", "NURSE", "HUNTRESS", "SHAPE",
                                                     "HAG", "DOCTOR",
                                                     "CANNIBAL", "NIGHTMARE", "PIG", "CLOWN", "SPIRIT", "LEGION",
                                                     "PLAGUE", "GHOST FACE", "DEMOGORGON", "ONI",
                                                     "DEATHSLINGER", "EXECUTIONER", "BLIGHT", "TWINS", "TRICKSTER",
                                                     "NEMESIS", "CENOBITE", "ARTIST", "ONRY6",
                                                     "DREDGE", "MASTERMIND", "KNIGHT", "SKULL MERCHANT", "SINGULARITY",
                                                     "XENOMORPH", "GOOD GUY"],
                              'stage_judge_switch': 0}
    settings = ConfigObj(CFG_PATH, default_encoding='utf8')
    log = Logger(LOG_PATH)
    cfg = ConfigParser()
    cfg.read(CFG_PATH, encoding='utf-8')
    initialize()
    read_cfg()
    if QLocale.system().language() != QLocale.Chinese or cfg.getboolean("UPDATE", "rb_english"):
        dbd_window.rb_english_change()
    custom_select = CustomSelectKiller()
    qss_style = '''
            QPushButton:hover {
                background-color: #EEF1F2;
                border: 1px solid #D0D3D4;
                border-radius: 5px;
            }
            QPushButton:pressed, QPushButton:checked {
                border: 1px solid #BEC9CA;
                background-color: #EDEEEF;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
            QCheckBox::indicator:unchecked {
                border-image: url(picture/checkbox_unchecked.png);
            }
            QCheckBox::indicator:checked{
                border-image: url(picture/checkbox_checked_border.png);
            }
            QCheckBox::indicator:unchecked:hover {
                border-image: url(picture/checkbox_hover.png);
            }
            QRadioButton::indicator {
                width: 15px;
                height: 15px;
            }
            QRadioButton::indicator:checked {
                border-image: url(picture/radiobutton_checked.png);
            }
            QRadioButton::indicator:unchecked {
                border-image: url(picture/radiobutton_unchecked.png);
            }
            QRadioButton::indicator:unchecked:hover {
                border-image: url(picture/radiobutton_hover_border.png);
            }
        '''
    hwnd = win32gui.FindWindow(None, u"DeadByDaylight  ")
    ScreenX = win32api.GetSystemMetrics(0)  # 屏幕分辨率
    ScreenY = win32api.GetSystemMetrics(1)
    max_click = 0  # 最少点几次不会上升
    front_times = 0  # 可上升部分的循环次数
    behind_times = 0  # 不可上升后的循环次数
    click_times = 1  # 角色点击次数，判断与输入值是否相等
    x, y = 548, 323  # 初始的坐标值[Second]
    # input_num = dbd_window.main_ui.sb_input_count.value()  # 输入值
    test_num = 0  # ocr的尝试次数
    match_stage = "匹配大厅"  # 阶段判断参数
    ready_stage = "准备房间"
    end_stage = "游戏结束"  #
    disconnect_check_area = 0  # 大退后判断区域状态码
    # 角色选择的参数
    ghX = [405, 548, 703, 854]
    ghY = [314, 323, 318, 302]
    glX = [549, 709, 858, 384, 556, 715, 882]
    glY = [517, 528, 523, 753, 741, 749, 750]
    character_num = []  # 列表，表示选择的角色序号
    character_num_b = 0  # 列表的下标
    circle = 0  # 选择的次数
    frequency = 0  # 换行的次数
    judge = 0
    # lw.SetUserTimeLimit("[2023年2月10日0时0分]")
    main_pid = os.getpid()
    # 创建子线程
    hotkey = threading.Thread(target=listen_key, args=(main_pid,), daemon=True)  # args=(os.getpid(),)
    begingame = threading.Thread(target=AFK, daemon=True)
    tip = threading.Thread(target=hall_tip, daemon=True)
    autospace = threading.Thread(target=auto_space, daemon=True)
    hotkey.start()
    authorization()
    notice()
    if eq(cfg.getboolean("UPDATE", "cb_autocheck"), True):
        check_update()
    # dbd_window.setStyleSheet(qss_style)
    dbd_window.show()
    sys.exit(app.exec())

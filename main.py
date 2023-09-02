import os.path
import random
import time
import threading
import sys
import webbrowser
import pyautogui as py
import win32api
import requests, re
import win32gui
import jsonlines
import pytesseract
import psutil
import json
import win32con
import PyQt5.QtCore as qc
from PIL import Image
from PIL import ImageGrab
from keyboard_operation import key_down, key_up
from operator import lt, eq, gt, ge, ne, floordiv, mod
from pynput import keyboard
from win32api import MessageBox
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
# from PyQt5.QtGui import QGuiApplication
from DBDAutoScriptUI import Ui_MainWindow
from selec_killerUI import Ui_Dialog
from AdvancedParameterUI import Ui_AdvancedWindow

class Coord:
    def __init__(self, x1_coor, y1_coor, x2_coor=0, y2_coor=0):
        self.x1_coor = x1_coor
        self.y1_coor = y1_coor
        self.x2_coor = x2_coor
        self.y2_coor = y2_coor

    def processed_coord(self):
        # 获取缩放后的屏幕分辨率,并获得比例
        ScreenX = win32api.GetSystemMetrics(0)
        ScreenY = win32api.GetSystemMetrics(1)
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

def begin():
    save_cfg()
    # begin = multiprocessing.Process(target=AFK)
    # begin.daemon = True
    begingame.start()
    autospace.start()
    # 如果开启提醒，则开启线程
    if eq(settings.value("CPCI/rb_survivor"), True) and eq(settings.value("CPCI/cb_survivor_do"), True):
        tip.start()




def kill():
    psutil.Process(os.getpid()).kill()


class DbdWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.main_ui = Ui_MainWindow()
        self.sel_dialog = SelectWindow()
        self.advanced_ui = AdvancedWindow()
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
        self.main_ui.pb_advanced.clicked.connect(self.pb_advanced_click)
        # self.main_ui.cb_rotate_solo.clicked.connect(self.cb_rotate_solo_click)
        # self.main_ui.cb_rotate_order.clicked.connect(self.cb_rotate_order_click)
        # self.main_ui.cb_select_killer.clicked.connect(self.cb_select_killer_click)
        # self.main_ui.pb_research.clicked.connect(self.pb_research_click)
        self.main_ui.pb_start.clicked.connect(begin)
        self.main_ui.pb_stop.clicked.connect(kill)
        self.main_ui.pb_github.clicked.connect(self.github)

    def pb_research_click(self): #-->> 废弃
        global killer_number
        # lw.SetDict(0, "DbdKillerNames.txt")  # 设置字库
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
        moveclick(141, 109, 1, 1)  # 打开角色按钮
        back_first()
        custom_select.search_killer_name(killer_number)  # 随版本更改

    def github(self):
        webbrowser.open("https://github.com/maskrs/DBD_AFK_TOOL")

    def pb_select_cfg_click(self):
        self.sel_dialog.exec()

    def pb_advanced_click(self):
        self.advanced_ui.exec()
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

    def pb_save_click(self):
        save_cfg()

class AdvancedWindow(QDialog, Ui_AdvancedWindow):
    def __init__(self):
        super().__init__()
        self.advanced_ui = Ui_AdvancedWindow()
        self.advanced_ui.setupUi(self)


class CustomSelectKiller:   #-->> 废弃
    global self_defined_parameter
    def __init__(self):
        self.ocr_error = 0
        self.killer_name_array = []
        self.own_number = 0
        self.select_killer_lst = []
        self.match_select_killer_lst = []
        # 随版本更改
        self.all_killer_name = self_defined_parameter['all_killer_name']

    def read_search_killer_name(self):
        with open(SEARCH_PATH, "r", encoding='UTF-8') as search_file:
            self.killer_name_array = search_file.readlines()
            self.killer_name_array = [c.strip() for c in self.killer_name_array]


    def killer_name_ocr(self):
        killername = Coord(373, 0, 657, 160)
        killername.processed_coord()
        killername.area_check()
        # self.killer_name = lw.Ocr(killername.x1_coor, killername.y1_coor, killername.x2_coor, killername.y2_coor,
        #                           "#125", 0.90)
        if self.killer_name in self.all_killer_name:
            self.write_killer_name()
            if self.killer_name == "奇点":  # 随版本更改
                self.ocr_error = 1
                back_first()
                moveclick(387, 300, 1, 1)
                moveclick(141, 109, 1, 1)  # 关闭角色按钮
                id = win32gui.FindWindow(None, u"DBD_AFK_TOOL")
                win32gui.SetWindowPos(id, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
                win32gui.SetWindowPos(id, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
                MessageBox(0, "角色检索已完成", "提醒", win32con.MB_ICONASTERISK)
                with open(SEARCH_PATH, "w", encoding='UTF-8') as search_file:
                    search_file.write("\n".join(self.killer_name_array))
                self.killer_name_array.clear()
        else:
            killername = Coord(239, 0, 359, 196)
            killername.processed_coord()
            killername.area_check()
            # self.ocr_notown = lw.Ocr(killername.x1_coor, killername.y1_coor, killername.x2_coor, killername.
            #                          y2_coor, "#125", 0.90)
            if self.ocr_notown == "角色":
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
                MessageBox(0, "角色检索已完成", "提醒", win32con.MB_ICONASTERISK)
                with open(SEARCH_PATH, "w", encoding='UTF-8') as search_file:
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
                MessageBox(0, "检索未完成，请检查以下：\n" + str(self.killer_name_array) + "\n有错误或乱码请重新检索", "提醒", win32con.MB_ICONASTERISK)
                with open(SEARCH_PATH, "w") as search_file:
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
        # 随版本更新
        if result_integer >= 7:
            timetypeone = 6

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
                    change_x += 158
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
        if result_integer > 5:
            if result_integer <= 6:
                timetypetwo = timetypetwo - 1
            elif result_integer >= 7:
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

    def select_killer_name(self):
        # 随版本更改
        if settings.value("CUSSEC/cb_jiage"):
            self.select_killer_lst.append("设陷者")
        if settings.value("CUSSEC/cb_dingdang"):
            self.select_killer_lst.append("幽灵")
        if settings.value("CUSSEC/cb_dianjv"):
            self.select_killer_lst.append("农场主")
        if settings.value("CUSSEC/cb_hushi"):
            self.select_killer_lst.append("护士")
        if settings.value("CUSSEC/cb_tuzi"):
            self.select_killer_lst.append("女猎手")
        if settings.value("CUSSEC/cb_maishu"):
            self.select_killer_lst.append("迈克尔迈尔斯")
        if settings.value("CUSSEC/cb_linainai"):
            self.select_killer_lst.append("妖巫")
        if settings.value("CUSSEC/cb_laoyang"):
            self.select_killer_lst.append("医生")
        if settings.value("CUSSEC/cb_babu"):
            self.select_killer_lst.append("食人魔")
        if settings.value("CUSSEC/cb_fulaidi"):
            self.select_killer_lst.append("梦魇")
        if settings.value("CUSSEC/cb_zhuzhu"):
            self.select_killer_lst.append("门徒")
        if settings.value("CUSSEC/cb_xiaochou"):
            self.select_killer_lst.append("小丑")
        if settings.value("CUSSEC/cb_lingmei"):
            self.select_killer_lst.append("怨灵")
        if settings.value("CUSSEC/cb_juntuan"):
            self.select_killer_lst.append("军团")
        if settings.value("CUSSEC/cb_wenyi"):
            self.select_killer_lst.append("瘟疫")
        if settings.value("CUSSEC/cb_guimian"):
            self.select_killer_lst.append("鬼面")
        if settings.value("CUSSEC/cb_mowang"):
            self.select_killer_lst.append("魔王")
        if settings.value("CUSSEC/cb_guiwushi"):
            self.select_killer_lst.append("鬼武士")
        if settings.value("CUSSEC/cb_qiangshou"):
            self.select_killer_lst.append("死亡枪手")
        if settings.value("CUSSEC/cb_sanjiaotou"):
            self.select_killer_lst.append("处刑者")
        if settings.value("CUSSEC/cb_kumo"):
            self.select_killer_lst.append("枯萎者")
        if settings.value("CUSSEC/cb_liantiying"):
            self.select_killer_lst.append("连体婴")
        if settings.value("CUSSEC/cb_gege"):
            self.select_killer_lst.append("骗术师")
        if settings.value("CUSSEC/cb_zhuizhui"):
            self.select_killer_lst.append("NEMESIS")
        if settings.value("CUSSEC/cb_dingzitou"):
            self.select_killer_lst.append("地狱修士")
        if settings.value("CUSSEC/cb_niaojie"):
            self.select_killer_lst.append("艺术家")
        if settings.value("CUSSEC/cb_zhenzi"):
            self.select_killer_lst.append("贞子")
        if settings.value("CUSSEC/cb_yingmo"):
            self.select_killer_lst.append("影魔")
        if settings.value("CUSSEC/cb_weishu"):
            self.select_killer_lst.append("操纵者")
        if settings.value("CUSSEC/cb_eqishi"):
            self.select_killer_lst.append("恶骑士")
        if settings.value("CUSSEC/cb_baigu"):
            self.select_killer_lst.append("白骨商人")
        if settings.value("CUSSEC/cb_jidian"):
            self.select_killer_lst.append("奇点")
        if settings.value("CUSSEC/cb_yixing"):
            self.select_killer_lst.append("异形")

    def match_select_killer_name(self):
        for i in self.select_killer_lst:
            self.match_select_killer_lst.append(self.killer_name_array.index(i)+1)

    def debug_traverse(self):  # 遍历调试
        killer_name_array_len = len(self.killer_name_array)
        print(*self.killer_name_array, sep=",")
        for i in range(0, killer_name_array_len):
            print(self.killer_name_array[i])


def initialize():
    """ 程序初始化 """
    global self_defined_parameter
    if not os.path.exists(CFG_PATH):
        with open(CFG_PATH, 'w') as configfile:
            configfile.write("")
        # 随版本更改
        settings.setValue("CPCI/rb_survivor", False)
        settings.setValue("CPCI/cb_survivor_do", False)
        settings.setValue("CPCI/rb_killer", False)
        settings.setValue("CPCI/cb_killer_do", False)
        settings.setValue("CPCI/rb_fixed_mode", False)
        settings.setValue("CPCI/rb_random_mode", False)
        # settings.setValue("CPCI/rb_no_action", False)
        settings.setValue("UPDATE/cb_autocheck", True)
        settings.setValue("CUSSEC/cb_jiage", False)
        settings.setValue("CUSSEC/cb_dingdang", False)
        settings.setValue("CUSSEC/cb_dianjv", False)
        settings.setValue("CUSSEC/cb_hushi", False)
        settings.setValue("CUSSEC/cb_tuzi", False)
        settings.setValue("CUSSEC/cb_maishu", False)
        settings.setValue("CUSSEC/cb_linainai", False)
        settings.setValue("CUSSEC/cb_laoyang", False)
        settings.setValue("CUSSEC/cb_babu", False)
        settings.setValue("CUSSEC/cb_fulaidi", False)
        settings.setValue("CUSSEC/cb_zhuzhu", False)
        settings.setValue("CUSSEC/cb_xiaochou", False)
        settings.setValue("CUSSEC/cb_lingmei", False)
        settings.setValue("CUSSEC/cb_juntuan", False)
        settings.setValue("CUSSEC/cb_wenyi", False)
        settings.setValue("CUSSEC/cb_guimian", False)
        settings.setValue("CUSSEC/cb_mowang", False)
        settings.setValue("CUSSEC/cb_guiwushi", False)
        settings.setValue("CUSSEC/cb_qiangshou", False)
        settings.setValue("CUSSEC/cb_sanjiaotou", False)
        settings.setValue("CUSSEC/cb_kumo", False)
        settings.setValue("CUSSEC/cb_liantiying", False)
        settings.setValue("CUSSEC/cb_gege", False)
        settings.setValue("CUSSEC/cb_zhuizhui", False)
        settings.setValue("CUSSEC/cb_dingzitou", False)
        settings.setValue("CUSSEC/cb_niaojie", False)
        settings.setValue("CUSSEC/cb_zhenzi", False)
        settings.setValue("CUSSEC/cb_yingmo", False)
        settings.setValue("CUSSEC/cb_weishu", False)
        settings.setValue("CUSSEC/cb_eqishi", False)
        settings.setValue("CUSSEC/cb_baigu", False)
        settings.setValue("CUSSEC/cb_jidian", False)
        settings.setValue("CUSSEC/cb_yixing", False)

    if not os.path.exists(SDPARAMETER_PATH):
        with jsonlines.open(SDPARAMETER_PATH, mode='w') as writer:
            writer.write(self_defined_parameter)


def save_cfg():
    """ 保存配置文件 """
    # 随版本更改
    settings.setValue("CPCI/rb_survivor", dbd_window.main_ui.rb_survivor.isChecked())
    settings.setValue("CPCI/cb_survivor_do", dbd_window.main_ui.cb_survivor_do.isChecked())
    settings.setValue("CPCI/rb_killer", dbd_window.main_ui.rb_killer.isChecked())
    settings.setValue("CPCI/cb_killer_do", dbd_window.main_ui.cb_killer_do.isChecked())
    settings.setValue("CPCI/rb_fixed_mode", dbd_window.main_ui.rb_fixed_mode.isChecked())
    settings.setValue("CPCI/rb_random_mode", dbd_window.main_ui.rb_random_mode.isChecked())
    # settings.setValue("CPCI/rb_no_action", dbd_window.main_ui.rb_no_action.isChecked())
    settings.setValue("UPDATE/cb_autocheck", dbd_window.main_ui.cb_autocheck.isChecked())
    settings.setValue("CUSSEC/cb_jiage", dbd_window.sel_dialog.select_ui.cb_jiage.isChecked())
    settings.setValue("CUSSEC/cb_dingdang", dbd_window.sel_dialog.select_ui.cb_dingdang.isChecked())
    settings.setValue("CUSSEC/cb_dianjv", dbd_window.sel_dialog.select_ui.cb_dianjv.isChecked())
    settings.setValue("CUSSEC/cb_hushi", dbd_window.sel_dialog.select_ui.cb_hushi.isChecked())
    settings.setValue("CUSSEC/cb_tuzi", dbd_window.sel_dialog.select_ui.cb_tuzi.isChecked())
    settings.setValue("CUSSEC/cb_maishu", dbd_window.sel_dialog.select_ui.cb_maishu.isChecked())
    settings.setValue("CUSSEC/cb_linainai", dbd_window.sel_dialog.select_ui.cb_linainai.isChecked())
    settings.setValue("CUSSEC/cb_laoyang", dbd_window.sel_dialog.select_ui.cb_laoyang.isChecked())
    settings.setValue("CUSSEC/cb_babu", dbd_window.sel_dialog.select_ui.cb_babu.isChecked())
    settings.setValue("CUSSEC/cb_fulaidi", dbd_window.sel_dialog.select_ui.cb_fulaidi.isChecked())
    settings.setValue("CUSSEC/cb_zhuzhu", dbd_window.sel_dialog.select_ui.cb_zhuzhu.isChecked())
    settings.setValue("CUSSEC/cb_xiaochou", dbd_window.sel_dialog.select_ui.cb_xiaochou.isChecked())
    settings.setValue("CUSSEC/cb_lingmei", dbd_window.sel_dialog.select_ui.cb_lingmei.isChecked())
    settings.setValue("CUSSEC/cb_juntuan", dbd_window.sel_dialog.select_ui.cb_juntuan.isChecked())
    settings.setValue("CUSSEC/cb_wenyi", dbd_window.sel_dialog.select_ui.cb_wenyi.isChecked())
    settings.setValue("CUSSEC/cb_guimian", dbd_window.sel_dialog.select_ui.cb_guimian.isChecked())
    settings.setValue("CUSSEC/cb_mowang", dbd_window.sel_dialog.select_ui.cb_mowang.isChecked())
    settings.setValue("CUSSEC/cb_guiwushi", dbd_window.sel_dialog.select_ui.cb_guiwushi.isChecked())
    settings.setValue("CUSSEC/cb_qiangshou", dbd_window.sel_dialog.select_ui.cb_qiangshou.isChecked())
    settings.setValue("CUSSEC/cb_sanjiaotou", dbd_window.sel_dialog.select_ui.cb_sanjiaotou.isChecked())
    settings.setValue("CUSSEC/cb_kumo", dbd_window.sel_dialog.select_ui.cb_kumo.isChecked())
    settings.setValue("CUSSEC/cb_liantiying", dbd_window.sel_dialog.select_ui.cb_liantiying.isChecked())
    settings.setValue("CUSSEC/cb_gege", dbd_window.sel_dialog.select_ui.cb_gege.isChecked())
    settings.setValue("CUSSEC/cb_zhuizhui", dbd_window.sel_dialog.select_ui.cb_zhuizhui.isChecked())
    settings.setValue("CUSSEC/cb_dingzitou", dbd_window.sel_dialog.select_ui.cb_dingzitou.isChecked())
    settings.setValue("CUSSEC/cb_niaojie", dbd_window.sel_dialog.select_ui.cb_niaojie.isChecked())
    settings.setValue("CUSSEC/cb_zhenzi", dbd_window.sel_dialog.select_ui.cb_zhenzi.isChecked())
    settings.setValue("CUSSEC/cb_yingmo", dbd_window.sel_dialog.select_ui.cb_yingmo.isChecked())
    settings.setValue("CUSSEC/cb_weishu", dbd_window.sel_dialog.select_ui.cb_weishu.isChecked())
    settings.setValue("CUSSEC/cb_eqishi", dbd_window.sel_dialog.select_ui.cb_eqishi.isChecked())
    settings.setValue("CUSSEC/cb_baigu", dbd_window.sel_dialog.select_ui.cb_baigu.isChecked())
    settings.setValue("CUSSEC/cb_jidian", dbd_window.sel_dialog.select_ui.cb_jidian.isChecked())
    settings.setValue("CUSSEC/cb_yixing", dbd_window.sel_dialog.select_ui.cb_yixing.isChecked())

def read_cfg():
    """读取配置文件"""
    global self_defined_parameter
    # 随版本更改
    dbd_window.main_ui.rb_survivor.setChecked(json.loads(settings.value("CPCI/rb_survivor")))
    dbd_window.main_ui.cb_survivor_do.setChecked(json.loads(settings.value("CPCI/cb_survivor_do")))
    dbd_window.main_ui.rb_killer.setChecked(json.loads(settings.value("CPCI/rb_killer")))
    dbd_window.main_ui.cb_killer_do.setChecked(json.loads(settings.value("CPCI/cb_killer_do")))
    dbd_window.main_ui.rb_fixed_mode.setChecked(json.loads(settings.value("CPCI/rb_fixed_mode")))
    dbd_window.main_ui.rb_random_mode.setChecked(json.loads(settings.value("CPCI/rb_random_mode")))
    # dbd_window.main_ui.rb_no_action.setChecked(json.loads(settings.value("CPCI/rb_no_action")))
    dbd_window.main_ui.cb_autocheck.setChecked(json.loads(settings.value("UPDATE/cb_autocheck")))
    dbd_window.sel_dialog.select_ui.cb_jiage.setChecked(json.loads(settings.value("CUSSEC/cb_jiage")))
    dbd_window.sel_dialog.select_ui.cb_dingdang.setChecked(json.loads(settings.value("CUSSEC/cb_dingdang")))
    dbd_window.sel_dialog.select_ui.cb_dianjv.setChecked(json.loads(settings.value("CUSSEC/cb_dianjv")))
    dbd_window.sel_dialog.select_ui.cb_hushi.setChecked(json.loads(settings.value("CUSSEC/cb_hushi")))
    dbd_window.sel_dialog.select_ui.cb_tuzi.setChecked(json.loads(settings.value("CUSSEC/cb_tuzi")))
    dbd_window.sel_dialog.select_ui.cb_maishu.setChecked(json.loads(settings.value("CUSSEC/cb_maishu")))
    dbd_window.sel_dialog.select_ui.cb_linainai.setChecked(json.loads(settings.value("CUSSEC/cb_linainai")))
    dbd_window.sel_dialog.select_ui.cb_laoyang.setChecked(json.loads(settings.value("CUSSEC/cb_laoyang")))
    dbd_window.sel_dialog.select_ui.cb_babu.setChecked(json.loads(settings.value("CUSSEC/cb_babu")))
    dbd_window.sel_dialog.select_ui.cb_fulaidi.setChecked(json.loads(settings.value("CUSSEC/cb_fulaidi")))
    dbd_window.sel_dialog.select_ui.cb_zhuzhu.setChecked(json.loads(settings.value("CUSSEC/cb_zhuzhu")))
    dbd_window.sel_dialog.select_ui.cb_xiaochou.setChecked(json.loads(settings.value("CUSSEC/cb_xiaochou")))
    dbd_window.sel_dialog.select_ui.cb_lingmei.setChecked(json.loads(settings.value("CUSSEC/cb_lingmei")))
    dbd_window.sel_dialog.select_ui.cb_juntuan.setChecked(json.loads(settings.value("CUSSEC/cb_juntuan")))
    dbd_window.sel_dialog.select_ui.cb_wenyi.setChecked(json.loads(settings.value("CUSSEC/cb_wenyi")))
    dbd_window.sel_dialog.select_ui.cb_guimian.setChecked(json.loads(settings.value("CUSSEC/cb_guimian")))
    dbd_window.sel_dialog.select_ui.cb_mowang.setChecked(json.loads(settings.value("CUSSEC/cb_mowang")))
    dbd_window.sel_dialog.select_ui.cb_guiwushi.setChecked(json.loads(settings.value("CUSSEC/cb_guiwushi")))
    dbd_window.sel_dialog.select_ui.cb_qiangshou.setChecked(json.loads(settings.value("CUSSEC/cb_qiangshou")))
    dbd_window.sel_dialog.select_ui.cb_sanjiaotou.setChecked(json.loads(settings.value("CUSSEC/cb_sanjiaotou")))
    dbd_window.sel_dialog.select_ui.cb_kumo.setChecked(json.loads(settings.value("CUSSEC/cb_kumo")))
    dbd_window.sel_dialog.select_ui.cb_liantiying.setChecked(json.loads(settings.value("CUSSEC/cb_liantiying")))
    dbd_window.sel_dialog.select_ui.cb_gege.setChecked(json.loads(settings.value("CUSSEC/cb_gege")))
    dbd_window.sel_dialog.select_ui.cb_zhuizhui.setChecked(json.loads(settings.value("CUSSEC/cb_zhuizhui")))
    dbd_window.sel_dialog.select_ui.cb_dingzitou.setChecked(json.loads(settings.value("CUSSEC/cb_dingzitou")))
    dbd_window.sel_dialog.select_ui.cb_niaojie.setChecked(json.loads(settings.value("CUSSEC/cb_niaojie")))
    dbd_window.sel_dialog.select_ui.cb_zhenzi.setChecked(json.loads(settings.value("CUSSEC/cb_zhenzi")))
    dbd_window.sel_dialog.select_ui.cb_yingmo.setChecked(json.loads(settings.value("CUSSEC/cb_yingmo")))
    dbd_window.sel_dialog.select_ui.cb_weishu.setChecked(json.loads(settings.value("CUSSEC/cb_weishu")))
    dbd_window.sel_dialog.select_ui.cb_eqishi.setChecked(json.loads(settings.value("CUSSEC/cb_eqishi")))
    dbd_window.sel_dialog.select_ui.cb_baigu.setChecked(json.loads(settings.value("CUSSEC/cb_baigu")))
    dbd_window.sel_dialog.select_ui.cb_jidian.setChecked(json.loads(settings.value("CUSSEC/cb_jidian")))
    dbd_window.sel_dialog.select_ui.cb_yixing.setChecked(json.loads(settings.value("CUSSEC/cb_yixing")))
    if settings.value("CPCI/rb_survivor") == "true":
        dbd_window.main_ui.cb_survivor_do.setEnabled(True)
        dbd_window.main_ui.rb_fixed_mode.setDisabled(True)
        dbd_window.main_ui.rb_random_mode.setDisabled(True)
        # dbd_window.main_ui.rb_no_action.setDisabled(True)
        # dbd_window.main_ui.pb_research.setDisabled(True)
        dbd_window.main_ui.pb_select_cfg.setDisabled(True)
    if settings.value("CPCI/rb_killer") == "true":
        dbd_window.main_ui.cb_killer_do.setEnabled(True)
    # if settings.value("CPCI/rb_no_action") == "true":
    #     dbd_window.main_ui.pb_research.setDisabled(True)
    #     dbd_window.main_ui.pb_select_cfg.setDisabled(True)

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
        win32api.MessageBox(0, "授权已过期", "授权失败", win32con.MB_OK | win32con.MB_ICONERROR)
        sys.exit(0)

def update():
    """check the update"""
    ver_now = 'V5.1.2'
    html_str = requests.get('https://gitee.com/kioley/DBD_AFK_TOOL').content.decode()
    ver_new = re.search('title>(.*?)<', html_str, re.S).group(1)[13:19]
    if ne(ver_now, ver_new):
        # confirm = pyautogui.confirm(text=text, title="检查更新", buttons=['OK', 'Cancel'])
        confirm = win32api.MessageBox(0,
                                      "检查到新版本：{b}\n\n当前的使用版本是：{a}，推荐更新。".format(a=ver_now, b=ver_new)
                                      , "检查更新", win32con.MB_YESNO | win32con.MB_ICONQUESTION)
        if eq(confirm, 6):  # 打开
            webbrowser.open("https://github.com/maskrs/DBD_AFK_TOOL/releases")


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
    cmb2 = [{keyboard.Key.alt_l, keyboard.KeyCode.from_char('p')}, {keyboard.Key.alt_r, keyboard.KeyCode.from_char('p')}]
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

def OCR(x1, y1, x2, y2,sum=128):
    """OCR识别图像，返回字符串
    :return: string"""
    ocrXY = Coord(x1, y1, x2, y2)
    ocrXY.processed_coord()
    ocrXY.area_check()
    image = ImageGrab.grab(bbox=(ocrXY.x1_coor, ocrXY.y1_coor, ocrXY.x2_coor, ocrXY.y2_coor))
    # 保存图像
    image.save('image.jpg')
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
    result = pytesseract.image_to_string(img, config=custom_config, lang='chi_sim')
    return result
def starthall():
    """check the start  hall
    :return: bool"""
    ocr = OCR(1666, 915, 1808, 955)
    if "开始游戏" in ocr:
        return True
    else:
        return False
def readyhall():
    """check the  ready hall
    :return: bool"""
    ocr = OCR(1666, 915, 1808, 955)
    if "准备就绪" in ocr:
        return True
    else:
        return False

def readycancle():
    """检查游戏准备后的取消，消失就进入对局加载
    :return: bool"""
    ocr = OCR(1771, 936, 1817, 957, 110)
    if "取消" in ocr:
        return True
    else:
        return False

def gameover():
    """检查对局后的继续
    :return: bool"""
    ocr = OCR(1756, 997, 1810, 1026, 120)
    if "继续" in ocr:
        return True
    else:
        return False
# def stage_judge():
#     """判断游戏所处在的阶段"""
#     global match_stage, ready_stage, end_stage
#     match_stageXY = Coord(1672, 919, 1707, 952)
#     match_stageXY.processed_coord()
#     match_stageXY.area_check()
#     match_stage = lw.FindMultiColor(match_stageXY.x1_coor, match_stageXY.y1_coor, match_stageXY.x2_coor, match_stageXY.y2_coor,
#                                     self_defined_parameter['match_stage_first_color'],self_defined_parameter['match_stage_offset_color'],
#                                    0.8, 0, 600)
#     if match_stage == 1:
#         match_stage = "匹配大厅"
#
#     ready_stageXY = Coord(1670, 916, 1708, 953)
#     ready_stageXY.processed_coord()
#     ready_stageXY.area_check()
#     ready_stage = lw.FindMultiColor(ready_stageXY.x1_coor, ready_stageXY.y1_coor, ready_stageXY.x2_coor, ready_stageXY.y2_coor,
#                                     self_defined_parameter['ready_stage_first_color'], self_defined_parameter['ready_stage_offset_color'],
#                                     0.8, 0, 600)
#     if ready_stage == 1:
#         ready_stage = "准备房间"
#
#     end_stageXY = Coord(1753, 993, 1784, 1022)
#     end_stageXY.processed_coord()
#     end_stageXY.area_check()
#     end_stage = lw.FindMultiColor(end_stageXY.x1_coor, end_stageXY.y1_coor, end_stageXY.x2_coor, end_stageXY.y2_coor,
#                                   self_defined_parameter['end_stage_first_color'],self_defined_parameter['end_stage_offset_color'],
#                                   0.8, 0, 600)
#     if end_stage == 1:
#         end_stage = "游戏结束"

def setting_button():
    """check the setting button
    :return: bool"""
    setting_buttonXY = Coord(292, 978, 341, 1032)
    setting_buttonXY.processed_coord()
    setting_buttonXY.area_check()
    ret1, ret2 = setting_buttonXY.find_color(self_defined_parameter['setting_button_color'], self_defined_parameter['setting_button_value'])
    if gt(ret1, 0) and gt(ret2, 0):
        return True
    else:
        return False

def set_race():
    """after race check setting button
    :return: bool"""
    set_raceXY = Coord(91, 985, 133, 1026)
    set_raceXY.processed_coord()
    set_raceXY.area_check()
    ret1, ret2 = set_raceXY.find_color(self_defined_parameter['set_race_color'], self_defined_parameter['set_race_value'])
    if gt(ret1, 0) and gt(ret2, 0):
        return True
    else:
        return False


def ready_red():
    """check after clicking the 'start' button """
    ready_redXY = Coord(1794, 983, 1850, 1037)
    ready_redXY.processed_coord()
    ready_redXY.area_check()
    ret1, ret2 = ready_redXY.find_color(self_defined_parameter['ready_color'], self_defined_parameter['ready_value'])
    if gt(ret1, 0) and gt(ret2, 0):
        return True
    else:
        return False



def segment_reset():
    """check Segment Reset
    :return: bool"""
    segmentXY = Coord(369, 221, 416, 277)
    segmentXY.processed_coord()
    segmentXY.area_check()
    ret1, ret2 = segmentXY.find_color(self_defined_parameter['segment_reset_color'], self_defined_parameter['segment_reset_value'])
    if gt(ret1, 0) and gt(ret2, 0):
        return True
    else:
        return False


def rites():
    """check rites complete
    :return:bool"""
    ocr = OCR(102, 269, 430, 339)
    if "每日祭礼" in ocr:
        return True
    else:
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
    ocr = OCR(447, 268, 674, 338)
    if "每日祭礼" in ocr:
        return True
    else:
        return False


def mainjudge():
    """after serious disconnect.
    check the game whether return the main menu. -->[quit button]
    :return: bool
    """
    ocr = OCR(170, 656, 265, 714, 120)
    if "商城" in ocr:
        return True
    else:
        return False


def disconnect_check():
    """After disconnect check the connection status
    :return: bool"""
    ocr = OCR(299, 614, 1796, 862, 120)
    if "好的" in ocr:
        return True
    else:
        return False
def news():
    """断线重连后的新闻
    :return: bool"""
    ocr = OCR(882, 88, 1030, 153)
    if "新内容" in ocr:
        return True
    else:
        return False

def disconnect_confirm():
    """After disconnection click confirm button. not need process.
    :return: int"""
    disconnect_check_colorXY = Coord(299, 614, 1796, 862)
    disconnect_check_colorXY.processed_coord()
    disconnect_check_colorXY.area_check()
    image = ImageGrab.grab(bbox=(disconnect_check_colorXY.x1_coor, disconnect_check_colorXY.y1_coor,
              disconnect_check_colorXY.x2_coor, disconnect_check_colorXY.y2_coor))
    # 保存图像
    image.save('image.jpg')
    image = Image.open('image.jpg')
    # 将图片转换为灰度图像
    grayscale_image = image.convert('L')
    # 对灰度图像进行二值化处理
    binary_image = grayscale_image.point(lambda x: 0 if x < 120 else 255, '1')
    # 保存二值化后的图片
    binary_image.save('image.jpg')
    # 读取图像
    img = Image.open('image.jpg')
    custom_config = r'--oem 3 --psm 6'
    # 使用Tesseract OCR引擎识别图像中的文本
    result = pytesseract.image_to_boxes(img, config=custom_config, lang='chi_sim')
    result = result.split(' ')
    if ne(len(result), 0):
        confirmX, confirmY = int(result[3]), int(result[4])
        moveclick(disconnect_check_colorXY.x1_coor+confirmX, disconnect_check_colorXY.y2_coor-confirmY, 1, 1)

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
    py.moveTo(coorXY.x1_coor, coorXY.y1_coor)
    time.sleep(delay)
    py.click()
    time.sleep(click_delay)


def auto_message():
    """对局结束后的自动留言"""
    py.press('enter')
    py.write('GG')
    py.press('enter')
    time.sleep(0.5)


def reconnect():
    """Determine whether the peer is disconnected and return to the matching hall
    :return: bool -->TRUE
    """
    time.sleep(2)
    # moveclick(586, 679, cli
    # moveclick(570, 710, click_delay=1)  # 错误代码2
    # moveclick(594, 721, click_delay=1)  # 错误代码3
    # moveclick(1334, 635, click_delay=1)  # 错误代码4
    # moveclick(1429, 640, click_delay=1)  # 错误代码5
    # moveclick(1389, 670, click_delay=1)  # 错误代码6
    # moveclick(563, 722, click_delay=1)  # 错误代码7
    while eq(disconnect_check(), True):
        disconnect_confirm()
    # 段位重置
    # if eq(segment_reset(), True):
    #     moveclick(1462, 841)
    # 检测血点，判断断线情况
    if eq(starthall(), True) or eq(readyhall(), True) or eq(gameover(), True):  # 小退
        if eq(gameover(), True):  # 意味着不在大厅
            moveclick(1335, 326, click_delay=1)
            moveclick(1736, 1010)
            return True
    else:  # 大退
        main_quit = False
        while main_quit == False:
            time.sleep(1)
            py.click()
            time.sleep(5)
            if eq(disconnect_check(), True):
                disconnect_confirm()
                continue
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
                if eq(settings.value("CPCI/rb_survivor"), True):
                    moveclick(143, 261)
                elif eq(settings.value("CPCI/rb_killer"), True):
                    moveclick(135, 133)
                main_quit = True
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
    rn = round(random.uniform(1.1, 2.0), 3) # 0.5 1.5
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

def hurt():
    """check survivor whether hurt
    ":return: bool"""
    hurtXY = Coord(106, 451, 150, 498)  # 102, 450, 159, 499
    hurtXY.processed_coord()
    hurtXY.area_check()
    ret1, ret2 = hurtXY.find_color("9F1409-000000")
    if gt(ret1, 0) and gt(ret2, 0):
        return True
    else:
        return False

def on_hook():
    """check survivor whether on the hook
    :return: bool"""
    hookXY = Coord(106, 451, 150, 498)  # 189, 492, 325, 508
    hookXY.processed_coord()
    hookXY.area_check()
    ret1, ret2 = hookXY.find_color("5F261E-000000")
    if gt(ret1, 0) and gt(ret2, 0):
        return True
    else:
        return False

def survivor_action():
    """survivor`s action"""
    if eq(on_hook(), True):
        time.sleep(2)
        for i in range(2):
            py.mouseDown()
            time.sleep(2)
            py.mouseUp()
            time.sleep(0.5)
    key_down(hwnd, 'lcontrol')
    act_move = random_movement()
    key_down(hwnd, act_move)
    act_direction = random_direction()
    key_down(hwnd, act_direction)
    time.sleep(random_veertime())
    key_up(hwnd, act_direction)
    time.sleep(2)
    if eq(hurt(), True):
        key_up(hwnd, 'lcontrol')
        key_down(hwnd, 'lshift')
        key_down(hwnd, 'w')
        time.sleep(2)
        key_down(hwnd, 'e')
        time.sleep(0.3)
        key_up(hwnd, 'e')
        key_up(hwnd, 'lshift')
        key_down(hwnd, 'lcontrol')
    key_up(hwnd, act_move)
    time.sleep(3)
    key_up(hwnd, 'lcontrol')

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
    ctrl_lst = ["医生", "梦魇", "小丑", "魔王", "连体婴", "影魔", "白骨商人"]
    need_lst = ["门徒", "魔王", "死亡枪手", "骗术师", "NEMESIS", "地狱修士", "艺术家", "影魔", "奇点", "操纵者"]
    if eq(custom_select.select_killer_lst[character_num_b - 1], "枯萎者"):
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
            #ctrl
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
    py.scroll(1)
    py.sleep(0.5)
    py.scroll(1)
    py.sleep(0.5)
    py.scroll(1)
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
    """自选特定的角色轮转【屠夫推荐】"""
    global ghX, ghY, glX, glY, character_num, character_num_b, circle, frequency, judge
    if eq(judge, 0):
        custom_select.read_search_killer_name()
        custom_select.match_select_killer_name()
        character_num = custom_select.match_select_killer_lst
        judge = 1
    py.sleep(1)
    moveclick(1, 1, 1, 1)
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
        moveclick(ghX[timex-1], ghY[timex-1], 1.5)
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
    custom_select.select_killer_name()
    list_number = len(custom_select.select_killer_lst)

    if not settings.value("CPCI/rb_survivor") and not settings.value("CPCI/rb_killer"):
        win32api.MessageBox(hwnd, "请选择阵营。", "提示", win32con.MB_OK | win32con.MB_ICONASTERISK)
        sys.exit(0)

    if not custom_select.select_killer_lst and eq(settings.value("CPCI/rb_killer"), True):
        win32api.MessageBox(hwnd, "至少选择一个屠夫。", "提示", win32con.MB_OK | win32con.MB_ICONASTERISK)
        sys.exit(0)
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
    moveclick(1, 1)
    while True:
        reconnection = False
        '''
        匹配

        '''
        matching = False
        while not matching:
            # 判断条件是否成立
            if eq(starthall(), True):
                # 判断游戏所处的阶段

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
                if eq(settings.value("CPCI/rb_killer"), True):
                    time.sleep(1)
                    # if eq(settings.value("CPCI/rb_no_action"), True):
                    #     list_number = 0
                    if eq(list_number, 1):
                        character_selection()
                        list_number = 0
                    elif gt(list_number, 1):
                        character_selection()
                elif eq(settings.value("CPCI/rb_survivor"), True):
                    time.sleep(1)
                    py.click()
                # 进行准备
                while eq(starthall(), True):  # debug:False -->test
                    moveclick(1742, 931, 1, 0.5)  # 处理坐标，开始匹配
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
        while not ready_load:
            if eq(readycancle(), False):
                ready_load = True

        # 重连返回值的判断
        if eq(reconnection, True):
            continue

        '''
        准备
        '''
        ready_room = False  # debug:False -->True
        while not ready_room:
            if eq(readyhall(), True):
                time.sleep(5)
                moveclick(1, 1, 2, 2)
                moveclick(1742, 931, 2, 0.5)
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
        while not game_load:
            if eq(readycancle(), False):
                game_load = True
                time.sleep(5)
        # 重连返回值判断
        if eq(reconnection, True):
            continue

        '''
        局内
        '''
        game = False
        while not game:
            if eq(gameover(), True):
                moveclick(1, 1, 0.5, 1)
                time.sleep(2)
                # 段位重置
                # if eq(segment_reset(), True):
                #     moveclick(1462, 841)
                # 祭礼完成
                if eq(rites(), True):
                    moveclick(396, 718, 0.5, 1)
                    moveclick(140, 880)
                time.sleep(5)

                # 判断是否开启
                if eq(settings.value("CPCI/cb_killer_do"), True) and eq(settings.value("CPCI/rb_killer"), True):
                    auto_message()
                moveclick(1761, 1009, 0.5, 1)  # return hall
                py.click()
                if eq(gameover(), False):
                    game = True
                elif eq(disconnect_check(), True):
                    reconnection = reconnect()
                    game = True
            else:
                # 从前台获取 阵营数据，再判断行为模式
                if eq(settings.value("CPCI/rb_survivor"), True):
                    survivor_action()
                elif eq(settings.value("CPCI/rb_fixed_mode"), True):
                    killer_fixed_act()
                elif eq(settings.value("CPCI/rb_random_mode"), True):
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
    OCR_PATH = "\\tesseract-ocr\\tesseract.exe"
    CFG_PATH = os.path.join(BASE_DIR, "cfg.ini")
    SEARCH_PATH = os.path.join(BASE_DIR, "searchfile.txt")
    SDPARAMETER_PATH = os.path.join(BASE_DIR, "SDparameter.json")
    pytesseract.pytesseract.tesseract_cmd = ''.join([BASE_DIR, OCR_PATH])
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("picture/dbdwindow.png"))
    dbd_window = DbdWindow()
    settings = qc.QSettings(CFG_PATH, qc.QSettings.IniFormat)
    # 判断的颜色值。相似度，屠夫列表
    self_defined_parameter = {'blood_color': 'C20408-000000',
                              'blood_value': 0.94,
                               'ceasma_color': '8378B2-000000',
                              'ceasma_value': 0.94,
                               'setting_button_color': '7F7F7F-000000',
                              'setting_button_value': 0.95,
                               'set_race_color': '7F7F7F-000000',
                              'set_race_value': 0.95,
                               'ready_color': 'EE0101-000000',
                              'ready_value': 0.95,
                               'segment_reset_color': 'F4F4F4-000000',
                              'segment_reset_value': 0.95,
                               'rites_color': '214826-000000',
                              'rites_value': 0.95,
                               'daily_ritual_main_color': 'FFFFFF-000000',
                              'daily_ritual_main_value': 1.0,
                               'exit_button_main_color': '7F7C78-000000',
                              'exit_button_main_value': 0.95,
                               'disconnect_check_color_red': '730000-000000|6F0000-000000|700000-000000',  # 6E0000-000000|620000-000000
                              'disconnect_check_color_blue': '2A3941-000000|2A3941-000000',
                              'disconnect_check_value': 0.9,
                               'disconnect_confirm_color': '660000-000000',
                              'disconnect_confirm_value': 0.95,
                              'killer_number': 33,
                              'all_killer_name': ["设陷者", "幽灵", "农场主", "护士", "女猎手", "迈克尔迈尔斯", "妖巫", "医生",
                                "食人魔", "梦魇", "门徒", "小丑", "怨灵", "军团", "瘟疫", "鬼面", "魔王", "鬼武士",
                                "死亡枪手", "处刑者", "枯萎者", "连体婴", "骗术师", "NEMESIS", "地狱修士", "艺术家",
                                "贞子", "影魔", "操纵者", "恶骑士", "白骨商人", "奇点", "异形"],
                              'survivor_hurt_color': 'BF221F-000000',
                              'survivor_hurt_value': '0.85',
                              'survivor_on_hook_color': 'BEBCB9-000000',
                              'survivor_on_hook_value': '0.85',
                              'match_stage_first_color': "999999-000000",
                              'match_stage_offset_color': "10|0|999999-000000,0|10|999999-000000,11|11|999999-000000",
                              'ready_stage_first_color': "999999-000000",
                              'ready_stage_offset_color': "0|10|999999-000000,0|16|999999-000000,-9|6|999999-000000",
                              'end_stage_first_color': "949494-000000",
                              'end_stage_offset_color': "0|12|949494-000000,6|17|999999-000000,6|5|989898-000000",
                              'ingame_icon_color': 'FFCC00-000000',
                              'stage_judge_switch': 1}
    initialize()
    read_cfg()
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
    # 判断游戏是否运行
    if hwnd == 0:
        win32api.MessageBox(hwnd, "未检测到游戏窗口，请先启动游戏。", "提示", win32con.MB_OK | win32con.MB_ICONWARNING)
        sys.exit()
    max_click = 0  # 最少点几次不会上升
    front_times = 0  # 可上升部分的循环次数
    behind_times = 0  # 不可上升后的循环次数
    click_times = 1  # 角色点击次数，判断与输入值是否相等
    x, y = 548, 323  # 初始的坐标值[Second]
    # input_num = dbd_window.main_ui.sb_input_count.value()  # 输入值
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
    killer_number = self_defined_parameter['killer_number']
    # lw.SetUserTimeLimit("[2023年2月10日0时0分]")
    main_pid = os.getpid()
    # 创建子线程
    hotkey = threading.Thread(target=listen_key, args=(main_pid,), daemon=True)  # args=(os.getpid(),)
    begingame = threading.Thread(target=AFK, daemon=True)
    tip = threading.Thread(target=hall_tip, daemon=True)
    autospace = threading.Thread(target=auto_space, daemon=True)
    hotkey.start()
    authorization()
    if eq(settings.value("UPDATE/cb_autocheck"), 'true'):
        update()
    # dbd_window.setStyleSheet(qss_style)
    dbd_window.show()
    sys.exit(app.exec())
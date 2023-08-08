import win32api
import os
import sys
from comtypes import client

BASE_DIR_MAIN = os.path.dirname(os.path.realpath(sys.argv[0]))
lwpath = os.path.join(BASE_DIR_MAIN, "lw9_09.dll")

# 这里只能用comtypes 不能用win32com来调用.不然会报错,研究了贼久才搞明白!并且必须是32位的python
def reglw():  # 注册乐玩插件
    try:
        lw = client.CreateObject('lw.lwsoft3')
    except:
        os.system('regsvr32 lwpath /s')
        lw = client.CreateObject('lw.lwsoft3')
    return lw


# 从系统中卸载DLL
def unreglw():
    os.system('regsvr32 lwpath /u')


'''

    if not windll.shell32.IsUserAnAdmin():
        # 不是管理员就提权
        windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, __file__, None, 1)
'''
# if not ctypes.windll.shell32.IsUserAnAdmin():
#         # 不是管理员就提权
#         ctypes.windll.shell32.ShellExecuteW(
#             None, "runas", sys.executable, '', None, 1)
lw = reglw()

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

    def find_color(self, target_color:str, sim=0.95, delay=0):
        lw.FindColor(self.x1_coor, self.y1_coor, self.x2_coor, self.y2_coor, target_color, sim, delay)
        return lw.x(),lw.y()



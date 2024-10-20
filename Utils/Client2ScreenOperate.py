import ctypes
import time
import pyautogui

# 定义Windows API函数
ClientToScreen = ctypes.windll.user32.ClientToScreen
ScreenToClient = ctypes.windll.user32.ScreenToClient
GetWindowRect = ctypes.windll.user32.GetClientRect

# RECT结构体
class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)]

# POINT结构体
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long),
                ("y", ctypes.c_long)]

class MouseController:
    def __init__(self, hwnd):
        self.hwnd = hwnd

    def get_window_rect(self):
        rect = RECT()
        if GetWindowRect(self.hwnd, ctypes.byref(rect)):
            return rect
        return None

    def client_to_screen(self, relative_x, relative_y):
        """
        将窗口相对坐标转换为屏幕坐标
        :param relative_x: 相对窗口的x坐标
        :param relative_y: 相对窗口的y坐标
        :return: 屏幕坐标
        """
        pt = POINT(relative_x, relative_y)
        if ClientToScreen(self.hwnd, ctypes.byref(pt)):
            return pt.x, pt.y
        return relative_x, relative_y

    def screen_to_client(self, screen_x, screen_y):
        """
        将屏幕坐标转换为窗口相对坐标
        :param screen_x: 屏幕的x坐标
        :param screen_y: 屏幕的y坐标
        :return: 窗口相对坐标
        """
        pt = POINT(screen_x, screen_y)
        if ScreenToClient(self.hwnd, ctypes.byref(pt)):
            return pt.x, pt.y
        return screen_x, screen_y

    def moveto(self, relative_x, relative_y):
        """
        移动鼠标到窗口内的相对坐标
        :param relative_x: 相对窗口的x坐标
        :param relative_y: 相对窗口的y坐标
        """
        screen_x, screen_y = self.client_to_screen(relative_x, relative_y)
        if screen_x is not None and screen_y is not None:
            try:
                pyautogui.moveTo(x=screen_x, y=screen_y)
            except pyautogui.FailSafeException:
                pyautogui.moveTo(0, 0)

    def moveclick(self, relative_x, relative_y, delay: float = 0, click_delay: float = 0, times: int = 1, interval: float = 0.0):
        """
        在窗口内的相对坐标点击鼠标
        :param relative_x: 相对窗口的x坐标
        :param relative_y: 相对窗口的y坐标
        :param delay: 鼠标移动到指定位置的延迟时间
        :param click_delay: 鼠标点击后等待时间
        :param times: 鼠标点击次数
        :param interval: 鼠标点击间隔
        """
        screen_x, screen_y = self.client_to_screen(relative_x, relative_y)
        if screen_x is not None and screen_y is not None:
            try:
                pyautogui.moveTo(x=screen_x, y=screen_y)
            except pyautogui.FailSafeException:
                pyautogui.moveTo(0, 0)
            time.sleep(delay)
            pyautogui.click(clicks=times, interval=interval)
            time.sleep(click_delay)

    @staticmethod
    def get_mouse_position():
        """
        获取当前鼠标在屏幕上的坐标
        """
        return pyautogui.position()


import string
import ctypes
from ctypes import windll, byref, sizeof
from ctypes.wintypes import HWND
from ctypes import wintypes
from PIL import Image  # pillow == 9.3.0
from PIL import ImageGrab
from PIL import UnidentifiedImageError
from PyQt5.QtGui import QImage

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
PostMessageW = windll.user32.PostMessageW
ClientToScreen = windll.user32.ClientToScreen
MapVirtualKeyW = windll.user32.MapVirtualKeyW
VkKeyScanA = windll.user32.VkKeyScanA
WM_KEYDOWN = 0x100
WM_KEYUP = 0x101
WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x202
WM_MOUSEWHEEL = 0x020A
WHEEL_DELTA = 120
# 定义消息类型
WM_COMMAND = 0x0111

# https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
VkCode = {
    "back": 0x08,
    "tab": 0x09,
    "return": 0x0D,
    "backspace": 0x08,
    "shift": 0x10,
    "control": 0x11,
    "alt": 0x12,
    "menu": 0x12,
    "pause": 0x13,
    "capital": 0x14,
    "escape": 0x1B,
    "space": 0x20,
    "end": 0x23,
    "home": 0x24,
    "left": 0x25,
    "up": 0x26,
    "right": 0x27,
    "down": 0x28,
    "print": 0x2A,
    "snapshot": 0x2C,
    "insert": 0x2D,
    "delete": 0x2E,
    "lwin": 0x5B,
    "rwin": 0x5C,
    "numpad0": 0x60,
    "numpad1": 0x61,
    "numpad2": 0x62,
    "numpad3": 0x63,
    "numpad4": 0x64,
    "numpad5": 0x65,
    "numpad6": 0x66,
    "numpad7": 0x67,
    "numpad8": 0x68,
    "numpad9": 0x69,
    "multiply": 0x6A,
    "add": 0x6B,
    "separator": 0x6C,
    "subtract": 0x6D,
    "decimal": 0x6E,
    "divide": 0x6F,
    "f1": 0x70,
    "f2": 0x71,
    "f3": 0x72,
    "f4": 0x73,
    "f5": 0x74,
    "f6": 0x75,
    "f7": 0x76,
    "f8": 0x77,
    "f9": 0x78,
    "f10": 0x79,
    "f11": 0x7A,
    "f12": 0x7B,
    "numlock": 0x90,
    "scroll": 0x91,
    "lshift": 0xA0,
    "rshift": 0xA1,
    "lcontrol": 0xA2,
    "rcontrol": 0xA3,
    "lalt": 0xA4,
    "ralt": 0xA5,
    "lmenu": 0xA4,
    "rmenu": 0XA5
}


def get_virtual_keycode(key: str):
    """根据按键名获取虚拟按键码

    Args:
        key (str): 按键名

    Returns:
        int: 虚拟按键码
    """
    if len(key) == 1 and key in string.printable:
        # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-vkkeyscana
        return VkKeyScanA(ord(key)) & 0xff
    else:
        return VkCode[key]


def key_down(handle: HWND, key: str):
    """按下指定按键

    Args:
        handle (HWND): 窗口句柄
        key (str): 按键名
    """
    vk_code = get_virtual_keycode(key)
    scan_code = MapVirtualKeyW(vk_code, 0)
    # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-keydown
    wparam = vk_code
    lparam = (scan_code << 16) | 1
    PostMessageW(handle, WM_KEYDOWN, wparam, lparam)


def key_up(handle: HWND, key: str):
    """放开指定按键

    Args:
        handle (HWND): 窗口句柄
        key (str): 按键名
    """
    vk_code = get_virtual_keycode(key)
    scan_code = MapVirtualKeyW(vk_code, 0)
    # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-keyup
    wparam = vk_code
    lparam = (scan_code << 16) | 0XC0000001
    PostMessageW(handle, WM_KEYUP, wparam, lparam)


# 定义 BITMAPINFOHEADER 结构体
class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ('biSize', wintypes.DWORD),
        ('biWidth', wintypes.LONG),
        ('biHeight', wintypes.LONG),
        ('biPlanes', wintypes.WORD),
        ('biBitCount', wintypes.WORD),
        ('biCompression', wintypes.DWORD),
        ('biSizeImage', wintypes.DWORD),
        ('biXPelsPerMeter', wintypes.LONG),
        ('biYPelsPerMeter', wintypes.LONG),
        ('biClrUsed', wintypes.DWORD),
        ('biClrImportant', wintypes.DWORD),
    ]


# 定义 BITMAPINFO 结构体，只包含 BITMAPINFOHEADER
class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ('bmiHeader', BITMAPINFOHEADER),
    ]


def screenshot(hwnd) -> Image:
    """后台截图
    :param hwnd:窗口句柄
    :return: Image"""

    # 获取窗口的设备上下文
    hdcScreen = user32.GetDC(None)
    hdcMem = gdi32.CreateCompatibleDC(hdcScreen)
    hwndRect = wintypes.RECT()
    user32.GetWindowRect(hwnd, byref(hwndRect))
    width = hwndRect.right - hwndRect.left
    height = hwndRect.bottom - hwndRect.top

    if width <= 0 and height <= 0:
        return None

    # 创建一个与屏幕兼容的位图
    hBitmap = gdi32.CreateCompatibleBitmap(hdcScreen, width, height)
    hOldBitmap = gdi32.SelectObject(hdcMem, hBitmap)

    # 截取窗口内容
    user32.PrintWindow(hwnd, hdcMem, 0x00000002)  # PRF_CLIENT

    # 准备 BITMAPINFO 结构
    bmpInfo = BITMAPINFO()
    bmpInfo.bmiHeader.biSize = sizeof(BITMAPINFOHEADER)
    bmpInfo.bmiHeader.biWidth = width
    bmpInfo.bmiHeader.biHeight = -height
    bmpInfo.bmiHeader.biPlanes = 1
    bmpInfo.bmiHeader.biBitCount = 32
    bmpInfo.bmiHeader.biCompression = 0  # BI_RGB 的值是 0

    # 计算所需的缓冲区大小，确保每个扫描线都是4字节对齐
    aligned_width = ((width + 3) // 4) * 4  # 对齐到最近的4的倍数
    buffer_size = aligned_width * height * 4  # 每个像素占用 4 字节

    # 为位图数据分配内存
    buffer = ctypes.create_string_buffer(buffer_size)

    # 从设备上下文复制像素数据
    gdi32.GetDIBits(hdcMem, hBitmap, 0, height, buffer, byref(bmpInfo), 0)

    # 创建 QImage 并从 buffer 中加载数据
    q_image = QImage(buffer, width, height, QImage.Format_RGB32)

    try:
        # 转换PIL.Image对象
        pillow_image = Image.fromqimage(q_image)
    except UnidentifiedImageError:
        pillow_image = ImageGrab.grab()

    # 清理资源
    gdi32.SelectObject(hdcMem, hOldBitmap)
    gdi32.DeleteObject(hBitmap)
    gdi32.DeleteDC(hdcMem)
    user32.ReleaseDC(None, hdcScreen)

    return pillow_image

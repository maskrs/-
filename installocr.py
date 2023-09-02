import zipfile39
import os
import sys
import win32api, win32con

BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
zipfile = os.path.join(BASE_DIR, 'curl-8.2.1_8-win64-mingw.zip')
with zipfile39.ZipFile(zipfile, 'r') as zip_ref:
    # 解压文件到指定目录
    zip_ref.extractall(BASE_DIR)

# 添加目录到系统环境变量
OCR_PATH = os.path.join(BASE_DIR, "curl-8.2.1_8-win64-mingw\\bin\\curl.exe")
os.environ['MY_DIRECTORY'] = OCR_PATH
# 检查环境变量是否添加成功
if 'MY_DIRECTORY' in os.environ:
    win32api.MessageBox(0, "初始化成功。", "提示", win32con.MB_OK | win32con.MB_ICONINFORMATION)
    sys.exit()

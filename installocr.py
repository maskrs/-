import os
import sys
import subprocess
import shutil
import win32api
import win32con
from tqdm import tqdm
import requests

def download_file(url, filename):
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024 #1 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    with open(filename, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("ERROR, something went wrong")


BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
# check_path= os.path.join(BASE_DIR, "tesseract-ocr.exe")
OCR_PATH = os.path.join(BASE_DIR, "tesseract-ocr")
# DOWN_PATH = os.path.join(BASE_DIR, "download")
GIT_PATH = os.path.join(BASE_DIR, "Git-2.42.0.2-64-bit.exe")
# OLD_PATH = os.path.join(BASE_DIR, 'download\\tesseract-ocr.exe')
# L_PATH = os.path.join(BASE_DIR, 'chi_sim.traineddata')
# N_PATH = os.path.join(BASE_DIR, 'tesseract-ocr\\tessdata')
print("请确保使用管理员权限运行本程序！！")
print(" ")
print("本程序将自动下载配置所需文件。如果下载速度过慢，可以手动下载。")
print(" ")
# print("手动下载地址：https://wwh.lanzoue.com/itGqd179rg0b?password=31vb ， 密码【31vb】，下载到当前目录，重新运行本程序。")
# print(" ")
# input("请按回车键继续...")
# if os.path.exists(DOWN_PATH):
#     # subprocess.run(['rmdir ', DOWN_PATH])
#     file_name = "del.bat"
#     with open(file_name, "w") as file:
#         # 写入命令
#         file.write("@echo off\n")
#         file.write("rmdir /s /q %~dp0download")
#     subprocess.call('del.bat')
#     os.remove('del.bat')
# 设置要下载的文件URL和存储路径
# print(" ")
if os.path.exists(OCR_PATH):
    print("tesseract-ocr引擎已安装。")
else:
    if os.path.exists(OCR_PATH) == False:
        try:
            # 尝试执行'git --version'命令
            subprocess.check_output('git --version', stderr=subprocess.DEVNULL, shell=True)
            print("Git无需配置。")
        except subprocess.CalledProcessError:
            print("未检测到GIT，配置GIT中...请稍后")
            download_file(
                'https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe',
                'Git-2.42.0.2-64-bit.exe')
            cmd = GIT_PATH + ' /sp- /silent /norestart'
            subprocess.run(cmd)
            os.environ['MY_GIT'] = 'C:\Program Files\Git\cmd'
            if os.path.exists(GIT_PATH):
                os.remove(GIT_PATH)
        print(" ")
        print("正在配置OCR引擎...")
        print(" ")
        subprocess.check_output(['git', 'clone', 'https://gitee.com/kioley/tesseract-ocr.git'])
        # if os.path.exists(DOWN_PATH):
        #     file_name = "del.bat"
        #     with open(file_name, "w") as file:
        #         # 写入命令
        #         file.write("@echo off\n")
        #         file.write("rmdir /s /q %~dp0download")
        #     subprocess.call('del.bat')
        #     os.remove('del.bat')
        # os.popen(check_path)
    elif os.path.exists(OCR_PATH):
        print("OCR引擎已配置。")
        # os.popen(check_path)
        # if os.path.exists(DOWN_PATH):
        #     file_name = "del.bat"
        #     with open(file_name, "w") as file:
        #         # 写入命令
        #         file.write("@echo off\n")
        #         file.write("rmdir /s /q %~dp0download")
        #     subprocess.call('del.bat')
        #     os.remove('del.bat')
    print(" ")
    # if os.path.exists(L_PATH):
    #     shutil.move(L_PATH, N_PATH)
    # else:
    #     win32api.MessageBox(0, "中文附加模块丢失！请重新解压压缩包。", "提示", win32con.MB_OK | win32con.MB_ICONWARNING)
    #     sys.exit()
os.environ['MY_DIRECTORY'] = OCR_PATH
# 检查环境变量是否添加成功
if 'MY_DIRECTORY' in os.environ:
    win32api.MessageBox(0, "初始化成功。", "提示", win32con.MB_OK | win32con.MB_ICONQUESTION)
    sys.exit()
# -*- mode: python ; coding: utf-8 -*-
import locale
import os
import sys
import subprocess
import time
import webbrowser
import win32api
import win32con
import requests
from tqdm import tqdm


def check_language():
    system_language, _ = locale.getdefaultlocale()
    return system_language.startswith('en')

def start_menu():
    if not system_language:
        print("\n1、自动配置")
        print("\n2、手动配置")
        print("\n自动配置将自动下载配置所需文件。如果自动下载过慢，请选择手动配置。")
        choice = input("\n请选择配置方式： ")
        return choice
    elif system_language:
        print("\n1、Automatic configuration")
        print("\n2、Manual configuration")
        print("\nAutomatic configuration files are downloaded automatically. "
              "If the automatic download is too slow, select manual configuration.")
        choice = input("\nPlease select the configuration mode: ")
        return choice
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
        print("Something Error。")

def auto_download():
    if not system_language:
        print("\n本程序将自动下载配置所需文件。\n")
        if os.path.exists(OCR_PATH):
            print("tesseract-ocr引擎已安装。")
        else:
            try:
                # 尝试执行'git --version'命令
                os.environ['PATH'] += os.pathsep + 'C:\\Program Files\\Git\\cmd'
                subprocess.check_output('git --version', stderr=subprocess.DEVNULL, shell=True)
                print("Git无需配置。")
            except subprocess.CalledProcessError:
                print("未检测到GIT，下载GIT中...请稍后\n")
                download_file(
                    'https://registry.npmmirror.com/-/binary/git-for-windows/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe',
                    'Git-2.42.0.2-64-bit.exe')
                print("\nGIT下载完成，等待安装…")
                cmd = GIT_PATH + ' /sp- /silent /norestart'
                subprocess.run(cmd)
                if os.path.exists(GIT_PATH):
                    os.remove(GIT_PATH)
            print("\n正在配置OCR引擎...\n")
            os.environ['PATH'] = r'C:\Program Files\Git\cmd' + ';' + os.environ['PATH']
            subprocess.check_output(
                ['git', 'clone', '--depth', '1', 'https://gitee.com/kioley/tesseract-ocr.git', 'tesseract-ocr'])
        win32api.MessageBox(0, "初始化完成。", "提示", win32con.MB_OK | win32con.MB_ICONINFORMATION)  ##########
        sys.exit()
    elif system_language:
        print("\nThis program will automatically download the required configuration files.\n")
        if os.path.exists(OCR_PATH):
            print("tesseract-ocr is installed.")
        else:
            try:
                # 尝试执行'git --version'命令
                os.environ['PATH'] += os.pathsep + 'C:\\Program Files\\Git\\cmd'
                subprocess.check_output('git --version', stderr=subprocess.DEVNULL, shell=True)
                print("GIT does not require configuration.")
            except subprocess.CalledProcessError:
                print("No GIT detected, download GIT... Please wait\n")
                download_file(
                    'https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe',
                    'Git-2.42.0.2-64-bit.exe')
                print("\nGIT download complete, waiting for installation...")
                cmd = GIT_PATH + ' /sp- /silent /norestart'
                subprocess.run(cmd)
                if os.path.exists(GIT_PATH):
                    os.remove(GIT_PATH)
            print("\nConfiguring the OCR engine...\n")
            os.environ['PATH'] = r'C:\Program Files\Git\cmd' + ';' + os.environ['PATH']
            subprocess.check_output(
                ['git', 'clone', '--depth', '1', 'https://gitee.com/kioley/tesseract-ocr.git', 'tesseract-ocr'])
        win32api.MessageBox(0, "Initialization is complete.", "Tip", win32con.MB_OK | win32con.MB_ICONINFORMATION)
        sys.exit()

def manual_download():
    if not system_language:
        print("\n即将打开项目，请手动下载整个项目文件。")
        time.sleep(2)
        webbrowser.open("https://gitee.com/kioley/tesseract-ocr.git")
        input("\n按任意键退出...")
        sys.exit()
    elif system_language:
        print("\nAbout to open the project, please download the entire project file manually.")
        time.sleep(2)
        webbrowser.open("https://gitee.com/kioley/tesseract-ocr.git")
        input("\nPress any key to exit...")
        sys.exit()

def main():
    print("""
            ____  ____  ____       ___    ________ __    __________  ____  __
           / __ \/ __ )/ __ \     /   |  / ____/ //_/   /_  __/ __ \/ __ \/ /
          / / / / __  / / / /    / /| | / /_  / ,<       / / / / / / / / / /
         / /_/ / /_/ / /_/ /    / ___ |/ __/ / /| |     / / / /_/ / /_/ / /___
        /_____/_____/_____/____/_/  |_/_/   /_/ |_|____/_/  \____/\____/_____/
                         /_____/                 /_____/
        ========================================================================
        """)
    choice = start_menu()
    if choice == "1":
        auto_download()
    elif choice == "2":
        manual_download()

if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
    OCR_PATH = os.path.join(BASE_DIR, "tesseract-ocr")
    GIT_PATH = os.path.join(BASE_DIR, "Git-2.42.0.2-64-bit.exe")
    os.environ['NO_PROXY'] = 'registry.npmmirror.com'
    system_language = check_language()
    main()

# -*- mode: python ; coding: utf-8 -*-
import locale
import os
import sys
import subprocess
import shutil
import win32api
import win32con
import win32gui
import configparser

def check_language():
    system_language, _ = locale.getdefaultlocale()
    return system_language.startswith('en')

def delete():
    with open("del.bat", "w") as file:
        file.write("@echo off\n")
        file.write(f"rmdir /s /q \"update\"\n")
        file.write(f"rmdir /s /q \".git\"")
    subprocess.call('del.bat')
    os.remove('del.bat')


def update_cfg():
    # 读取源文件
    src_config = configparser.ConfigParser()
    src_config.read(CFG_PATH)

    # 读取目标文件
    dst_config = configparser.ConfigParser()
    dst_config.read(UCFG_PATH)

    # 遍历目标文件的所有键值对
    for section in dst_config.sections():
        for key, value in dst_config.items(section):
            # 如果键存在于源文件中，则用源文件中的值覆盖目标文件中的值
            if src_config.has_option(section, key):
                dst_config.set(section, key, src_config.get(section, key))

    # 将修改后的目标文件保存到磁盘
    with open(UCFG_PATH, 'w') as f:
        dst_config.write(f)


def get_update():
    # 克隆远程仓库到临时目录
    subprocess.check_output(['git', 'clone', '--depth', '1', 'https://gitee.com/kioley/update', 'update'])  # https://gitee.com/wkhistory/update

    # 获取当前目录
    current_dir = os.getcwd()

    # 获取更新目录中的所有文件和子目录
    update_files = set(os.listdir('update'))

    # 检查更新目录中是否存在cfg文件
    if os.path.exists(UCFG_PATH):
        update_cfg()

    # 删除当前目录下需要被替换的文件和子目录
    for filename in os.listdir(current_dir):
        if filename in update_files:
            file_path = os.path.join(current_dir, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

    # 将克隆的文件复制到当前目录
    for filename in update_files:
        shutil.move(os.path.join('update', filename), os.path.join(current_dir, filename))


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
    if os.path.exists(U_PATH) or os.path.exists(G_PATH):
        delete()
    if not system_language:
        try:
            # 尝试执行'git --version'命令
            os.environ['MY_GIT'] = 'C:\Program Files\Git\cmd'
            subprocess.check_output('git --version', stderr=subprocess.DEVNULL, shell=True)
            print("开始更新…\n")
        except subprocess.CalledProcessError:
            win32api.MessageBox(0, "未检测到GIT，请安装Git。", "提示", win32con.MB_OK | win32con.MB_ICONQUESTION)
            sys.exit()
        get_update()
        delete()
        win32api.MessageBox(win32gui.GetForegroundWindow(), "更新完成。", "提示", win32con.MB_OK | win32con.MB_ICONQUESTION)
        sys.exit()
    elif system_language:
        try:
            # 尝试执行'git --version'命令
            os.environ['MY_GIT'] = 'C:\Program Files\Git\cmd'
            subprocess.check_output('git --version', stderr=subprocess.DEVNULL, shell=True)
            print("Start updating...\n")
        except subprocess.CalledProcessError:
            win32api.MessageBox(0, "GIT is not detected, please install Git.", "Tip",
                                win32con.MB_OK | win32con.MB_ICONQUESTION)
            sys.exit()
        get_update()
        delete()
        win32api.MessageBox(win32gui.GetForegroundWindow(), "Update completed", "Tip",
                            win32con.MB_OK | win32con.MB_ICONQUESTION)
        sys.exit()

if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
    CFG_PATH = os.path.join(BASE_DIR, "cfg.cfg")
    U_PATH = os.path.join(BASE_DIR, "update")
    UCFG_PATH = os.path.join(U_PATH, "cfg.cfg")
    G_PATH = os.path.join(BASE_DIR, ".git")
    system_language = check_language()
    main()

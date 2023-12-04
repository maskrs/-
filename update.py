import os
import sys
import subprocess
import shutil
import win32api
import win32con
import win32gui


def delete():
    with open("del.bat", "w") as file:
        file.write("@echo off\n")
        file.write(f"rmdir /s /q \"update\"\n")
        file.write(f"rmdir /s /q \".git\"")
    subprocess.call('del.bat')
    os.remove('del.bat')

def get_update():
    # 克隆远程仓库到临时目录
    subprocess.check_output(['git', 'clone', 'https://gitee.com/kioley/dbd_-afk_-tool.git', 'update'])

    # 获取当前目录
    current_dir = os.getcwd()

    # 获取更新目录中的所有文件和子目录
    update_files = set(os.listdir('update'))

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

if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
    U_PATH = os.path.join(BASE_DIR, "update")
    G_PATH = os.path.join(BASE_DIR, ".git")
    if os.path.exists(U_PATH) or os.path.exists(G_PATH):
        delete()
    try:
        # 尝试执行'git --version'命令
        subprocess.check_output('git --version', stderr=subprocess.DEVNULL, shell=True)
        print("Git无需配置。")
        print(" ")
    except subprocess.CalledProcessError:
        win32api.MessageBox(0, "未检测到GIT，请安装Git。", "提示", win32con.MB_OK | win32con.MB_ICONQUESTION)
    get_update()
    delete()
    win32api.MessageBox(win32gui.GetForegroundWindow(), "更新完成。", "提示", win32con.MB_OK | win32con.MB_ICONQUESTION)

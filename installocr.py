import os
import sys
import win32api, win32con
import subprocess
import shutil
import requests

BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
check_path= os.path.join(BASE_DIR, "tesseract-ocr.exe")
OCR_PATH = os.path.join(BASE_DIR, "tesseract-ocr")
DOWN_PATH = os.path.join(BASE_DIR, "download")
GIT_PATH = os.path.join(BASE_DIR, "Git-2.42.0.2-64-bit.exe")
OLD_PATH = os.path.join(BASE_DIR, 'download\\tesseract-ocr.exe')
L_PATH = os.path.join(BASE_DIR, 'chi_sim.traineddata')
N_PATH = os.path.join(BASE_DIR, 'tesseract-ocr\\tessdata')
url = 'https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe'
print("请确保使用管理员权限运行本程序！！")
input("请按回车键继续...")
print(" ")
try:
        # 尝试执行'git --version'命令
        subprocess.check_output('git --version', shell=True)
        print("Git无需配置。")
        print(" ")
except subprocess.CalledProcessError:
    print("配置GIT中...请稍后")
    response = requests.get(url)
    with open(GIT_PATH, 'wb') as f:
        f.write(response.content)
    cmd = GIT_PATH + ' /sp- /silent /norestart'
    subprocess.run(cmd)
    os.environ['MY_GIT'] = 'C:\Program Files\Git\cmd'
    if os.path.exists(GIT_PATH):
        os.remove(GIT_PATH)
# 设置要下载的文件URL和存储路径
print("请确保目录下无 'download' 文件夹。")
print(" ")
input("请按回车键继续...")
print(" ")
if os.path.exists(check_path) == False:
    subprocess.check_output(['git', 'clone', 'https://gitee.com/kioley/test-git.git', DOWN_PATH])
    shutil.move(OLD_PATH, BASE_DIR)
    print("程序下载中...完成后会自动启动程序。")
    os.popen(check_path)
    input("请按回车键继续...")
elif os.path.exists(check_path):
    print("程序已存在。")
    print(" ")
    os.popen(check_path)
elif os.path.exists(OCR_PATH):
    print("tesseract-ocr引擎已安装。")
print("一路点'OK'，直到 安装目录选择")
print(" ")
print("路径安装到当前目录，复制下面路径即可：")
print(OCR_PATH)
print(" ")
input("请按回车键继续...")
shutil.move(L_PATH, N_PATH)
os.environ['MY_DIRECTORY'] = OCR_PATH
# 检查环境变量是否添加成功
if 'MY_DIRECTORY' in os.environ:
    print("初始化成功！")
    print(" ")
    input("按任意键退出。")

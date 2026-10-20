# -*- coding: utf-8 -*-
"""生成 exe 文件图标 icon.ico。

图形直接复用 logo.py，保证 exe 图标、托盘图标、窗口标题栏图标三处完全一致。
改了 logo.py 里的形状或配色后，重跑本脚本再重新打包即可。
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from PIL import Image
from PySide6.QtWidgets import QApplication

import logo

app = QApplication(sys.argv)

SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

png_path = os.path.join(ROOT, "icon_256.png")
logo.logo_pixmap(256).save(png_path)

img = Image.open(png_path).convert("RGBA")
ico_path = os.path.join(ROOT, "icon.ico")
img.save(ico_path, sizes=SIZES)

print("saved", ico_path)

# -*- coding: utf-8 -*-
"""应用图标：靛蓝底 + 白色消息卡片 + 未读圆点。

刻意不用绿色和对话气泡——微信的官方标识是「绿底 + 白色气泡」，
两者组合在一起容易被认为视觉近似。这里换成产品本身的形态（弹出一张卡片），
颜色也改用靛蓝，从颜色和图形两处同时避开。

托盘、窗口标题栏、exe 文件图标都用这里画的同一份图形，保证三处一致。
"""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap

BRAND = "#4C5BD4"      # 靛蓝，主色
CARD = "#FFFFFF"       # 卡片
LINE = "#D9DCF7"       # 卡片里的消息线
DOT = "#F2994A"        # 未读圆点


def draw_logo(p: QPainter, size: float) -> None:
    """在 (0,0)-(size,size) 区域内画出 logo，坐标全部按比例计算。"""
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setPen(Qt.NoPen)

    # 底色圆角方块
    p.setBrush(QColor(BRAND))
    r = size * 0.25
    p.drawRoundedRect(QRectF(0, 0, size, size), r, r)

    # 白色卡片。小尺寸要放大一点，否则缩下去只剩一个白点
    small = size < 32
    if small:
        cx, cy = size * 0.17, size * 0.20
        cw, ch = size * 0.66, size * 0.60
    else:
        cx, cy = size * 0.19, size * 0.24
        cw, ch = size * 0.62, size * 0.48
    cr = size * (0.11 if small else 0.094)
    p.setBrush(QColor(CARD))
    p.drawRoundedRect(QRectF(cx, cy, cw, ch), cr, cr)

    # 卡片内的消息线。尺寸太小时只画一条，否则会糊成一团
    p.setBrush(QColor(LINE))
    if small:
        lh = size * 0.09
        p.drawRoundedRect(
            QRectF(cx + cw * 0.16, cy + (ch - lh) / 2, cw * 0.52, lh), lh / 2, lh / 2
        )
    else:
        lx = size * 0.304
        lw, lh = size * 0.392, size * 0.056
        lr = lh / 2
        p.drawRoundedRect(QRectF(lx, size * 0.368, lw, lh), lr, lr)
        p.drawRoundedRect(QRectF(lx, size * 0.496, size * 0.245, lh), lr, lr)

    # 右上角未读圆点，带一圈白边把它和卡片分开。太小时不画，否则只是噪点
    if size >= 24:
        dr = size * (0.10 if small else 0.086)
        ring = max(1.0, size * 0.018)
        dot_cx = size * (0.76 if small else 0.80)
        dot_cy = size * (0.24 if small else 0.20)
        p.setBrush(QColor(CARD))
        p.drawEllipse(QRectF(dot_cx - dr - ring, dot_cy - dr - ring,
                             (dr + ring) * 2, (dr + ring) * 2))
        p.setBrush(QColor(DOT))
        p.drawEllipse(QRectF(dot_cx - dr, dot_cy - dr, dr * 2, dr * 2))


def logo_pixmap(size: int) -> QPixmap:
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    try:
        draw_logo(p, float(size))
    finally:
        p.end()
    return pm


def logo_icon() -> QIcon:
    """多尺寸 QIcon，Windows 标题栏取 16，托盘取 32/64，任务栏取大图。"""
    icon = QIcon()
    for s in (16, 20, 24, 32, 48, 64, 128, 256):
        icon.addPixmap(logo_pixmap(s))
    return icon

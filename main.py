# -*- coding: utf-8 -*-
"""微信消息悬浮提示 —— 程序入口。

微信隐藏在后台时来消息，屏幕角落浮出卡片显示「谁发的 + 说了什么」，
默认 3 秒淡出。支持可视化调参、系统托盘常驻。
"""
from __future__ import annotations

import sys
import time

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon

import config as cfgmod
import logo
import wechat
from settings_window import SettingsWindow
from toast import Toast, ToastManager
from watcher import WeChatMessage, WeChatWatcher

APP_TITLE = "微信消息提示"
SERVER_NAME = "WeChatToast.SingleInstance"


def make_tray_icon() -> QIcon:
    return logo.logo_icon()


class Bridge(QObject):
    """把后台线程的消息安全地送回 UI 线程。"""
    message = Signal(object)
    denied = Signal()


def ensure_single_instance() -> bool:
    """已有实例在跑时，通知它打开设置窗口并返回 False。"""
    try:
        from PySide6.QtNetwork import QLocalServer, QLocalSocket  # noqa: F401
    except Exception:
        return True

    sock = QLocalSocket()
    sock.connectToServer(SERVER_NAME)
    if sock.waitForConnected(300):
        sock.write(b"show-settings")
        sock.flush()
        sock.waitForBytesWritten(300)
        sock.disconnectFromServer()
        return False
    return True


def main() -> int:
    cfg = cfgmod.load()

    app = QApplication(sys.argv)
    app.setApplicationName(cfgmod.APP_NAME)
    app.setQuitOnLastWindowClosed(False)

    if not ensure_single_instance():
        return 0

    bridge = Bridge()
    state = {"paused": False}
    test_toasts: list[Toast] = []

    manager = ToastManager(cfg, app, on_open_wechat=wechat.open_wechat)
    settings = SettingsWindow(cfg)

    # ---------- 托盘 ----------
    tray = QSystemTrayIcon(make_tray_icon(), app)
    tray.setToolTip(f"{APP_TITLE} · 运行中")

    menu = QMenu()
    act_open = QAction("打开微信", menu)
    act_open.triggered.connect(wechat.open_wechat)
    menu.addAction(act_open)

    act_settings = QAction("设置…", menu)
    act_settings.triggered.connect(lambda: settings.show_window(cfgmod.load()))
    menu.addAction(act_settings)

    menu.addSeparator()

    act_pause = QAction("暂停监听", menu)
    menu.addAction(act_pause)

    menu.addSeparator()
    act_quit = QAction("退出", menu)
    menu.addAction(act_quit)

    tray.setContextMenu(menu)
    tray.show()

    # ---------- 事件 ----------
    def toggle_pause():
        state["paused"] = not state["paused"]
        act_pause.setText("继续监听" if state["paused"] else "暂停监听")
        tray.setToolTip(f"{APP_TITLE} · {'已暂停' if state['paused'] else '运行中'}")

    act_pause.triggered.connect(toggle_pause)

    def quit_app():
        watcher.stop()
        app.quit()

    act_quit.triggered.connect(quit_app)

    def on_tray_activated(reason):
        if reason == QSystemTrayIcon.Trigger:          # 单击
            wechat.open_wechat()
        elif reason == QSystemTrayIcon.DoubleClick:    # 双击
            settings.show_window(cfgmod.load())

    tray.activated.connect(on_tray_activated)

    # ---------- 配置应用 ----------
    def apply_cfg(new_cfg: dict):
        cfg.clear()
        cfg.update(new_cfg)
        manager.cfg = cfg

    settings.applied.connect(apply_cfg)

    def show_test(test_cfg: dict):
        msg = WeChatMessage(
            "产品研发群", "张伟",
            "这是一条测试消息，看看现在的效果是否合适", time.time(), 0,
        )
        t = Toast(msg, test_cfg, on_open_wechat=wechat.open_wechat)
        t.closed.connect(lambda x: test_toasts.remove(x) if x in test_toasts else None)
        test_toasts.append(t)
        t.appear()

    settings.test_requested.connect(show_test)

    # ---------- 消息监听 ----------
    def on_denied():
        QMessageBox.warning(
            settings, "无法读取系统通知",
            "需要允许本程序访问系统通知。\n\n"
            "请打开：设置 → 隐私和安全性 → 通知 → 允许应用访问通知；\n"
            "并确认微信「设置 → 通用设置 → 新消息通知」已开启。",
        )

    bridge.message.connect(lambda m: None if state["paused"] else manager.push(m))
    bridge.denied.connect(on_denied)

    def on_status(status: str):
        print(f"[status] {status}")
        if status == "access_denied":
            bridge.denied.emit()

    watcher = WeChatWatcher(
        on_message=bridge.message.emit,
        on_status=on_status,
        poll_interval=cfg.get("poll_interval_ms", 1000) / 1000.0,
        ignore_sources=cfg.get("ignore_sources", []),
    )
    watcher.start()

    # ---------- 单实例服务端 ----------
    server = None
    try:
        from PySide6.QtNetwork import QLocalServer

        QLocalServer.removeServer(SERVER_NAME)
        server = QLocalServer(app)
        server.listen(SERVER_NAME)

        def on_new_connection():
            conn = server.nextPendingConnection()
            if conn is not None:
                conn.disconnected.connect(conn.deleteLater)
            settings.show_window(cfgmod.load())

        server.newConnection.connect(on_new_connection)
    except Exception as e:
        print(f"[warn] 单实例服务启动失败: {e}")

    print(f"{APP_TITLE}已启动。右键托盘图标可进入设置或退出。")
    code = app.exec()
    watcher.stop()
    if server is not None:
        server.close()
    return code


if __name__ == "__main__":
    sys.exit(main())

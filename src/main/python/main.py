#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fbs_runtime.application_context.PyQt5 import ApplicationContext
from fbs_runtime.application_context import cached_property

from PyQt5.QtWidgets import (
    QApplication,
    QMessageBox,
    QSystemTrayIcon,
    QMenu,
    QAction,
    QStyle,
    QWidgetAction,
    QLabel,
    QSizePolicy,
)
from PyQt5.QtCore import pyqtSlot, QTimer, QPoint, Qt
from PyQt5.QtGui import QCursor, QIcon
import darkdetect
import sys

from cutoff import CutOff, ELECTRICITY, CUTOFF

__doc__ = """Ishtirak time"""


class AppContext(ApplicationContext):
    def run(self):
        my_tray = TrayIcon(self)
        my_tray.show()

        return self.app.exec_()

    @cached_property
    def status_icons(self):
        return {
            "electricity-light": QIcon(
                self.get_resource("images/electricity-light.png")
            ),
            "electricity-dark": QIcon(self.get_resource("images/electricity-dark.png")),
            "cutoff-light": QIcon(self.get_resource("images/cutoff-light.png")),
            "cutoff-dark": QIcon(self.get_resource("images/cutoff-dark.png")),
        }


class TrayIcon(QSystemTrayIcon):
    def __init__(self, ctx, parent=None):
        super(TrayIcon, self).__init__(parent)
        self.activated.connect(self.icon_activated_slot)
        self.messageClicked.connect(self.message_clicked_slot)
        self.ctx = ctx
        # self.setIcon(QApplication.style().standardIcon(QStyle.SP_DriveDVDIcon))

        self.cutoff = CutOff(cutoff_range_index=1)
        self.last_status = self.cutoff.status()
        self.last_theme = darkdetect.theme().lower()
        self.updateIcon()
        self._timer = QTimer()
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self.recurring_timer)
        self._timer.start()
        self.create_menu()

    def create_menu(self):
        _menu = QMenu()

        label = QLabel(self.last_status)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.last_theme == "dark":
            label.setStyleSheet("QLabel {color: white;}")

        action = QWidgetAction(label)
        action.setDefaultWidget(label)
        _menu.addAction(action)

        _menu.addSeparator()

        quiteA = QAction("Exit", _menu)
        quiteA.triggered.connect(self.exit_slot)
        _menu.addAction(quiteA)

        self._menu = _menu
        self.setContextMenu(self._menu)

    @pyqtSlot()
    def exit_slot(self):
        print("exit_slot")
        reply = QMessageBox.question(
            None, "Message", "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._timer.stop()
            self._menu.deleteLater()
            self.hide()
            QApplication.instance().exit(0)

    @pyqtSlot()
    def recurring_timer(self):
        status = self.cutoff.status()
        theme = darkdetect.theme().lower()

        print(f"status: {status}")

        if theme != self.last_theme:
            self.last_theme = theme
            self.updateIcon()

        if status != self.last_status:
            self.last_status = status
            msg = f"It's {status} now"
            self.updateIcon()

            self.setToolTip(msg)
            if self.supportsMessages():
                self.showMessage("Electricity", msg, QSystemTrayIcon.Information, 1000)

    def updateIcon(self):
        status = self.last_status

        if status == ELECTRICITY:
            icon = f"electricity-{self.last_theme}"
        else:
            icon = f"cutoff-{self.last_theme}"

        self.setIcon(self.ctx.status_icons[icon])

    def icon_activated_slot(self, reason):
        print("icon_activated_slot")
        if reason == QSystemTrayIcon.Unknown:
            print("QSystemTrayIcon.Unknown")
            pass
        elif reason == QSystemTrayIcon.Context:
            print("QSystemTrayIcon.Context")
            pass
        elif reason == QSystemTrayIcon.DoubleClick:
            print("QSystemTrayIcon.DoubleClick")
            pass
        elif reason == QSystemTrayIcon.Trigger:
            print("QSystemTrayIcon.Trigger")
            pass
        elif reason == QSystemTrayIcon.MiddleClick:
            print("QSystemTrayIcon.MiddleClick")
            current_mouse_cursor = QCursor.pos() - QPoint(50, 50)
            menu = self.contextMenu()
            menu.popup(current_mouse_cursor)

    @pyqtSlot()
    def message_clicked_slot(self):
        print("message was clicked")

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "Message", "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._timer.stop()
            self._menu.deleteLater()
            self.hide()
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    appctxt = AppContext()  # 4. Instantiate the subclass
    exit_code = appctxt.run()  # 5. Invoke run()
    sys.exit(exit_code)

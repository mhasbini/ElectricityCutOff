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
    QWidgetAction,
    QLabel,
    QSizePolicy,
)
from PyQt5.QtCore import pyqtSlot, QTimer, QPoint, Qt, QSettings
from PyQt5.QtGui import QCursor, QIcon
import darkdetect
import sys
import os

from cutoff import CutOff, ELECTRICITY, CUTOFF


class AppContext(ApplicationContext):
    def run(self):
        my_tray = TrayIcon(self)
        my_tray.show()

        return self.app.exec_()

    def config(self):
        return self.get_resource("config.ini")

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

        self.config = self.loadConfig()
        self.cutoff = CutOff(
            cutoff_range_index=int(self.config.value("range/cutoff_range_index"))
        )
        self.last_status, self.last_timeleft = self.cutoff.status()
        self.last_theme = darkdetect.theme().lower()
        self.updateIcon()
        self._timer = QTimer()
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self.recurring_timer)
        self._timer.start()
        self.create_menu()
        self.showNotification()

    def loadConfig(self):
        config = QSettings(self.ctx.config(), QSettings.IniFormat)
        return config

    def updateConfig(self, key, value):
        self.config.setValue(key, value)
        self.config.sync()
        self.reloadCutOff()

    def reloadCutOff(self):
        self.cutoff = CutOff(
            cutoff_range_index=int(self.config.value("range/cutoff_range_index"))
        )

    def create_menu(self):
        _menu = QMenu()

        self.label = QLabel(self.formatStatus())
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("status_text")
        if self.last_theme == "dark":
            self.label.setStyleSheet("QLabel {color: white;}")

        label_action = QWidgetAction(self.label)
        label_action.setDefaultWidget(self.label)
        _menu.addAction(label_action)

        _menu.addSeparator()

        _submenu = QMenu(_menu)
        _submenu.setTitle("Preferences")

        invert = QAction("⇆ Invert", _submenu)
        invert.triggered.connect(self.invert)
        invert.setShortcut("Ctrl+I")
        _submenu.addAction(invert)

        self.launchAtLogin = QAction("Launch At Login", _submenu)
        self.launchAtLogin.setCheckable(True)

        config_value = self.config.value("config/start_at_login")
        if config_value:
            config_value = True
        else:
            config_value = False

        self.launchAtLogin.setChecked(config_value)
        self.launchAtLogin.triggered.connect(self.launchAtLoginAction)
        _submenu.addAction(self.launchAtLogin)

        _menu.addMenu(_submenu)

        quiteA = QAction("Exit", _menu)
        quiteA.triggered.connect(self.exit_slot)
        _menu.addAction(quiteA)

        self._menu = _menu
        self.setContextMenu(self._menu)

    def plist_file_path(self):
        return os.path.expanduser('~/Library/LaunchAgents/ElectricityCutOff.plist')

    def plist_file_contents(self):
        return f"""
      <?xml version="1.0" encoding="UTF-8"?>
      <plist version="1.0">
        <dict>
          <key>RunAtLoad</key>
          <true />
          <key>Label</key>
          <string>ElectricityCutOff</string>
          <key>ProgramArguments</key>
          <array>
            <string>/Applications/ElectricityCutOff.app/Contents//MacOS/ElectricityCutOff</string>
          </array>
          <key>KeepAlive</key>
          <false/>
          <key>RunAtLoad</key>
          <true/>
          </dict>
      </plist>
      """

    @pyqtSlot()
    def launchAtLoginAction(self):
        self.updateConfig("config/start_at_login", self.launchAtLogin.isChecked())
        if self.launchAtLogin.isChecked():
            with open(self.plist_file_path(), 'w+') as file:
                file.write(self.plist_file_contents())
        elif os.path.exists(self.plist_file_path()):
            os.remove(self.plist_file_path())


    @pyqtSlot()
    def exit_slot(self):
        reply = QMessageBox.question(
            None, "Message", "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._timer.stop()
            self._menu.deleteLater()
            self.hide()
            QApplication.instance().exit(0)

    @pyqtSlot()
    def invert(self):
        self.cutoff.invert()
        self.last_status, self.last_timeleft = self.cutoff.status()
        self.updateStatus(showNotification=False)
        self.updateConfig("range/cutoff_range_index", self.cutoff.cutoff_range_index)

    @pyqtSlot()
    def recurring_timer(self):
        status, time_left = self.cutoff.status()
        theme = darkdetect.theme().lower()

        self.updateStatusText(time_left)

        if theme != self.last_theme:
            self.last_theme = theme
            self.updateIcon()
            self.updateText()

        if status != self.last_status:
            self.last_status = status
            self.updateStatus()

    def updateStatus(self, showNotification=True):
        self.cutoff.update_range()
        self.updateIcon()
        if showNotification:
            self.showNotification()
        self.updateStatusText()

    def updateStatusText(self, timeleft=None):
        if not timeleft:
            timeleft = self.last_timeleft

        self.label.setText(self.formatStatus(timeleft))

    def formatStatus(self, timeleft=""):
      if timeleft:
          return f"({timeleft}-) {self.last_status}"
      else:
          return f"{self.last_status}"

    def updateText(self):
        if self.last_theme == "light":
            self.label.setStyleSheet("QLabel {color: black;}")
        else:
            self.label.setStyleSheet("QLabel {color: white;}")

    def showNotification(self):
        msg = f"It's {self.last_status} now"

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
        if reason == QSystemTrayIcon.Unknown:
            pass
        elif reason == QSystemTrayIcon.Context:
            pass
        elif reason == QSystemTrayIcon.DoubleClick:
            pass
        elif reason == QSystemTrayIcon.Trigger:
            pass
        elif reason == QSystemTrayIcon.MiddleClick:
            current_mouse_cursor = QCursor.pos() - QPoint(50, 50)
            menu = self.contextMenu()
            menu.popup(current_mouse_cursor)

    @pyqtSlot()
    def message_clicked_slot(self):
        pass

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
    appctxt = AppContext()

    exit_code = appctxt.run()
    sys.exit(exit_code)

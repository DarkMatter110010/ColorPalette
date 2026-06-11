import sys
from PyQt6.QtWidgets import (QWidget, QLabel, QLineEdit, QApplication, QVBoxLayout,
                             QHBoxLayout, QTabWidget, QFrame, QSlider, QPushButton)
from PyQt6.QtGui import QColor, QIntValidator, QFont, QClipboard
from PyQt6.QtCore import Qt, QTimer

# ===== 自定义控件 =====

class NumberLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaxLength(3)
        self.setValidator(QIntValidator(0, 255, self))
        self.setFont(QFont("Arial", 12))

    def wheelEvent(self, event):
        text = self.text()
        current = int(text) if text.isdigit() else 0
        delta = event.angleDelta().y()
        new_value = current + (1 if delta > 0 else -1)
        new_value = max(0, min(255, new_value))
        self.setText(str(new_value))
        event.accept()

class HexLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaxLength(7)
        self.setFont(QFont("Courier New", 12))

    def wheelEvent(self, event):
        text = self.text().strip()
        if not text:
            current_int = 0
        else:
            clean = text.lstrip('#')
            if len(clean) != 6 or not all(c in '0123456789ABCDEFabcdef' for c in clean):
                current_int = 0
            else:
                try:
                    current_int = int(clean, 16)
                except ValueError:
                    current_int = 0
        delta = event.angleDelta().y()
        step = 1 if delta > 0 else -1
        new_int = max(0, min(0xFFFFFF, current_int + step))
        self.setText(f"#{new_int:06X}")
        event.accept()

# ===== 主窗口 =====

class ColorPickerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setFont(QFont("Arial", 11))
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Arial", 12))
        self.rgb_tab = QWidget()
        self.hex_tab = QWidget()
        self.hsv_tab = QWidget()

        self.tabs.addTab(self.rgb_tab, "RGB")
        self.tabs.addTab(self.hex_tab, "HEX")
        self.tabs.addTab(self.hsv_tab, "HSV")

        # === RGB Tab with Sliders ===
        rgb_layout = QVBoxLayout()
        rgb_layout.setSpacing(10)

        # 红色
        rgb_layout.addWidget(QLabel('红色 (0–255):'))
        self.redInput = NumberLineEdit()
        rgb_layout.addWidget(self.redInput)
        self.redSlider = QSlider(Qt.Orientation.Horizontal)
        self.redSlider.setRange(0, 255)
        rgb_layout.addWidget(self.redSlider)

        # 绿色
        rgb_layout.addWidget(QLabel('绿色 (0–255):'))
        self.greenInput = NumberLineEdit()
        rgb_layout.addWidget(self.greenInput)
        self.greenSlider = QSlider(Qt.Orientation.Horizontal)
        self.greenSlider.setRange(0, 255)
        rgb_layout.addWidget(self.greenSlider)

        # 蓝色
        rgb_layout.addWidget(QLabel('蓝色 (0–255):'))
        self.blueInput = NumberLineEdit()
        rgb_layout.addWidget(self.blueInput)
        self.blueSlider = QSlider(Qt.Orientation.Horizontal)
        self.blueSlider.setRange(0, 255)
        rgb_layout.addWidget(self.blueSlider)

        self.rgb_tab.setLayout(rgb_layout)

        # === HEX Tab with Copy Button ===
        hex_layout = QVBoxLayout()
        hex_layout.setSpacing(10)
        hex_layout.addWidget(QLabel('十六进制颜色 (例如 #FF5733):'))
        self.hexInput = HexLineEdit()
        hex_layout.addWidget(self.hexInput)

        self.copyButton = QPushButton("📋 复制十六进制到剪贴板")
        self.copyButton.clicked.connect(self.copyHexToClipboard)
        hex_layout.addWidget(self.copyButton)

        self.hex_tab.setLayout(hex_layout)

        # === HSV Tab ===
        hsv_layout = QVBoxLayout()
        hsv_layout.setSpacing(10)

        # 色相 (0-359)
        hsv_layout.addWidget(QLabel('色相 (0–359):'))
        self.hueInput = NumberLineEdit()
        self.hueInput.setValidator(QIntValidator(0, 359, self))
        hsv_layout.addWidget(self.hueInput)
        self.hueSlider = QSlider(Qt.Orientation.Horizontal)
        self.hueSlider.setRange(0, 359)
        hsv_layout.addWidget(self.hueSlider)

        # 饱和度 (0-255)
        hsv_layout.addWidget(QLabel('饱和度 (0–255):'))
        self.satInput = NumberLineEdit()
        hsv_layout.addWidget(self.satInput)
        self.satSlider = QSlider(Qt.Orientation.Horizontal)
        self.satSlider.setRange(0, 255)
        hsv_layout.addWidget(self.satSlider)

        # 明度 (0-255)
        hsv_layout.addWidget(QLabel('明度 (0–255):'))
        self.valInput = NumberLineEdit()
        hsv_layout.addWidget(self.valInput)
        self.valSlider = QSlider(Qt.Orientation.Horizontal)
        self.valSlider.setRange(0, 255)
        hsv_layout.addWidget(self.valSlider)

        self.hsv_tab.setLayout(hsv_layout)

        # === 公共颜色显示区 ===
        self.colorDisplay = QFrame()
        self.colorDisplay.setMinimumHeight(180)
        self.colorDisplay.setStyleSheet("background-color: black; border: 2px solid #666;")

        # 布局组装
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(self.colorDisplay)

        self.setLayout(main_layout)

        # ========== 连接信号 ==========
        self._updating = False

        # RGB
        self.redInput.textChanged.connect(self.onRgbChanged)
        self.greenInput.textChanged.connect(self.onRgbChanged)
        self.blueInput.textChanged.connect(self.onRgbChanged)
        self.redSlider.valueChanged.connect(self.onRedSlider)
        self.greenSlider.valueChanged.connect(self.onGreenSlider)
        self.blueSlider.valueChanged.connect(self.onBlueSlider)

        # HEX
        self.hexInput.textChanged.connect(self.onHexChanged)

        # HSV
        self.hueInput.textChanged.connect(self.onHsvChanged)
        self.satInput.textChanged.connect(self.onHsvChanged)
        self.valInput.textChanged.connect(self.onHsvChanged)
        self.hueSlider.valueChanged.connect(self.onHueSlider)
        self.satSlider.valueChanged.connect(self.onSatSlider)
        self.valSlider.valueChanged.connect(self.onValSlider)

        # 初始化默认颜色
        self.setColor(QColor(100, 150, 255))

        self.setWindowTitle('🎨 高级颜色选择器')
        self.setFixedSize(500, 700)
        self.show()

    # ===== RGB 相关 =====
    def onRgbChanged(self):
        if self._updating:
            return
        try:
            r = int(self.redInput.text()) if self.redInput.text() else 0
            g = int(self.greenInput.text()) if self.greenInput.text() else 0
            b = int(self.blueInput.text()) if self.blueInput.text() else 0
            r, g, b = [max(0, min(255, x)) for x in (r, g, b)]
            color = QColor(r, g, b)
            self._updating = True
            self.updateAllFromColor(color)
            self._updating = False
        except Exception:
            pass

    def onRedSlider(self, value):
        if not self._updating:
            self._updating = True
            self.redInput.setText(str(value))
            self._updating = False
            self.onRgbChanged()

    def onGreenSlider(self, value):
        if not self._updating:
            self._updating = True
            self.greenInput.setText(str(value))
            self._updating = False
            self.onRgbChanged()

    def onBlueSlider(self, value):
        if not self._updating:
            self._updating = True
            self.blueInput.setText(str(value))
            self._updating = False
            self.onRgbChanged()

    # ===== HEX 相关 =====
    def onHexChanged(self):
        if self._updating:
            return
        text = self.hexInput.text().strip()
        if not text:
            return
        if not text.startswith('#'):
            text = '#' + text
        if len(text) != 7:
            return
        try:
            color = QColor(text)
            if color.isValid():
                self._updating = True
                self.updateAllFromColor(color)
                self._updating = False
        except Exception:
            pass

    def copyHexToClipboard(self):
        hex_text = self.hexInput.text().strip()
        if not hex_text.startswith('#'):
            hex_text = '#' + hex_text
        if len(hex_text) == 7:
            clipboard = QApplication.clipboard()
            clipboard.setText(hex_text.upper())
            original = self.copyButton.text()
            self.copyButton.setText("✅ 已复制！")
            self.copyButton.setEnabled(False)
            QTimer.singleShot(1000, lambda: (
                self.copyButton.setText(original),
                self.copyButton.setEnabled(True)
            ))

    # ===== HSV 相关 =====
    def onHsvChanged(self):
        if self._updating:
            return
        try:
            h = int(self.hueInput.text()) if self.hueInput.text() else 0
            s = int(self.satInput.text()) if self.satInput.text() else 0
            v = int(self.valInput.text()) if self.valInput.text() else 0
            h = max(0, min(359, h))
            s = max(0, min(255, s))
            v = max(0, min(255, v))
            color = QColor.fromHsv(h, s, v)
            self._updating = True
            self.updateAllFromColor(color)
            self._updating = False
        except Exception:
            pass

    def onHueSlider(self, value):
        if not self._updating:
            self._updating = True
            self.hueInput.setText(str(value))
            self._updating = False
            self.onHsvChanged()

    def onSatSlider(self, value):
        if not self._updating:
            self._updating = True
            self.satInput.setText(str(value))
            self._updating = False
            self.onHsvChanged()

    def onValSlider(self, value):
        if not self._updating:
            self._updating = True
            self.valInput.setText(str(value))
            self._updating = False
            self.onHsvChanged()

    # ===== 统一更新所有控件 =====
    def updateAllFromColor(self, color: QColor):
        # RGB
        self.redInput.setText(str(color.red()))
        self.greenInput.setText(str(color.green()))
        self.blueInput.setText(str(color.blue()))
        self.redSlider.setValue(color.red())
        self.greenSlider.setValue(color.green())
        self.blueSlider.setValue(color.blue())

        # HEX
        self.hexInput.setText(color.name().upper())

        # HSV
        h, s, v, _ = color.getHsv()
        if h == -1:
            h = 0  # QColor 返回 -1 表示未定义（如纯灰），设为 0
        self.hueInput.setText(str(h))
        self.satInput.setText(str(s))
        self.valInput.setText(str(v))
        self.hueSlider.setValue(h)
        self.satSlider.setValue(s)
        self.valSlider.setValue(v)

        # 显示
        self.updateColorDisplay(color)

    def setColor(self, color: QColor):
        self._updating = True
        self.updateAllFromColor(color)
        self._updating = False

    def updateColorDisplay(self, color: QColor):
        self.colorDisplay.setStyleSheet(f"background-color: {color.name()}; border: 2px solid #555;")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ColorPickerApp()
    sys.exit(app.exec())

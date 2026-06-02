"""Minimal PyQt6 test to diagnose admin crash."""
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtCore import Qt

app = QApplication(sys.argv)
w = QMainWindow()
w.setWindowTitle("Test Window")
w.resize(400, 300)
label = QLabel("Hello World - Test OK", w)
label.setAlignment(Qt.AlignmentFlag.AlignCenter)
w.setCentralWidget(label)
w.show()
sys.exit(app.exec())

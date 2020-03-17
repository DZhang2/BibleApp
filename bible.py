from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal
import requests
import sys
import pyttsx3
import re
from scrapedBible import *
from esvBible import *

# export GOOGLE_APPLICATION_CREDENTIALS="/Users/davidzhang/Desktop/Python/Bible/MyFirstProject.json"    

class Main(QWidget):
    switch_window1 = pyqtSignal()
    switch_window2 = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Bible')
        layout = QVBoxLayout()
        bible1 = QPushButton('ESV Bible')
        bible2 = QPushButton('Scraped Bible')
        bible1.clicked.connect(lambda: self.switch_window1.emit())
        bible2.clicked.connect(lambda: self.switch_window2.emit())
        layout.addWidget(bible1)
        layout.addWidget(bible2)
        self.setLayout(layout)

class Controller:
    def __init__(self):
        pass
    
    def show_main(self):
        main_screen = Main()
        main_screen.switch_window1.connect(self.show_ESV)
        main_screen.switch_window2.connect(self.show_scraped)
        main_screen.show()

    def show_ESV(self):
        esv_bible = EsvBible()
        esv_bible.show()

    def show_scraped(self):
        scraped = ScrapedBible()
        scraped.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = Controller()
    controller.show_main()
    sys.exit(app.exec_())

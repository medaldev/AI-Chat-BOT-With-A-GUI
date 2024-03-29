# coding: utf-8
import sys
import time
import json
import threading
# import pyttsx3
import numpy as np
from pathlib import Path
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import QCursor, QIcon, QMovie
from sklearn.preprocessing import LabelEncoder
import random 
import pickle
import requests

with open("intents/intents.json") as file:
    data = json.load(file)

with open("settings/json_file_chooser.txt", "r") as file:
    file_name = file.read()
    file.close()
with open(f"settings/{file_name}", "r") as j:
    json_data = json.loads(j.read())
    j.close()


max_len = 20

state = 0

color1 = json_data['color1']
color2 = json_data['color2']
color3 = json_data['color3']
color4 = json_data['color4']
color5 = json_data['color5']
color6 = json_data['color6']
color7 = json_data['color7']
color8 = json_data['color8']
color9 = json_data['color9']
color10 = json_data['color10']
color11 = json_data['color11']
color12 = json_data['color12']
color13 = json_data['color13']
color14 = json_data['color14']
sp1 = json_data['sp1']
sp2 = json_data['sp2']
opc = json_data['opc']

# def talk(text):
    # engine = pyttsx3.init()
    # # voice = engine.getProperty('voices')
    # # engine.setProperty('voice', voice[2].id)
    # engine.setProperty('rate', 150)
    # engine.say(text)
    # engine.runAndWait()



class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.sw = None
        self.hw = None

        # Window size
        self.WIDTH = 1000
        self.HEIGHT = 800
        self.resize(self.WIDTH, self.HEIGHT)

        # Stylesheet
        self.setStyleSheet(f'''
        QPushButton{{
            color: {color8};
            font-size: 20px;
            font-weight: bold;
            font-family: Georgia;
            background: {color9};
            border-radius: 20px;
        }}
        QPushButton:hover{{
            color: {color10};
            background: {color11};
        }}
        QPushButton::pressed{{
            background: {color12};
        }}
        QLineEdit{{
            color: {color13};
            font-weight: bold;
            font-family: Georgia;
            font-size: 20px;
            background: transparent;
            border: 5px solid {color14};
            border-radius: 20px;
        }}
        ''')

        # Widget
        self.centralwidget = QWidget(self)
        self.centralwidget.resize(self.WIDTH, self.HEIGHT)



        self.close_button = QPushButton('x', self)
        self.close_button.setStatusTip("   Close")
        self.close_button.clicked.connect(self.close_ap)
        self.close_button.setGeometry(950, 10, 40, 40)

        self.mini_button = QPushButton('_' ,self)
        self.mini_button.clicked.connect(self.showMinimized)
        self.mini_button.setStatusTip("   Minimize")
        self.mini_button.setGeometry(905, 10, 40, 40)


        self.msg_list = QListWidget(self)
        self.msg_list.setStyleSheet(
        f"""
        border: None;
        background-color: {color2};
        color: {color1};
        font-size: 20px;
        font-family: Georgia;
        QListWidget::item{{
            border: None;
        }}
        """
        )
        self.msg_list.setGeometry(250, 100, 500, 500)

        scroll_bar = QScrollBar(self)
        scroll_bar.setStyleSheet(
        f"""
        QScrollBar:vertical{{
            background-color: {color1};
            width: 2px;
            border: 1px transparent;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical{{
            background-color: blue;
            min-height: 5px;
            border-radius: 4px;
        }}
        QScrollBar::sub-line:vertical{{
            subcontrol-position: top;
            subcontrol-origin: margin;
        }}
        
        """
        )
        self.msg_list.setVerticalScrollBar(scroll_bar)
        self.msg_list.setWordWrap(True)

        # text area
        self.text_area = QLineEdit(self)
        # self.text_area.setGeometry(200, 100, 300, 50)
        self.text_area.returnPressed.connect(self.navigate_url)
        self.text_area.setGeometry(250, 700, 500, 55)

        # Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_menu)

        # Initial
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(opc)

        self.centralwidget.setStyleSheet(
            f"""
            background:{sp2};
            border: 5px solid blue;
            border-top-left-radius:30px;
            border-bottom-left-radius:30px;
            border-top-right-radius:30px;
            border-bottom-right-radius:30px;
            """
        )
        self.add_msg("Llama: Welcome!")
        self.conversation_id = ""


    def add_msg(self, msg):
        self.msg_list.addItem(QListWidgetItem(msg))
        self.msg_list.scrollToBottom()

    def close_ap(self):
        sys.exit(0)

    def right_menu(self, pos):
        menu = QMenu()
        exit_option = menu.addAction('Exit')
        exit_option.triggered.connect(lambda: exit(0))
        menu.exec_(self.mapToGlobal(pos))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moveFlag = True
            self.movePosition = event.globalPos() - self.pos()
            self.setCursor(QCursor(Qt.OpenHandCursor))
            event.accept()

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.moveFlag:
            self.move(event.globalPos() - self.movePosition)
            event.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.moveFlag = False
        self.setCursor(Qt.CrossCursor)



    def update_text_area(self):
        self.text_area.setText("")
        self.text_area.setCursorPosition(0)

    def navigate_url(self):
        self.add_msg("")
        inp = self.text_area.text()
        self.add_msg("You: " + inp)
        if inp.lower() == 'quit' or inp.lower() == 'exit':
            self.close_ap()
        self.update_text_area()
        result = send(inp, self.conversation_id)
        self.conversation_id = result[1] if result[1] else self.conversation_id
        self.add_msg("Llama: " + result[0])
        self.update_text_area()

def send(message, conversation_id=""):
    answer = requests.get("http://127.0.0.1:5000/chat", json={
        "message": {
            "role": "user",
            "content": message
        },
        "conversation_id": conversation_id
    })
    answer = answer.json()
    print(answer)
    if answer["status"] == "ok":
        return answer["content"], answer['conversation_id']
    return "Увы, произошла ошибка :(", conversation_id

if __name__ == '__main__':
    app = QApplication([])
    with open("settings/json_file_chooser.txt", "w") as file:
        file.write("black.json")
        file.close()
    window = MainWindow()
    window.show()


    sys.exit(app.exec_())

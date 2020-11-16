import sys
import csv
import sqlite3
import random
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QListWidgetItem
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap, QFont
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')

USER_NAME = ''
EMAIL = ''
USERID = 1
IMAGE = 'no_avatar.png'
CON = sqlite3.connect('App.db')


class MyWidget(QMainWindow):
    def __init__(self, rating):
        global USER_NAME, IMAGE, CON
        super().__init__()

    def chat(self):
        self.chat_window = Chat()
        self.chat_window.show()
        self.hide()

    def acc_func(self):
        self.acc_window = Account()
        self.acc_window.show()
        self.hide()


class Account(QMainWindow):
    def __init__(self):
        global USER_NAME, EMAIL, IMAGE
        super().__init__()
        uic.loadUi(r'account.ui', self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.avatar.setIcon(QIcon(IMAGE))
        self.avatar.clicked.connect(self.change)
        self.avatar.setIconSize(QSize(100, 100))
        self.avatar.setToolTip('Изменение аккаунта')
        self.setWindowIcon(QIcon(r'logo.png'))
        self.exit_btn.clicked.connect(self.exit_exe)
        self.home_btn.setIcon(QIcon(r'home.png'))
        self.home_btn.setIconSize(QSize(40, 40))
        self.home_btn.clicked.connect(self.home)
        self.login.setText(USER_NAME)
        self.email.setText(EMAIL)
        self.delete_btn.clicked.connect(self.delete_acc)

    def change(self):
        self.hide()
        self.widget = Change()
        self.widget.show()

    def exit_exe(self):
        msg = QMessageBox(self)
        msg.setFont(QFont('Comfortaa', 16))
        msg.setStyleSheet('color: black; background-color: white')
        msg.setText('Вы уверены, что хотите выйти?')
        msg.setWindowTitle('Выход')
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        retval = msg.exec_()
        if retval == QMessageBox.Yes:
            self.close()
        else:
            pass

    def home(self):
        self.hide()
        self.mywidget = MyWidget(0)
        self.mywidget.show()

    def closeEvent(self, event):
        event.accept()

    def delete_acc(self):
        global USERID
        msg = QMessageBox(self)
        msg.setFont(QFont('Comfortaa', 16))
        msg.setStyleSheet('color: black; background-color: white')
        msg.setText('Вы уверены, что хотите удалить аккаунт?')
        msg.setWindowTitle('Удаление аккаунта')
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        retval = msg.exec_()
        if retval == QMessageBox.Yes:
            cur = CON.cursor()
            cur.execute("DELETE FROM Users WHERE id = ?", (USERID,))
            cur.execute("DELETE FROM Messages WHERE user_id = ?", (USERID,))
            CON.commit()
            self.close()
        else:
            pass


class Entering(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(r'login.ui', self)
        # self.setWindowIcon(QIcon(r'logo.png'))
        self.enter.clicked.connect(self.enter_func)
        self.enter.setAutoDefault(True)
        self.error.hide()
        self.reg_btn.clicked.connect(self.reg)

    def reg(self):
        self.hide()
        self.mywidget = Registration()
        self.mywidget.show()

    def enter_func(self):
        global RATING, USER_NAME, EMAIL, CON, IMAGE, USERID
        cur = CON.cursor()
        res = cur.execute("""SELECT password, email, rating, image, id FROM Users WHERE user = ?""",
                          (self.login.text(),)).fetchall()
        if res:
            if self.password.text() == res[0][0]:
                USER_NAME = self.login.text()
                EMAIL = res[0][1]
                RATING = res[0][2]
                USERID = res[0][4]
                print(USERID)
                self.home()
            else:
                self.error.show()
                self.error.setText('Неверный пароль!')
                self.password.clear()
        else:
            self.error.setText('Неверный логин!')
            self.error.show()
            self.password.clear()

    def home(self):
        self.hide()
        self.mywidget = MyWidget(0)
        self.mywidget.show()


class Materials(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(r'materials.ui', self)
        self.setWindowIcon(QIcon(r'logo.png'))

    def home(self):
        self.close()
        self.mywidget = MyWidget(0)
        self.mywidget.show()

    def closeEvent(self, event):
        self.home()
        event.accept()


class Registration(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(r'registration.ui', self)
        self.setWindowIcon(QIcon(r'logo.png'))
        self.regist_btn.clicked.connect(self.reg_func)
        self.regist_btn.setAutoDefault(True)
        self.image_btn.setIcon(QIcon(r'image.png'))
        self.image_btn.setIconSize(QSize(30, 30))
        self.image_btn.clicked.connect(self.choose_image)
        self.error.hide()
        self.home_btn.setIcon(QIcon(r'back.png'))
        self.home_btn.setIconSize(QSize(40, 40))
        self.home_btn.clicked.connect(self.enter)

    def choose_image(self):
        global IMAGE
        image = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '',
                                            'Картинка png (*.png);;jpg (*.jpg);;jpeg (*.jpeg)')[0]
        self.image.setText(image)
        IMAGE = image

    def reg_func(self):
        global CON, USER_NAME, EMAIL, RATING, IMAGE
        login = self.login.text()
        password = self.password.text()
        password_2 = self.password_2.text()
        email = self.email.text()
        check_login = True
        check_email = True
        if login and password_2 and password and email:
            cur = CON.cursor()
            usernames = cur.execute("""SELECT user FROM Users""").fetchall()
            emails = cur.execute("""SELECT email FROM Users""").fetchall()
            if emails:
                for email_bd in emails:
                    if email == email_bd[0]:
                        check_email = False
                        break
            if usernames:
                for username in usernames:
                    if username[0] == login:
                        check_login = False
                        break
            if not check_login:
                self.error.show()
                self.error.setText('Такой логин уже существует!')
            elif not check_email:
                self.error.show()
                self.error.setText('Такой email уже существует!')
            elif password != password_2:
                self.error.show()
                self.error.setText('Пароли не совпадают!')
            else:
                USER_NAME = login
                EMAIL = email
                RATING = 0
                self.insertBLOB(login, password, email, IMAGE)
                self.home()
        else:
            self.error.show()
            self.error.setText('Поля отмеченные * обязательны для заполнения!')

    def convertToBinaryData(self, filename):
        with open(filename, 'rb') as file:
            blobData = file.read()
        return blobData

    def insertBLOB(self, login, password, email, image):
        sqliteConnection = sqlite3.connect('App.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")
        sqlite_insert_blob_query = """ INSERT INTO Users(user, password, email, image) VALUES (?, ?, ?, ?)"""

        IMAGE = self.convertToBinaryData(image)
        # Convert data into tuple format
        data_tuple = (login, password, email, IMAGE)
        cursor.execute(sqlite_insert_blob_query, data_tuple)
        sqliteConnection.commit()
        print("Image and file inserted successfully as a BLOB into a table")
        cursor.close()

    def home(self):
        self.hide()
        self.mywidget = MyWidget(0)
        self.mywidget.show()

    def enter(self):
        self.hide()
        self.mywidget = Entering()
        self.mywidget.show()


class Change(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(r'change.ui', self)
        self.setWindowIcon(QIcon(r'logo.png'))
        self.regist_btn.clicked.connect(self.reg_func)
        self.regist_btn.setAutoDefault(True)
        self.image_btn.setIcon(QIcon(r'image.png'))
        self.image_btn.setIconSize(QSize(30, 30))
        self.image_btn.clicked.connect(self.choose_image)
        self.error.hide()
        self.login.setText(USER_NAME)
        self.email.setText(EMAIL)
        self.image.setText(IMAGE)
        self.home_btn.setIcon(QIcon(r'back.png'))
        self.home_btn.setIconSize(QSize(40, 40))
        self.home_btn.clicked.connect(self.home)

    def choose_image(self):
        global IMAGE
        image = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '',
                                            'Картинка png (*.png);;jpg (*.jpg);;jpeg (*.jpeg)')[0]
        self.image.setText(image)
        IMAGE = image

    def reg_func(self):
        global CON, USER_NAME, EMAIL, IMAGE
        login = self.login.text()
        email = self.email.text()
        check_login = True
        check_email = True
        cur = CON.cursor()
        usernames = cur.execute("""SELECT user FROM Users WHERE user != ?""",
                                (USER_NAME,)).fetchall()
        emails = cur.execute("""SELECT email FROM Users WHERE user != ?""", (USER_NAME,)).fetchall()
        for email_bd in emails:
            if email == email_bd[0]:
                check_email = False
                break
        for username in usernames:
            if username[0] == login:
                check_login = False
                break
        if login and email:
            if not check_login:
                self.error.show()
                self.error.setText('Такой логин уже существует!')
            elif not check_email:
                self.error.show()
                self.error.setText('Такой email уже существует!')
            else:
                EMAIL = email
                cur.execute("""UPDATE Users SET image = ? WHERE user = ?""", (IMAGE, USER_NAME))
                user = USER_NAME
                USER_NAME = login
                cur.execute("""UPDATE Users SET user = ? WHERE user = ?""", (USER_NAME, user))
                cur.execute("""UPDATE Users SET email = ? WHERE user = ?""", (EMAIL, USER_NAME))
                CON.commit()
                self.home()
        else:
            self.error.show()
            self.error.setText('Все поля должны быть заполнены!')

    def home(self):
        self.hide()
        self.mywidget = Account()
        self.mywidget.show()

    def closeEvent(self, event):
        self.home()
        event.accept()


class Chat(QMainWindow):
    def __init__(self):
        global USER_NAME
        super().__init__()
        uic.loadUi(r'chat.ui', self)
        self.setWindowIcon(QIcon(r'logo.png'))
        self.home_btn.setIcon(QIcon(r'back.png'))
        self.home_btn.setIconSize(QSize(40, 40))
        self.home_btn.clicked.connect(self.home)
        cur = CON.cursor()
        info = cur.execute(
            """SELECT * FROM (SELECT user, message, msg_id FROM Messages JOIN Users ON Messages.user_id = Users.id ORDER BY Messages.msg_id DESC LIMIT 20) ORDER BY msg_id ASC;""")
        for elem in info:
            name = 'Я' if elem[0] == USER_NAME else elem[0]
            self.listWidget.addItem('{} : {}'.format(name, elem[1]))
        self.send_btn.clicked.connect(self.send)

    def home(self):
        self.hide()
        self.mywidget = MyWidget(0)
        self.mywidget.show()

    def send(self):
        global USERID
        text = self.lineEdit.text()
        if bool(text):
            self.listWidget.addItem('Я : {}'.format(text))
            cur = CON.cursor()
            cur.execute("""INSERT INTO Messages(user_id, message) VALUES(?,?)""", (USERID, text))
            CON.commit()
            self.lineEdit.clear()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Entering()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())

#!/usr/bin/env python
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget,QTableWidgetItem)
import json

class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)

        self.originalPalette = QApplication.palette()

        styleComboBox = QComboBox()
        styleComboBox.addItems(QStyleFactory.keys())

        styleLabel = QLabel("&Style:")
        styleLabel.setBuddy(styleComboBox)

        self.useStylePaletteCheckBox = QCheckBox("&Use style's standard palette")
        self.useStylePaletteCheckBox.setChecked(True)

        disableWidgetsCheckBox = QCheckBox("&Disable widgets")

        self.createTopLeftGroupBox()
        self.createTopRightGroupBox()
        self.createBottomLeftTabWidget()
        self.createBottomRightGroupBox()


        styleComboBox.activated[str].connect(self.changeStyle)
        self.useStylePaletteCheckBox.toggled.connect(self.changePalette)
        disableWidgetsCheckBox.toggled.connect(self.topLeftGroupBox.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.topRightGroupBox.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.bottomLeftTabWidget.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.bottomRightGroupBox.setDisabled)

        topLayout = QHBoxLayout()
        topLayout.addWidget(styleLabel)
        topLayout.addWidget(styleComboBox)
        topLayout.addStretch(1)
        #topLayout.addWidget(self.useStylePaletteCheckBox)
        #topLayout.addWidget(disableWidgetsCheckBox)
        reButton = QPushButton("refresh")
        topLayout.addWidget(reButton)
        reButton.clicked.connect(self.clicked)


        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        mainLayout.addWidget(self.topLeftGroupBox, 1, 0)
        mainLayout.addWidget(self.topRightGroupBox, 1, 1)
        #mainLayout.addWidget(self.bottomLeftTabWidget, 2, 0)
        mainLayout.addWidget(self.bottomRightGroupBox, 2, 1)

        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)

        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setColumnWidth(0,150)
        self.tableWidget.setHorizontalHeaderLabels(['interface', 'IP', 'status'])
        self.clicked()
        mainLayout.addWidget(self.tableWidget, 2, 0)

        self.setLayout(mainLayout)

        self.setWindowTitle("GUi")
        self.changeStyle('Windows')

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))
        self.changePalette()

    def changePalette(self):
        if (self.useStylePaletteCheckBox.isChecked()):
            QApplication.setPalette(QApplication.style().standardPalette())
        else:
            QApplication.setPalette(self.originalPalette)

    def advanceProgressBar(self):
        curVal = self.progressBar.value()
        maxVal = self.progressBar.maximum()
        self.progressBar.setValue(curVal + (maxVal - curVal) // 100)

    def createTopLeftGroupBox(self):
        self.topLeftGroupBox = QGroupBox("Group 1")
        lineUser = QLineEdit('user')
        linePassword = QLineEdit('password')
        lineHost = QLineEdit('host')
        loginButton = QPushButton("Add")
        layout = QVBoxLayout()

        layout.addWidget(lineHost)
        layout.addWidget(lineUser)
        layout.addWidget(linePassword)
        layout.addWidget(loginButton)
        layout.addStretch(1)
        #loginButton.clicked.connect(self.clicked)
        self.topLeftGroupBox.setLayout(layout)

    def createTopRightGroupBox(self):
        self.topRightGroupBox = QGroupBox("???")

        defaultPushButton = QPushButton("Default Push Button")
        defaultPushButton.setDefault(True)

        togglePushButton = QPushButton("Toggle Push Button")
        togglePushButton.setCheckable(True)
        togglePushButton.setChecked(True)

        flatPushButton = QPushButton("Flat Push Button")
        flatPushButton.setFlat(True)

        layout = QVBoxLayout()
       # layout.addWidget(defaultPushButton)
       # layout.addWidget(togglePushButton)
      #  layout.addWidget(flatPushButton)
      #  layout.addStretch(1)
        self.topRightGroupBox.setLayout(layout)

    def createBottomLeftTabWidget(self):
        self.bottomLeftTabWidget = QTabWidget()
        self.bottomLeftTabWidget.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Ignored)

        tab1 = QWidget()
        tableWidget = QTableWidget()
        tableWidget.setRowCount(1)
        tableWidget.setColumnCount(3)
        tableWidget.setColumnWidth(0,150)
        tab1hbox = QHBoxLayout()
        tab1hbox.setContentsMargins(5, 5, 5, 5)
        tab1hbox.addWidget(tableWidget)
        tab1.setLayout(tab1hbox)
        tableWidget.setHorizontalHeaderLabels(['interface', 'IP', 'status'])
        self.f = open('info.json')
        self.data = json.load(self.f)
        tableWidget.setItem(0, 0, QTableWidgetItem(self.data["menu"]))
        self.f.close()

        tab2 = QWidget()
        textEdit = QTextEdit()

        textEdit.setPlainText("Twinkle, twinkle, little star,\n"
                              "How I wonder what you are.\n"
                              "Up above the world so high,\n"
                              "Like a diamond in the sky.\n"
                              "Twinkle, twinkle, little star,\n"
                              "How I wonder what you are!\n")

        tab2hbox = QHBoxLayout()
        tab2hbox.setContentsMargins(5, 5, 5, 5)
        tab2hbox.addWidget(textEdit)
        tab2.setLayout(tab2hbox)

        self.bottomLeftTabWidget.addTab(tab1, "&Table")
        self.bottomLeftTabWidget.addTab(tab2, "log")

    def createBottomRightGroupBox(self):
        self.bottomRightGroupBox = QGroupBox("interface")
        self.bottomRightGroupBox.setCheckable(True)
        self.bottomRightGroupBox.setChecked(True)

        lineIP = QLineEdit('192.168.3.3')
        #lineEdit.setEchoMode(QLineEdit.Password)
        lineMask = QLineEdit('255.255.255.0')
        lineGateway = QLineEdit('192.168.3.254')
        configButton = QPushButton("OK")
        layout = QGridLayout()
        layout.addWidget(lineIP, 0, 0, 1, 2)
        layout.addWidget(lineMask, 1, 0, 1, 2)
        layout.addWidget(lineGateway, 2, 0, 1, 2)
        layout.addWidget(configButton, 3, 0, 1, 2)
        #layout.addWidget(dateTimeEdit, 2, 0, 1, 2)
        #layout.addWidget(slider, 3, 0)

        layout.setRowStretch(5, 1)
        self.bottomRightGroupBox.setLayout(layout)

    def clicked(self):
        print("clicked")
        f = open('info.json')
        data = json.load(f)
        self.tableWidget.setItem(0, 0, QTableWidgetItem(data["menu"]))
        f.close()

    def createProgressBar(self):
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 10000)
        self.progressBar.setValue(0)

        timer = QTimer(self)
        timer.timeout.connect(self.advanceProgressBar)
        timer.start(1000)
    def loaddata(self):
        people=[{"name":"John","age":45,"address":"New York"}, {"name":"Mark", "age":40,"address":"LA"},
                {"name":"George","age":30,"address":"London"}]
        row=0
        self.tableWidget.setRowCount(len(people))
        for person in people:
            self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(person["name"]))
            self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(str(person["age"])))
            self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(person["address"]))
            row=row+1

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.setGeometry(0, 0, 1000, 800)
    gallery.show()
    sys.exit(app.exec_())

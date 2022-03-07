#!/usr/bin/env python
from pickletools import UP_TO_NEWLINE
from re import S
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget,QTableWidgetItem)
import json
import yaml
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_config,netmiko_send_command
from nornir_utils.plugins.functions import print_result
class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)
        self.Hostcurrent = ""
        f = open('hosts.yaml')
        host = yaml.load(f, Loader=yaml.FullLoader)
        f.close()
        hostdict = []
        for hosts in host:
            hostdict.append(hosts)
        
        self.originalPalette = QApplication.palette()

        styleComboBox = QComboBox()
        styleComboBox.addItems(hostdict)

        styleLabel = QLabel("&Host:")
        styleLabel.setBuddy(styleComboBox)
        self.changeStyle(hostdict[0])
        self.useStylePaletteCheckBox = QCheckBox("&Use style's standard palette")
        self.useStylePaletteCheckBox.setChecked(True)

        disableWidgetsCheckBox = QCheckBox("&Disable widgets")

        #self.createTopLeftGroupBox()
        self.createTopRightGroupBox()
        self.createBottomLeftTabWidget()
        self.createBottomRightGroupBox()


        styleComboBox.activated[str].connect(self.changeHost)
        self.useStylePaletteCheckBox.toggled.connect(self.changePalette)
       # disableWidgetsCheckBox.toggled.connect(self.topLeftGroupBox.setDisabled)
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
#-------------------------------
        self.topLeftGroupBox = QGroupBox("Port")
        self.interfaceComboBox = QComboBox()
        f = open('./logs/'+self.Hostcurrent+'.json')
        data = json.load(f)
        datalen = len(data['get_facts']['interface_list'])
        interfaceData = data['get_facts']['interface_list']
        self.interfaceComboBox.addItems(interfaceData)
        self.spinVlan = QSpinBox()
        self.spinVlan.setValue(1)
        self.spinNative = QSpinBox()
        self.spinNative.setValue(1)
        self.lineAllowvlan = QLineEdit('1,1-99')
        loginButton = QPushButton("send")
        loginButton.clicked.connect(self.send_command)
        self.disableAccess = QRadioButton("&Access")
        self.disableAccess.toggled.connect(self.lineAllowvlan.setDisabled)
        self.disableAccess.toggled.connect(self.spinNative.setDisabled)
        self.disableAccess.setChecked(True)
        disableTrunk = QRadioButton("&Trunk")
        disableTrunk.toggled.connect(self.spinVlan.setDisabled)
        labelAllowvlan = QLabel('&Allow Vlan')
        labelAllowvlan.setBuddy(self.lineAllowvlan)
        labelNative = QLabel('Native Vlan')
        labelAllowvlan.setBuddy(self.spinNative)
        layout = QVBoxLayout()       
        layout.addWidget(self.interfaceComboBox)
        layout.addWidget(self.disableAccess)
        layout.addWidget(self.spinVlan)
        layout.addWidget(disableTrunk)
        layout.addWidget(labelAllowvlan)
        layout.addWidget(self.lineAllowvlan)
        layout.addWidget(labelNative)
        layout.addWidget(self.spinNative)

        layout.addWidget(loginButton)
        layout.addStretch(1)

        #loginButton.clicked.connect(self.clicked)
        self.topLeftGroupBox.setLayout(layout)
#------------------



        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        mainLayout.addWidget(self.topLeftGroupBox, 1, 0)
        mainLayout.addWidget(self.topRightGroupBox, 1, 1)
        #mainLayout.addWidget(self.bottomLeftTabWidget, 2, 0)
        #mainLayout.addWidget(self.bottomRightGroupBox, 2, 1)

        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)

        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setColumnWidth(0,150)
        self.tableWidget.setColumnWidth(1,100)
        self.tableWidget.setColumnWidth(2,80)
        self.tableWidget.setColumnWidth(3,400)
        self.tableWidget.setHorizontalHeaderLabels(['interface', 'Type', 'status','description'])
        self.clicked()
        mainLayout.addWidget(self.tableWidget, 2, 0,2,2)

        self.setLayout(mainLayout)

        self.setWindowTitle("GUi")
        #self.changeStyle(hostdict[0])

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create("Fusion"))
        self.Hostcurrent = styleName
    
    def changeHost(self,hostName):
        self.Hostcurrent = hostName
        self.changePalette()
        self.clicked()

    def changePalette(self):
        print("change HOST")
        print(self.Hostcurrent)
        #if (self.useStylePaletteCheckBox.isChecked()):
        #    QApplication.setPalette(QApplication.style().standardPalette())
       # else:
         #   QApplication.setPalette(self.originalPalette)

    def advanceProgressBar(self):
        curVal = self.progressBar.value()
        maxVal = self.progressBar.maximum()
        self.progressBar.setValue(curVal + (maxVal - curVal) // 100)

    def createTopLeftGroupBox(self):
        self.topLeftGroupBox = QGroupBox("Port")
        self.interfaceComboBox = QComboBox()
        f = open('./logs/'+self.Hostcurrent+'.json')
        data = json.load(f)
        datalen = len(data['get_facts']['interface_list'])
        interfaceData = data['get_facts']['interface_list']
        self.interfaceComboBox.addItems(interfaceData)
        self.spinVlan = QSpinBox()
        self.spinVlan.setValue(1)
        self.lineAllowvlan = QLineEdit('1,1-99')
        loginButton = QPushButton("Add")
        self.disableAccess = QRadioButton("&Access")
        self.disableAccess.toggled.connect(self.lineAllowvlan.setDisabled)
        self.disableAccess.setChecked(True)
        disableTrunk = QRadioButton("&Trunk")
        disableTrunk.toggled.connect(self.spinVlan.setDisabled)
        labelAllowvlan = QLabel('&Allow Vlan')
        labelAllowvlan.setBuddy(self.lineAllowvlan)
        layout = QVBoxLayout()       
        layout.addWidget(self.interfaceComboBox)
        layout.addWidget(self.disableAccess)
        layout.addWidget(self.spinVlan)
        layout.addWidget(disableTrunk)
        layout.addWidget(labelAllowvlan)
        layout.addWidget(self.lineAllowvlan)
        
        
        layout.addWidget(loginButton)
        layout.addStretch(1)

        #loginButton.clicked.connect(self.clicked)
        self.topLeftGroupBox.setLayout(layout)

    def createTopRightGroupBox(self):
        self.topRightGroupBox = QGroupBox("??")

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
        tableWidget.setHorizontalHeaderLabels(['interface', 'Type', 'status'])
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
        print("Refesh")
        f = open('./logs/'+self.Hostcurrent+'.json')
        data = json.load(f)
        datalen = len(data['get_facts']['interface_list'])
        interfaceData = data['get_facts']['interface_list']
        self.tableWidget.setRowCount(datalen)
        row = 0
        for intF in interfaceData:
            statusint = ""
            if (data['get_interfaces'][intF]['is_up']):
                statusint = "UP"
            else:
                statusint = "DOWN"
            descripint = data['get_interfaces'][intF]['description']

            self.tableWidget.setItem(row, 0, QTableWidgetItem(intF))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(statusint))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(descripint))

            row=row+1
        f.close()
        self.interfaceComboBox.clear()
        self.interfaceComboBox.addItems(interfaceData)
        self.interfaceComboBox.setCurrentIndex(1)
        self.spinVlan.setValue(1)
        self.spinNative.setValue(1)
        self.disableAccess.setChecked(True)
        self.lineAllowvlan.setText('1,1-99')

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
    def send_command(self):
        if self.disableAccess:
            nr = InitNornir(
            config_file="config.yaml",
            logging={"enabled": False},
            runner={"plugin": "threaded", "options": {"num_workers": 15}},
            )
            f = open('hosts.yaml')
            host = yaml.load(f, Loader=yaml.FullLoader)
            f.close()
            hostname = host[self.Hostcurrent]['hostname']
            sendto = nr.filter(hostname = hostname)
            interface = "int "+self.interfaceComboBox.currentText()
            vlan = "switchport access vlan "+str(self.spinVlan.value())
            command = []
            command.append(interface)
            command.append(vlan)
            print(command)
            print(hostname)
            result= sendto.run(task=netmiko_send_config, config_commands=command)
            print_result(result)

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.setGeometry(0, 0, 1000, 800)
    gallery.show()
    sys.exit(app.exec_())

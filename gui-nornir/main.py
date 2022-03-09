#!/usr/bin/env python
from pickletools import UP_TO_NEWLINE
from re import S
from PyQt5.QtCore import *#QDateTime, Qt, QTimer,QRunnable, QThreadPool,QMetaObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget,QTableWidgetItem,)
from PyQt5.QtGui import QMovie
import json
import yaml
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_config,netmiko_send_command
from nornir_utils.plugins.functions import print_result
from nornir_napalm.plugins.tasks import napalm_get,napalm_cli,napalm_configure

class AddHost(QWidget):
    def __init__(self):
        super().__init__()
        topGroupBox = QGroupBox("")
        layout = QGridLayout()

        labelH = QLabel("Host IP:" )
        lineHost = QLineEdit('')
        labelU = QLabel("Username:" )
        lineUser = QLineEdit('')
        labelP = QLabel("Password:" )
        linePassword = QLineEdit('')
        addButton = QPushButton("Add")
        layout.addWidget(labelH,0,0)
        layout.addWidget(lineHost,0,1)
        layout.addWidget(labelU,1,0)
        layout.addWidget(lineUser,1,1)
        layout.addWidget(labelP,2,0)
        layout.addWidget(linePassword,2,1)
        layout.addWidget(addButton,3,1)
        layout.setRowStretch(0, 0)
        topGroupBox.setLayout(layout)
        mainLayout = QGridLayout()
        mainLayout.addWidget(topGroupBox, 1, 1)

        self.setLayout(mainLayout)
        self.setWindowTitle("Add Host")


class PopupUpdate(QWidget):
    def __init__(self):
        super().__init__()

        super().__init__()
        topGroupBox = QGroupBox("Add")
        layout = QGridLayout()
        self.label = QLabel()
        self.movie = QMovie("loading.gif")
        self.label.setMovie(self.movie)

        topGroupBox.setLayout(layout)

        mainLayout = QGridLayout()
        #mainLayout.addWidget(topGroupBox, 1, 1)
        self.setLayout(mainLayout)
        self.setWindowTitle("")




        self.startAnimation()



    def startAnimation(self):
        self.movie.start()


    def stopAnimation(self):
        self.movie.stop()

class GetHost(QRunnable):
    def __init__(self, n,w):
        QRunnable.__init__(self)
        self.n = n
        self.w = w
    def run(self):
        nr = InitNornir(
            config_file="config.yaml",
            logging={"enabled": False},
            runner={"plugin": "threaded", "options": {"num_workers": 20}},)
        result = nr.run(napalm_get, getters=['get_interfaces_ip','get_interfaces','get_facts','get_vlans'])
        print_result(result)
        f = open('hosts.yaml')
        data = yaml.load(f, Loader=yaml.FullLoader)
        f.close()
        for keyyaml in data:
            print(keyyaml)
            rjson = json.dumps(result[keyyaml].result, indent=2)
            with open("./logs/"+keyyaml+".json", "w") as outfile:
              outfile.write(rjson)
        QMetaObject.invokeMethod(self.w, "stopGet",
                                 Qt.QueuedConnection,
                                 Q_ARG(str, "gg"))
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
        self.updatingH = QLabel("       UPDATING ....")
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

        self.topLayout = QHBoxLayout()
        self.topLayout.addWidget(styleLabel)
        self.topLayout.addWidget(styleComboBox)
        #topLayout.addStretch(1)
        #topLayout.addWidget(self.useStylePaletteCheckBox)
        #topLayout.addWidget(disableWidgetsCheckBox)
        reButton = QPushButton("Edit")
        self.topLayout.addWidget(reButton)
        self.topLayout.addWidget(self.updatingH)
        self.topLayout.addStretch(1)
        reButton.clicked.connect(self.winAddhost)
#-------------------------------
        self.topLeftGroupBox = QGroupBox("Port")
        self.interfaceComboBox = QComboBox()
        f = open('./logs/'+self.Hostcurrent+'.json')
        data = json.load(f)
        datalen = len(data['get_facts']['interface_list'])
        interfaceData = data['get_facts']['interface_list']
        self.interfaceComboBox.addItems(interfaceData)
        self.interfaceComboBox.activated[str].connect(self.changePort)
        self.spinVlan = QSpinBox()
        self.spinVlan.setValue(1)
        self.spinNative = QSpinBox()
        self.spinNative.setValue(1)
        self.checkShut = QCheckBox("Enable Port")
        self.lineAllowvlan = QLineEdit('1,1-99')
        loginButton = QPushButton("send")
        loginButton.clicked.connect(self.send_command)
        self.disableAccess = QRadioButton("Access")
        self.disableAccess.toggled.connect(self.lineAllowvlan.setDisabled)
        self.disableAccess.toggled.connect(self.spinNative.setDisabled)
        self.disableAccess.setChecked(True)
        self.checkShut.setChecked(True)
        disableTrunk = QRadioButton("Trunk")
        disableTrunk.toggled.connect(self.spinVlan.setDisabled)
        labelAllowvlan = QLabel('Allow Vlan:')
        labelVlan = QLabel('Vlan:')
        labelVlan.setBuddy(self.spinVlan)
        labelAllowvlan.setBuddy(self.lineAllowvlan)
        labelNative = QLabel('Native Vlan:')
        labelAllowvlan.setBuddy(self.spinNative)
        layout = QGridLayout()
        layout.addWidget(self.interfaceComboBox,0,0)
        layout.addWidget(self.checkShut,0,4)
        layout.addWidget(self.disableAccess,1,0)
        layout.addWidget(labelVlan,2,0)
        layout.addWidget(self.spinVlan,2,1,1,1)
        layout.addWidget(disableTrunk,3,0)
        layout.addWidget(labelAllowvlan,4,0)
        layout.addWidget(self.lineAllowvlan,4,1,1,1)
        layout.addWidget(labelNative,5,0)
        layout.addWidget(self.spinNative,5,1,1,1)

        layout.addWidget(loginButton,7,4)
        #layout.setRowStretch(10, 1)

       # layout.addStretch(1)

        #loginButton.clicked.connect(self.clicked)
        self.topLeftGroupBox.setLayout(layout)
#------------------



        mainLayout = QGridLayout()
        mainLayout.addLayout(self.topLayout, 0, 0, 1, 2)
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
        self.tableWidget.setColumnWidth(3,600)
        self.tableWidget.setHorizontalHeaderLabels(['interface', 'Type', 'status','description'])
        self.clicked()
        mainLayout.addWidget(self.tableWidget, 2, 0,2,2)

        self.setLayout(mainLayout)

        self.setWindowTitle("GUi")
        self.clickload()


    def hideUpdate(self):
        self.updatingH.setHidden(True)
    def showUpdate(self):
        self.updatingH.setHidden(False)
    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create("Fusion"))
        self.Hostcurrent = styleName

    def changeHost(self,hostName):
        self.Hostcurrent = hostName
        self.changePalette()
        self.clicked()

    def changePort(self,port):
        self.spinVlan.setValue(1)
        self.spinNative.setValue(1)
        self.disableAccess.setChecked(True)
        self.checkShut.setChecked(True)
        self.lineAllowvlan.setText('all')

    def changePalette(self):
        print("change HOST")
        print(self.Hostcurrent)

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
        self.lineAllowvlan = QLineEdit('all')
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
        self.topRightGroupBox = QGroupBox("Quick Manage")

        autoButton = QPushButton("Auto Assign Vlan")
        autoButton.setDefault(True)

        changeButton = QPushButton("Change Vlan for Group")
        changeButton.setDefault(True)

        flatPushButton = QPushButton("Flat Push Button")
        flatPushButton.setFlat(False)

        layout = QVBoxLayout()
        layout.addWidget(autoButton)
        layout.addWidget(changeButton)
        layout.addWidget(flatPushButton)
        layout.addStretch(1)

        changeButton.clicked.connect(lambda:self.requestVlan("20",3))
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
            vlans = data['get_vlans']
            typeport = "IP"
            checkTrunking = 0
            for vlan in vlans:
                if intF in vlans[vlan]["interfaces"]:
                    typeport = "Vlan " +vlan
                    checkTrunking = checkTrunking+1
            if checkTrunking >1:
                typeport = "Trunk "
            self.tableWidget.setItem(row, 0, QTableWidgetItem(intF))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(typeport))
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
        self.checkShut.setChecked(True)
        self.lineAllowvlan.setText('all')

    def createProgressBar(self):
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 10000)
        self.progressBar.setValue(0)

        timer = QTimer(self)
        timer.timeout.connect(self.advanceProgressBar)
        timer.start(1000)

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
            f = open('./logs/'+self.Hostcurrent+'.json')
            data = json.load(f)
            f.close()
            command = []
            if (str(self.spinVlan.value()) in data['get_vlans']):
                print("Vlaned")
            else :
                createV = "va "+ str(self.spinVlan.value())
                command.append(createV)
                print("Create Vlan "+str(self.spinVlan.value()))

            command.append(interface)
            command.append(vlan)
            print(command)
            print(hostname)
            result= sendto.run(task=netmiko_send_config, config_commands=command)
            print_result(result)
            seld.loadOnedata()
    def winAddhost(self, checked):
            self.w = AddHost()
            self.w.setGeometry(250, 100, 300, 200)
            self.w.show()
    def winLoading(self):
            self.w = PopupUpdate()
            self.w.setGeometry(250, 100, 400, 400)
            self.w.show()
    def clickload(self):
        runnable = GetHost("1",self)
        QThreadPool.globalInstance().start(runnable)
    @pyqtSlot(str)
    def stopGet(self, data):
        print(data)
        self.clicked()
        self.hideUpdate()
    def requestVlan(self, request,number):
        f = open('./logs/'+self.Hostcurrent+'.json')
        data = json.load(f)
        f.close()

        commandAll = []
        port = data['get_vlans']['1']['interfaces']
        for dup in data['get_vlans']:
            if dup != '1':
                port = [inter for inter in port if inter not in data['get_vlans'][dup]['interfaces']]
        print(port)
        if len(port)>=number:
            print(len(port))
            give = len(port)-number
            del port[-give:]
            print(len(port))
            for interface in port:
                interfaceIn = "int "+interface
                commandAll.append(interfaceIn)
                commandAll.append("switchport mode access")
                accessVlan = "switchport access vlan "+request
                commandAll.append(accessVlan)
                commandAll.append("exit")
            print(commandAll)

            nr = InitNornir(
            config_file="config.yaml",
            logging={"enabled": False},
            runner={"plugin": "threaded", "options": {"num_workers": 15}},)
            f = open('hosts.yaml')
            host = yaml.load(f, Loader=yaml.FullLoader)
            f.close()
            hostname = host[self.Hostcurrent]['hostname']
            sendto = nr.filter(hostname = hostname)
            result= sendto.run(task=netmiko_send_config, config_commands=commandAll)
            print_result(result)
            self.loadOnedata()
        else :
            print("Not enough channels available")

    def loadData(self,):
        nr = InitNornir(
            config_file="config.yaml",
            logging={"enabled": False},
            runner={"plugin": "threaded", "options": {"num_workers": 20}},)
        result = nr.run(napalm_get, getters=['get_interfaces_ip','get_interfaces','get_facts','get_vlans'])
        print_result(result)
        f = open('hosts.yaml')
        data = yaml.load(f, Loader=yaml.FullLoader)
        f.close()
        for keyyaml in data:
            print(keyyaml)
            rjson = json.dumps(result[keyyaml].result, indent=2)
            #jstr = json.loads(rjson)
            with open("./logs/"+keyyaml+".json", "w") as outfile:
              outfile.write(rjson)
        self.clicked()
    def loadOnedata(self):
        nr = InitNornir(
        config_file="config.yaml",
        logging={"enabled": False},
        runner={"plugin": "threaded", "options": {"num_workers": 15}},)
        f = open('hosts.yaml')
        host = yaml.load(f, Loader=yaml.FullLoader)
        f.close()
        hostname = host[self.Hostcurrent]['hostname']
        sendto = nr.filter(hostname = hostname)
        result= sendto.run(napalm_get, getters=['get_interfaces_ip','get_interfaces','get_facts','get_vlans'])
        rjson = json.dumps(result[self.Hostcurrent].result, indent=2)
        with open("./logs/"+self.Hostcurrent+".json", "w") as outfile:
          outfile.write(rjson)
        self.clicked()


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.setGeometry(200, 300, 1000, 800)
    gallery.show()

    sys.exit(app.exec_())

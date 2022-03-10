#!/usr/bin/env python
from http.client import OK
from logging import shutdown
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
        labelN = QLabel("Profile Name:" )
        self.lineN = QLineEdit('')
        labelH = QLabel("Host IP:" )
        self.lineHost = QLineEdit('')
        labelU = QLabel("Username:" )
        self.lineUser = QLineEdit('')
        labelP = QLabel("Password:" )
        self.linePassword = QLineEdit('')
        addButton = QPushButton("Add")
        layout.addWidget(labelN,0,0)
        layout.addWidget(self.lineN,0,1)
        layout.addWidget(labelH,1,0)
        layout.addWidget(self.lineHost,1,1)
        layout.addWidget(labelU,2,0)
        layout.addWidget(self.lineUser,2,1)
        layout.addWidget(labelP,3,0)
        layout.addWidget(self.linePassword,3,1)
        layout.addWidget(addButton,4,1)
        layout.setRowStretch(0, 0)
        topGroupBox.setLayout(layout)
        mainLayout = QGridLayout()
        mainLayout.addWidget(topGroupBox, 1, 1)
        addButton.clicked.connect(lambda:self.addHos())
        self.setLayout(mainLayout)
        self.setWindowTitle("Add Host")

    def addHos(self):
        newSW={
                self.lineN.text(): {
                    'hostname': self.lineHost.text(),
                    'platform': 'ios',
                    'username': self.lineUser.text(),
                    'password': self.linePassword.text()
                }
            }
        

        with open('hosts.yaml','r') as yamlfile:
                cur_yaml = yaml.load(yamlfile,Loader=yaml.FullLoader)
                cur_yaml.update(newSW)
                print(cur_yaml)
        with open(r'hosts.yaml', 'w') as file:
            documents = yaml.dump(cur_yaml, file)
        self.close()

class sendComplete(QWidget):
    def __init__(self):
        super().__init__()
        topGroupBox = QGroupBox("")
        layout = QGridLayout()
        labelN = QLabel("Sent" )
        layout.addWidget(labelN,0,0)
        layout.setRowStretch(0, 0)
        topGroupBox.setLayout(layout)
        mainLayout = QGridLayout()
        mainLayout.addWidget(topGroupBox, 1, 1)
        
        self.setLayout(mainLayout)
        self.setWindowTitle("")

class TranferGroup(QWidget):
    def __init__(self,host):
        super().__init__()
        topGroupBox = QGroupBox("")
        layout = QGridLayout()
        self.Hostcurrent = host

        labelFrom = QLabel("From Vlan" )
        self.labelWait = QLabel("Waiting.." )
        self.labelSuccess = QLabel("Success" )
        self.spinFromVlan = QSpinBox()
        labelTo = QLabel(" To Vlan " )
        self.spinToVlan = QSpinBox()
        self.transferButton = QPushButton("Tranfer")
        layout.addWidget(labelFrom,0,0)

        layout.addWidget(self.spinFromVlan,1,0)
        layout.addWidget(labelTo,0,2)
        layout.addWidget(self.spinToVlan,1,2)
        layout.addWidget(self.labelWait,2,1)
        layout.addWidget(self.labelSuccess,2,1)
        layout.addWidget(self.transferButton,2,1)
        layout.setRowStretch(0, 0)
        topGroupBox.setLayout(layout)
        mainLayout = QGridLayout()
        mainLayout.addWidget(topGroupBox, 1, 1)
        self.labelWait.setHidden(True)
        self.labelSuccess.setHidden(True)
        self.transferButton.clicked.connect(lambda:self.trans(str(self.spinFromVlan.value()),str(self.spinToVlan.value())))
        self.setLayout(mainLayout)
        self.setWindowTitle("Tranfer Group")

    def trans(self,f,t):
          self.transferButton.setHidden(True)
          self.labelWait.setHidden(False)
          runnable = TranferGroupVlan(f,t,self.Hostcurrent,self)
          QThreadPool.globalInstance().start(runnable)

    @pyqtSlot(str)
    def successOK(self,data):
        self.labelSuccess.setHidden(False)
        self.labelWait.setHidden(True)
        print(data)

class AccessAll(QWidget):
    def __init__(self,host):
        super().__init__()
        topGroupBox = QGroupBox("")
        layout = QGridLayout()
        self.Hostcurrent = host

        labelFrom = QLabel("Access All Vlan to:" )
        self.labelWait = QLabel("Waiting.." )
        self.labelSuccess = QLabel("Success" )
        self.spinTo = QSpinBox()
        self.transferButton = QPushButton("Access all")
        layout.addWidget(labelFrom,0,0)

        layout.addWidget(self.spinTo,1,0)
        layout.addWidget(self.labelWait,2,1)
        layout.addWidget(self.labelSuccess,2,1)
        layout.addWidget(self.transferButton,2,1)
        layout.setRowStretch(0, 0)
        topGroupBox.setLayout(layout)
        mainLayout = QGridLayout()
        mainLayout.addWidget(topGroupBox, 1, 1)
        self.labelWait.setHidden(True)
        self.labelSuccess.setHidden(True)
        self.transferButton.clicked.connect(lambda:self.trans(str(self.spinTo.value())))
        self.setWindowTitle("Access All")
        self.setLayout(mainLayout)
    def trans(self,f):
          self.transferButton.setHidden(True)
          self.labelWait.setHidden(False)
          runnable = AccessAllVlan(f,self.Hostcurrent,self)
          QThreadPool.globalInstance().start(runnable)

    @pyqtSlot(str)
    def successOK(self,data):
        self.labelSuccess.setHidden(False)
        self.labelWait.setHidden(True)
        print(data)

class AutoHost(QWidget):
    def __init__(self,host,w):
        super().__init__()
        self.Hostcurrent = host
        self.wid = w
        topGroupBox = QGroupBox("")
        layout = QGridLayout()

        self.labelH = QLabel("Access Vlan:" )
        self.labelTo = QLabel("Access Vlan to:" )
        self.labelAlert = QLabel("" )
        self.labelW8 = QLabel("Waiting for a sec...")
        self.lineHost = QSpinBox()
        self.labelU = QLabel("How many do u need?:" )
        self.lineUser = QSpinBox()
        self.goButton = QPushButton("Go")
        self.SucButton = QPushButton("Close")
        layout.addWidget(self.labelH,0,0)
        layout.addWidget(self.labelTo,0,0)
        layout.addWidget(self.lineHost,0,1)
        layout.addWidget(self.labelU,1,0)
        layout.addWidget(self.lineUser,1,1)
        layout.addWidget(self.labelAlert,2,1)
        layout.addWidget(self.goButton,3,1)
        layout.addWidget(self.SucButton,3,1)
        layout.addWidget(self.labelW8,3,1)
        layout.setRowStretch(0, 0)
        topGroupBox.setLayout(layout)
        mainLayout = QGridLayout()
        mainLayout.addWidget(topGroupBox, 1, 1)
        self.labelAlert.setHidden(True)
        self.labelW8.setHidden(True)
        self.labelTo.setHidden(True)
        self.SucButton.setHidden(True)
        self.goButton.clicked.connect(lambda:self.checkEnaf(self.lineHost.value(),self.lineUser.value()))
        self.SucButton.clicked.connect(lambda:self.close())
        self.setLayout(mainLayout)
        self.setWindowTitle("Auto Assign")



    def checkEnaf(self, request,number):
        f = open('./logs/'+self.Hostcurrent+'.json')
        data = json.load(f)
        f.close()
        port = data['get_vlans']['1']['interfaces']
        for dup in data['get_vlans']:
            if dup != '1':
                port = [inter for inter in port if inter not in data['get_vlans'][dup]['interfaces']]

        if len(port)>=number:
            give = len(port)-number
            del port[-give:]
            self.goButton.setHidden(True)
            self.labelW8.setHidden(False)
            runnable = RunAutoHost(request,number,self.Hostcurrent,self)
            QThreadPool.globalInstance().start(runnable)
            text = "Access Vlan "+str(request)+" to:\n"
            for i in port:
                text=text+i+'\n'
            self.labelTo.setText(text)
            self.labelAlert.setHidden(True)
        else:
            self.labelAlert.setHidden(False)
            self.labelAlert.setText('There is only '+str(len(port))+' available')
    @pyqtSlot(str)
    def successYeah(self,data):
        self.labelW8.setHidden(True)
        self.SucButton.setHidden(False)
        self.labelTo.setHidden(False)
        self.labelH.setHidden(True)
        self.lineHost.setHidden(True)
        self.labelU.setHidden(True)
        self.lineUser.setHidden(True)
        print(data)

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

        #print_result(result)
        f = open('hosts.yaml')
        data = yaml.load(f, Loader=yaml.FullLoader)
        f.close()



        if self.n =="1":
            result = nr.run(napalm_get, getters=['get_interfaces_ip','get_interfaces','get_facts','get_vlans'])
            for keyyaml in data:
                print(keyyaml)
                rjson = json.dumps(result[keyyaml].result, indent=2)
                with open("./logs/"+keyyaml+".json", "w") as outfile:
                 outfile.write(rjson)
        else:
            f = open('hosts.yaml')
            host = yaml.load(f, Loader=yaml.FullLoader)
            f.close()
            hostname = host[self.n]['hostname']
            sendto = nr.filter(hostname = hostname)
            result= sendto.run(napalm_get, getters=['get_interfaces_ip','get_interfaces','get_facts','get_vlans'])
            rjson = json.dumps(result[self.n].result, indent=2)
            with open("./logs/"+self.n+".json", "w") as outfile:
             outfile.write(rjson)

        QMetaObject.invokeMethod(self.w, "stopGet",
                                 Qt.QueuedConnection,
                                 Q_ARG(str, "gg"))

class TranferGroupVlan(QRunnable):
    def __init__(self, f,t,h,w):
        QRunnable.__init__(self)
        self.w = w
        self.fromv = f
        self.tov = t
        self.Hostcurrent = h
    def run(self,):
        f = open('./logs/'+self.Hostcurrent+'.json')
        data = json.load(f)
        f.close()

        commandAll = []
        port = data['get_vlans'][self.fromv]['interfaces']
        for dup in data['get_vlans']:
            if dup != self.fromv:
                    port = [inter for inter in port if inter not in data['get_vlans'][dup]['interfaces']]
        print(port)
        for interface in port:
            interfaceIn = "int "+interface
            commandAll.append(interfaceIn)
            commandAll.append("switchport mode access")
            accessVlan = "switchport access vlan "+self.tov
            commandAll.append(accessVlan)
            commandAll.append("exit")

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
        QMetaObject.invokeMethod(self.w, "successOK",
                                 Qt.QueuedConnection,
                                 Q_ARG(str, "Success"))

class RunAutoHost(QRunnable):
    def __init__(self, r,n,h,w):
        QRunnable.__init__(self)
        self.r = r
        self.n = n
        self.w = w
        self.Hostcurrent = h
    def run(self,):
        f = open('./logs/'+self.Hostcurrent+'.json')
        data = json.load(f)
        f.close()

        commandAll = []
        if (str(self.r) in data['get_vlans']):
                print("Vlaned")
        else :
            createV = "va "+ str(self.r)
            commandAll.append(createV)
            print("Create Vlan "+str(self.r))
        port = data['get_vlans']['1']['interfaces']
        for dup in data['get_vlans']:
            if dup != '1':
                port = [inter for inter in port if inter not in data['get_vlans'][dup]['interfaces']]
        print(port)
        if len(port)>=self.n:
            print(len(port))
            give = len(port)-self.n
            del port[-give:]
            print(len(port))
            for interface in port:
                interfaceIn = "int "+interface
                commandAll.append(interfaceIn)
                commandAll.append("switchport mode access")
                accessVlan = "switchport access vlan "+str(self.r)
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
            QMetaObject.invokeMethod(self.w, "successYeah",
                                 Qt.QueuedConnection,
                                 Q_ARG(str, "Success"))
        else :
            print("Not enough port available")

class AccessAllVlan(QRunnable):
    def __init__(self, f,h,w):
        QRunnable.__init__(self)
        self.w = w
        self.fromv = f
        self.Hostcurrent = h
    def run(self,):
        f = open('./logs/'+self.Hostcurrent+'.json')
        data = json.load(f)
        f.close()

        commandAll = []
        ports=[]
        interfaceData = data['get_facts']['interface_list']
        for intF in interfaceData:
                    vlans = data['get_vlans']
                    checkTrunking = 0
                    for vlan in vlans:
                        if intF in vlans[vlan]["interfaces"]:
                            if intF not in ports:
                                ports.append(intF)
                            checkTrunking = checkTrunking+1
                    if checkTrunking >1:
                        ports.remove(intF) 
        print(ports)       
        for interface in ports:
            interfaceIn = "int "+interface
            commandAll.append(interfaceIn)
            commandAll.append("switchport mode access")
            accessVlan = "switchport access vlan "+self.fromv
            commandAll.append(accessVlan)
            commandAll.append("exit")

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
        QMetaObject.invokeMethod(self.w, "successOK",
                                 Qt.QueuedConnection,
                                 Q_ARG(str, "Success"))

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
        self.updatingH = QLabel("UPDATING ....")
        styleLabel.setBuddy(styleComboBox)
        self.changeStyle(hostdict[0])
        self.useStylePaletteCheckBox = QCheckBox("&Use style's standard palette")
        self.useStylePaletteCheckBox.setChecked(True)
        self.loadData()



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
        self.loadButton = QPushButton("Reload")
        self.topLayout.addWidget(reButton)
        self.topLayout.addStretch(1)
        self.topLayout.addWidget(self.updatingH)
        self.topLayout.addWidget(self.loadButton)
        reButton.clicked.connect(self.winAddhost)
        self.loadButton.clicked.connect(lambda:self.clickload())
        #self.loadButton.setHidden(True)
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
        self.disableTrunk = QRadioButton("Trunk")
        self.disableTrunk.toggled.connect(self.spinVlan.setDisabled)
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
        layout.addWidget(self.disableTrunk,3,0)
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
        


    def hideUpdate(self):
        self.updatingH.setHidden(True)
        self.loadButton.setHidden(False)
    def showUpdate(self):
        self.updatingH.setHidden(False)
        self.loadButton.setHidden(True)
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

        changeButton = QPushButton("Tranfer Group")
        changeButton.setDefault(True)

        flatPushButton = QPushButton("Access all")
        flatPushButton.setFlat(False)

        layout = QVBoxLayout()
        layout.addWidget(autoButton)
        layout.addWidget(changeButton)
        layout.addWidget(flatPushButton)
        layout.addStretch(1)

        autoButton.clicked.connect(self.winAutohost)
        changeButton.clicked.connect(self.winTranferGroup)
        flatPushButton.clicked.connect(self.winAccessAll)
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
        trunkAllow = "switchport trunk allowed vlan "+self.lineAllowvlan.text()
        trunkNative = "switchport trunk native vlan "+str(self.spinNative.value())
        f = open('./logs/'+self.Hostcurrent+'.json')
        data = json.load(f)
        f.close()
        if self.disableAccess.isChecked():
            command = []
            if (str(self.spinVlan.value()) in data['get_vlans']):
                print("Vlaned")
            else :
                createV = "va "+ str(self.spinVlan.value())
                command.append(createV)
                print("Create Vlan "+str(self.spinVlan.value()))
            command.append(interface)
            if self.checkShut.isChecked():
                command.append("no Shutdown")
            else:
                command.append("Shutdown")
            command.append("switchport mode access")
            command.append(vlan)
            print(command)
            print(hostname)
            result= sendto.run(task=netmiko_send_config, config_commands=command)
            print_result(result)
            self.clickloadOne()
        if self.disableTrunk.isChecked():
            command = []
            command.append(interface)
            command.append("switchport mode trunk")
            command.append(trunkAllow)
            command.append(trunkNative)
            print(command)
            print(hostname)
            result= sendto.run(task=netmiko_send_config, config_commands=command)
            print_result(result)
            self.clickloadOne()
        self.winSent()
    def winAddhost(self, checked):
            self.w = AddHost()
            self.w.setGeometry(250, 100, 300, 200)
            self.w.show()
    def winSent(self):
            self.w = sendComplete()
            self.w.setGeometry(250, 100, 50, 100)
            self.w.show()
    def winTranferGroup(self, checked):
            self.t = TranferGroup(self.Hostcurrent)
            self.t.setGeometry(700, 150, 250, 150)
            self.t.show()
    def winAccessAll(self, checked):
            self.t = AccessAll(self.Hostcurrent)
            self.t.setGeometry(700, 150, 250, 150)
            self.t.show()
    def winLoading(self):
            self.w = PopupUpdate()
            self.w.setGeometry(250, 100, 400, 400)
            self.w.show()
    def winAutohost(self):
            self.a = AutoHost(self.Hostcurrent,self)
            self.a.setGeometry(700, 100, 300, 200)
            self.a.show()
    def clickload(self):
        self.showUpdate()
        runnable = GetHost("1",self)
        QThreadPool.globalInstance().start(runnable)
    def clickloadOne(self):
        self.showUpdate()
        runnable = GetHost(self.Hostcurrent,self)
        QThreadPool.globalInstance().start(runnable)
    @pyqtSlot(str)
    def stopGet(self, data):
        print(data)
        self.clicked()
        self.hideUpdate()

    def fromAuto(self, data):
        self.clickloadOne()

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
            print("Not enough port available")

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

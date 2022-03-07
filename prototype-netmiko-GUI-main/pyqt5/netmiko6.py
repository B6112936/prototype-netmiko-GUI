from netmiko import ConnectHandler

configlist=[]

def putCommand(inputco):
    configlist.append(inputco)


#configsw = ["int e0/2","no sh","ip address 172.168.2.1 255.255.255.0","end"]
def getCommand():
    device = {
        'host': '10.11.0.16',
        'username': 'non',
        'password': 'non',
        'secret': 'non',
        'device_type': 'cisco_ios'
    }
    with ConnectHandler(**device) as net_connect:
        net_connect.enable()
        output = net_connect.send_command('show version | include uptime')
        print(output.strip())
        output = net_connect.send_config_set(configlist)
        print(output.strip())

choice = ""

while choice != "stop":
    choice = input("What would you like to do")
    if choice != "stop":
        putCommand(choice)

configlist.extend(["int e0/2","no sh","ip address 172.168.2.1 255.255.255.0","end"])        
getCommand()


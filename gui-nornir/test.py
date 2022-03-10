from distutils import command
import json
import yaml
f = open('./logs/SW-CORE2.json')
data = json.load(f)
#datalen = len(data.get_facts["interface_list"])
print(len(data['get_facts']['interface_list']))
interfaceData = data['get_facts']['interface_list']
print(interfaceData)
f.close()

if ("3" in data['get_vlans']):
    print("ok")
else:
    print("no")

if "fa1" in "f2f4f1f5":
    print("ok")
commandAll = []
if len(data['get_vlans']['1']['interfaces'])>=5:
    print(len(data['get_vlans']['1']['interfaces']))
    port = data['get_vlans']['1']['interfaces']
    for dup in data['get_vlans']:
        if dup != '1':
            port = [inter for inter in port if inter not in data['get_vlans'][dup]['interfaces']]
    #print(port)
    for interface in port:
        interfaceIn = "int "+interface
        commandAll.append(interfaceIn)
        commandAll.append("switchport mode access")
        accessVlan = "switchport access vlan "+"20"
        commandAll.append(accessVlan)
        commandAll.append("exit")
    #print(commandAll)

commandAll = []
port1= "20"
port = data['get_vlans'][port1]['interfaces']
for dup in data['get_vlans']:
    if dup != port1:
            port = [inter for inter in port if inter not in data['get_vlans'][dup]['interfaces']]
print(port)
for interface in port:
    interfaceIn = "int "+interface
    commandAll.append(interfaceIn)
    commandAll.append("switchport mode access")
    accessVlan = "switchport access vlan "+port1
    commandAll.append(accessVlan)
    commandAll.append("exit")
#rint(commandAll)
newSW={
        'SW-CORE3': {
            'hostname': '10.11.0.72',
            'platform': 'ios',
            'username': 'non',
            'password': 'non'
        }
    }

with open('hosts.yaml','r') as yamlfile:
        cur_yaml = yaml.load(yamlfile,Loader=yaml.FullLoader)
        cur_yaml.update(newSW)
        print(cur_yaml)
with open(r'hosts.yaml', 'w') as file:
    documents = yaml.dump(cur_yaml, file)

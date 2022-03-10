from distutils import command
import json
import yaml
        
        
f = open('./logs/'+'SW-CORE'+'.json')
data = json.load(f)
ports=[]
interfaceData = data['get_facts']['interface_list']
for intF in interfaceData:
            vlans = data['get_vlans']
            typeport = "IP"
            checkTrunking = 0
            for vlan in vlans:
                if intF in vlans[vlan]["interfaces"]:
                    if intF not in ports:
                        ports.append(intF)
                    checkTrunking = checkTrunking+1
            if checkTrunking >1:
                ports.remove(intF) 
print(ports)       
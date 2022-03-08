from distutils import command
import json
f = open('./logs/SW-CORE.json')
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
    print(port)
    for interface in port:
        interfaceIn = "int "+interface
        commandAll.append(interfaceIn)
        


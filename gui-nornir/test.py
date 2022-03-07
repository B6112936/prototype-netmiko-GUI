import json
f = open('./logs/SW-CORE.json')
data = json.load(f)
#datalen = len(data.get_facts["interface_list"])
print(len(data['get_facts']['interface_list']))
interfaceData = data['get_facts']['interface_list']
print(interfaceData)
f.close()
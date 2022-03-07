import json
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

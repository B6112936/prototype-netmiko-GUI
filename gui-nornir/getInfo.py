from gzip import READ
from importlib.abc import Loader
import json
import yaml
import os
import re
from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_napalm.plugins.tasks import napalm_get,napalm_cli,napalm_configure
from nornir_netmiko.tasks import netmiko_send_config,netmiko_send_command
from nornir.core.filter import F
def dictojson(dict):
    return json.dumps(dict, indent=2)

nr = InitNornir(
    config_file="config.yaml",
    logging={"enabled": False},
    runner={"plugin": "threaded", "options": {"num_workers": 20}},
)

onlyhost = nr.filter(hostname= '10.10.99.254')
result = nr.run(napalm_get, getters=['get_interfaces_ip','get_interfaces','get_facts','get_vlans'])
print_result(result)

f = open('hosts.yaml')
data = yaml.load(f, Loader=yaml.FullLoader)
f.close()


for keyyaml in data:
    print(keyyaml)
    rjson = dictojson(result[keyyaml].result)
    #jstr = json.loads(rjson)
    with open("./logs/"+keyyaml+".json", "w") as outfile:
      outfile.write(rjson)





#jstr = json.loads(rjson)
#keyd = (jstr['get_interfaces'].keys())
#for key in jstr['get_interfaces']:
 #   print(key)
print(data)


#result2= nr.run(task=napalm_cli, commands=["vlan database","vlan 11"])
#result2= nr.run(task=netmiko_send_config, config_commands=['do vlan database','vlan 11'])
#result2= nr.run(task=netmiko_send_command, command_string=["sh vlan-switch"])

from gzip import READ
import json
import re
from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_napalm.plugins.tasks import napalm_get,napalm_cli

def dictojson(dict):
    return json.dumps(dict, indent=2)

nr = InitNornir(
    config_file="config.yaml",
    logging={"enabled": False},
    runner={"plugin": "threaded", "options": {"num_workers": 15}},
)

result = nr.run(napalm_get, getters=['get_interfaces_ip','get_interfaces','get_facts'])
result2= nr.run(task=napalm_cli, commands=["show cdp neighbors"])
print_result(result2)
rjson = dictojson(result['sw1'].result)
jstr = json.loads(rjson)
keyd = (jstr['get_interfaces'].keys())
for key in jstr['get_interfaces']:
    print(key)

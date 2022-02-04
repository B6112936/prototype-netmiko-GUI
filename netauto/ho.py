from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_napalm.plugins.tasks import napalm_get
nr = InitNornir(
    config_file="config.yaml",
    logging={"enabled": False},
    runner={"plugin": "threaded", "options": {"num_workers": 15}},
)

result = nr.run(napalm_get, getters=['get_interfaces_ip','get_interfaces'])


print_result(result)

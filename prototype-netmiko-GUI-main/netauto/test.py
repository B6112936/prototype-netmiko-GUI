from nornir import InitNornir
from nornir_utils.plugins.functions import print_result,print_title
from nornir_napalm.plugins.tasks import napalm_get
nr = InitNornir(
)

result = nr.run(
    task=napalm_get,getters=["fact","interfaces","environment","interfaces_ip"]
)

print_result(result)

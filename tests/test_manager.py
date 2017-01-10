from pylm.registry.manager import ClusterManager


cluster = """
[DEFAULT]

[Valuation Manager]
Script = valuation_standalone_master.py
--pull = $1
--pub = $2
--workerpull = $3
--workerpush = $4
--db = $5
MinReplicas = 1
MaxReplicas = 1

[Valuation Worker]
Script = valuation_worker.py
--db = $5
MinReplicas = 1
MaxReplicas = 32
"""

server = """
[My Server]
ip = 127.0.0.1
processors = 3
ports_from = 5555
"""


def test_load():
    manager = ClusterManager(cluster)
    for s in manager.requested_services:
        print(s)
    assert len(manager.requested_services) == 3
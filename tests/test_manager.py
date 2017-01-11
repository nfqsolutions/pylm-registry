from pylm.registry.manager import ClusterManager


cluster = """
[Valuation Master]
Script = valuation_standalone_master.py
--pull = {_1}
--pub = {_2}
--workerpull = {_3}
--workerpush = {_4}
--db = {_5}
Role = Master
Replicas = 0

[Valuation Worker]
Script = valuation_worker.py
--db = {_5}
Connected = Valuation Master
Role = Worker
"""

server = """
[DEFAULT]
Name = My Worker
Ip = 127.0.0.1
Processors = 3
Ports_from = 5555
"""


def test_00load_cluster():
    manager = ClusterManager(cluster)
    for s in manager.requested_services:
        print(s)
    assert len(manager.requested_services) == 3


def test_01simple_request():
    manager = ClusterManager(cluster)
    manager.process_resource(server)
    assert 0 == 1
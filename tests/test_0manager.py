from pylm.registry.handlers.manager import ConfigManager


cluster = """
[Valuation Master]
Script = python3 valuation_standalone_master.py
--pull = _1
--pub = _2
--workerpull = _3
--workerpush = _4
--db = _5

[Valuation Worker]
Script = python3 valuation_worker.py
--db = _5
Connected = Valuation Master
Role = Worker
Replicas = 1
"""

server = """
[DEFAULT]
Name = My Worker
Ip = 127.0.0.1
Processors = 3
Ports_from = 5555
"""

server1 = """
[DEFAULT]
Name = My Worker
Ip = 127.0.0.1
Processors = 1
Ports_from = 5555
"""
server2 = """
[DEFAULT]
Name = My Worker
Ip = 127.0.0.2
Processors = 2
Ports_from = 5555
"""


def test_00load_cluster():
    manager = ConfigManager(cluster)
    for s in manager.requested_services:
        print(s)
    assert len(manager.requested_services) == 3


def test_01simple_request():
    manager = ConfigManager(cluster)
    commands = manager.process_resource(server)
    assert commands == ['python3 valuation_standalone_master.py '
                        '--pull tcp://127.0.0.1:5555 '
                        '--pub tcp://127.0.0.1:5556 '
                        '--workerpull tcp://127.0.0.1:5557 '
                        '--workerpush tcp://127.0.0.1:5558 '
                        '--db tcp://127.0.0.1:5559',
                        'python3 valuation_worker.py --db tcp://127.0.0.1:5559',
                        'python3 valuation_worker.py --db tcp://127.0.0.1:5559']


def test_02multiple_requests():
    manager = ConfigManager(cluster)

    commands = manager.process_resource(server1)
    assert commands == ['python3 valuation_standalone_master.py '
                        '--pull tcp://127.0.0.1:5555 '
                        '--pub tcp://127.0.0.1:5556 '
                        '--workerpull tcp://127.0.0.1:5557 '
                        '--workerpush tcp://127.0.0.1:5558 '
                        '--db tcp://127.0.0.1:5559']

    commands = manager.process_resource(server2)
    assert commands == ['python3 valuation_worker.py --db tcp://127.0.0.1:5559',
                        'python3 valuation_worker.py --db tcp://127.0.0.1:5559']


"""
Functional test. It is about sending the server logs to the registry. All
processes have to be run manually.
"""

# Activate the registry in your local machine with
# pylm-registry --config pylm/registry/static/registry.conf --sync

# In a different console, go to the static folder where all the
# test configuration files are

# >>> from pylm.registry.clients import *
# >>> admin_key = new_admin_account(uri='http://localhost:8080', admin_name='Admin', key='admin', master_key='test')
# >>> admin = AdminClient('http://localhost:8080', admin_key)
# >>> user_key = admin.new_user(name='Any name')
# >>> client = RegistryClient('http://localhost:8080', user_key)
# >>> client.set_cluster('echo_cluster.conf')
# 77345592-0ca1-4366-839f-67b4a84ddf2d

# The code that the command returns is a cluster key, that has to be used to connect
# The runner to the client. In a different console we can now run the runner

# pylm-runner --registry http://localhost:8080 --cluster 77345592-0ca1-4366-839f-67b4a84ddf2d --config node2.conf

# This starts the test runners, that start sending logs to the central registry.
# To check the contents of the log, we can go back to the interactive console,

# >>> logs = LogClient('http://localhost:8080', '77345592-0ca1-4366-839f-67b4a84ddf2d')
# >>> logs.view()

# And you should see lots of logs. You can now kill the registry and the runner.
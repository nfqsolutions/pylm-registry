import inspect
import os

import pylm.registry


ROOT_PATH = os.path.abspath(os.path.join(
    inspect.getfile(pylm.registry),
    os.pardir)
    )

STATIC_PATH = os.path.abspath(os.path.join(
    inspect.getfile(pylm.registry),
    os.pardir,
    'static')
    )

from pylm.registry.handlers.index import IndexHandler
from pylm.registry.handlers.static import StaticHandler
from pylm.registry.handlers.cluster import ClusterHandler
from pylm.registry.handlers.logs import LogsHandler
from pylm.registry.handlers.login import LoginHandler
from pylm.registry.handlers.base import BaseHandler
from pylm.registry.handlers.dashboard import DashboardHandler, \
    NewClusterHandler, ViewClusterHandler, ViewLogsHandler, NewUserHandler, \
    LogoutHandler
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
from pylm.registry.handlers.admin import AdminHandler
from pylm.registry.handlers.cluster import ClusterHandler
from pylm.registry.handlers.logs import LogsHandler

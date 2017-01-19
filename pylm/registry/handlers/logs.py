import json
from datetime import datetime

import tornado.web
from sqlalchemy import and_

from pylm.registry.handlers.persistency.db import DB
from pylm.registry.handlers.persistency.models import ClusterLog, Cluster


class LogsHandler(tornado.web.RequestHandler):
    def get(self):
        cluster = self.get_argument('cluster')
        fr = self.get_argument('fr', default='1970-01-01T00:00:00.000000')
        to = self.get_argument('to', default='2200-01-01T00:00:00.000000')

        # Parse the dates
        fr = datetime.strptime(fr, "%Y-%m-%dT%H:%M:%S.%f")
        to = datetime.strptime(to, "%Y-%m-%dT%H:%M:%S.%f")

        logs = list()
        for log_line in DB.session.query(
            ClusterLog
        ).filter(and_(ClusterLog.cluster == cluster,
                      ClusterLog.when < to,
                      ClusterLog.when > fr)).all():
            logs.append(log_line.to_dict())

        self.set_status(200)
        self.write(json.dumps(logs).encode('utf-8'))

    def post(self):
        cluster = self.get_argument('cluster')
        cluster_in_db = DB.session.query(
            Cluster).filter(Cluster.key == cluster).one_or_none()

        if cluster_in_db:
            log = ClusterLog()
            log.when = datetime.now()
            log.cluster = cluster

            # This is important. A Post request requires something
            # in its body, otherwise it gives a 599 HTTP error.
            log.text = self.request.body

            DB.session.add(log)
            DB.session.commit()

            self.set_status(200)
            self.write(b'')

        else:
            self.set_status(400)
            self.write(b'')

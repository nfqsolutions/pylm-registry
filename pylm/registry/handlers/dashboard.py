from pylm.registry.handlers.base import BaseHandler
from pylm.registry.handlers.persistency.models import User, Cluster, ClusterLog
from pylm.registry.handlers.persistency.db import DB
from pylm.registry.handlers import ROOT_PATH
from uuid import uuid4
from sqlalchemy import and_
import tornado
import datetime
import pickle
import os


class DashboardHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        user = DB.session.query(User).filter(User.name == name).one_or_none()
        template_dir = os.path.join(ROOT_PATH, 'templates')
        loader = tornado.template.Loader(template_dir)
        self.write(loader.load("dashboard.html").generate(
            user=user)
        )


class NewClusterHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        user = DB.session.query(User).filter(User.name == name).one_or_none()
        template_dir = os.path.join(ROOT_PATH, 'templates')
        loader = tornado.template.Loader(template_dir)
        self.write(loader.load("new_cluster.html").generate(
            user=user)
        )

    @tornado.web.authenticated
    def post(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        user = DB.session.query(User).filter(User.name == name).one_or_none()
        description = self.get_argument("description")
        new_cluster = Cluster()
        new_cluster.description = description
        new_cluster.user = user
        new_cluster.key = str(uuid4())
        new_cluster.when = datetime.datetime.now()

        DB.session.add(new_cluster)
        DB.session.commit()

        self.redirect('/dashboard')


class ViewClusterHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)

        cluster = DB.session.query(
            Cluster
            ).filter(Cluster.key == self.get_argument("cluster")).one_or_none()

        template_dir = os.path.join(ROOT_PATH, 'templates')
        loader = tornado.template.Loader(template_dir)
        if cluster.status:
            status = pickle.load(cluster.status)
        else:
            status = ''

        self.write(loader.load("view_cluster.html").generate(
            cluster=cluster,
            status=status)
        )


class ViewLogsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)

        cluster = self.get_argument('cluster')
        fr = self.get_argument('fr', default='1970-01-01T00:00:00.000000')
        to = self.get_argument('to', default='2200-01-01T00:00:00.000000')

        logs = list()
        for log_line in DB.session.query(
            ClusterLog
        ).filter(and_(ClusterLog.cluster == cluster,
                      ClusterLog.when < to,
                      ClusterLog.when > fr)).all():
            logs.append(log_line.to_dict())

        self.set_status(200)
        for log in logs:
            self.write(str(log).encode('utf-8'))
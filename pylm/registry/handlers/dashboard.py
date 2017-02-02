from pylm.registry.handlers.base import BaseHandler
from pylm.registry.handlers.persistency.models import User, Cluster
from pylm.registry.handlers.persistency.db import DB
from pylm.registry.handlers import ROOT_PATH
from uuid import uuid4
import tornado
import datetime
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
    @tornado.web.autenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
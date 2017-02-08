from pylm.registry.handlers.base import BaseHandler
from pylm.registry.handlers.persistency.models import User, Cluster, ClusterLog
from pylm.registry.handlers.persistency.db import DB
from pylm.registry.handlers import ROOT_PATH
from pylm.registry.application import password_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
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

        users = DB.session.query(User).all()

        self.write(loader.load("dashboard.html").generate(
            user=user,
            users=users)
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
        user = DB.session.query(User).filter(User.name == name).one_or_none()

        cluster = DB.session.query(
            Cluster
            ).filter(Cluster.key == self.get_argument("cluster")).one_or_none()

        template_dir = os.path.join(ROOT_PATH, 'templates')
        loader = tornado.template.Loader(template_dir)
        if cluster.status:
            status = pickle.loads(cluster.status)
        else:
            status = ''

        if user == cluster.user:
            self.write(loader.load("view_cluster.html").generate(
                cluster=cluster,
                status=status)
            )
        else:
            self.redirect('/dashboard?error=forbidden')


class ViewLogsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        user = DB.session.query(User).filter(User.name == name).one_or_none()

        cluster = self.get_argument('cluster')
        clusterobj = DB.session.query(
            Cluster
        ).filter(Cluster.key == cluster).one_or_none()

        fr = self.get_argument('fr', default='1970-01-01T00:00:00.000000')
        to = self.get_argument('to', default='2200-01-01T00:00:00.000000')

        logs = list()
        for log_line in DB.session.query(
            ClusterLog
        ).filter(and_(ClusterLog.cluster == cluster,
                      ClusterLog.when < to,
                      ClusterLog.when > fr)).all():
            logs.append(log_line.to_dict())

        if user == clusterobj.user:
            self.set_status(200)
            for log in logs:
                self.write(str(log).encode('utf-8'))
        else:
            self.redirect('/dashboard?error=forbidden')


class NewUserHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)

        template_dir = os.path.join(ROOT_PATH, 'templates')
        loader = tornado.template.Loader(template_dir)
        self.write(loader.load("new_user.html").generate())

    @tornado.web.authenticated
    def post(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        user = DB.session.query(User).filter(User.name == name).one_or_none()

        kpdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.settings['secret'].encode('utf-8'),
            iterations=1000000,
            backend=password_backend
        )

        new_user = User()
        new_user.name = tornado.escape.xhtml_escape(self.get_argument('name'))
        new_user.password = kpdf.derive(
            tornado.escape.xhtml_escape(
                self.get_argument('password')
            ).encode('utf-8'))
        new_user.fullname = tornado.escape.xhtml_escape(
            self.get_argument('fullname')
        )
        new_user.email = self.get_argument('email')
        new_user.key = str(uuid4())
        new_user.active = True
        new_user.admin = False
        new_user.when = datetime.datetime.now()

        if user.admin:
            DB.session.add(new_user)
            DB.session.commit()
            self.redirect('/dashboard')
        else:
            self.redirect('/dashboard?error=forbidden')


class ResetHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        user = DB.session.query(User).filter(User.name == name).one_or_none()

        cluster = self.get_argument('cluster')
        clusterobj = DB.session.query(
            Cluster
        ).filter(Cluster.key == cluster).one_or_none()

        if user == clusterobj.user:
            clusterobj.status = b''
            DB.session.commit()

        self.redirect('/view_cluster?cluster={}'.format(cluster))


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect('/')


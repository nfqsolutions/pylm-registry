from pylm.registry.config import configuration
from pylm.registry.db import DB
from pylm.registry.models import AdminProfile, UserProfile, AdminLog
from uuid import uuid4
import tornado.web
import tornado.template
import pylm.registry
import datetime
import inspect
import os

ROOT_PATH = os.path.abspath(os.path.join(
    inspect.getfile(pylm.registry),
    os.pardir)
    )

STATIC_PATH = os.path.abspath(os.path.join(
    inspect.getfile(pylm.registry),
    os.pardir,
    'static')
    )


def db_log(text):
    log_item = AdminLog()
    log_item.when = datetime.datetime.now()
    log_item.text = text

    DB.session.add(log_item)
    DB.session.commit()


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        template_dir = os.path.join(ROOT_PATH, 'templates')
        loader = tornado.template.Loader(template_dir)
        self.write(loader.load("index.html").generate(
            version=pylm.registry.__version__)
        )


class ClusterHandler(tornado.web.RequestHandler):
    def get(self):
        template_dir = os.path.join(ROOT_PATH, 'templates')
        loader = tornado.template.Loader(template_dir)
        self.write(loader.load("cluster.html").generate(
            version=pylm.registry.__version__))


class AdminHandler(tornado.web.RequestHandler):
    def set_new_admin(self):
        """
        Set new admin

        :return:
        """
        if 'Key' in self.request.headers:
            if self.request.headers['Key'] == configuration['Admin']['Key']:
                # This part generates an administrator user and key
                user_key = self.get_argument('key', default=str(uuid4()))
                name = self.get_argument('name', default='No name given')
                
                admin = AdminProfile()
                admin.key = user_key
                admin.name = name
                admin.when = datetime.datetime.now()

                DB.session.add(admin)
                DB.session.commit()

                db_log('Created Admin {}'.format(name))
                
                self.set_status(200)
                self.write(user_key.encode('utf-8'))
            else:
                self.set_status(400)
                self.write(b'Bad master key')
        else:
            self.set_status(400)
            self.write(b'Key not present')

    def set_new_user(self):
        """
        Set new user

        :return: User key as bits
        """
        if 'Key' in self.request.headers:
            admin_key = self.request.headers['Key']
            # Check if the admin key is one of the valid admins.
            all_admin = DB.session.query(AdminProfile).all()
            all_admin_keys = [a.key for a in all_admin]

            if admin_key in all_admin_keys:
                user_key = self.get_argument('key', default=str(uuid4()))
                name = self.get_argument('name', default='Anonymous')
                data = self.get_argument('data', default='')

                user = UserProfile()
                user.key = user_key
                user.when = datetime.datetime.now()
                user.data = data
                user.name = name

                DB.session.add(user)
                DB.session.commit()

                db_log('Create user {}'.format(name))

                self.set_status(200)
                self.write(user_key.encode('utf-8'))

            else:
                self.set_status(400)
                self.write(b'Admin key not valid')

        else:
            self.set_status(400)
            self.write(b'Admin key not present')

    def get(self):
        methods = {
            'new_admin': self.set_new_admin,
            'new_user': self.set_new_user
        }
        user_method = self.get_argument('method', default=False)

        if user_method and user_method in methods:
            methods[self.get_argument('method')]()
        else:
            self.set_status(400)
            self.write(b'Bad method or method not present')


class StaticHandler(tornado.web.RequestHandler):
    @staticmethod
    def get_favicon():
        with open(os.path.join(STATIC_PATH, 'favicon.ico'), 'rb') as file_handler:
            return file_handler.read()

    def get(self):
        parser_dict = {
            '/favicon.ico': self.get_favicon
        }
        self.write(parser_dict[self.request.uri]())

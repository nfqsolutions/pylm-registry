from pylm.registry.config import configuration
from pylm.registry.db import DB
from pylm.registry.models import Admin, User, AdminLog, Cluster
from pylm.registry.manager import ConfigManager
from uuid import uuid4
import pandas as pd
import tornado.web
import tornado.template
import pylm.registry
import datetime
import inspect
import json
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
    def is_user(self):
        """
        Check if the request is from a user with admin privileges

        :return: True if has admin privileges, False otherwise
        """
        if 'Key' in self.request.headers:
            user_key = self.request.headers['Key']
            # Check if the admin key is one of the valid admins.
            is_user = DB.session.query(
                User).filter(User.key == user_key).one_or_none()

            if is_user:
                return True

            else:
                self.set_status(400)
                self.write(b'User key not valid')

        else:
            self.set_status(400)
            self.write(b'User key not present')

        return False

    def set_new_cluster(self):
        if self.is_user():
            # Get the user from the user key
            user_key = self.request.headers['Key']
            user = DB.session.query(
                User).filter(User.key == user_key).one_or_none()

            cluster = Cluster()
            cluster.key = self.get_argument('key', default=str(uuid4()))
            cluster.description = self.get_argument('description')
            cluster.when = datetime.datetime.now()
            cluster.status = ''
            cluster.user = user

            DB.session.add(cluster)
            DB.session.commit()

            self.set_status(200)
            self.write(cluster.key.encode('utf-8'))

    def get_clusters_list(self):
        if self.is_user():
            # Get the user from the user key
            user_key = self.request.headers['Key']
            user = DB.session.query(
                User).filter(User.key == user_key).one_or_none()

            clusters_dump = dict()
            for cluster in user.clusters:
                clusters_dump[cluster.key] = {
                    "description": cluster.description
                }

            self.set_status(200)
            self.write(json.dumps(clusters_dump).encode('utf-8'))

    def set_cluster_reset(self):
        if self.is_user():
            cluster_key = self.get_argument('cluster')
            cluster_data = DB.session.query(
                Cluster).filter(Cluster.key == cluster_key).one_or_none()
            cluster_data.status = ''
            DB.session.commit()

            self.set_status(200)
            self.write(cluster_key.encode('utf-8'))

    def get_node_config(self):
        if self.is_user():
            cluster_key = self.get_argument('cluster')
            node_specs = self.get_argument('node')
            cluster_data = DB.session.query(
                Cluster).filter(Cluster.key == cluster_key).one_or_none()

            # Assign the configuration
            configurator = ConfigManager(cluster_data.description)
            # Load the temporal status of the cluster
            configurator.load_status(cluster_data.status)
            # Process the node configuration
            commands = configurator.process_resource(node_specs)
            # Update the cluster status in the database.
            cluster_data.status = configurator.dump_status()
            DB.session.commit()

            self.set_status(200)
            self.write(json.dumps(commands).encode('utf-8'))

    def get(self):
        methods = {
            'new_cluster': self.set_new_cluster,
            'clusters_list': self.get_clusters_list,
            'node_config': self.get_node_config,
            'cluster_reset': self.set_cluster_reset
        }
        user_method = self.get_argument('method', default=False)

        if user_method and user_method in methods:
            methods[self.get_argument('method')]()
        else:
            self.set_status(400)
            self.write(b'Bad method or method not present')


class AdminHandler(tornado.web.RequestHandler):
    def is_admin(self):
        """
        Check if the request is from a user with admin privileges

        :return: True if has admin privileges, False otherwise
        """
        if 'Key' in self.request.headers:
            admin_key = self.request.headers['Key']
            # Check if the admin key is one of the valid admins.
            is_admin = DB.session.query(
                Admin).filter(Admin.key == admin_key).one_or_none()

            if is_admin:
                return True

            else:
                self.set_status(400)
                self.write(b'Admin key not valid')

        else:
            self.set_status(400)
            self.write(b'Admin key not present')

        return False

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
                
                admin = Admin()
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
        if self.is_admin():
            user_key = self.get_argument('key', default=str(uuid4()))
            name = self.get_argument('name', default='Anonymous')
            data = self.get_argument('data', default='')

            user = User()
            user.key = user_key
            user.when = datetime.datetime.now()
            user.data = data
            user.name = name

            DB.session.add(user)
            DB.session.commit()

            db_log('Create user {}'.format(name))

            self.set_status(200)
            self.write(user_key.encode('utf-8'))

    def get_user_list(self):
        """
        Get a list of users

        :return: User key as bits
        """
        if self.is_admin():
            users = pd.read_sql('users', DB.engine)
            self.set_status(200)
            self.write(users.to_csv().encode('utf-8'))

    def set_user_inactive(self):
        pass

    def get(self):
        methods = {
            'new_admin': self.set_new_admin,
            'new_user': self.set_new_user,
            'user_list': self.get_user_list
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

import datetime
import json
import pickle
from uuid import uuid4

import tornado.web

from pylm.registry.handlers.manager import ConfigManager
from pylm.registry.handlers.persistency.db import DB
from pylm.registry.handlers.persistency.models import User, Cluster


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

            if is_user and is_user.active:
                return True

            elif is_user and not is_user.active:
                self.set_status(400)
                self.write(b'User not active')

            else:
                self.set_status(400)
                self.write(b'User key not valid')

        else:
            self.set_status(400)
            self.write(b'User key not present')

        return False

    def is_owner(self, cluster):
        """
        Check if the request is from the user that owns the cluster

        :return: True or False
        """
        if self.is_user():
            user_key = self.request.headers['key']
            user = DB.session.query(
                User
            ).filter(User.key == user_key).one_or_none()
            clusters = [cluster.key for cluster in user.clusters]
            if cluster in clusters:
                return True

            else:
                self.set_status(400)
                self.write(b'User does not own the cluster')
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
            cluster.status = b''
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
                clusters_dump[cluster.key] = cluster.to_dict()

            self.set_status(200)
            self.write(json.dumps(clusters_dump).encode('utf-8'))

    def set_cluster_reset(self):
        cluster_key = self.get_argument('cluster')
        if self.is_owner(cluster_key):
            cluster_data = DB.session.query(
                Cluster).filter(Cluster.key == cluster_key).one_or_none()
            cluster_data.status = b''
            DB.session.commit()

            self.set_status(200)
            self.write(cluster_key.encode('utf-8'))

    def set_cluster_delete(self):
        cluster_key = self.get_argument('cluster')
        if self.is_owner(cluster_key):
            cluster = DB.session.query(
                Cluster
                ).filter(Cluster.key == cluster_key).one_or_none()

            DB.session.delete(cluster)
            DB.session.commit()

            self.set_status(200)
            self.write(cluster_key)

    def get_cluster_status(self):
        cluster_key = self.get_argument('cluster')
        if self.is_owner(cluster_key):
            cluster = DB.session.query(
                Cluster).filter(Cluster.key == cluster_key).one_or_none()

            if cluster.status:
                serialized_status = pickle.loads(cluster.status)
                cluster_status = json.dumps(
                    {
                        "socket mapping": serialized_status[0],
                        "configured resources": serialized_status[1],
                        "highest port used": serialized_status[2],
                        "ready": serialized_status[3]
                    }
                )
            else:
                cluster_status = ''

            self.set_status(200)
            self.write(cluster_status.encode('utf-8'))

    def get_node_config(self):
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
            'cluster_reset': self.set_cluster_reset,
            'cluster_delete': self.set_cluster_delete,
            'cluster_status': self.get_cluster_status
        }
        user_method = self.get_argument('method', default=False)

        if user_method and user_method in methods:
            methods[self.get_argument('method')]()
        else:
            self.set_status(400)
            self.write(b'Bad method or method not present')

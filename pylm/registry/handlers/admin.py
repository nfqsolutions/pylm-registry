import datetime
import json
from uuid import uuid4

import tornado.web

from pylm.registry.handlers.persistency.db import DB
from pylm.registry.handlers.persistency.models import Admin, User
from pylm.registry.handlers.persistency.models import AdminLog


def admin_log(text):
    log_item = AdminLog()
    log_item.when = datetime.datetime.now()
    log_item.text = text

    DB.session.add(log_item)
    DB.session.commit()


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
                # User key query param may be missing
                user_key = self.get_argument('key', default=str(uuid4()))

                # User key can be an empty string
                if not user_key:
                    user_key = str(uuid4())

                name = self.get_argument('name', default='Anonymous')

                admin = Admin()
                admin.key = user_key
                admin.name = name
                admin.when = datetime.datetime.now()

                DB.session.add(admin)
                DB.session.commit()

                admin_log('Created Admin {}'.format(name))

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
            user.active = True

            DB.session.add(user)
            DB.session.commit()

            admin_log('Create user {}'.format(name))

            self.set_status(200)
            self.write(user_key.encode('utf-8'))

    def set_delete_user(self):
        if self.is_admin():
            user_key = self.get_argument('key')
            user = DB.session.query(
                User
            ).filter(User.key == user_key).one_or_none()
            DB.session.delete(user)
            admin_log('Deleted user {}'.format(user.name))

            self.set_status(200)
            self.write(user_key.encode('utf-8'))

    def get_user_list(self):
        """
        Get a list of users

        :return: User key as bits
        """
        if self.is_admin():
            user_list = [u.to_dict() for u in DB.session.query(User).all()]
            self.set_status(200)
            self.write(json.dumps(user_list).encode('utf-8'))

    def get_user(self):
        """
        Get user from its id key

        :return:
        """
        if self.is_admin():
            user_key = self.get_argument('key')
            user = DB.session.query(
                User).filter(User.key == user_key).one_or_none()

            self.set_status(200)
            self.write(user.to_json().encode('utf-8'))

    def set_deactivate_user(self):
        if self.is_admin():
            user_key = self.get_argument('key')
            user = DB.session.query(
                User).filter(User.key == user_key).one_or_none()
            user.active = False

            DB.session.commit()

    def set_activate_user(self):
        if self.is_admin():
            user_key = self.get_argument('key')
            user = DB.session.query(
                User).filter(User.key == user_key).one_or_none()
            user.active = True

            DB.session.commit()

    def get(self):
        methods = {
            'new_admin': self.set_new_admin,
            'new_user': self.set_new_user,
            'user_list': self.get_user_list,
            'user': self.get_user,
            'activate_user': self.set_activate_user,
            'deactivate_user': self.set_deactivate_user,
            'delete_user': self.set_delete_user
        }
        user_method = self.get_argument('method', default=False)

        if user_method and user_method in methods:
            methods[self.get_argument('method')]()
        else:
            self.set_status(400)
            self.write(b'Bad method or method not present')
from pylm.registry.handlers.base import BaseHandler
from pylm.registry.application import password_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidKey
from pylm.registry.handlers.persistency.models import User
from pylm.registry.handlers.persistency.db import DB
from pylm.registry.handlers import ROOT_PATH
import tornado
import os


class LoginHandler(BaseHandler):
    def get(self):
        template_dir = os.path.join(ROOT_PATH, 'templates')
        loader = tornado.template.Loader(template_dir)
        self.write(loader.load("login.html").generate())

    def post(self):
        user = DB.session.query(
                User).filter(User.name == self.get_argument(
            "name")).one_or_none()
        if user:
            password = self.get_argument("password").encode('utf-8')

            kpdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.settings['secret'].encode('utf-8'),
                iterations=1000000,
                backend=password_backend
            )
            try:
                kpdf.verify(password, user.password)
                self.set_secure_cookie("user", self.get_argument("name"))
                self.redirect("/dashboard")

            except InvalidKey:
                print(self.get_argument("password"))
                print(user.password)
                self.redirect("/login?status=wrongpassword")
        else:
            self.redirect("/login?status=usernotfound")


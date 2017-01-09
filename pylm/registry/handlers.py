from pylm.registry.config import configuration
from uuid import uuid4
import tornado.web
import tornado.template
import pylm.registry
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

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        template_dir = os.path.join(ROOT_PATH, 'templates')
        loader = tornado.template.Loader(template_dir)
        self.write(loader.load("index.html").generate(version=pylm.registry.__version__))


class ClusterHandler(tornado.web.RequestHandler):
    def get(self):
        template_dir = os.path.join(ROOT_PATH, 'templates')
        loader = tornado.template.Loader(template_dir)
        self.write(loader.load("cluster.html").generate(version=pylm.registry.__version__))


class AdminHandler(tornado.web.RequestHandler):
    def get_new_key(self):
        if 'Key' in self.request.headers:
            if self.request.headers['Key'] == configuration['Admin']['Key']:
                # This part generates an administrator user and key
                self.set_status(200)
                self.write('Admin interface')
            else:
                self.set_status(400)
                self.write(b'Bad master key')
        else:
            self.set_status(400)
            self.write(b'Key not present')

    def get(self):
        methods = {
            'new': self.get_new_key
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
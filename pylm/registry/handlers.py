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
        #print(self.request.headers)
        self.write(loader.load("index.html").generate(version=pylm.registry.__version__))


class ClusterHandler(tornado.web.RequestHandler):
    def get(self):
        template_dir = os.path.join(ROOT_PATH, 'templates')
        loader = tornado.template.Loader(template_dir)
        self.write(loader.load("cluster.html").generate(version=pylm.registry.__version__))


class AdminHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('Admin interface')


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
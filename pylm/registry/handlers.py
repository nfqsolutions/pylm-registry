import tornado.web
import tornado.template
import pylm.registry
import os


ROOT_PATH = os.path.join(os.path.abspath(pylm.registry.__file__), os.pardir)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        loader = tornado.template.Loader(os.path.join(ROOT_PATH, 'templates'))
        self.write(loader.load("index.html").generate(version=pylm.registry.__version__))

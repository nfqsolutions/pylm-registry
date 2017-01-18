import os

import tornado.template
import tornado.web

import pylm.registry
from pylm.registry.handlers import ROOT_PATH


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        template_dir = os.path.join(ROOT_PATH, 'templates')
        loader = tornado.template.Loader(template_dir)
        self.write(loader.load("index.html").generate(
            version=pylm.registry.__version__)
        )
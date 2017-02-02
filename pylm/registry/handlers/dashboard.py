from pylm.registry.handlers.base import BaseHandler
import tornado


class DashboardHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        self.write("Hello, " + name)

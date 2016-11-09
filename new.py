#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys

import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import options, define
from tornado.log import logging

from model import User
from model import Post
from model import session


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/archive", ArchiveHandler),
            (r"/feed", FeedHandler),
            (r"/entry/([^/]+)", EntryHandler),
            (r"/compose", ComposeHandler),
            (r"/auth/create", AuthCreateHandler),
            (r"/auth/login", AuthLoginHandler),
            (r"/auth/logout", AuthLogoutHandler),
        ]
        settings = dict(
            blog_title=u"Tornado Blog",
            template_path=os.path.join(os.path.dirname(__file__), "template"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            ui_modules={"Entry": EntryModule},
            xsrf_cookies=True,
            cookie_secret="$2b$12$ggtyoLhkugxfy355uXv/eu",
            login_url="/auth/login",
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)
        

class BaseHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("hello world")

    def get_current_user(self):
        username = self.get_secure_cookie("username")
        if not username: return None
        return session.query(User).filter_by(username=username).first()

    def any_author_exists(self):
        return bool(session.query(User).count())


class HomeHandler(BaseHandler):
    def get(self):
        entries = session.query(Post).limit(5)
        if not entries:
            self.redirect("/compose")
            return
        self.render("home.html", entries=entries)


class EntryHandler(BaseHandler):
    pass



class IndexHandler(BaseHandler):
    pass


if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8888)
    tornado.ioloop.IOLoop.current().start()

        

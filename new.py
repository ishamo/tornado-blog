#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys

import markdown
import bcrypt
import concurrent.futures
import tornado.web
import tornado.httpserver
import tornado.escape
import tornado.ioloop
import tornado.options
from tornado.options import options, define
from tornado import gen
from tornado.log import logging

from model import User
from model import Article
from model import session


executor = concurrent.futures.ThreadPoolExecutor(2)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/archive", ArchiveHandler),
            (r"/feed", FeedHandler),
            (r"/article/([0-9]+)", ArticleHandler),
            (r"/compose", ComposeHandler),
            (r"/auth/create", AuthCreateHandler),
            (r"/auth/login", AuthLoginHandler),
            (r"/auth/logout", AuthLogoutHandler),
        ]
        settings = dict(
            blog_title=u"Sample Blog",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            ui_modules={"Article": ArticleModule},
            xsrf_cookies=True,
            cookie_secret="$2b$12$ggtyoLhkugxfy355uXv/eu",
            login_url="/auth/login",
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user = self.get_secure_cookie("blog_user")
        if not user: return None
        return session.query(User).filter_by(username=user).first()

    def any_author_exists(self):
        return bool(session.query(User).count())


class HomeHandler(BaseHandler):
    def get(self):
        articles = session.query(Article).limit(5)
        if not articles:
            return self.redirect("/compose")
        self.render("home.html", articles=articles)


class ArchiveHandler(BaseHandler):
    def get(self):
        articles = session.query(Article).all()
        self.render("archive.html", articles=articles)


class FeedHandler(BaseHandler):
    def get(self):
        articles = session.query(Article).limit(10).all()
        self.set_header("Content-Type", "application/atom+xml")
        self.render("feed.xml", articles=articles)


class ArticleHandler(BaseHandler):
    def get(self, id):
        article = session.query(Article).filter_by(id=id).first()
        if not article:
            raise tornado.web.HTTPError(404)
        self.render("article.html", article=article)


class ComposeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        id = self.get_argument("id", None)
        article = None
        if id:
            article = session.query(Article).filter_by(id=id).first()
        self.render("compose.html", article=article)

    @tornado.web.authenticated
    def post(self):
        id = self.get_argument("id", None)
        title = self.get_argument("title")
        content = self.get_argument("content")
        clazz = self.get_argument("clazz")
        if id:
            article = sessin.query(Article).filter_by(id=id).first()
            if not article: raise tornado.web.HTTPError(404)
            article.title=title
            article.content=markdown.markdown(content)
            article.clazz=clazz
            session.add(article)
            session.commit()
            return self.redirect("/article/id")
        article = Article(title=title, content=markdown.markdown(content),
                          clazz=clazz)
        session.add(article)
        session.commit()
        id = article.id
        return self.redirect("/article/id")


class AuthCreateHandler(BaseHandler):
    def get(self):
        self.render("create_auther.html")

    @gen.coroutine
    def post(self):
        username = self.get_argument("username")
        email = self.get_argument("email")
        hashed_password = yield executor.submit(
            bcrypt.hashpw, tornado.escape.utf8(self.get_argument("password")),
            bcrypt.gensalt())
        user = User(username=username, email=email, password=hashed_password)
        session.add(user)
        session.commit(user)
        self.set_secure_cookie("blog_user", str(username))
        self.redirect(self.get_argument("next", "/"))


class AuthLoginHandler(BaseHandler):
    def get(self):
        if not self.any_author_exists():
            self.reirect("/auth/create")
        else:
            self.render("login.html", error=None)

    @gen.coroutine
    def post(self):
        hashed_password = yield executor.submit(
            bcrypt.hashpw, tornado.escape.utf8(self.get-argument("password")),
            tornado.escape.utf8(author.hashed_password))
        if hashed_password == user.password:
            self.set_secure_cookie("blog_user", str(user.username))
            self.redirect(self.get_argument("next", "/"))
        else:
            self.render("login.html", error="incorrect passowrd")


class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("blog_user")
        self.redirect(self.get_argument("next", "/"))


class ArticleModule(tornado.web.UIModule):
    def render(self, article):
        return self.render-string("modules/article.html", article=article)



if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8888)
    tornado.ioloop.IOLoop.current().start()

#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from model import User
from model import Post
from model import session

if __name__ == "__main__":
    import pdb; pdb.set_trace()
    user = User(username="qiandiao", email="qian.diao@eisoo.com", password="123456")
    session.add(user)
    session.commit()
    user = session.query(User).filter_by(username='qiandiao').first()
    print "hello"


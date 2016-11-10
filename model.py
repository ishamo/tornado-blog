#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import String, Integer, INT, TIMESTAMP, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import text

engine = create_engine('mysql://root:eisoo.com@localhost:3306/new')
DBSession = sessionmaker(engine)
session = DBSession()
BaseModel = declarative_base()

class User(BaseModel):
    __tablename__ = 'user'

    id = Column(INT, primary_key=True, autoincrement=True)
    username = Column(String(30), index=True, nullable=False)
    password = Column(String(30), nullable=False)
    email = Column(String(64), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text('NOW()'), nullable=False)
    updated_at = Column(TIMESTAMP, onupdate=func.now(), nullable=False)

class Article(BaseModel):
    __tablename__ = 'article' 

    id = Column(INT, primary_key=True)
    title = Column(String(64), nullable=False)
    clazz = Column(String(64), nullable=False)
    content = Column(TEXT, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text('NOW()'), nullable=False)
    updated_at = Column(TIMESTAMP, onupdate=func.now(), nullable=False)
    user_id = Column(ForeignKey("user.id"), nullable=False)


if __name__ == "__main__":
    BaseModel.metadata.bind=engine
    if len(sys.argv) is not 2:
        print "Usage: python model.py [create|drop]"
        exit()
    if sys.argv[1] == "create":
        BaseModel.metadata.create_all()
    elif sys.argv[1] == "drop":
        BaseModel.metadata.drop_all()
    else:
        print "Usage: python model.py [create|drop]"
   

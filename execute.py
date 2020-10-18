from flask import *  # 必要なライブラリのインポート
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
from user import User, session
from scrape import *

users = session.query(User).all()
for user in users :
    userId = user.id
    password = user.password
    crawl_panda(userId,password)

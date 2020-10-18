from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///user.db')  # user.db というデータベースを使うという宣言です
Base = declarative_base()  # データベースのテーブルの親です

class User(Base):  # PythonではUserというクラスのインスタンスとしてデータを扱います
    __tablename__ = 'users'  # テーブル名は users です
    id = Column(String(10), primary_key=True, nullable=False)
    password = Column(String(50), unique=True, nullable=False)

    def __init__(self, id, password):
        self.id = id
        self.password = password

    def __repr__(self):
        return "User<{}, {}, {}>".format(self.id, self.password)

Base.metadata.create_all(engine)  # 実際にデータベースを構築します
SessionMaker = sessionmaker(bind=engine)  # Pythonとデータベースの経路です
session = SessionMaker()  # 経路を実際に作成しました
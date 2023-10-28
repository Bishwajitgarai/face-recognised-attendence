import os
# SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:Bishwajit_123@localhost/faceattendence"
# SQLALCHEMY_DATABASE_URI = 'sqlite:///faceattendence.db'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.getcwd(), 'faceattendence.db')

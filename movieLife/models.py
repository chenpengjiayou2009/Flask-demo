from movieLife import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model, UserMixin):  # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)  # 主键
    username = db.Column(db.String(20))  # 用户的名字
    password_hash = db.Column(db.String(128))
    def set_password(self, password):  # 用来设置密码的方法，接受密码作为参数
        self.password_hash = generate_password_hash(password)  # 将生成的密码保持到对应字段

    def validate_password(self, password):  # 用于验证密码的方法，接受密码作为参数
        return check_password_hash(self.password_hash, password)  # 返回布尔值

class Movie(db.Model):  # 表名将会是 movie
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(60))  # 明星的名字
    year = db.Column(db.String(4))  # 明星出生的年份
    image = db.Column(db.String(200)) # 图片地址
    userId = db.Column(db.Integer)
import os
import sys
import click
from flask import url_for, escape
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)


db = SQLAlchemy(app)

class User(db.Model):  # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(20))  # 用户的名字

class Star(db.Model):  # 表名将会是 movie
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(60))  # 明星的名字
    year = db.Column(db.String(4))  # 明星出生的年份
    image = db.Column(db.String(200)) # 图片地址

@app.route('/')
def index():
    user = User.query.first()
    stars = Star.query.all()
    return render_template('index.html', name=user.name, stars=stars)

@app.route('/user/<name>')
def user_page(name):
    return 'User: %s' % escape(name)

@app.route('/test')
def test_url_for():
    # 下面是一些调用示例（请在命令行窗口查看输出的 URL）：
    print(url_for('hello'))  # 输出：/
    # 注意下面两个调用是如何生成包含 URL 变量的 URL 的
    print(url_for('user_page', name='greyli'))  # 输出：/user/greyli
    print(url_for('user_page', name='peter'))  # 输出：/user/peter
    print(url_for('test_url_for'))  # 输出：/test
    # 下面这个调用传入了多余的关键字参数，它们会被作为查询字符串附加到 URL 后面。
    print(url_for('test_url_for', num=2))  # 输出：/test?num=2
    return 'Test page'



@app.cli.command()  # 注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息


@app.cli.command()
def forge():
    """Generate fake data."""
    # db.create_all()

    # 全局的两个变量移动到这个函数内
    name = 'chenpeng'
    stars = [{'name': '刘昊然', 'year': 1997, 'image': 'images/lhr.jpg'},
             {'name': 'Troye sivan', 'year': 1997, 'image': 'images/tye.jpg'}]

    user = User(name=name)
    db.session.add(user)
    for s in stars:
        star = Star(name=s['name'], year=s['year'], image=s['image'])
        db.session.add(star)

    db.session.commit()
    click.echo('Done.')

@app.context_processor
def inject_user():  # 函数名可以随意修改
    user = User.query.first()
    return dict(user=user)  # 需要返回字典，等同于 return {'user': user}
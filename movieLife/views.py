import os
from movieLife import app, db
from movieLife.models import *
from flask import request, flash, redirect, url_for, render_template
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy import and_, or_
# 主页
@app.route('/')
@app.route('/index')
def index():
    page = int(request.args.get("page",0))
    # user = User.query.filter(User.id==current_user.id).first()
    movies = Movie.query.offset(page*20).limit(20).all()
    return render_template('index.html', movies=movies)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.filter(User.username==username).first()
        # 验证用户名和密码是否一致
        if user and user.validate_password(password):
            login_user(user)  # 登入用户
            flash('Login success.')
            return redirect(url_for('index'))  # 重定向到主页

        flash('Invalid username or password.')  # 如果验证失败，显示错误消息
        return redirect(url_for('login'))  # 重定向回登录页面

    return render_template('login.html')

@app.route('/logout')
@login_required  # 用于视图保护，后面会详细介绍
def logout():
    logout_user()  # 登出用户
    flash('Goodbye.')
    return redirect(url_for('index'))  # 重定向回首页


def valid_regist(username):
    user = User.query.filter(or_(User.username == username)).first()
    if user:
        return False
    else:
        return True

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        if request.form['password1'] != request.form['password2']:
            flash('两次密码不相同！')
        elif valid_regist(request.form['username']):
            username = request.form['username']
            password = request.form['password1']
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            flash("用户名已存在")
    return render_template('register.html')

@app.route('/add',methods=['GET','POST'])
@login_required
def add():
    name = request.form.get('name')  # 传入表单对应输入字段的 name 值
    year = request.form.get('year')
    imgPath = ''
    img = request.files['image']
    userId = current_user.id
    if img.filename!="":
        path = os.path.join(app.root_path, 'static/images/')
        file_path = path + img.filename
        img.save(file_path)
        imgPath = "images/" + img.filename
    # 验证数据
    if not name or not year or len(year) > 4 or len(name) > 60:
        flash('Invalid input.')  # 显示错误提示
        return redirect(url_for('index'))  # 重定向回主页
    # 保存表单数据到数据库
    movie = Movie(name=name, year=year, image=imgPath,userId=userId)  # 创建记录
    db.session.add(movie)  # 添加到数据库会话
    db.session.commit()  # 提交数据库会话
    flash('Item created.')  # 显示成功创建的提示
    return redirect(url_for('index'))  # 重定向回主页

@app.route('/movie/delete/<int:movie_id>', methods=['POST'])  # 限定只接受 POST 请求
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)  # 获取电影记录
    db.session.delete(movie)  # 删除对应的记录
    db.session.commit()  # 提交数据库会话
    flash('Item deleted.')
    return redirect(url_for('index'))


@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':  # 处理编辑表单的提交请求
        name = request.form['title']
        year = request.form['year']

        if not name or not year or len(year) > 4 or len(name) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))  # 重定向回对应的编辑页面

        movie.name = name  # 更新标题
        movie.year = year  # 更新年份
        db.session.commit()  # 提交数据库会话
        flash('Item updated.')
        return redirect(url_for('index'))  # 重定向回主页

    return render_template('edit.html', movie=movie)  # 传入被编辑的电影记录

@app.route('/admin')
def user_page():
    return render_template("admin.html")

@app.route('/movie/rec/<int:movie_id>')
def rec(movie_id):
    recs = Recommend.query.filter(Recommend.movieId==movie_id).order_by('id').all()
    recSet = []
    for recItem in recs:
        recId = recItem.recId
        recSet.append(Movie.query.get(recId))
    return render_template('recommend.html',recs=recSet)

@app.route('/search',methods=['POST','GET'])
def search():
    if request.method == 'GET':
        return render_template('search.html')
    title = request.form['title']
    results = Movie.query.filter(Movie.title.like('%{title}%'.format(title=title))).all()
    return render_template('results.html',results=results)

@app.route('/movie/like/<int:movie_id>',methods=['POST'])
def like(movie_id):
    userId = current_user.id
    movieId = movie_id
    preference = Preference(movieId=movieId,userId=userId)
    db.session.add(preference)
    db.session.commit()
    flash("preference created")
    return redirect(url_for('index'))

@app.route('/user/like/<int:user_id>',methods=['GET'])
def preference(user_id):
    likes = Preference.query.filter(Preference.userId==user_id).order_by(Preference.id).all()
    likeSet = []
    for likeItem in likes:
        likeId = likeItem.movieId
        likeSet.append(Movie.query.get(likeId))
    return render_template('like.html',likes=likeSet)

# @app('/movie/<int:movie_id>/rating',methods=['POST'])
# @login_required
# def rating(movie_id):
#     user_id = current_user.id
#     rating = request.form['rating']
#     db_rating = Rating(user_id, movie_id, rating)
#     db.session.add(db_rating)
#     db.session.commit()
#     flash("rating succeed")
#     return redirect(url_for("index"))

@app.route("/movie/<int:movie_id>")
def detail(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    return render_template("detail.html",movie=movie)


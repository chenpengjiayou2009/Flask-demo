import click
from movieLife import app, db
from movieLife.models import User, Movie, Recommend

@app.cli.command()  # 注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息

@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo('Done.')

@app.cli.command()
def forge():
    movie = Movie(title="肖申克的救赎",year=2000,keywords="美国 励志")
    movie2 = Movie(title="阿甘正传",year=2004,keywords="美国 励志")
    recommend = Recommend(movieId=1,recId=2,score=0.9)
    db.session.add(movie)
    db.session.add(movie2)
    db.session.add(recommend)
    db.session.commit()

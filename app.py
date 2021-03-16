# -*- coding: utf-8 -*-

import os
import sys
import click
from flask import Flask
from flask_sqlalchemy import SQLAlchemy  # 数据库依赖


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'
# 数据库设置
dev_db = prefix + os.path.join(basedir, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_ECHO'] = True # 输出SQL语句到控制台
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', dev_db)
db = SQLAlchemy(app)


''' 一对一
uselist=False 标志指示在关系的“多”端放置标量属性而不是集合。将一对多转换为一对一

User为用户基本资料，UserData为用户扩展资料，一对一关系。
'''


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    userdata = db.relationship(
        'UserData', uselist=False, back_populates='user')


class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates=('userdata'))

##################################################


'''
一对多，作者和文章是一对多关系，一个作者可以写多篇文章。
ForeignKey(author_id))定义外键，关联作者
relationship('Article')定义一个属性，表示多篇文章。
'''


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    articles = db.relationship(
        'Article', back_populates='author')



#关系表要放到表的前边建立
tags = db.Table('tags',
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
                db.Column('article_id', db.Integer,
                          db.ForeignKey('article.id'))
                )



class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), unique=True)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    author = db.relationship('Author', back_populates='articles')
    # 建立多对多关系
    tags = db.relationship('Tag', secondary=tags, back_populates='articles')


###########################
'''
多对多关系，常见的有：学生和老师，文章和标签。
需要一个关联表，关联表不存储数据，只存储关系，关联表要建立在数据表之前。
这里我们新建一个Tag表，和上边的Article表进行多对多关联关系。
'''


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    articles = db.relationship(
        'Article', secondary=tags, back_populates='tags')




@app.shell_context_processor
def make_shell_context():
    print('shell上下文：@app.shell_context_processor')
    return dict(db=db, User=User, Userdata=UserData, Author=Author, Article=Article,Tag = Tag, )


@app.cli.command()
def dbinit():
    '''删除并重新构建数据库'''
    click.echo('删除数据库和表')
    db.drop_all()
    click.echo("创建数据库！")
    db.create_all()
    click.echo("数据库创建成功！")


@app.cli.command()
def test1to1():
    '''一对一测试'''
    print("开始测试")
    user = User()
    user.name = 'baby'
    db.session.add(user)
    db.session.commit()
    userdata = UserData()
    userdata.email = 'bosi@qq.com'
    # userdata.user_id = user.id #建立关系方法1
    userdata.user = user  # 建立关系方法2
    db.session.add(userdata)
    db.session.commit()
    print("添加{}成功！".format(user.userdata.email))


@app.cli.command()
def test1tomore():
    author = Author()
    author.name = 'J.sky'
    db.session.add(author)
    db.session.commit()

    ac1 = Article()
    ac1.title = '一对一关系'
    ac1.author_id = author.id  # 建立关系方法1
    ac2 = Article()
    ac2.title = '多对多关系'
    ac2.author = author  # 建立关系方法2
    ac3 = Article()
    ac3.title = '添加append测试'
    author.articles.append(ac3)  # 建立关系方法3
    db.session.add(ac1)
    db.session.add(ac2)
    db.session.commit()

    for ar in author.articles:
        print(ar.title)

@app.cli.command()
def testmtom():
    art1 = Article(title='我是王大锤')
    art2 = Article(title='小狗露西很可爱')
    art3 = Article(title='快乐的写代码')

    tag1 = Tag(name='分类1')
    tag2 = Tag(name='分类2')

    tag1.articles.append(art1)
    tag1.articles.append(art2)
    tag2.articles.append(art2)
    tag2.articles.append(art3)

    db.session.add(art1)
    db.session.add(art2)
    db.session.add(art3)
    db.session.add(tag1)
    db.session.add(tag2)
    db.session.commit()

    for a in tag1.articles:
        print(a.title)

    for t in art2.tags:
        print(t.name)


@app.route('/')
def hello():
    u = User.query.get(1)
    print(u)
    return 'Welcome to hello Hi!'

from . import db, bcrypt
from nanoid import generate
from datetime import datetime


class AdminUser(db.Model):
    id = db.Column(db.String(40), primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __init__(self, username, password):
        self.id = generate()
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode("UTF-8")


class Question(db.Model):
    id = db.Column(db.String(40), primary_key=True)
    nickname = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(300), nullable=True)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=True)
    like = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(10), nullable=False, default="public")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.now())
    answers = db.relationship("Answer", backref="question", lazy=True)

    def __init__(self, password):
        self.id = generate()
        self.password = bcrypt.generate_password_hash(password).decode("UTF-8")


class Answer(db.Model):
    id = db.Column(db.String(40), primary_key=True)
    nickname = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(300), nullable=True)
    content = db.Column(db.Text, nullable=False)
    depth = db.Column(db.Integer, nullable=False, default=0)
    like = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(10), nullable=False, default="public")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.now())
    question_id = db.Column(db.String(40), db.ForeignKey("question.id"), nullable=False)

    def __init__(self, password):
        self.id = generate()
        self.password = bcrypt.generate_password_hash(password).decode("UTF-8")


class Article(db.Model):
    id = db.Column(db.String(40), primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(30), nullable=False)
    thumbnail = db.Column(db.String(300), nullable=True)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(10), nullable=False, default="draft")
    tags = db.Column(db.String(300), nullable=True)
    like_count = db.Column(db.Integer, nullable=False, default=0)
    view_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.now())
    comments = db.relationship("ArticleComment", backref="article", lazy=True)

    def __init__(
        self, title, category, content, thumbnail=None, status="draft", tags=None
    ):
        self.id = generate()
        self.title = title
        self.category = category
        self.content = content
        self.thumbnail = thumbnail
        self.tags = tags
        self.status = status


class ArticleComment(db.Model):
    id = db.Column(db.String(40), primary_key=True)
    content = db.Column(db.Text, nullable=False)
    nickname = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    like_count = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(10), nullable=False, default="public")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.now())
    article_id = db.Column(db.String(40), db.ForeignKey("article.id"), nullable=False)
    parent_id = db.Column(
        db.String(40), db.ForeignKey("article_comment.id"), nullable=True
    )
    replies = db.relationship(
        "ArticleComment", backref=db.backref("parent", remote_side=[id]), lazy="dynamic"
    )

    def __init__(self, content, nickname, password, article_id, parent_id=None):
        self.id = generate()
        self.content = content
        self.nickname = nickname
        self.password = bcrypt.generate_password_hash(password).decode("UTF-8")
        self.article_id = article_id
        self.parent_id = parent_id


class SqlDocCategory(db.Model):
    id = db.Column(db.String(40), primary_key=True)
    category = db.Column(db.String(200), nullable=False)
    parent_id = db.Column(
        db.String(40), db.ForeignKey("sql_doc_category.id"), nullable=True
    )
    order_num = db.Column(db.Integer, nullable=False, default=0)
    children = db.relationship(
        "SqlDocCategory", backref=db.backref("parent", remote_side=[id])
    )

    def __init__(self, category, parent_id=None, order_num=0):
        self.id = generate()
        self.category = category
        self.parent_id = parent_id
        self.order_num = order_num


class SqlDoc(db.Model):
    id = db.Column(db.String(40), primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(10), nullable=False, default="public")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=True)
    order_num = db.Column(db.Integer, nullable=False, default=0)
    category_id = db.Column(
        db.String(40), db.ForeignKey("sql_doc_category.id"), nullable=False
    )
    category = db.relationship(
        "SqlDocCategory", backref=db.backref("sql_docs", lazy=True)
    )

    def __init__(self, title, content, order_num, category_id):
        self.id = generate()
        self.title = title
        self.content = content
        self.category_id = category_id
        self.order_num = order_num

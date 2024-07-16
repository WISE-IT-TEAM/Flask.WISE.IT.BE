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
    deleted_at = db.Column(db.DateTime, nullable=True)
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
    deleted_at = db.Column(db.DateTime, nullable=True)
    question_id = db.Column(db.String(40), db.ForeignKey("question.id"), nullable=False)

    def __init__(self, password):
        self.id = generate()
        self.password = bcrypt.generate_password_hash(password).decode("UTF-8")


class ArticleCategory(db.Model):
    id = db.Column(db.String(40), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    parent_id = db.Column(
        db.String(40), db.ForeignKey("article_category.id"), nullable=True
    )
    children = db.relationship(
        "ArticleCategory", backref=db.backref("parent", remote_side=[id])
    )
    articles = db.relationship("Article", backref="category", lazy=True)

    def __init__(self, name, parent_id=None):
        self.id = generate()
        self.name = name
        self.parent_id = parent_id


class Tag(db.Model):
    id = db.Column(db.String(40), primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __init__(self, name):
        self.id = generate()
        self.name = name


article_tags = db.Table(
    "article_tags",
    db.Column(
        "article_id", db.String(40), db.ForeignKey("article.id"), primary_key=True
    ),
    db.Column("tag_id", db.String(40), db.ForeignKey("tag.id"), primary_key=True),
)


class Article(db.Model):
    id = db.Column(db.String(40), primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    thumbnail = db.Column(db.String(300), nullable=True)
    status = db.Column(db.String(10), nullable=False, default="draft")
    like_count = db.Column(db.Integer, nullable=False, default=0)
    view_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.now())
    category_id = db.Column(
        db.String(40), db.ForeignKey("article_category.id"), nullable=False
    )
    tags = db.relationship(
        "Tag", secondary=article_tags, backref=db.backref("articles", lazy="dynamic")
    )
    comments = db.relationship("ArticleComment", backref="article", lazy=True)

    def __init__(self, title, content, category_id):
        self.id = generate()
        self.title = title
        self.content = content
        self.category_id = category_id


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
    sql_docs = db.relationship("SqlDoc", backref="category", lazy=True)

    def __init__(self, category):
        self.id = generate()
        self.category = category


class SqlDoc(db.Model):
    id = db.Column(db.String(40), primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(10), nullable=False, default="public")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=True)
    category_id = db.Column(
        db.String(40), db.ForeignKey("sql_doc_category.id"), nullable=False
    )
    parent_id = db.Column(db.String(40), db.ForeignKey("sql_doc.id"), nullable=True)
    children = db.relationship(
        "SqlDoc", backref=db.backref("parent", remote_side=[id]), lazy="dynamic"
    )

    def __init__(self, title, content, category_id, parent_id=None):
        self.id = generate()
        self.title = title
        self.content = content
        self.category_id = category_id
        self.parent_id = parent_id

    @property
    def depth(self):
        if self.parent is None:
            return 0
        return self.parent.depth + 1

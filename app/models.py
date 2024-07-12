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
    tags = db.Column(db.String(300), nullable=False)
    like = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(10), nullable=False, default="public")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=True)
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
    updated_at = db.Column(db.DateTime, nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    question_id = db.Column(db.String(40), db.ForeignKey("question.id"), nullable=False)

    def __init__(self, password):
        self.id = generate()
        self.password = bcrypt.generate_password_hash(password).decode("UTF-8")

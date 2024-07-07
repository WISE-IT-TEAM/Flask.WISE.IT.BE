from flask import Blueprint

admin = Blueprint("admin", __name__)
# api = Blueprint("api", __name__)


from .admin import *

from flask import render_template
from flask_login import current_user
from ..models import User
from . import main


@main.route('/')
def index():
    users = []
    if current_user.is_authenticated:
        users = User.query.order_by(User.id).all()
    return render_template('index.html', users=users)

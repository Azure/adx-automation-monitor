import logging
import os
import datetime

from flask import Flask, render_template, redirect, url_for, request, session
from flask_login import LoginManager, login_required, login_user, logout_user

from app.models import User, db, Run
from app.auth import get_authorization_url, acquire_token, get_logout_uri

# pylint: disable=invalid-name

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'local_test')

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['A01_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


@login_manager.user_loader
def load_user(user_id):
    if 'user_id' not in session or 'user_name' not in session:
        return None
    if user_id != session['user_id']:
        return None
    return User(session['user_id'], session['user_name'])


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login', requiest_uri=request.path))


@app.route('/login')
def login():
    return render_template('login.html', auth_link=get_authorization_url(url_for('index')))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(get_logout_uri())


@app.route('/login_callback', methods=['GET'])
def login_callback():
    code, state = request.args['code'], request.args['state']
    token = acquire_token(code)

    session['user_id'] = token['userId']
    session['user_name'] = f'{token.get("givenName", "")} {token.get("familyName", "")}'

    login_user(User(session['user_id'], session['user_name']), remember=True, duration=datetime.timedelta(days=14))

    return redirect(state)


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/runs')
@login_required
def runs():
    page_size = 20
    page = int(request.args.get('page', 1))
    query = Run.query.order_by(Run.creation.desc()).offset(page_size * (page - 1)).limit(20)

    return render_template('runs.html', runs=query, page=page,
                           previous_page=url_for('runs', page=max(page - 1, 1)),
                           next_page=url_for('runs', page=page + 1))


@app.route('/help', methods=['GET'])
def help_page():
    return render_template('help.html')


@app.route('/profile', methods=['GET'])
def profile():
    return render_template('profile.html')

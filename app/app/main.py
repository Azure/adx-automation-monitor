import logging
import os
import datetime
import re

import requests
from flask import Flask, render_template, redirect, url_for, request, session
from flask_login import LoginManager, login_required, login_user, logout_user

from app.models import User, db, Run, Task
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
    return redirect(url_for('login', request_uri=request.url))


@app.route('/login')
def login():
    callback_url = request.args.get('request_uri', url_for('index'))
    return render_template('login.html', auth_link=get_authorization_url(callback_url))


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

    page_previous = url_for('runs', page=page - 1) if page > 1 else None
    page_next = url_for('runs', page=page + 1)

    return render_template('runs.html', runs=query,
                           page=page,
                           page_previous=page_previous,
                           page_next=page_next)


@app.route('/run/<int:run_id>')
@login_required
def run(run_id: int):
    this_run = Run.query.filter_by(id=run_id).first()
    if not this_run:
        return 404

    show_log = request.args.get('logs', 'False') == 'true'
    query = request.args.get('query', '')

    tasks = [t for t in this_run.tasks if t.result != 'Passed']

    if query:
        tasks = [t for t in tasks if re.search(query, t.identifier)]

    logs = dict()
    if show_log:
        for t in tasks:
            resp = requests.get(t.log_path)
            if resp.status_code < 300:
                logs[t.id] = resp.text

    tasks = sorted(tasks, key=lambda t: t.name)

    return render_template('run.html', run=this_run, tasks=tasks, logs=logs, query=query)


@app.route('/task/<int:task_id>')
@login_required
def task(task_id: int):
    this_task = Task.query.filter_by(id=task_id).first()
    if not this_task:
        return 404, 'not found'

    resp = requests.get(this_task.log_path)
    log = resp.text if resp.status_code < 300 else None

    resp = requests.get(this_task.record_path)
    rec = resp.text if resp.status_code < 300 else None

    return render_template('task.html', task=this_task, record=rec, log=log)


@app.route('/help', methods=['GET'])
def help_page():
    return render_template('help.html')


@app.route('/profile', methods=['GET'])
def profile():
    return render_template('profile.html')

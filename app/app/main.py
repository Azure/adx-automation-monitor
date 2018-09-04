import logging
import os
import datetime
import re
import json

import requests
from flask import Flask, render_template, redirect, url_for, request, session
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

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
    run = Run.query.filter_by(id=run_id).first()
    if not run:
        return 404

    query = ""

    entity = {
        "metadata": {
            "type": "Run",
            "id": run.id,
            "query": query,
            "link": url_for("run", run_id=run.id),
            "tags": {
                "major": [
                    {"value": run.remark, "type": "primary"},
                    {"value": f"Failure {len([_ for t in run.tasks if t.result != 'Passed'])}", "type": "danger"},
                    {"value": f"Total {len(run.tasks)}"},
                    {"value": run.status},
                ],
                "minor": [
                    {"value": run.creation.strftime('%Y/%m/%d %H:%M')},
                    {"value": run.image},
                ]
            }
        },
        "data:": {
            "content": [{
                "id": t.id,
                "category": t.category,
                "identifier": t.short_name or t.identifier,
                "result": t.result,
                "link": url_for('task', task_id=t.id),
                "duration": t.duration,
            } for t in run.tasks]
        }
    }

    user = {
        'is_authenticated': current_user.is_authenticated,
        'name': current_user.user_name,
    }

    links = [{'name': 'Runs', 'link': url_for('runs')},
             {'name': 'Diagnose', 'link': url_for('diagnose')}]

    data = json.dumps({"entity": entity, "user": user, "links": links})

    return render_template('run.html', data=data)


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


@app.route('/diagnose', methods=['GET'])
def diagnose():
    try:
        with open(os.path.join(app.root_path, '..', 'app_version')) as fq:
            app_version = fq.read()
    except (OSError, IOError):
        app_version = None

    try:
        with open(os.path.join(app.root_path, '..', 'source_repo')) as fq:
            source_repo = fq.read()
            if source_repo:
                commit_uri = f'{source_repo}/commit/{app_version}'
            else:
                commit_uri = None
    except (OSError, IOError):
        commit_uri = None

    data = {}
    if commit_uri:
        data['App Version'] = {"Value": app_version, "URI": commit_uri}
    elif app_version:
        data['App Version'] = {"Value": app_version}

    return render_template('diagnose.html', data=data)


@app.route('/profile', methods=['GET'])
def profile():
    return render_template('profile.html')

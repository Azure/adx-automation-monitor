import sys
import os
import time
import itertools
import logging
from datetime import datetime, timedelta
from collections import OrderedDict, defaultdict

import coloredlogs
import requests
from tabulate import tabulate

from kubernetes import client, config
from kubernetes.client import CoreV1Api


class InternalAuth(object):  # pylint: disable=too-few-public-methods
    def __call__(self, req):
        req.headers['Authorization'] = os.environ['A01_INTERNAL_COMKEY']
        return req


def get_kube_api(local: False) -> CoreV1Api:
    if local:
        config.load_kube_config()
    else:
        config.load_incluster_config()
    return client.CoreV1Api()


def get_store_uri(store_uri: str, local: bool = False) -> str:
    return f'https://{store_uri}' if local else f'http://{store_uri}'


def get_namespace() -> str:
    try:
        with open('/var/run/secrets/kubernetes.io/serviceaccount/namespace', 'r') as file_handle:
            return file_handle.read().strip()
    except IOError:
        pass

    return os.environ.get('A01_REPORT_NAMESPACE', 'az')


def send_report(tasks: list, run: dict) -> None:
    # Move this part to a standalone reporting service
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from smtplib import SMTP

    smtp_server = os.environ.get('A01_REPORT_SMTP_SERVER', None)
    smtp_user = os.environ.get('A01_REPORT_SENDER_ADDRESS', None)
    smtp_pass = os.environ.get('A01_REPORT_SENDER_PASSWORD', None)
    receivers = os.environ.get('A01_REPORT_RECEIVER', None)

    if not smtp_server or not smtp_user or not smtp_pass or not receivers:
        logger.warning('Skip sending email.')
        sys.exit(1)

    statuses = defaultdict(lambda: 0)
    results = defaultdict(lambda: 0)

    failure = []

    for task in tasks:
        status = task['status']
        result = task['result']

        statuses[status] = statuses[status] + 1
        results[result] = results[result] + 1

        if result != 'Passed':
            failure.append(
                (task['id'],
                 task['name'].rsplit('.')[-1],
                 task['status'],
                 task['result'],
                 (task.get('result_details') or dict()).get('duration')))

    status_summary = ' | '.join([f'{status_name}: {count}' for status_name, count in statuses.items()])
    result_summary = ' | '.join([f'{result or "Not run"}: {count}' for result, count in results.items()])

    creation = datetime.strptime(run['creation'], '%Y-%m-%dT%H:%M:%SZ') - timedelta(hours=8)

    summaries = [('Id', run['id']),
                 ('Creation', str(creation) + ' PST'),
                 ('Creator', run['details']['creator']),
                 ('Remark', run['details']['remark']),
                 ('Live', run['details']['live']),
                 ('Task', status_summary),
                 ('Image', run['settings']['droid_image']),
                 ('Result', result_summary)]

    content = f"""\
<html>
    <body>
        <div>
            <h2>Summary</h2>
            {tabulate(summaries, tablefmt="html")}
        </div>
        <div>
            <h2>Failures</h2>
            {tabulate(failure, headers=("id", "name", "status", "result", "duration(ms)"), tablefmt="html")}
        </div>
        <div>
            <h2>More details</h2>
            <p>Install the latest release of A01 client to download log and recordings.</p>
            <code>
            $ virtualenv env --python=python3.6 <br>
            $ . env/bin/activate <br>
            $ pip install https://github.com/troydai/a01client/releases/download/0.4.0/a01ctl-0.4.0-py3-none-any.whl<br>
            $ a01 login<br>
            $ a01 get runs -l {run['id']}<br>
            </code>
            <p>Contact: trdai@microsoft.com</p>
        </div>
    </body>
</html>"""

    mail = MIMEMultipart()
    mail['Subject'] = f'Azure CLI Automation Run {str(creation)} - {result_summary}.'
    mail['From'] = smtp_user
    mail['To'] = receivers
    mail.attach(MIMEText(content, 'html'))

    logger.info('Sending emails.')
    with SMTP(smtp_server) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(mail)


def main(store: str, run: str, sleep: int = 5, local: bool = False) -> None:
    session = requests.Session()
    session.auth = InternalAuth()
    api = get_kube_api(local=local)

    while True:
        resp = session.get(f'{store}/run/{run}/tasks')
        resp.raise_for_status()

        def get_status(task: dict) -> str:
            return task['status']

        tasks = sorted(resp.json(), key=get_status)
        status = OrderedDict()
        for status_name, rec in itertools.groupby(tasks, key=get_status):
            status[status_name] = list(rec)

        logger.info('|'.join([f'{k}={len(v)}' for k, v in status.items()]))

        lost_task = []
        active_pods = api.list_namespaced_pod(get_namespace()).items
        for running_task in status.get('scheduled', []):
            task_details = running_task['result_details']
            if not task_details:
                continue
            if 'agent' not in task_details:
                continue

            pod_name = task_details['agent'].split('@')[0]
            if pod_name:
                pod = next(pod for pod in active_pods if pod.metadata.name == pod_name)
                if pod.status.phase != 'Running':
                    # When the task is scheduled to run on a pod but the pod is not running, the task is lost.
                    # Resubmit the task - need improve in a01store
                    lost_task.append(running_task['id'])

        if 'initialized' not in status:
            if 'scheduled' not in status:
                logger.info(f'Run {run_id} is finished.')
                send_report(tasks, session.get(f'{store}/run/{run}').json())
                sys.exit(0)
            elif len(status['scheduled']) - len(lost_task) == 0:
                lost_tasks = ', '.join(lost_task)
                logger.warning(f'Despite tasks {lost_tasks} are lost. Run {run_id} is finished.')
                send_report(tasks, session.get(f'{store}/run/{run}').json())
                sys.exit(0)

        time.sleep(sleep)


if __name__ == '__main__':
    # pylint: disable=invalid-name
    coloredlogs.install(level=logging.INFO)
    logger = logging.getLogger('a01report')

    interval = int(os.environ.get('A01_MONITOR_INTERVAL', 5))
    logger.info(f'Interval: {interval}s')

    is_local = os.environ.get('A01_MONITOR_LOCAL', False)
    logger.info(f'Is local: {is_local}')

    run_id = os.environ['A01_MONITOR_RUN_ID']
    logger.info(f'Run id: {run_id}')

    task_store = os.environ.get('A01_STORE_NAME', 'task-store-web-service-internal')
    logger.info(f'Store: {task_store}')

    main(store=get_store_uri(task_store, is_local), run=run_id, sleep=interval, local=is_local)

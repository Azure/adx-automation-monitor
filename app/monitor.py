import sys
import os
import time
import itertools
import logging
from collections import OrderedDict

import coloredlogs
import requests

from kubernetes import client, config


class InternalAuth(object):  # pylint: disable=too-few-public-methods
    def __call__(self, req):
        req.headers['Authorization'] = os.environ['A01_INTERNAL_COMKEY']
        return req


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
                sys.exit(0)
            elif len(status['scheduled']) - len(lost_task) == 0:
                lost_tasks = ', '.join(lost_task)
                logger.warning(f'Despite tasks {lost_tasks} are lost. Run {run_id} is finished.')
                sys.exit(0)

        time.sleep(sleep)


def get_kube_api(local: False):
    if local:
        config.load_kube_config()
    else:
        config.load_incluster_config()
    return client.CoreV1Api()


def get_store_uri(store_uri: str, local: bool = False) -> str:
    return f'https://{store_uri}' if local else f'http://{store_uri}'


def get_namespace():
    try:
        with open('/var/run/secrets/kubernetes.io/serviceaccount/namespace', 'r') as file_handle:
            return file_handle.read().strip()
    except IOError:
        pass

    return os.environ.get('A01_REPORT_NAMESPACE', 'az')


if __name__ == '__main__':
    # pylint: disable=invalid-name
    coloredlogs.install(level=logging.INFO)
    logger = logging.getLogger('a01report')

    interval = int(os.environ.get('A01_REPORT_INTERVAL', 5))
    logger.info(f'Interval: {interval}s')

    is_local = os.environ.get('A01_REPORT_LOCAL', False)
    logger.info(f'Is local: {is_local}')

    run_id = os.environ['A01_REPORT_RUN_ID']
    logger.info(f'Run id: {run_id}')

    task_store = os.environ['A01_STORE_NAME']
    logger.info(f'Store: {task_store}')

    main(store=get_store_uri(task_store, is_local), run=run_id, sleep=interval, local=is_local)

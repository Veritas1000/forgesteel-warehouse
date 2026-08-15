import logging
import multiprocessing
import os
import re
import sys

import gunicorn.app.base

from forgesteel_warehouse import init_app
from forgesteel_warehouse.utils.app_utils import bootstrap


def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1

class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

class RequestPathFilter(logging.Filter):
    def __init__(self, *args, path_re, **kwargs):
        super().__init__(*args, **kwargs)
        self.path_filter = re.compile(path_re)

    def filter(self, record):
        req_path = record.args['U'] # type: ignore
        if not self.path_filter.match(req_path):
            return True
        return False


def on_starting(server):
    server.log.access_log.addFilter(RequestPathFilter(path_re=r'^/(healthz|favicon.ico)$'))


if __name__ == "__main__":
    bootstrap()
    sys.stdout.flush()

    options = {
        "workers": int(os.environ.get("GUNICORN_PROCESSES", number_of_workers())),
        "threads": int(os.environ.get("GUNICORN_THREADS", "4")),
        "bind": os.environ.get("GUNICORN_BIND", "0.0.0.0:5000"),
        "accesslog": "-",
        "access_log_format": "%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s '%(f)s' '%(a)s' in %(D)sµs",
        "forwarded_allow_ips": "*",
        "secure_scheme_headers": {"X-Forwarded-Proto": "https"},
        "on_starting": on_starting,
    }

    app = init_app()
    StandaloneApplication(app, options).run()

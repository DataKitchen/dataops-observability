# type: ignore
# invoke type issue: https://github.com/pyinvoke/invoke/issues/357
__all__ = ["get_minikube_ip", "get_host_env", "get_docker_env", "mount", "MINIKUBE_PROFILE"]

import contextlib
import os
import re
import signal
from shutil import which

from invoke import Exit

MINIKUBE_PROFILE = os.environ.get("INVOKE_MINIKUBE_PROFILE", "dk-observability-dev")
""" Minikube profile name """


def get_minikube_ip(ctx):
    return ctx.run(f"minikube -p {MINIKUBE_PROFILE} ip", hide=True).stdout.strip()


def check_env_tools(required_tools):
    result = [
        f"ERROR: Required tool '{tool}' is not installed on your path."
        for tool in required_tools
        if which(tool) is None
    ]
    if result:
        raise Exit(message="\n".join(msg for msg in result), code=1)


def get_pod_env_var(ctx, pod, var):
    return ctx.run(
        f"minikube -p {MINIKUBE_PROFILE} kubectl -- exec {pod} -- bash -c 'echo ${var}'",
        hide=True,
    ).stdout.strip()


def get_host_env(ctx):
    minikube_ip = get_minikube_ip(ctx)
    mysql_password = get_pod_env_var(ctx, "svc/mysql", "MYSQL_PASSWORD")
    env_vars = {
        "OBSERVABILITY_CONFIG": "minikube",
        "MYSQL_USER": "observability",
        "MYSQL_PASSWORD": mysql_password,
        "MYSQL_SERVICE_HOST": minikube_ip,
        "MYSQL_SERVICE_PORT": "3306",
        "KAFKA_SERVICE_HOST": minikube_ip,
        "KAFKA_SERVICE_PORT": "9092",
        "FLASK_DEBUG": "true",
    }
    return env_vars


def get_docker_env(ctx):
    env_ret = ctx.run(f"minikube -p {MINIKUBE_PROFILE} docker-env --shell=bash", hide=True)
    env = dict(re.findall(r'export ([\w_]+)="([^"]+)"', env_ret.stdout, re.M))
    return env


@contextlib.contextmanager
def mount(ctx, source, target, **kwargs):
    args = " ".join(f"--{k}={v}" for k, v in kwargs.items())
    mount_cmd = f"minikube -p {MINIKUBE_PROFILE} mount {args} {source}:{target}"
    try:
        mount_run = ctx.run(mount_cmd, asynchronous=True, pty=True)
        yield
    finally:
        os.kill(mount_run.runner.pid, signal.SIGINT)
        mount_run.join()

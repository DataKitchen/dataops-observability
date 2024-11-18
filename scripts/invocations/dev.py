# type: ignore
__all__ = [
    "pyclean",
    "dev_install",
    "mypy",
    "precommit",
    "required_dev_tools",
    "validate",
    "build_docs",
    "lint_docs",
    "mysql_shell",
]

import sys
from os.path import exists
from pathlib import Path
from sys import stderr

import pymysql
from invoke import UnexpectedExit, call, task

from scripts.invocations.common import (
    check_env_tools,
    get_host_env,
)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
OBSERVABILITY_DATABASE_NAMES = ("datakitchen",)


@task(name="required-tools")
def required_dev_tools(ctx):
    check_env_tools(required_tools=("mypy", "docker", "npx"))


@task
def is_venv(ctx):
    """
    Check if one is an environment.

    Note: Invoke de-duplicates redundant tasks. Do not worry if this is in multiple consecutive tasks.
    """
    if not (hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)):
        raise RuntimeError("You have not sourced a virtual environment.")


@task(name="dev-install", pre=(is_venv,))
def dev_install(ctx, quiet_pip=False):
    """Installs the package as a developer (editable, all optional dependencies)."""
    if quiet_pip:
        print("observability-be package is being re-installed.")
    ctx.run("pip install -e .[dev,build]", hide=quiet_pip)


@task
def pyclean(ctx):
    """Deletes old python files and build artifacts."""
    ctx.run("find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete")
    if exists("dist"):
        ctx.run("rm -rf dist")
    if exists("Observability_BE.egg-info"):
        ctx.run("rm -rf Observability_BE.egg-info")
    if exists("build"):
        ctx.run("rm -rf build")


@task(pre=(is_venv, required_dev_tools))
def precommit(ctx):
    try:
        ctx.run("pre-commit run --all-files")
    except UnexpectedExit:
        print("pre-commit has failed - stopping validation.", file=stderr)
        raise


@task(pre=(is_venv,))
def mypy(ctx):
    ctx.run("mypy . --config-file=./pyproject.toml")


@task(pre=(is_venv,))
def format_code(ctx):
    ctx.run("ruff check --fix-only .")
    ctx.run("ruff format .")


@task(pre=(is_venv,))
def lint_code(ctx):
    ctx.run("ruff check .")


@task(name="build-docs", pre=(is_venv, call(dev_install, quiet_pip=True)))
def build_docs(ctx):
    ctx.run("python deploy/generate_swagger_spec.py")
    ctx.run("python deploy/pages/deploy-pages.py local")


@task(name="lint-docs", pre=(is_venv, build_docs, required_dev_tools))
def lint_docs(ctx, generate_ignore_file=False):
    ignore_string = ""
    if generate_ignore_file:
        ignore_string = "--generate-ignore-file"
    ctx.run(f"npx @redocly/cli@1.0.0-beta.112 lint {ignore_string} observability@v1 event@v1 event@v2")


@task(pre=(precommit, mypy, lint_docs))
def validate(ctx):
    # note the pre-list for validation steps.
    print("Validation passed!")


@task
def mysql_shell(ctx):
    env = get_host_env(ctx)
    ctx.run(
        f"mysql --host={env['MYSQL_SERVICE_HOST']} --port={env['MYSQL_SERVICE_PORT']} "
        f"--user={env['MYSQL_USER']} --password={env['MYSQL_PASSWORD']} datakitchen",
        pty=True,
    )


@task
def recreate_databases(ctx):
    env = get_host_env(ctx)
    connection = pymysql.connect(host=env["MYSQL_SERVICE_HOST"], user=env["MYSQL_USER"], password=env["MYSQL_PASSWORD"])
    with connection:
        with connection.cursor() as cursor:
            for database in OBSERVABILITY_DATABASE_NAMES:
                cursor.execute(f"DROP DATABASE IF EXISTS {database}")
                cursor.execute(f"CREATE DATABASE {database}")

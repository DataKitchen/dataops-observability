# type: ignore
__all__ = ("test_ns",)

from pathlib import Path

from invoke import Collection, task

CWD = Path(__file__).resolve().parent.parent.parent
"""Working directory for commands."""


def _generate_cmd(**kwargs):
    """Simple pytest command generator."""
    base = ["pytest", "-o", "log_cli=True"]
    if (mark := kwargs.get("mark", None)) is not None:
        base.append(f"-m {mark}")

    processes = kwargs.get("processes") or "5"
    base.append(f"--numprocesses={processes}")
    base.append(f"--log-level={kwargs.get('level', 'DEBUG')}")

    # Setup the coverage report output using the given format.
    coverage_format = kwargs.get("coverage_format", "html")
    if coverage_format != "none":
        base.extend(["--cov", f"--cov-report={coverage_format}", "--no-cov-on-fail"])

    if (maxfail := kwargs.get("maxfail", None)) is not None:
        base.append(f"--maxfail={maxfail}")

    if kwargs.get("last_failed"):
        base.append("--last-failed")

    if kwargs.get("failed_first"):
        base.append("--failed-first")

    extra = kwargs.get("args", ())
    base.extend(extra)
    cmd = " ".join(base)
    return cmd


default_args = {
    "processes": "Number of processes to run in parallel; defaults to `5`",
    "level": "Logger level; defaults to DEBUG",
    "coverage-format": "Format for coverage output [term, xml, html, none, etc]; defaults to `html`",
    "maxfail": "Maximum number of tests to fail before aborting test run; defaults to 10",
    "last-failed": "Only rerun the tests that previously failed; defaults to False",
    "failed-first": "Run previous failures first and then the rest of the tests",
    "skip-slow": "Skip tests marked as `slow`",
}


@task(name="unit", help=default_args)
def unit_tests(
    ctx,
    processes=None,
    level="DEBUG",
    maxfail=10,
    last_failed=False,
    failed_first=False,
    coverage_format="html",
    skip_slow=True,
):
    """Invoke all tests marked `unit`."""
    mark = "'unit and not slow'" if skip_slow is True else "unit"
    cmd = _generate_cmd(
        processes=processes,
        level=level,
        mark=mark,
        maxfail=maxfail,
        last_failed=last_failed,
        failed_first=failed_first,
        coverage_format=coverage_format,
    )
    with ctx.cd(CWD):
        ctx.run(cmd, pty=True)


@task(name="integration", help=default_args)
def integration_tests(
    ctx,
    processes=None,
    level="DEBUG",
    maxfail=10,
    last_failed=False,
    failed_first=False,
    coverage_format="html",
    skip_slow=True,
):
    """Invoke all tests marked `integration`."""
    mark = "'integration and not slow'" if skip_slow is True else "integration"
    cmd = _generate_cmd(
        processes=processes,
        level=level,
        mark=mark,
        maxfail=maxfail,
        last_failed=last_failed,
        failed_first=failed_first,
        coverage_format=coverage_format,
    )
    with ctx.cd(CWD):
        ctx.run(cmd, pty=True)


@task(name="all", help=default_args)
def all_tests(
    ctx,
    processes=None,
    level="DEBUG",
    maxfail=10,
    last_failed=False,
    failed_first=False,
    coverage_format="html",
    skip_slow=True,
):
    """Invoke all tests marked `unit` or `integration` (does not run functional tests)."""
    kwargs = {
        "processes": processes,
        "level": level,
        "maxfail": maxfail,
        "last_failed": last_failed,
        "failed_first": failed_first,
        "coverage_format": coverage_format,
    }
    if skip_slow is True:
        kwargs["mark"] = "'not slow'"

    cmd = _generate_cmd(**kwargs)
    with ctx.cd(CWD):
        ctx.run(cmd, pty=True)


test_ns = Collection("test")
test_ns.add_task(unit_tests, "unit")
test_ns.add_task(integration_tests, "integration")
test_ns.add_task(all_tests, "all")

#! python
# A little history.
# We decided to group our tests on a per-module basis. This allows closer
# association, but it does make test-type discovery harder. So, we decided
# to rely on pytest to discover and run rests by marker (unit, integration, functional).
# However, this does require that the developer mark every test with a
# @pytest.<type> decorator, and every single developer (including myself) has
# forgotten to do so at one point or another.
#
# This script is used to add a check to the build-system that fails
# if a developer has forgotten to add a tag, and calls out those tests.
#
# Pre-commit note: As a part of test discovery, pytest imports the
# test files. This means that it also does the import of whatever
# is in the module, and thus the pytest in pre-commit's separate
# environment will throw a fit about missing modules.
# If someone can discover a way around it, this script would make an
# excellent pre-commit hook.
import re
import sys
from subprocess import CalledProcessError, CompletedProcess, run


def main() -> int:
    # Check all files if no files were given
    check_files = sys.argv[1:] or ["."]
    pytest_run: CompletedProcess = run(
        [
            "pytest",
            "--no-header",
            "--collect-only",
            "-m",
            "not unit and not integration and not functional",
            *check_files,
        ],
        capture_output=True,
    )
    # 5 means 'no tests collected'
    # https://docs.pytest.org/en/latest/reference/exit-codes.html
    if pytest_run.returncode == 5:
        print("All tests are properly marked. Success!")
        return 0
    if pytest_run.returncode == 2:
        print(
            "The tests could not be collected. This is probably caused by an import error. See the following error:",
            file=sys.stderr,
        )
        print(f"{pytest_run.stdout.decode('utf-8')}", file=sys.stderr)
        return pytest_run.returncode
    try:
        pytest_run.check_returncode()
    except CalledProcessError as e:
        # This probably occurs because you're not in your virtual-environment, there is
        # an import error in your tests, or because one of your marks was mispelled.
        print(pytest_run.stderr.decode("utf-8"), file=sys.stderr)
        print(f"{e}", file=sys.stderr)
        return pytest_run.returncode
    # with the above pytest run, the first group will represent the tests
    # missing tags, while the second group is a pair of numbers in the form
    # <number-of-untagged/total-tests>
    # Note: `.` in python regex does not match newlines, unless you specify re.DOTALL.
    tests_collected_regex = r"(.*)(\d+\/\d+)"
    result = re.search(tests_collected_regex, pytest_run.stdout.decode("utf-8"), re.DOTALL)
    if not result:
        print("Pytest produced no viable output. Unknown error.", file=sys.stderr)
        print(f"output:\n{pytest_run.stdout.decode('utf-8')}", file=sys.stderr)
        return 1

    tests_collected: list[str] = result.group(2).split("/")
    print(f"{tests_collected[0]} tests are unmarked and must be fixed.\n", file=sys.stderr)
    print(
        "Apply one of [@pytest.mark.unit, @pytest.mark.integration, @pytest.mark.functional] to the following tests:",
        file=sys.stderr,
    )
    print(result.group(1).strip(), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

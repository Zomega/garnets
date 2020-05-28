"""A series of tests designed to ensure every is nicely formatted."""

import json
import subprocess  # noqa: bandit:B404

import pytest


def tidypy_issues():
    """Find all the issues identified by tidypy."""
    command = subprocess.Popen(  # noqa: B603,B607
        ['tidypy', 'check', '--report', 'json'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    output, _ = command.communicate()
    return json.loads(output.decode("utf-8"))['issues']


def mypy_issues(args):
    """Find all the issues identified by mypy."""
    command = subprocess.Popen(  # noqa: B603
        ['mypy', '--ignore-missing-imports'] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    output, _ = command.communicate()
    if not command.returncode:
        return None
    return output.decode("utf-8")


ALL_TRACKED_FILENAMES = list(map(
    lambda bytes: bytes.decode("utf-8"),
    subprocess.check_output(  # noqa: B607
        "git ls-files",
        shell=True  # noqa: B602
    ).splitlines()
))

TIDYPY_OUTPUT = None


@pytest.mark.parametrize("filename", ALL_TRACKED_FILENAMES)
def test_tidypy(filename):
    """Tests that the given file passes tidypy."""
    global TIDYPY_OUTPUT  # noqa: global-statement
    if TIDYPY_OUTPUT is None:
        TIDYPY_OUTPUT = tidypy_issues()
    issues = TIDYPY_OUTPUT.get(filename, [])
    if len(issues) > 0:
        pytest.fail(
            '\n'.join(map(
                lambda issue: "%d:%d\t%s (%s:%s)" % (
                    issue['line'],
                    issue['character'],
                    issue['message'],
                    issue['tool'],
                    issue['code'],
                ),
                issues
            )),
            pytrace=False
        )


def test_python_type_safety():
    """Looks for python type annotation violations using mypy."""
    issues = mypy_issues(
        list(
            filter(
                lambda fname: fname.endswith('.py'),
                ALL_TRACKED_FILENAMES
            )
        )
    )
    if issues:
        pytest.fail(issues, pytrace=False)

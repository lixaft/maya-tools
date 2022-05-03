# pylint: disable=import-outside-toplevel
"""Run unit tests."""
import argparse
import os
import subprocess
import sys

import utilities


def test():
    """Test entry point."""
    from maya import standalone

    standalone.initialize()

    import pytest

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(os.path.join(root, "src"))
    os.chdir(root)

    argv = [
        "src",
        "tests",
        "--doctest-modules",
        "--cov=src",
        "--cov-report=term",
        "--cov-report=html",
        "--showlocals",
    ]
    argv.extend(sys.argv[1:])
    status = pytest.main(argv)

    standalone.uninitialize()
    return status


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "versions",
        metavar="N",
        nargs="+",
        help="The maya version on which the test should be runned",
    )
    parser.add_argument(
        "remainder",
        nargs=argparse.REMAINDER,
        help="The arguments to pass to pytest command.",
    )
    args = parser.parse_args()

    command = (
        "import sys;"
        "sys.path.append(r'{}');"
        "import run_tests;"
        "exit_code = run_tests.test();"
        "sys.exit(exit_code);"
    ).format(os.path.dirname(__file__))
    exit_code = 0
    for version in args.versions or [None]:
        try:
            argv = [utilities.find_mayapy(version), "-c", command]
            exit_code = subprocess.check_call(argv + args.remainder)
        except subprocess.CalledProcessError:
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

"""
A small wrapper around `github-backup`.
https://pypi.org/project/github-backup/
"""

import subprocess
from shutil import which


class GitHubBackup:
    def run(self, args):
        cmd = [which("github-backup")] + args
        subprocess.check_call(cmd)  # noqa: S603

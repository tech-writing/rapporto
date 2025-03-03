import datetime as dt
import sys
import time
import typing as t

import dateparser


class Zapper:
    """
    Support zapping messages after a) pressing enter, or b) waiting a few seconds.
    """

    def __init__(self, zap: str) -> None:
        self.zap = zap

    def wait(self) -> None:
        self.check()
        if self.zap.endswith("s"):
            duration = dateparser.parse(self.zap)
            if duration is None:
                raise ValueError(f"Unable to parse duration: {duration}")
            delay = dt.datetime.now() - duration
            time.sleep(delay.total_seconds())
        elif self.zap.startswith("key"):
            print("Press enter to zap messages and continue the program flow.", file=sys.stderr)
            tty_input()
            # wait_key()

    def check(self):
        if self.zap is None:
            return True
        if self.zap.endswith("s") or self.zap.startswith("key"):
            return True
        raise ValueError(
            f"Invalid configuration for zap: {self.zap}. "
            f"Either provide a duration (e.g. 1.42s), or `keypress`."
        )

    def process(self):
        if self.zap:
            self.wait()
            return True
        return False


def tty_input(prompt: t.Union[str, None] = None):
    """
    Read string from TTY.
    """
    with open("/dev/tty") as terminal:
        sys.stdin = terminal
        if prompt is None:
            user_input = input()
        else:
            user_input = input(prompt)
    sys.stdin = sys.__stdin__
    return user_input

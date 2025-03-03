import datetime as dt
import sys
import time
import typing as t

import dateparser


class Zapper:
    """
    Wait for a) pressing enter, or b) a few seconds.
    """

    def __init__(self, when: str, action: t.Optional[t.Callable] = None) -> None:
        self.when = when
        self.action: t.Optional[t.Callable] = action
        self.validate()
        self.delay: float = self._compute_delay()

    @property
    def is_stopclock(self):
        return self.when.endswith("s")

    @property
    def is_keypress(self):
        return self.when.startswith("key")

    def _compute_delay(self) -> float:
        if self.is_stopclock:
            duration = dateparser.parse(self.when)
            if duration is None:
                raise ValueError(f"Unable to parse duration: {duration}")
            return (dt.datetime.now() - duration).total_seconds()
        return 0

    def validate(self) -> bool:
        if self.is_stopclock or self.is_keypress:
            return True
        raise ValueError(
            f"Invalid value for `when` argument: {self.when}. "
            f"Either provide a duration (e.g. 1.42s), or `keypress`."
        )

    def process(self) -> bool:
        if self.when:
            self.wait()
            if self.action is not None:
                self.action()
            return True
        return False

    def wait(self) -> None:
        if self.is_stopclock:
            time.sleep(self.delay)
        elif self.is_keypress:
            print("Press enter to zap and continue the program flow.", file=sys.stderr)
            tty_input()


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

import signal
from contextlib import contextmanager

__all__ = ['timeout', 'raise_timeout']


@contextmanager
def timeout(seconds):
    signal.signal(signal.SIGALRM, raise_timeout)
    signal.alarm(seconds)

    try:
        yield
    # except TimeoutError:
    #     print(f'timeout error')
    #     pass
    finally:
        signal.signal(signal.SIGALRM, signal.SIG_IGN)


def raise_timeout(signum, frame):
    raise TimeoutError()

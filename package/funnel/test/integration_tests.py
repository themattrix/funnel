import sys
from os import linesep
from pprint import pprint
from multiprocessing import Queue
from funnel.__main__ import _SysRedirectWrapper, capture_output
from funnel.redirect import Redirect


def test_generic_redirect():
    expected_result = [
        ('[stdout] ', 'hello there!\n'),
        ('[stderr] ', 'meh meh mehhhh!\n'),
        ('[stdout] ', 'abcdefghij\n'),
        ('[stderr] ', 'ABCDEFGHIJ\n'),
        ('[stdout] ', 'klmn stranger\n'),
        ('[stdout] ', 'things\n'),
        ('[stdout] ', 'have\n'),
        ('[stderr] ', 'KLMN STRANGER\n'),
        ('[stderr] ', 'THINGS\n'),
        ('[stderr] ', 'HAVE\n'),
        ('[stdout] ', 'happened!\n'),
        ('[stderr] ', 'HAPPENED!\n')]

    # Used to retrieve the actual results from the TestOutputObserver subprocess.
    results = Queue()

    class TestOutputObserver(object):
        def __init__(self):
            self.actual_results = []

        def __call__(self, src, msg):
            self.actual_results.append((src, msg))

        def __enter__(self):
            pass

        # noinspection PyUnusedLocal
        def __exit__(self, exc_type, exc_val, exc_tb):
            results.put(self.actual_results)

    r = Redirect(TestOutputObserver())

    out = r.write_wrapper('[stdout] ')
    err = r.write_wrapper('[stderr] ')

    with r.context_manager():
        out.write('hello there!\n')
        err.write('meh meh mehhhh!\n')
        for c in 'abcde':
            out.write(c)
        for c in 'ABCDE':
            err.write(c)
        for c in 'fghij':
            out.write(c)
        for c in 'FGHIJ':
            err.write(c)
        out.write('\nklmn')
        err.write('\nKLMN')
        out.write(' stranger\nthings\nhave\nhappened!')
        err.write(' STRANGER\nTHINGS\nHAVE\nHAPPENED!')

    actual_results = results.get()

    pprint(actual_results)
    pprint(expected_result)

    assert actual_results == expected_result


def test_sys_redirect_wrapper():
    expected_non_redirected_results = (
        'stdout before\n'
        'stderr before\n'
        'print before\n'
        'stdout after\n'
        'stderr after\n'
        'print after\n')

    expected_redirected_results = [
        ('[stdout] ', 'stdout redirected\n'),
        ('[stderr] ', 'stderr redirected\n'),
        ('[stdout] ', 'print redirected\n')]

    results = Queue()

    class TestOutputObserver(object):
        def __init__(self):
            self.actual_results = []

        def __call__(self, src, msg):
            self.actual_results.append((src, msg))

        def __enter__(self):
            pass

        # noinspection PyUnusedLocal
        def __exit__(self, exc_type, exc_val, exc_tb):
            results.put(self.actual_results)

    actual_non_redirected_results = []

    class FakeStd(object):
        def write(self, msg):
            # noinspection PyUnresolvedReferences
            actual_non_redirected_results.append(msg)

        def flush(self):
            pass

    stdout = sys.stdout
    stderr = sys.stderr

    try:
        fake_std = FakeStd()

        sys.stdout = fake_std
        sys.stderr = fake_std

        sys.stdout.write('stdout before\n')
        sys.stderr.write('stderr before\n')
        print('print before')

        with _SysRedirectWrapper(TestOutputObserver()):
            sys.stdout.write('stdout redirected\n')
            sys.stderr.write('stderr redirected\n')
            print('print redirected')

        sys.stdout.write('stdout after\n')
        sys.stderr.write('stderr after\n')
        print('print after')

    finally:
        sys.stdout = stdout
        sys.stderr = stderr

    actual_redirected_results = results.get()
    actual_non_redirected_results = ''.join(actual_non_redirected_results)

    pprint(actual_non_redirected_results)
    pprint(expected_non_redirected_results)
    pprint(actual_redirected_results)
    pprint(expected_redirected_results)

    assert actual_non_redirected_results == expected_non_redirected_results
    assert actual_redirected_results == expected_redirected_results


def test_capture_output():
    with capture_output() as out:
        print("Hello!")
        sys.stderr.write('Error!' + linesep)
        print("Nice day!")

    result = out.get_output()

    assert result == [
        ('stdout', 'Hello!'),
        ('stderr', 'Error!'),
        ('stdout', 'Nice day!')]
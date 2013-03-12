import sys
from funnel.redirect import Redirect
from funnel.observers import FileOutputObserver, concat_formatter, ConsoleOutputObserver, ListOutputObserver


def redirect_output_to_file(filename, format_output=concat_formatter):
    return _SysRedirectWrapper(FileOutputObserver(filename, format_output))


def redirect_output_to_console(format_output=concat_formatter):
    return _SysRedirectWrapper(ConsoleOutputObserver(format_output=format_output))


def capture_output():
    """
    Capture the stdout and stderr into a list of (source, message) tuples.

    Example usage:

        with capture_output() as out:
            print("Hello!")
            sys.stderr.write('Error!\n')

        result = out.get_output()

        assert result == [
            ('stdout', 'Hello!'),
            ('stderr', 'Error!')]
    """
    class CaptureWrapper(object):
        def __init__(self):
            self.__sys_redirect_wrapper = _SysRedirectWrapper(
                ListOutputObserver(),
                stdout_prefix='stdout',
                stderr_prefix='stderr')

        def __enter__(self):
            self.__sys_redirect_wrapper.__enter__()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.__sys_redirect_wrapper.__exit__(exc_type, exc_val, exc_tb)

        def get_output(self):
            return self.__sys_redirect_wrapper.redirect.observer.get_output()

    return CaptureWrapper()


class _SysRedirectWrapper(object):
    def __init__(self, output_observer, stdout_prefix='[stdout] ', stderr_prefix='[stderr] '):
        self.__stdout = sys.stdout
        self.__stderr = sys.stderr
        self.redirect = Redirect(output_observer)
        self.__stdout_proxy = self.redirect.write_wrapper(stdout_prefix)
        self.__stderr_proxy = self.redirect.write_wrapper(stderr_prefix)

    def __enter__(self):
        sys.stdout = self.__stdout_proxy
        sys.stderr = self.__stderr_proxy
        self.redirect.start()
        return self

    # noinspection PyUnusedLocal
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.redirect.stop()
        sys.stdout = self.__stdout
        sys.stderr = self.__stderr

import sys
from os import linesep
from multiprocessing import Queue


# Concatenate the source and message into one string.
concat_formatter = lambda src, msg: src + msg


class NullOutputObserver(object):
    """Swallow all messages."""

    def __call__(self, src, msg):
        pass

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class ListOutputObserver(object):
    """Appends every message to a list. Get the entire list with get_output()."""

    def __init__(self, query_output_src='query_output'):
        self.__query_output_src = query_output_src
        self.__output = []
        self.__queue = Queue()

    def __call__(self, src, msg):
        self.__output.append((src, msg.rstrip(linesep)))

    def __enter__(self):
        pass

    # noinspection PyUnusedLocal
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__queue.put(self.__output)

    def get_output(self):
        """
        Must not be called until after the Redirect object has called the __exit__() function.
        """
        return self.__queue.get()


class ConsoleOutputObserver(object):
    """Write all messages to the specified output stream (stdout by default)."""

    def __init__(self, out_stream=sys.stdout, format_output=concat_formatter):
        self.__out_stream = out_stream
        self.__format_output = format_output

    def __call__(self, src, msg):
        self.__out_stream.write(self.__format_output(src, msg))

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class FileOutputObserver(object):
    """Append all messages to the specified file. The file is opened and closed with each line written."""

    def __init__(self, filename, format_output=concat_formatter):
        self.__filename = filename
        self.__format_output = format_output

    def __call__(self, src, msg):
        with open(self.__filename, 'a') as f:
            f.write(self.__format_output(src, msg))

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

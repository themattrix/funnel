from collections import namedtuple
from os import linesep
from multiprocessing import Process, Queue
from util import tear, split_last


# Redirect is the only useful thing for scripts to import.
__all__ = ['Redirect']


MetaMessage = namedtuple('MetaMessage', ('src', 'msg'))


class Redirect(object):
    """
    It is often necessary to redirect stdout and/or stderr from a script to somewhere else (like a file). The redirects
    provided by shells (>, >>, 1>, 2>, &>, etc) usually suffice for this purpose. However, it is occasionally useful
    to separate the output of disparate scripts.
    """

    def __init__(self, observer):
        # This observer should have the signature: fn(src, msg) -> None
        # After start() has been called, it is notified every time a write occurs.
        self.observer = observer
        # Provides a communication channel between producers calling the write() method and the consumer residing in the
        # __consumer() method.
        self.__queue = None
        # List of fragments which haven't yet been written because they don't have newlines.
        # A fragment is a non-newline terminated string.
        # For example, the string 'hello' is a fragment, but 'world\n' is not.
        self.__fragments = []

    def __del__(self):
        self.stop()

    def __append_fragment(self, src, msg):
        self.__fragments.append(MetaMessage(src, msg))

    def __join_fragments(self, fragments):
        return ''.join(f for _, f in fragments)

    def __prepend_existing_fragments(self, src, msg):
        """
        Gather all fragments with a source matching 'src', join them together, and prepend them to 'msg'. These matching
        fragments are removed from the fragment list.
        """
        matching_fragments, self.__fragments = tear(self.__fragments, lambda f: f.src == src)
        if matching_fragments:
            msg = self.__join_fragments(matching_fragments) + msg
        return msg

    def __flush_fragments(self):
        for f in self.__fragments:
            self.observer(f.src, f.msg + linesep)
        self.__fragments = []

    def __get_messages(self):
        while True:
            msg = self.__queue.get()
            if msg is None:
                # Getting None from the queue denotes the end of transmission.
                raise StopIteration()
            yield msg

    def __consumer(self):
        with self.observer:
            for src, msg in self.__get_messages():
                # Prepend any existing fragments with a matching source to the message.
                msg = self.__prepend_existing_fragments(src, msg)
                # Split the message into lines, then the lines into the tuple: (all-lines-but-last, last).
                body, tail = split_last(msg.splitlines(True))
                # Notify the observer of unambiguously terminated lines.
                for line in body:
                    self.observer(src, line)
                if tail.endswith(linesep):
                    # Also notify the observer of the final line, if it's terminated.
                    self.observer(src, tail)
                else:
                    # Otherwise, store it for later.
                    self.__append_fragment(src, tail)
            self.__flush_fragments()

    def start(self):
        if not self.__queue:
            self.write = self.__initialized_write
            self.__queue = Queue()
            self.__consumer_process = Process(target=self.__consumer)
            self.__consumer_process.start()

    def stop(self):
        if self.__queue:
            self.__queue.put(None)
            self.__consumer_process.join()
            self.__consumer_process = None
            self.__queue = None
            self.write = self.__uninitialized_write

    def context_manager(self):
        class RedirectContextManager(object):
            def __init__(self, redirect):
                self.__redirect = redirect

            def __enter__(self):
                self.__redirect.start()

            # noinspection PyUnusedLocal
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.__redirect.stop()

        return RedirectContextManager(self)

    def write_wrapper(self, src):
        class RedirectWrapper(object):
            def __init__(self, redirect, src):
                self.__redirect = redirect
                self.__src = src
            
            def write(self, msg):
                self.__redirect.write(self.__src, msg)

            def flush(self):
                pass

        return RedirectWrapper(self, src)

    def __uninitialized_write(self, src, msg):
        raise RuntimeError('The Redirect object must be started with start() before write() is called.')

    def __initialized_write(self, src, msg):
        self.__queue.put(MetaMessage(src, msg))

    write = __uninitialized_write

    def flush(self):
        pass

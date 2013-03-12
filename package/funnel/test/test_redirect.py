from nose.tools import raises
from funnel.observers import NullOutputObserver
from funnel.redirect import Redirect


@raises(RuntimeError)
def test_uninitialized_write_before_starting():
    Redirect(None).write('', '')


@raises(RuntimeError)
def test_uninitialized_write_after_stopping():
    r = Redirect(NullOutputObserver())
    with r.context_manager():
        r.write('src', 'msg')
    r.write('src', 'msg')

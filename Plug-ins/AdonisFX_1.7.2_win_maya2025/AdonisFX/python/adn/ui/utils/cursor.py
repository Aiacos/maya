from contextlib import contextmanager

try:
    from PySide6 import QtCore, QtWidgets, QtGui
except ImportError:
    from PySide2 import QtCore, QtWidgets, QtGui


@contextmanager
def wait_cursor_context():
    """This is a context to override the cursor to `Qt.WaitCursor` and restore it back when the context ends.

    Examples:
        >>> with wait_cursor_context():
        >>>     // do something
    """
    try:
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        yield
    finally:
        QtWidgets.QApplication.restoreOverrideCursor()


def wait_cursor_decorator_self(input_function):
    """Decorate a function to override the cursor to `Qt.WaitCursor` and restore it back when the function executes.
    Use this function to decorate methods inside of a class.

    Args:
        input_function (:obj:`function`): function to decorate.

    Examples:
        >>> @wait_cursor_decorator_self
        >>> def foo(self):
        >>>     // do something
    """
    def decorated_function(self):
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            input_function(self)
        except Exception as e:
            print("[AdonisFX] An error occurred overriding QCursor for function: {0}".format(input_function.__name__))
            raise e
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
    return decorated_function


def wait_cursor_decorator(input_function):
    """Decorate a function to override the cursor to `Qt.WaitCursor` and restore it back when the function executes.

    Args:
        input_function (:obj:`function`): function to decorate.

    Examples:
        >>> @wait_cursor_decorator
        >>> def foo():
        >>>     // do something
    """
    def decorated_function():
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            input_function()
        except Exception as e:
            print("[AdonisFX] An error occurred overriding QCursor for function: {0}".format(input_function.__name__))
            raise e
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
    return decorated_function

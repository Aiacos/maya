try:
    from PySide6 import QtCore, QtGui
except ImportError:
    from PySide2 import QtCore, QtGui


def open_url(url):
    """Utility method to launch the browser and open the give url link.

    Args:
        url (str): link to the website to launch on the browser.
    """
    QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

from PySide2 import QtGui, QtCore


def open_url(url):
    """Utility method to launch the browser and open the give url link.

    Args:
        url (str): link to the website to launch on the browser.
    """
    QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

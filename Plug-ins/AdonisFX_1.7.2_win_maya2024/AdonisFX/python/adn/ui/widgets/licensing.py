try:
    from PySide6 import QtCore, QtWidgets, QtGui
except ImportError:
    from PySide2 import QtCore, QtWidgets, QtGui

from adn.ui.widgets.base import BaseDialog
from adn.ui.widgets.dialogs import msg_box
from adn.utils.constants import UiConstants


class LicenseDialog:
    """Help class to associate each licensing dialog to a numeric identifier."""
    # Specific to activation stage
    DIALOG_ACTIVATE_QUESTION = 0
    DIALOG_ENTER_PRODUCT_KEY = 1
    DIALOG_ACTIVATED_SUCCESSFULLY = 2
    DIALOG_ACTIVATE_QUESTION_RETRY = 3
    # Specific to trial version use case
    DIALOG_INVALID_PRODUCT_KEY = 4
    DIALOG_TRIAL = 5
    DIALOG_TRIAL_EXPIRED = 6
    # Specific to invalid license or connection issues
    DIALOG_GENERIC_ERRORS = 7
    DIALOG_GRACE_PERIOD = 8
    DIALOG_RETRY_VERIFICATION_QUESTION = 9
    DIALOG_RETRY_VERIFICATION_SUCCESSFULLY = 10
    DIALOG_RETRY_VERIFICATION_FAILED = 11
    DIALOG_ALREADY_ACTIVATED = 12

    @staticmethod
    def check_dialog_id(dialog_id):
        """Check if the given dialog id is supported.

        Args:
            dialog_id (int): Numeric value to validate.

        Returns:
            bool: True if the id is valid, False otherwise.
        """
        return 0 <= int(dialog_id) <= 12


class ActivateQuestionDialog(BaseDialog):
    """Custom dialog to prompt a question to ask the user to activate the product.

    Args:
        parent (:obj:`QtWidgets.QWindow`, optional): Parent window to the dialog.
            Defaults to None.
    """
    def __init__(self, parent=None):
        title = "License Activation"
        super(ActivateQuestionDialog, self).__init__(
            title, parent, width=450, height=125,
            use_content=True, use_buttons=True, icon="question")

        # User response: close (0), use trial (1), activate (2)
        self.response = 0

        # Customize message
        self.message_label = QtWidgets.QLabel(self)
        self.message_label.setAlignment(QtCore.Qt.AlignLeft)
        self.message_label.setText("Do you want to activate the product "
                                   "or continue with your trial period?")
        self.message_layout.addWidget(self.message_label)
        self.message_layout.addStretch()

        # Configure buttons
        yes_button = QtWidgets.QPushButton("Activate")
        yes_button.clicked.connect(self.activate)
        trial_button = QtWidgets.QPushButton("Continue With Trial")
        trial_button.clicked.connect(self.trial)
        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(yes_button)
        self.buttons_layout.addWidget(trial_button)
        self.buttons_layout.addStretch()

    def activate(self):
        """Callback when activate button is pressed."""
        self.response = 2
        self.accept()

    def trial(self):
        """Callback when continue trial button is pressed."""
        self.response = 1
        self.reject()


class ActivateDialog(BaseDialog):
    """Custom dialog to allow the user to enter a product key.

    Args:
        parent (:obj:`QtWidgets.QWindow`, optional): Parent window to the dialog.
            Defaults to None.
        attempts (int, optional): Number of attempts remaining.
            Defaults to None.
    """
    def __init__(self, parent=None, attempts=None):
        title = "License Activation"
        super(ActivateDialog, self).__init__(
            title, parent, width=450, height=125,
            use_content=True, use_buttons=True)

        # User response: close or cancel (0), activate (product key as str)
        self.response = 0

        # Create product key line edit
        self.product_key = QtWidgets.QLineEdit(self)
        self.product_key.setAlignment(QtCore.Qt.AlignLeft)
        self.product_key.setPlaceholderText("Enter your product key here...")

        # Create attempts remaining label
        self.attempts_label = QtWidgets.QLabel()
        self.attempts_label.setAlignment(QtCore.Qt.AlignLeft)
        self.attempts_label.setStyleSheet("color: yellow")
        self.attempts_label.setHidden(True)
        if attempts is not None:
            text = "Attempts remaining: {0}".format(attempts)
            self.attempts_label.setText(text)
            self.attempts_label.setHidden(False)

        # Create label with help
        self.help_label = QtWidgets.QLabel()
        self.help_label.setAlignment(QtCore.Qt.AlignLeft)
        self.help_label.setText("Example: XXXX-XXXX-XXXX-XXXX-XXXX-XXXX-XXXX")
        self.help_label.setStyleSheet("font-style: italic")

        self.message_layout.addWidget(self.product_key)
        self.message_layout.addWidget(self.attempts_label)
        self.message_layout.addWidget(self.help_label)
        self.message_layout.addStretch()

        # Configure buttons
        activate_button = QtWidgets.QPushButton("Activate")
        activate_button.clicked.connect(self.activate)
        cancel_button = QtWidgets.QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(activate_button)
        self.buttons_layout.addWidget(cancel_button)
        self.buttons_layout.addStretch()

    def activate(self):
        """Callback when activate button is pressed."""
        self.response = self.product_key.text()
        self.accept()


class ActivateQuestionRetryDialog(BaseDialog):
    """Custom dialog to prompt a question to ask the user to try again to
    enter a product key when a previous activation attempt failed.

    Args:
        parent (:obj:`QtWidgets.QWindow`, optional): Parent window to the dialog.
            Defaults to None.
    """
    def __init__(self, parent=None):
        title = "License Activation"
        super(ActivateQuestionRetryDialog, self).__init__(
            title, parent, width=450, height=125,
            use_content=True, use_buttons=True, icon="error")

        # User response: close or cancel (0), try again (1)
        self.response = 0

        # Customize message
        self.message_label = QtWidgets.QLabel(self)
        self.message_label.setAlignment(QtCore.Qt.AlignLeft)
        self.message_label.setText("Invalid product key. "
                                   "Do you want to try again?")
        self.message_layout.addWidget(self.message_label)
        self.message_layout.addStretch()

        # Configure buttons
        yes_button = QtWidgets.QPushButton("Try Again")
        yes_button.clicked.connect(self.activate)
        cancel_button = QtWidgets.QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(yes_button)
        self.buttons_layout.addWidget(cancel_button)
        self.buttons_layout.addStretch()

    def activate(self):
        """Callback when try again button is pressed."""
        self.response = 1
        self.accept()


class RetryVerificationQuestionDialog(BaseDialog):
    """Custom dialog to prompt a question to ask the user to retry again to
    connect to the license server to verify the status of the activation.

    Args:
        parent (:obj:`QtWidgets.QWindow`, optional): Parent window to the dialog.
            Defaults to None.
    """
    def __init__(self, parent=None):
        title = "License Activation"
        super(RetryVerificationQuestionDialog, self).__init__(
            title, parent, width=450, height=125,
            use_content=True, use_buttons=True, icon="error")

        # User response: close or cancel (0), retry (1)
        self.response = 0

        # Customize message
        self.message_label = QtWidgets.QLabel(self)
        self.message_label.setAlignment(QtCore.Qt.AlignLeft)
        self.message_label.setText("Failed to connect to the license server.\n"
                                   "Make sure you are connected to the "
                                   "internet.\nDo you want to retry to "
                                   "connect?")
        self.message_layout.addWidget(self.message_label)
        self.message_layout.addStretch()

        # Configure buttons
        yes_button = QtWidgets.QPushButton("Retry")
        yes_button.clicked.connect(self.retry)
        cancel_button = QtWidgets.QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(yes_button)
        self.buttons_layout.addWidget(cancel_button)
        self.buttons_layout.addStretch()

    def retry(self):
        """Callback when retry again button is pressed."""
        self.response = 1
        self.accept()


def licensing_dialog(parent, dialog_id, info):
    """Helper function to launch the correct dialog based on the given id.

    Args:
        parent (:obj:`QtWidgets.QWindow`): Parent window to the dialog.
        dialog_id (int): Identifier of the dialog to prompt.
        info (int): Extra value to expose in the UI.

    Raises:
        NotImplementedError: if the dialog_id is not recognized.

    Returns:
        int, string or bool: user response to the dialog.
    """
    if not LicenseDialog.check_dialog_id(dialog_id):
        err = "{0} License dialog {1}.".format(UiConstants.LOG_PREFIX,
                                               dialog_id)
        raise NotImplementedError(err)

    title = "License Activation"

    # Ask user to activate: the user has never activated the product on
    # this machine and/or the machine was deactivated for some reason
    if dialog_id == LicenseDialog.DIALOG_ACTIVATE_QUESTION:
        question = ActivateQuestionDialog(parent=parent)
        question.exec_()
        return question.response

    # Ask user to enter product key: the user has a product key to register
    if dialog_id == LicenseDialog.DIALOG_ENTER_PRODUCT_KEY:
        product_key_dialog = ActivateDialog(parent=parent, attempts=info)
        product_key_dialog.exec_()
        return product_key_dialog.response

    # Activated successfully: the user entered a product key which was
    # validated by the license server. Product registered successfully
    if dialog_id == LicenseDialog.DIALOG_ACTIVATED_SUCCESSFULLY:
        message = "Product activated successfully! Please, restart the " \
                  "application to start using all AdonisFX features."
        try_again = msg_box(parent, "info", message, title=title)
        return int(try_again)

    # Error product key: the product key entered by the user is wrong
    # or not valid. We ask the user if he/she wants to try again
    if dialog_id == LicenseDialog.DIALOG_ACTIVATE_QUESTION_RETRY:
        question = ActivateQuestionRetryDialog(parent=parent)
        question.exec_()
        return question.response

    # Maximum product key attempts: the product key entered by the user
    # was wrong or not valid and he/she reached the maximum number of attempts
    # allowed. We prompt an error and exit
    if dialog_id == LicenseDialog.DIALOG_INVALID_PRODUCT_KEY:
        message = "Invalid product key. Please, contact support."
        return msg_box(parent, "error", message, title=title)

    # Trial: the user decided to use or continue the trial version and
    # the trial is still valid
    if dialog_id == LicenseDialog.DIALOG_TRIAL:
        days = info if info is not None else 1
        message = "Your trial expires in {0} days.".format(days)
        return msg_box(parent, "info", message, title=title)

    # Trial expired: the user decided to use or continue the trial version
    # but it expired. We prompt and error and exit
    if dialog_id == LicenseDialog.DIALOG_TRIAL_EXPIRED:
        message = "Your trial has expired. Please, activate your license or contact support."
        return msg_box(parent, "error", message, title=title)

    # Generic error message. This could include error messages from:
    # - Licensing server errors: the system could not complete the license check
    # process due to errors while communicating to the server. We prompt an
    # error and exit
    # - Incorrect GUID: The guid was not set for a specific launch mode.
    if dialog_id == LicenseDialog.DIALOG_GENERIC_ERRORS:
        message = ("License validation failed. Please, check the console for "
                   "more information or contact support.")
        return msg_box(parent, "error", message, title=title)

    # Grace period: could not connect to the server but this machine did the
    # request within the grace period. We prompt a warning and allow the user
    # to load the plugin
    if dialog_id == LicenseDialog.DIALOG_GRACE_PERIOD:
        days = info if info is not None else 1
        message = ("Could not connect to the license server for "
                   "verification. You can still use the product for a "
                   "maximum of {0} days.".format(days))
        return msg_box(parent, "warning", message, title=title)

    # Ask user to retry verification: could not connect to the server and
    # we can't allow the user to load the plugin. We ask the user if he/she
    # wants to retry the connection now
    if dialog_id == LicenseDialog.DIALOG_RETRY_VERIFICATION_QUESTION:
        retry_dialog = RetryVerificationQuestionDialog(parent=parent)
        retry_dialog.exec_()
        return retry_dialog.response

    # Retry verification succeed: the activation was verified after a
    # retry. We prompt an info message and allow the user to load the plugin.
    if dialog_id == LicenseDialog.DIALOG_RETRY_VERIFICATION_SUCCESSFULLY:
        message = "Your license has been verified successfully!"
        return msg_box(parent, "info", message, title=title)

    # Retry verification failed: could not connect to the server during
    # a verification process. We can't allow the user to load the plugin.
    # We prompt a message and exit
    if dialog_id == LicenseDialog.DIALOG_RETRY_VERIFICATION_FAILED:
        message = ("Could not connect to the license server for "
                   "verification. Make sure you are connected to the internet "
                   "and not blocking access to the activation servers.\n"
                   "Check the console for more information.")
        return msg_box(parent, "error", message, title=title)

    # The product had already been activated, inform the user
    if dialog_id == LicenseDialog.DIALOG_ALREADY_ACTIVATED:
        message = "Product already activated."
        return msg_box(parent, "info", message, title=title)

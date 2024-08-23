"""AbstractCheckData is the base logic for all checks. """

from arise.utils.decorators_utils import simple_catch_error_dec, undo_chunk_dec

class AbstractCheckData(object):
    """Base logic all checks will inherit from.

    Arguments:
        main (IORMainWindow): Arise main window
    """
    def __init__(self, main):
        self.main = main
        self._status = None

        self.name = ""
        self.info = ""
        self.has_fix = True
        self.type = "warning"  # warning or error.
        self.error_msg = ""
        self.position = 100


    @property
    def status(self):
        """Check status: None - wasn't run, True - passed, False - failed. """
        return self._status

    @undo_chunk_dec
    @simple_catch_error_dec
    def run_check(self):
        """Run check operation by UI. """
        self._status = self.check()

    def check(self):
        """Check logic subclasses will be placed here. (access IoMainWindow with self.main).

        Returns:
            bool: True if passed else False
        """
        pass

    @undo_chunk_dec
    @simple_catch_error_dec
    def run_fix(self):
        """Run check fix by UI. """
        self.fix()
        self._status = self.check()

    def fix(self):
        """Check fix logic subclasses will be placed here. (access IoMainWindow with self.main). """
        pass

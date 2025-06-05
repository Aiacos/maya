import maya.cmds as cmds


def undo_chunk(input_function):
    """Decorate a function to encapsulate all contained actions in the function inside of a single undo chunk.
    This would allow Maya to for example undo the whole stack of operations contained in a single function
    in one single go. Eg. Remove a weights display node and all connections in one go when the undo/redo
    actions are triggered.
    This function will rely on N input arguments.

    Args:
        input_function (:obj:`function`): function to decorate.

    Returns:
        any type: returned elements by the input_function.

    Examples:
        >>> @undo_chunk
        >>> def foo(*args, **kwargs):
        >>>     // do something
    """
    def decorated_function(*args, **kwargs):
        cmds.undoInfo(openChunk=True)
        try:
            return input_function(*args, **kwargs)
        finally:
            cmds.undoInfo(closeChunk=True)
    return decorated_function


def undo_disabled(input_function):
    """Decorate a function to avoid the actions to be added to the undo stack without flushing the stack.
    This function will rely on N input arguments.

    Args:
        input_function (:obj:`function`): function to decorate.

    Returns:
        any type: returned elements by the input_function.

    Examples:
        >>> @undo_disabled
        >>> def foo(*args, **kwargs):
        >>>     // do something
    """
    def decorated_function(*args, **kwargs):
        cmds.undoInfo(stateWithoutFlush=False)
        try:
            return input_function(*args, **kwargs)
        finally:
            cmds.undoInfo(stateWithoutFlush=True)
    return decorated_function

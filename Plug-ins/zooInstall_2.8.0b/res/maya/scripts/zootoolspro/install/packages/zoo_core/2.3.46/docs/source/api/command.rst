.. _ZooCommands:

Zoo Command
########################################

Python command pattern with undo,redo functionality for standard applications and or DCCs if supported via command executors

Commands follow some strict rules.

- All commands must inherent from zoo.libs.command.command.ZooCommand
- All commands must have the following overrides
    - id(property) the command id
    - creator(property) the developer of the command name
    - isUndoable(property) Does the command support undo
    - doIt(method), Main method to do the operation
    - undoIt(method), if is undoable then undoIt() must be implemented

Commands provide persistent Gui data aka settings
These include: Label, icon, toolip, color(foreground), backgroundColor

Any command can have a QAction generate on demand via command.commandAction()

Usage
=====

The built command library lives under zoo.libs.command.library but users can add there own path via the environment
variable 'ZOO_COMMAND_LIB' then running the following

.. code-block:: python

    from zoo.libs.command import executor
    executor.Executor().registerEnv("ZOO_COMMAND_LIB")

To execute commands one must use the executor class and never execute the command directly otherwise
it will not be added to the internal undo stack and or the redostack.

.. code-block:: python

    # to execute a command
    from zoo.libs.command import executor
    exe = executor.Executor()
    exe.executor("commandId", **kwargs)


To undo a command.

.. code-block:: python

    from zoo.libs.command import executor
    executor.Executor().registerEnv("ZOO_COMMAND_LIB")
    executor.undoLast()

To redo a command from the undostack.

.. code-block:: python

    from zoo.libs.command import executor
    executor.Executor().registerEnv("ZOO_COMMAND_LIB")
    executor.redoLast()

API
---

.. automodule:: zoo.libs.command.base
    :members:
    :undoc-members:
    :show-inheritance:

.. automodule:: zoo.libs.command.command
    :members:
    :undoc-members:
    :show-inheritance:

Executor
--------------------------------

.. automodule:: zoo.libs.command.executor
    :members:
    :undoc-members:
    :show-inheritance:


GUI
---------------------------------

.. automodule:: zoo.libs.command.commandui
    :members:
    :undoc-members:
    :show-inheritance:

.. automodule:: zoo.libs.command.commandviewer
    :members:
    :undoc-members:
    :show-inheritance:

Errors
------------------------------

.. automodule:: zoo.libs.command.errors
    :members:
    :undoc-members:
    :show-inheritance:


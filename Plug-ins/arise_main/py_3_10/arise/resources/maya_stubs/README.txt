These static stubs provide editor completion for maya.cmds without inspecting
Maya's live modules with Jedi. OpenMaya completion is disabled.

The command names were collected from Maya 2022, 2024 and 2026.
Command flags combine Maya's help metadata for those versions and selected
command synopsis flag names from Autodesk's Maya 2018 Python command reference:
https://help.autodesk.com/cloudhelp/2018/ENU/Maya-Tech-Docs/CommandsPython/
The result is a combined snapshot: a suggestion may not exist in every Maya
version, and newly installed plug-in commands may be missing. Commands without
available flag metadata retain generic signatures. Flags are optional keyword
parameters with placeholder defaults; their real types, default values,
positional arguments and documentation are not included. The stubs
are for analysis only and are never imported to execute a user's script.

For version-specific stubs, ARISE_MAYA_STUBS_PATH can contain one or more
directories separated by the operating system's path separator. Jedi searches
those directories before this bundled snapshot.

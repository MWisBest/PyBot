To add a command, it should be put in a new folder.

This folder should contain an "__init__.py" containing:
"from .FOLDER_NAME_HERE import *"

Then, add a "FOLDER_NAME_HERE.py" file (e.x. if the folder is "paste" the .py should also be called "paste").


Commands have a "standard" of sorts that they should follow.


It NEEDS a dict variable named "info". This dict should contain an entry called "names", and that entry should contain a list of strings which, when matched as the command name the bot user tries to use, executes this particular command. I don't care if it only wants to match one name either, put it in a 1-entry list. the dict should also contain an entry titled "access" with a default access level required (0 should be fine for most things).
It should import "__main__" and use that to reference any variables and functions in the main script (i.e. __main__.sendMessage( "e.x." )).

API Versions:

1:
It needs a dict variable named "info". The dict should contain:
- "names": LIST (even if it's just one entry) of names which run this command.
- "access": default access level required (0 should be fine for most things)
- "version": version of the command API used.
It should contain one function, titled "command".
That function should have three args:
1. "message": Whatever came after the command.
2. "user": The username of who used the command.
3. "recvfrom": The location the command was received from, (usually a channel, however a /msg directly from a user is also possible).
It should return True if the command was successful, or False if there was a problem.

2:
Version 1, with the following changes:
"command" function now has FOUR args:
That function should have three args:
NEW: 1. "command": The entry from the info dict's "names" that activated the command. (see: urban.py)
2. "message": Whatever came after the command.
3. "user": The username of who used the command.
4. "recvfrom": The location the command was received from, (usually a channel, however a /msg directly from a user is also possible).


SEE THE PASTE COMMAND FOR MORE REFERENCE, THANK YOU!

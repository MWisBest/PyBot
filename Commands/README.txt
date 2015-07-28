To add a command, it should be put in a new folder.

This folder should contain an "__init__.py" containing:
"from .FOLDER_NAME_HERE import *"

Then, add a "FOLDER_NAME_HERE.py" file (e.x. if the folder is "paste" the .py should also be called "paste").


Commands have a "standard" of sorts that they should follow.

Imports should try and be limited, and make sure that it isn't importing anything it doesn't need.
It NEEDS a dict variable named "info". This dict should contain an entry called "names", and that entry should contain a list of strings which, when matched as the command name the bot user tries to use, executes this particular command. I don't care if it only wants to match one name either, put it in a 1-entry list. the dict should also contain an entry titled "access" with a default access level required (0 should be fine for most things).
It should import "__main__" and use that to reference any variables and functions in the main script (i.e. __main__.sendMessage( "e.x." )).
They should contain 1 function, called command.
That function should have 2 args, the first being "message" and the second being "user"
It should return True if the command was successful, or False if there was a problem.

SEE THE PASTE COMMAND FOR MORE REFERENCE, THANK YOU!

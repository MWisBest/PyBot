To add a handler, it should be put in a new folder.

This folder should contain an "__init__.py" containing:
"from .FOLDER_NAME_HERE import *"

Then, add a "FOLDER_NAME_HERE.py" file (e.x. if the folder is "ctcp" the .py should also be called "ctcp").


Handlers have a "standard" of sorts that they should follow.


It should import "__main__" and use that to reference any variables and functions in the main script (i.e. __main__.sendMessage( "e.x." )).


API Versions:
MIN SUPPORTED: 2

1:
It needs a dict variable named "info". The dict should contain:
- "access": default access level required (0 should be fine for most things)
- "version": version of the handler API used.
It should contain one function, titled "handle".
That function should have one arg, 'packet'. This is a packet dict, see the main script for more info on packets.
It should return True if the packet was handled, or False if it wasn't or if there was a problem.

2:
Version 1, with the following changes:
info dict should now contain:
- "access": default access level required (0 should be fine for most things)
- "packets": LIST (even if it's just one entry! seriously, it's FASTER!!!) of packet types which this handler parses (e.x. PRIVMSG)
- "version": version of the handler API used.

SEE THE CTCP HANDLER FOR MORE REFERENCE, THANK YOU!

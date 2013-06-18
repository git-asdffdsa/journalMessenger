journalMessenger
================

alter output of journalctl (or any other json source) and forward it to different destinations

How It Works
------------
Whenever a new input line comes, it matches it with all the rules in rules/
If first applying rule is blocked in the current profile, no output is made, otherwise it is formatted according to the rule and then forwarded to whatever output you have specified (currently stdout or libnotify)
This means, rules read in first (they are read alphabetically) are matched first (override others). In a profile, mentioning a rule later overrides a previous mention
The rules heavily depend on regex, as well as the profiles. 
Q&A
---
*   *what can this be used for?*
   *   you can automatically get informed by your notification manager if a certain information is logged (e.g. there has been an error, something was mounted, etc.)
   *   you can easily format & clarify a certain log (e.g. there must be something suspicious within this log)
*   *how do I use it?*
   *   use ```./journalMessenger.py --help``` for more information
*   *I get an error by systemd/journal.py / the journal live feed is buggy*
   *   Currently, the systemd python module may be broken for some (actually fixed by now,
see [this commit](http://cgit.freedesktop.org/systemd/systemd/commit/?id=0a0c35d151570)), in which case you can workaround it by using
  ```journalctl -f -n 0 --output=json | ./journalMessenger.py --input stdin```
    

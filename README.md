meyerbot
========

A Python web bot for automatically posting "Tests?" to github pull requests lacking enough tests

Instructions
------------

To run the bot on a regular schedule, create a Python file with the following code.

```python
from meyerbot import *

mb = MeyerBot("<botuser>", "<password>", "<org/user>", "<repo>")
mb.post()
```

Add your appropriate secret credentials. You can add a cron job like the following
to run it every five minutes.

```
*/5 * * * * * /usr/local/bin/python /path/to/meyerbot/run.py
```



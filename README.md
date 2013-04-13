# Yet Another Django Project Template

This is my kickstarter for django projects.
It uses config files (see [python docs][1] for syntax) to form `django.conf.settings`.

Configuration files are:
* `etc/runtime.cfg` for basic setup;
* `etc/private-runtime.cfg` for security, email and admins settings;
* `etc/private-mq.cfg` for celery config (optional);
* `etc/private-db.cfg` for db config (optional).

See also `etc/example.*.cfg` files.

[1]: http://docs.python.org/2/library/configparser.html

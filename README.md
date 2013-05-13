# Yet Another Django Project Template

This is my kickstarter for django projects.
It uses config files (see [python docs][1] for syntax) to form `django.conf.settings`.

Configuration files are:
* `etc/runtime.cfg` for basic setup;
* `etc/private-runtime.cfg` for security, email and admins settings;
* `etc/url.cfg` for common tom level urls;
* `etc/private-urls.cfg` for top level urls;
* `etc/mq.cfg` for common celery config (optional);
* `etc/private-mq.cfg` for celery config (optional);
* `etc/private-db.cfg` for db config (optional).

You can store all settings in one cfg file if you want.

List apps you want to see in `INSTALLED_APPS` in `etc/private-apps.txt` and in `etc/apps.txt`.

See also `etc/example.*.cfg` files.

[1]: http://docs.python.org/2/library/configparser.html

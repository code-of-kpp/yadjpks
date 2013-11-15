from django.conf import settings
from django.conf.urls import patterns, include, url

urlpatterns_list = []

if 'django.contrib.admindocs' in settings.INSTALLED_APPS:
    urlpatterns_list.append(
            url(r'^admin/doc/', include('django.contrib.admindocs.urls'))
        )

if 'django.contrib.admin' in settings.INSTALLED_APPS:
    from django.contrib import admin
    admin.autodiscover()

    urlpatterns_list.append(
            url(r'^admin/', include(admin.site.urls))
        )

if 'admin_tools' in settings.INSTALLED_APPS:
    urlpatterns_list.append(
            url(r'^admin/tools/', include('admin_tools.urls'))
        )

if hasattr(settings, 'TOP_LEVEL_URLS'):
    for app, path in settings.TOP_LEVEL_URLS:
        urlpatterns_list.append(
                url(path, include(app +
                    ('' if app.endswith('.urls') else '.urls')))
            )

urlpatterns = patterns('', *urlpatterns_list)

del urlpatterns_list

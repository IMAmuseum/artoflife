from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'artoflife.views.home', name='home'),
    # url(r'^artoflife/', include('artoflife.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    # A view screen for abbyy scan data
    url(r'^abbyy_viewer/$', 'abbyy_viewer.views.scandata'),
    url(r'^abbyy_viewer/(?P<scan_id>.+)$', 'abbyy_viewer.views.scandata'),
    url(r'^scandata/(?P<scan_id>.+)/jp2_(?P<index>\d+)\.jp2$', 'abbyy_viewer.views.jp2_image'),
    url(r'^scandata/(?P<scan_id>.+)/flippy_(?P<index>\d+)\.jpg$', 'abbyy_viewer.views.flippy_image'),
)

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
    url(r'^picture_blocks/(?P<scan_id>.+)/$', 'abbyy_viewer.views.picture_block_index'),
    url(r'^picture_blocks_analysis/(?P<scan_id>.+)/$', 'abbyy_viewer.views.picture_blocks_analysis'),
    url(r'^picture_blocks_gold_analysis/(?P<scan_id>.+)/$', 'abbyy_viewer.views.picture_blocks_gold_analysis'),
    url(r'^picture_blocks/(?P<scan_id>.+)/(?P<index>\d+)\.(?P<ext>.+)$', 'abbyy_viewer.views.picture_blocks'),
    url(r'^scandata/(?P<scan_id>.+)/jp2_(?P<index>\d+)\.jp2$', 'abbyy_viewer.views.jp2_image'),
    url(r'^scandata/(?P<scan_id>.+)/flippy_(?P<index>\d+)\.jpg$', 'abbyy_viewer.views.flippy_image'),

    # Views for browsing the mongo database
    url(r'^mongo/$', 'mongo_viewer.views.main'),
    url(r'^mongo/scan/(?P<scan_id>.+)$', 'mongo_viewer.views.scan'),
    url(r'^mongo/page/(?P<scan_id>.+)/(?P<page_id>\d+)$', 'mongo_viewer.views.page'),
    url(r'^mongo/picture_blocks/(?P<scan_id>.+)/(?P<page_id>\d+)$', 'mongo_viewer.views.pageWithPictureBlocks'),
    url(r'^mongo/picture_blocks/(?P<scan_id>.+)/(?P<page_id>\d+)\.svg$', 'mongo_viewer.views.pictureBlocksAsSVG'),
    url(r'^mongo/coverage-histogram/$', 'mongo_viewer.views.coverageHistogram'),
    url(r'^mongo/compression-histogram/$', 'mongo_viewer.views.compressionHistogram'),
    url(r'^mongo/ia-thumb/(?P<scan_id>.+)/(?P<index>\d+)$', 'mongo_viewer.views.thumbImage')

)

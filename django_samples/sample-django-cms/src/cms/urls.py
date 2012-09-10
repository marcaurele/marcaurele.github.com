from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^tiny_mce/(?P<path>.*)$', 'django.views.static.serve',
        { 'document_root': '/home/marco/workspaces/lux4you/sample-django-cms/resources/jscripts/tiny_mce/' }),

    (r'^search/$', 'cms.search.views.search'),
    
    (r'^weblog/categories/', include('coltrane.urls.categories')),
    (r'^weblog/links/', include('coltrane.urls.links')),
    (r'^weblog/tags/', include('coltrane.urls.tags')),
    (r'^weblog/', include('coltrane.urls.entries')),

    #last item ALWAYS!
    (r'', include('django.contrib.flatpages.urls')),
)

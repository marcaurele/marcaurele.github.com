import os
from bookmarks.views import *
from bookmarks.feeds import *
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

site_media = os.path.join(
	os.path.dirname(__file__), 'site_media'
)

# Create the feeds dict before the url pattern
feeds = {
	'recent': RecentBookmarks,
	'user': UserBookmarks
}

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^django_bookmarks/', include('django_bookmarks.foo.urls')),
    # Browsing
    (r'^$', main_page),
    (r'^user/(\w+)/$', user_page),
    
    # Session management
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', logout_page),
    (r'^register/$', register_page),
    (r'^register/success/$', direct_to_template, {'template': 'registration/register_success.html'}),
    (r'^password/$', 'django.contrib.auth.views.password_change'),
    (r'^password/success$', 'django.contrib.auth.views.password_change_done'),
    
    # Bookmark management
    (r'^save/$', bookmark_save_page),
    (r'^tag/$', tag_cloud_page),
    (r'^tag/([^\s]+)/$', tag_page),
    (r'^search/$', search_page),
    (r'^ajax/tag/autocomplete/$', ajax_tag_autocomplete),
    (r'^vote/$', bookmark_vote_page),
    (r'^popular/$', popular_bookmark_page),
    (r'^bookmark/(\d+)/$', bookmark_page),
    
    # Friends
    (r'^friends/(\w+)/$', friends_page),
    (r'^friend/add/$', friend_add),
    (r'^friend/invite/$', friend_invite),
    (r'^friend/accept/(\w+)/$', friend_accept),
    
    # Comments
    (r'^comments/', include('django.contrib.comments.urls')),
    
    # Feeds
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    
    # i18n
    (r'^i18n/', include('django.conf.urls.i18n')),
    
    # Static files
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': site_media}),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^admin/', include(admin.site.urls)),
)

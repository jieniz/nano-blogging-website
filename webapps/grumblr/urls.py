from django.conf.urls import include, url
import grumblr.views
import django.contrib.auth.views

urlpatterns = [

    url(r'^$', grumblr.views.home, name='main'),
    url(r'^global_stream$', grumblr.views.home, name='home'),
    url(r'^follower_stream$', grumblr.views.follower_stream, name='follower_stream'), 
    url(r'^follow/(?P<username>\w+)$', grumblr.views.follow, name='follow'),
    url(r'^unfollow/(?P<username>\w+)$', grumblr.views.unfollow, name='unfollow'),

    url(r'^profile/(?P<username>\w+)$', grumblr.views.profile, name='profile'),
    url(r'^photo/(?P<username>\w+)$', grumblr.views.photo, name='photo'),
    url(r'^edit_profile$', grumblr.views.edit_profile, name='edit_profile'),
    url(r'^change_password$', grumblr.views.change_password, name='change_password'),

    url(r'^login', grumblr.views.log_in, name='login'),
    url(r'^logout', django.contrib.auth.views.LogoutView.as_view(), name='logout'),
    url(r'^register$', grumblr.views.register, name='register'),
    url(r'^confirmation/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$', grumblr.views.confirmation, name='confirm'),
    url(r'^reset_password$', grumblr.views.reset_password, name='reset_password'),
    url(r'^reset_confirmation/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$', grumblr.views.reset_confirmation),

    url(r'^add_post', grumblr.views.add_post, name='add_post'),
    url(r'^post', grumblr.views.post, name='post'),
    url(r'^update-profile/(?P<username>.+)/(?P<time>.+)$', grumblr.views.update_profile),
    url(r'^update-profile/(?P<username>.+)/?$', grumblr.views.update_profile),
    url(r'^update-follower/(?P<time>.+)$', grumblr.views.update_follower),
    url(r'^update-follower/?$', grumblr.views.update_follower),
    url(r'^update/(?P<time>.+)$', grumblr.views.update),
    url(r'^update/?$', grumblr.views.update),

    url(r'^update-comments/(?P<time>.+)/(?P<post_id>\d+)$', grumblr.views.update_comments),    
    url(r'^add-comment/(?P<post_id>\d+)$', grumblr.views.add_comment),

]

from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'trainingProject.views.home', name='home'),
    # url(r'^trainingProject/', include('trainingProject.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('trainingApp.views',
                        url(r'^$', 'posts'),
                        url(r'^posts/$', 'posts'),
                        url(r'^post/(?P<post_id>\d+)/$', 'post'),
                        url(r'^signUp/$', 'signUp', name='pageSignUp'),
                        url(r'^signIn/$', 'signIn', name='pageSignIn'),
                        url(r'^cmail/$', 'confirmMail', name='pageConfirmMail'),
                        )


from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

handler404 = 'trainingApp.errors.error404'
handler500 = 'trainingApp.errors.error500'

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
                        url(r'^$', 'posts', name='pageHome'),
                        url(r'^posts/$', 'posts', name='pagePosts'),
                        url(r'^post/(?P<slug>[\w-]+).html$', 'post', name='pagePost'),
                        url(r'^category/(?P<slug>[\w-]+).html$', 'category', name='pageCategory'),
                        url(r'^profile/(?P<slug>[\w-]+).html$', 'profile', name='pageProfile'),
                        url(r'^settings/$', 'settings', name='pageSettings'),
                        url(r'^signUp/$', 'signUp', name='pageSignUp'),
                        url(r'^signIn/$', 'signIn', name='pageSignIn'),
                        url(r'^signOut/$', 'signOut', name='pageSignOut'),
                        url(r'^post/add/$', 'postAdd', name='pagePostAdd'),
                        url(r'^category/add/$', 'categoryAdd', name='pageCategoryAdd'),
                        url(r'^comment/add/(?P<slug>[\w-]+).html$', 'commentAdd', name='pageCommentAdd'),
                        url(r'^deleteAccount/$', 'deleteAccount', name='pageDeleteAccount'),
                        url(r'^confirmMail/(?P<key>\w+)$', 'confirmMail', name='pageConfirmMail'),
                        url(r'^confirmCommentWithMail/(?P<post_id>\w+)/(?P<comment_id>\w+)/(?P<key>\w+)$',
                            'confirmCommentWithMail', name='pageConfirmCommentWithMail'),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
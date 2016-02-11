__author__ = 'Monte'
from django.conf.urls import url
import easy.views

urlpatterns = [
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^$', 'easy.views.my_view', name="home"),
    url(r'^signup/$', 'easy.views.signup_view', name="signup"),
    url(r'^details/$', 'easy.views.details_view', name="details"),
]



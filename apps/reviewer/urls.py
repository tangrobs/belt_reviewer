from django.conf.urls import url
from . import views

urlpatterns =[
    url(r'^$',views.index),
    url(r'^register$', views.register),
    url(r'^books$', views.books),
    url(r'^logout$', views.logout),
    url(r'^login$', views.login),
    url(r'^books/add$', views.addbookpage),
    url(r'^addbook$', views.addbook),
    url(r'^books/(?P<id>\d+)$', views.showbook),
    url(r'^addreview$', views.addreview),
    url(r'^users/(?P<id>\d+)$', views.user),
    url(r'^deletereview/(?P<id>\d+)$', views.deletereview),
]
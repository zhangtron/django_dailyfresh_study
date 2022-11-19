from django.conf.urls import url, include
from df_cart.views import *

urlpatterns = [
    url(r'^$', cart),
    url(r'^add(\d+)_(\d+)/$', add),
    url(r'^cart_num/$', cart_num),
    url(r'^edit(\d+)_(\d+)/$', edit),
    url(r'^delete(\d+)/$', delete),
]
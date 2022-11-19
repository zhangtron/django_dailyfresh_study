from django.conf.urls import url, include
from df_order.views import *

urlpatterns = [
    url(r'^$', order),
    url(r'^order_handle/$', order_handle),
    url(r'^pay/$', pay),
]
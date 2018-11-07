from django.conf.urls import url
from hardware import views


urlpatterns = [
    url(r'^$', views.root_view, name='hw_root'),
    url(r'^api/$', views.hardware_api, name='hw_api'),
    url(r'^list/$', views.HardwareAvailableView.as_view(), name='hw_list'),
    url(r'^request/$', views.HackerCurrentRequestView.as_view(), name='hw_request'),
    url(r'^active/$', views.HackerCurrentActiveView.as_view(), name='hw_active'),
    url(r'^list/amount$', views.HardwareSelectAmountView.as_view(), name='hw_selectamount'),
    url(r'^hacker/$', views.HardwarePickUpReturnView.as_view(), name='hw_pickupreturn'),
    url(r'^all/$', views.HardwareAvailableAdmin.as_view(), name='hw_listall'),
    url(r'^active/all/$', views.HardwareActiveAdmin.as_view(), name='hw_active'),
    url(r'^hacker/(?P<id>[\w-]+)/return/$', views.HackerReturnView.as_view(), name='hw_return'),
    url(r'^hacker/(?P<id>[\w-]+)/pickup/$', views.HackerPickupView.as_view(), name='hw_pickup'),
    url(r'^hacker/(?P<id>[\w-]+)/$', views.RequestsHistoricView.as_view(), name='hw_requestor'),
]

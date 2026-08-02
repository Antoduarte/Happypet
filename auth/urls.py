from django.urls import re_path
from django.views.generic import TemplateView
from .views import CustomLoginView, CustomLogoutView

urlpatterns = [
    re_path(r'^$', TemplateView.as_view(template_name='welcome.html'), name='welcome'),
    re_path(r'^login/$', CustomLoginView.as_view(), name='login'),
    re_path(r'^logout/$', CustomLogoutView.as_view(), name='logout'),
]

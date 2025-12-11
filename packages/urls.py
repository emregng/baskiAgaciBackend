from django.urls import path
from . import views

app_name = 'packages'

urlpatterns = [
    path('package-list/', views.package_list, name='package-list'),
    path('buy-package/', views.buy_package, name='buy-package'),


]
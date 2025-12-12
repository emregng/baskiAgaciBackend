from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('user/', views.profile, name='profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('sektor/', views.sektor, name='sektor'),
    path('send-sms/', views.send_sms_code, name='send_sms'),
    path('check-sms/', views.check_sms_code, name='check_sms'),
    path('city/', views.city_list, name='city_list'),
    path('district/<int:city_id>/', views.district_list, name='district_list'),
]
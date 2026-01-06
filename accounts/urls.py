from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views,panel

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
    path('get-company-profile/', views.get_company_profile, name='get-company-profile'),
    path('update-profile/', views.update_profile, name='update-profile'),
    path('payment-types/', views.payment_type_list, name='payment_type_list'),
    # ADMIN PANEL URLS
    path('active-users/', panel.ActiveUsersListView.as_view(), name='active_users_list'),
    path('users/create/', panel.create_user, name='create_user'),
    path('users/update-status/', panel.update_user_status, name='update_user_status'),
    path('users/detail/<int:id>/', panel.user_detail, name='user_detail'),
    path('users/update/<int:id>/', panel.update_user, name='update_user'),
    path('users/delete/', panel.delete_user, name='delete_user'),
    path('media-list/', panel.CompanyMediaListView.as_view(), name='company_media_list'),
    path('images/update-status/', panel.update_image_status, name='update_image_status'),

    


  


]
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_step1, name='register_step1'),
    path('register/verify/', views.verify_otp, name='verify_otp'),
    path('register/complete/', views.complete_profile, name='complete_profile'),
    path('login/', views.login_password, name='login_step1'),
    path('login/otp/', views.login_otp_step1, name='login_otp_step1'),
    path('login/otp/verify/', views.login_otp_verify, name='login_otp_verify'),
    path('logout/', views.logout_view, name='logout'),
    
    # تغییر رمز و حذف اکانت
    path('change-password/', views.change_password_step1, name='change_password_step1'),
    path('change-password/verify/', views.change_password_verify, name='change_password_verify'),
    path('delete-account/', views.delete_account, name='delete_account'),
    
    # تیکت‌ها (کاربر)
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/create/', views.create_ticket, name='create_ticket'),
    path('tickets/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    
    # تیکت‌ها (مدیر)
    path('admin-tickets/', views.admin_ticket_list, name='admin_ticket_list'),
    path('admin-tickets/<int:pk>/', views.admin_ticket_detail, name='admin_ticket_detail'),
]
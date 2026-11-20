from django.urls import path
from . import views

app_name = 'competitions'

urlpatterns = [
    # پنل ادمین
    path('admin/list/', views.admin_competition_list, name='admin_list'),
    path('admin/create/', views.admin_competition_create, name='admin_create'),
    path('admin/<int:pk>/edit/', views.admin_competition_edit, name='admin_edit'),
    path('admin/<int:pk>/delete/', views.admin_competition_delete, name='admin_delete'),
    path('admin/<int:pk>/questions/', views.manage_questions, name='manage_questions'),  # 👈 جدید
    
    # عمومی
    path('<int:pk>/', views.competition_detail, name='detail'),
    path('<int:pk>/take/', views.take_competition, name='take'),  # 👈 جدید
    path('<int:pk>/result/<int:attempt_id>/', views.competition_result, name='result'), 
     path('', views.competition_list, name='list'),
      # 👈 جدید
]

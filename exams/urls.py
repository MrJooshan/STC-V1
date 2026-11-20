from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('', views.exam_list, name='list'),
    path('create/', views.create_exam, name='create'),
    path('my-exams/', views.my_exams, name='my_exams'),
    path('<int:pk>/', views.exam_detail, name='detail'),
    path('<int:pk>/study/', views.study_page, name='study'),
    path('<int:pk>/study/<int:page_num>/', views.study_page, name='study_page'),
    path('<int:pk>/take/', views.take_exam, name='take'),
    path('<int:pk>/result/<int:attempt_id>/', views.exam_result, name='result'),
    path('<int:pk>/manage/', views.manage_exam, name='manage_exam'),
]
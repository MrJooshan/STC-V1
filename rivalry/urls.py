from django.urls import path
from . import views

app_name = 'rivalry'

urlpatterns = [
    path('lobby/', views.lobby, name='lobby'),
]
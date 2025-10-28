from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('upload/', views.Upload.as_view(), name='upload_song_file'),
    path('newsletter/<str:action>/', views.Newsletter.as_view(), name='newsletter'),
]
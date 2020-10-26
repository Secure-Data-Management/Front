from django.urls import path
from frontend import views


app_name = 'frontend'
urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_file, name='upload'),
    path('search/', views.search_files, name='search'),
]

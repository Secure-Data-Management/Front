from django.urls import path
from frontend import views

app_name = 'frontend'
urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_file, name='upload'),
    path('search/', views.search_files, name='search'),
    path('server_ip/', views.change_server, name='server_ip'),
    path('create-account/', views.create_account, name='new_account'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
]

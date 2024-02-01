from django.urls import path

from . import views

app_name = 'authentication'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout_view'),
    path('password_change/', views.password_change, name='password_change'),
]

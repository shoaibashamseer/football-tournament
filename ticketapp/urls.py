from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login'),
    path('base/', views.base_page, name='base'),
    path('check-in/', views.check_in_page, name='check_in'),
    path('scan/', views.scan_page, name='scan_page'),
    path('scan/<str:action>/', views.scan_qr, name='scan_qr'),
    path('logout/', views.logout_page, name='logout'),
]

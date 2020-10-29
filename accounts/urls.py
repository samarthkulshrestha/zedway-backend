from django.urls import path
from django.conf.urls import url
from . import views
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('update/', views.update, name='update'),
    path('settings/', views.settings, name='settings'),
    path('reset-password/', PasswordResetView.as_view(), name='password_reset'),
    path('reset-password/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset-password/confirm/<token>/<uidb64>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset-password/complete', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('follow/<slug>/', views.follow, name='follow'),
    path('<slug>/report', views.report_user, name='report-user'),
    path('<slug>/followers', views.list_followers, name='followers'),
    path('<slug>/followers/<int:pk>/remove', views.remove_follower, name='remove-follower'),
    path('<slug>/following', views.list_following, name='following'),
    path('<slug>/block', views.block_user, name='block-user'),
    path('<slug:slug>/', views.view_profile, name='view_profile'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('new/', views.newPost, name='new-post'),
    path('new-type/', views.new_type, name='new-post-type'),
    path('like/', views.like_post, name='like-post'),
    path('ajax-like/', views.ajax_like_post, name='ajax-like-post'),
    path('<slug:slug>/', views.view_post, name='view-post'),
    path('<slug:slug>/likes/', views.liked_by, name='likes'),
    path('<slug:slug>/delete/', views.delete_post, name='delete-post'),
    path('<slug:slug>/report', views.report_post, name='report-post'),
    path('<slug:slug>/comment/<id>/report', views.report_comment, name='report-comment'),
    path('add-view/', views.view_post, name='add-view')
]

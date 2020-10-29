from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('land/', views.land, name='land'),
    path('explore/', views.explore, name='explore'),
    path('search/', views.search, name='search'),
    path('hashtags/<tag>/', views.hashtag, name='hashtag'),
    path('follow/<tag>/', views.follow_hashtag, name='follow-hashtag'),
    path('crop/<int:pk>', views.crop_post, name='crop-post'),
    path('crop/', views.crop_profile, name='crop-profile'),
    path('update-profile/', views.update_img_set, name='update-profile-set'),
    path('update-profile-u/', views.update_img_sign2, name='update-profile-u'),
    path('about/', views.about, name='about'),
    path('contact/', views.contactus, name='contact'),
    path('cookies-policy/', views.cookies_policy, name='cookies-policy'),
    path('privacy-policy/', views.privacy_policy, name='privacy-policy'),
    path('security-policy/', views.security_policy, name='security-policy'),
    path('terms-of-use/', views.terms_of_use, name='terms-of-use'),
    path('community-guidelines/', views.community_guidelines, name='community-guidelines'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/add/', views.add_blog_post, name='add_blog_post'),
    path('blog/<slug:slug>/edit/', views.edit_blog_post, name='edit_blog_post'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
]

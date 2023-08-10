from django.urls import path 
from . import views

urlpatterns = [
    path('login/', views.login_view , name= 'login'),
    path('logout/', views.logout_view , name= 'logout'),
    path('signup/', views.signup_view , name= 'signup'),
    path('dashboard/' , views.dashboard_view  , name='dashboard'),
    path('edit_profile/' , views.edit_profile_view , name='edit_profile'),
]
from django.urls import path 
from . import views
urlpatterns = [
    path('' , views.index , name='index') ,
    path('register_container/' , views.register_container),
    path('start_container/<int:container_id>/', views.start_container , name='start_container'),
    path('stop_container/<int:container_id>/', views.stop_container , name='stop_container'),
    path('list_container/' , views.list_container , name='list_container'),
    path('delete_container/<int:container_id>/' , views.delete_container , name='delete_container'),
    path('add_image/' , views.add_image , name='add_image'),
    path('list_images/' , views.list_images , name='list_images'),
    path('create_container/<int:image_obj_id>/' , views.create_container , name='create_container'),
    path('register_container/' , views.register_container , name='register_container'),
    path('register_image/' , views.register_image , name='register_image'),
    path('list_logs/' , views.list_logs,  name='list_logs'),
    path('user_detail/<int:user_id>/', views.user_detail , name='user_detail'),
    path('delete_user/<int:user_id>/' , views.delete_user , name='delete_user'),
    path('users_info/' , views.users_info , name='users_info'),
]
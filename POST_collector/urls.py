from django.urls import path
from . import views



app_name = 'POST_collector'


urlpatterns = [
    # post views
    path('', views.hello_page, name='hello_page'),
    path('old', views.hello_page_old, name='hello_page_old'),
    


    path('hook_reciever', views.hook_reciever, name='hook_reciever'),

    path('add_app_from_podio', views.add_app_from_podio, name='add_app_from_podio'),

    path('refresh_workspaces', views.refresh_workspaces, name='refresh_workspaces'),
    path('refresh_applications', views.refresh_applications, name='refresh_applications'),
   
    path('refresh_hooks', views.refresh_hooks, name='refresh_hooks'),
    path('delete_hooks', views.delete_hooks, name='delete_hooks'),
   
    path('refresh_current_items', views.refresh_current_items, name='refresh_current_items'),
    

]


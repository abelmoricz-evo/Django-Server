from django.urls import path
from . import views



app_name = 'POST_collector'


urlpatterns = [
    # post views
    path('', views.hello_page, name='hello_page'),

    path('data', views.data_management.as_view(), name='data_management'),
    
    path('refresh_workspaces', views.refresh_workspaces, name='refresh_workspaces'),
    path('refresh_applications', views.refresh_applications, name='refresh_applications'),
   

]


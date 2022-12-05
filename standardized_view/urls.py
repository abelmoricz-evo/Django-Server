from django.urls import path,include
from . import views



app_name = 'standardized_view'


urlpatterns = [
    # post views
    path('', views.hello_page, name='hello_page'),
    path('home_simple', views.home_simple, name='home_simple'),
    path('home_simple/<str:name>', views.home_simple_name),
    path('download_all_items', views.download_all_items, name='download_all_items'),
    
    path('IR', views.IR, name='IR'),

]


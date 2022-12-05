from django.contrib import admin
from .models import Podio_Item, Podio_Workspace, Podio_Application, Podio_Hook # , Post
#from sales.models import Podio_Sales_Item


# Register your models here.


'''
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')
'''
    
@admin.register(Podio_Item)
class Podio_ItemAdmin(admin.ModelAdmin):
    list_display = [ 'Title', 'Status',]
    list_filter = ('Status', 'app__space__space_name','app__app_name')

admin.site.register(Podio_Workspace)
admin.site.register(Podio_Application)
admin.site.register(Podio_Hook)
#admin.site.register(Podio_Sales_Item)


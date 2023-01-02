from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.generic.list import ListView

from .models import  Podio_Item, Podio_Workspace, Podio_Application, Podio_Hook # , Post
import environ
import pandas as pd
from .OLD_pypodio2 import api
import datetime
import re
import json


env = environ.Env()
environ.Env.read_env()
PODIO_client = api.OAuthClient( env('PODIO_CLIENT_ID'),env('PODIO_CLIENT_SECRET'),env('PODIO_UN'),env('PODIO_PW') )
Podio_client_counter = 0


def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)


def reload_PODIO_client():
    global Podio_client_counter
    Podio_client_counter += 1
    print("reloaded podio Client for the " + str(Podio_client_counter) + " th time")
    return api.OAuthClient( env('PODIO_CLIENT_ID'),env('PODIO_CLIENT_SECRET'),env('PODIO_UN'),env('PODIO_PW') )



@csrf_exempt # defaults are for item update
def add_item(request):
    item_id = request.session['item_id']  

    print("Started adding item " + str(int(float( item_id ))))

    defaults = {}
    global PODIO_client

    if 'PODIO_client' not in globals():
        PODIO_client = reload_PODIO_client()

    item = ( PODIO_client.Item.find(int(float(item_id)), attributes={'limit':500}) )

    fields = pd.DataFrame(item['fields'])

    items_total = PODIO_client.Item.filter(int(item['app']['app_id']),attributes={'limit':1, 'offset':0})['total']
    podio_application = Podio_Application.objects.update_or_create( app_id=item['app']['app_id'], defaults={'number_of_items':items_total})     

    defaults['app'] = Podio_Application.objects.get(pk=item['app']['app_id'])
    defaults['link'] = item['link']
    defaults['created_by'] = item['created_by']['name']
    defaults['last_event_on'] = item['last_event_on']


    defaults['created_on'] = pd.to_datetime(item['created_on']) + datetime.timedelta(hours=2)
    defaults['last_event_on'] = pd.to_datetime(item['last_event_on']) + datetime.timedelta(hours=2)
    
    comments = item['comments']
    if len(comments):
        first_date = (comments[0]['created_on'])
        second_date = item['last_event_on']
        if first_date>second_date:
            defaults['last_event_on'] = pd.to_datetime(first_date) + datetime.timedelta(hours=2)

    for text_field in ['Title','Goal','Approach','Constraints and assumptions','Target result description','On-hold/cancellation reason', 'Problem Statement', 'Outcome', 'Notes','File location (Sharepoint/Server)','Podio Best Practices']:
        try:    defaults[text_field.replace(' (Sharepoint/Server)','').replace(' ','_').replace('-','_').replace('/','_')] = (fields[fields['label']==text_field]['values'].iloc[0][0]['value'])
        except: defaults[text_field.replace(' (Sharepoint/Server)','').replace(' ','_').replace('-','_').replace('/','_')] = 'NO '+ text_field

    for date_field in ['Due Date','Start Date']:
        try:    defaults[date_field.replace(' ','_')] = (fields[fields['label']==date_field]['values'].iloc[0][0]['start'])
        except: defaults[date_field.replace(' ','_')] = datetime.datetime(2000,1,1)

    for contact_field in ['Responsible','Accountable', 'Team']:
        try:    defaults[contact_field] = (fields[fields['label']==contact_field]['values'].iloc[0][0]['value']['name'])
        except: defaults[contact_field] = 'NO '+ contact_field

    for number_field in ['Estimated hours','old_podio_item_id']:
        try:    defaults[number_field.replace(' ','_')] = (fields[fields['label']==number_field]['values'].iloc[0][0]['value'])
        except: defaults[number_field.replace(' ','_')] = 'NO '+ number_field

    try:    defaults['Status'] = (fields[fields['label']=='Status']['values'].iloc[0][0]['value']['text'])
    except: defaults['Status'] = 'NO '+ 'Status'

    try:    defaults['Title_clean'] = striphtml( fields[fields['label']=='Title']['values'].iloc[0][0]['value'] )
    except: defaults['Title_clean'] = 'NO '+ 'Title_clean'

    
    Podio_Item.objects.update_or_create(item_id=item_id, defaults=defaults)


    try: 
        parent_id = ( fields[fields['label']=='PARENT']['values'].iloc[0][0]['value']['item_id'] )
        parent_objects = Podio_Item.objects.filter(item_id=parent_id)
        child_object = Podio_Item.objects.get(item_id=item_id)
        
        child_object.PARENT.add(*parent_objects)
        child_object.save()
    except Exception as e: 
        print(e)

    redirect('POST_collector:hello_page')



@csrf_exempt
def hook_reciever(request):
    request.session['item_id'] = request.POST['item_id']
    print("POST request raw: " + str(request.POST))

    if request.POST['type']=='item.update' or request.POST['type']=='item.create' or request.POST['type']=='comment.create' or request.POST['type']=='comment.delete':
        add_item(request)


    elif request.POST['type']=='item.delete':
        try:
            query = Podio_Item.objects.get(pk=request.POST['item_id'])
            items_total = PODIO_client.Item.filter(int(query.app_id),attributes={'limit':1, 'offset':0})['total']
            Podio_Application.objects.update_or_create( app_id=query.app_id, defaults={'number_of_items':items_total})   
            query.delete()
            
        except Exception as e:
            print(e)


    return HttpResponse("thanks")


def hello_page(request):
    raw_projects = (Podio_Item.objects.values('app__space__space_id','app__space__space_name', 'app__app_name', 'Title_clean', 'link', 'item_id', 'PARENT__item_id').filter(app__type_of_application='standard'))

    projects = raw_projects.filter(app__app_name='Projects')
    subprojects = raw_projects.filter(app__app_name='Subprojects')
    tasks = raw_projects.filter(app__app_name='Tasks')
    todos = raw_projects.filter(app__app_name='ToDos')

    workspaces = Podio_Workspace.objects.values('space_name', 'link','space_id')
    
    bottom_up = {"parent": "null", "name": "Organization", "children":[] }

    level = []
    for t in todos:
        print(t['Title_clean'])
        level.append( {"name": t['Title_clean'], "link": t['link'], "PARENT__item_id": t['PARENT__item_id']} )
    
    level_1 = []
    for ta in tasks:
        children = []
        for t in level:
            if t['PARENT__item_id'] == ta['item_id']:
                children.append(t)
                level.pop(level.index(t))
        level_1.append( {"name": ta['Title_clean'], "link": ta['link'], "PARENT__item_id": ta['PARENT__item_id'], "children": children} )
    if len(level):
        level_1.append({"name": "NO Task", "link": "", "PARENT__item_id": ta['PARENT__item_id'], "children": level})

    level_2 = []
    for s in subprojects:
        children = []
        for ta in level_1:
            if ta['PARENT__item_id'] == s['item_id']:
                children.append(ta)
                level_1.pop(level_1.index(ta))
        level_2.append( {"name": s['Title_clean'], "link": s['link'], "PARENT__item_id": s['PARENT__item_id'], "children": children} )
    if len(level):
        level_2.append({"name": "NO Subproject", "link": "", "PARENT__item_id": s['PARENT__item_id'], "children": level_1})

    
    level_3 = []
    for p in projects:
        children = []
        for s in level_2:
            if s['PARENT__item_id'] == p['item_id']:
                children.append(s)
                level_2.pop(level_2.index(s))
        level_3.append( {"name": p['Title_clean'], "wsp":p["app__space__space_id"], "link": p['link'], "children": children} )
    if len(level):
        level_3.append({"name": "NO Project", "wsp":p["app__space__space_id"], "link": "", "children": level_2})
    

    level_workspace = []
    for wsp in workspaces:
        children = []
        for p in level_3:
            if p['wsp'] == wsp['space_id']:
                children.append(p)
                level_3.pop(level_3.index(p))
        level_workspace.append( {"name": wsp['space_name'], "link": wsp['link'], "children": children} )
    if len(level):
        level_workspace.append( {"name": "NO Workspace", "link": "", "children": level_3} )


    bottom_up['children'] = level_workspace

    input_data = json.dumps(bottom_up)

    with open('data.json', 'w') as f:
        json.dump(input_data, f)

    return render(request, 'POST_collector/collapsible_tree.html', context={'json':input_data})





class updates(View):

    def get(self, request, item_id):
        request.session['item_id'] = item_id
        add_item(request)

        return redirect('POST_collector:data_management')

    def post (self,request):
        print("post reuqests")

        return redirect('data_management')



class data_management(ListView):
    model = Podio_Item
    ordering = ['-last_updated_on_heroku']



# Redirect to hook_viewer
@login_required
@csrf_exempt
def refresh_workspaces(request):
    spaces = Podio_Workspace.objects.all()
    spaces.delete()
    spaces = PODIO_client.Org.get_all()
    for space in spaces[0]['spaces']:        
        if (space['space_id']) in [7237066,7505294,7309056,7316095,7199698,7677577,6831851,7991757,7851231,6588474,6791227,6831858,8063266,]:
            type_of_workspace = "standard"
        else: 
            type_of_workspace = "custom"
        if not space['archived']:
            Podio_Workspace.objects.update_or_create(   space_id=space['space_id'], 
                                                        link=space['url'],
                                                        space_name=space['name'], 
                                                        archived=False,
                                                        type_of_workspace=type_of_workspace,
                                                    )
            print("added: " + str(space['name']))
        else:
            print("archived workspace not added")
    return redirect('/POST_collector')



@login_required
@csrf_exempt
def refresh_applications(request):
    spaces = Podio_Workspace.objects.all()
    all_apps = Podio_Application.objects.all()
    all_apps.delete()
    for space in (spaces):
        wsps = PODIO_client.Application.list_in_space(space.space_id)
        for i, wsp in enumerate(wsps):
            items_total = PODIO_client.Item.filter(int(wsp['app_id']),attributes={'limit':1, 'offset':0})['total']
            type_of_app = "custom"
            #                     | back office                        | Bridge Project Longevitality    | Contracting biohelp              | Contracting CALYXT               | Contracting Globachem             | Contracting KWS                  | Contracting Valent Bioscience     | Finance and Administration          | Grants and Applications           | InfraServ                         | Investor Realations               | R&D                               | Sales
            if (wsp['app_id']) in [27759965,27759966,27759967,27759968,25968882,25968933,25968939,25968945,25286192,25286193,25286194,25286195,27981976,27981977,27981978,27981979,25286144,25286150,25286151,25286152,24864256,24864257,24864259,24864281,26598743,26598744,26598745,26598746,27760977,27760978,27760979,27760980,  27731996,27731997,27731998,27731999,27228215,27228216,27228218,27228219,27751170,27751171,27751172,27751173,27751721,27751722,27751723,27751724, 27742097,27742098,27741424,27741425, ]:
                type_of_app = "standard"
            else: type_of_app = "custom"
            app_space = Podio_Workspace.objects.get(pk=wsp['space_id'])
            Podio_Application.objects.update_or_create( app_id=wsp['app_id'], 
                                                        defaults={
                                                                'link':wsp['link'],
                                                                'app_name':wsp['config']['name'],
                                                                'space':app_space,
                                                                'number_of_items':items_total,
                                                                'type_of_application':type_of_app,
                                                                })  
            print("app created: "+ str(wsp['config']['name'])) 
    return redirect('POST_collector:hello_page')



'''

# without creating hooks
@login_required
@csrf_exempt
def refresh_hooks(request):
    for app in Podio_Application.objects.filter(type_of_application='standard'):
        print(app.app_name)
        print(app.type_of_application)
        hook_app = Podio_Application.objects.get(pk=app.app_id)
        hooks = PODIO_client.Hook.find_all_for('app',app.app_id)
        abels_hooks_needed = ['comment.create', 'comment.delete']
        for hook in hooks:
            Podio_Hook.objects.update_or_create( hook_id=hook['hook_id'], 
                                        defaults= { 'url':hook['url'],
                                                    'hook_type':hook['type'],
                                                    'status':hook['status'],
                                                    'app':hook_app,
                                                })
            if hook['url']=='https://evologic-podio.herokuapp.com/POST_collector/hook_reciever':
                if hook['type'] in abels_hooks_needed:
                    abels_hooks_needed.remove(hook['type'])
        for hook_type in abels_hooks_needed:
            hook = PODIO_client.Hook.create('app', app.app_id, {'url':'https://evologic-podio.herokuapp.com/POST_collector/hook_reciever', 'type': hook_type})
    return redirect('POST_collector:hello_page')



@login_required
@csrf_exempt
def delete_hooks(request):
    for app in Podio_Application.objects.all():
        print(app.app_name)
        hooks = PODIO_client.Hook.find_all_for('app',app.app_id)
        for hook in hooks:
            if hook['url'] == 'https://evologic-podio.herokuapp.com/podio_collect/hook':
                print("Deleting hook")
                PODIO_client.Hook.delete(hook['hook_id'])
    return redirect('/')



@login_required
@csrf_exempt
def add_app_from_podio(request):
    if request.GET.get('id'):
        id = request.GET.get('id')
    else:
        id = request.session['app_id']
    global PODIO_client
    if 'PODIO_client' not in globals():
        PODIO_client = reload_PODIO_client()

    items_total = PODIO_client.Item.filter(int(id),attributes={'limit':1, 'offset':0 })['total']
    
    Podio_Application.objects.update_or_create( app_id=id, defaults={'number_of_items':items_total})   
    to_add_items = []
    i = 0
    first_time = True
    app_items = [{},]
    while (len(app_items) == 500) or (first_time):
        offset = i * 500
        app_items = PODIO_client.Item.filter(int(id), attributes={'limit':500, 'offset':offset})['items']
        first_time = False
        i = i + 1
        for item in app_items: 
            to_add_items.append(item)
            request.session['item_id'] = item['item_id']
            add_item(request)
    print("Added " + str(len(to_add_items)) + " items") 
    return redirect('POST_collector:hello_page')



@login_required
@csrf_exempt
def add_current_items_from_podio(request):
    for app in Podio_Application.objects.filter(type_of_application='standard'):
        if app.app_id:
            print("ADDING APP " + str(app.app_name) + ' wsp: '+str(app.space.space_name))
            request.session['app_id'] = app.app_id
            Podio_app_id_check = PODIO_client.Item.filter(int(float(app.app_id)),attributes={'limit':1, 'offset':0})['total']
            podio_heroku_check = Podio_Application.objects.get(pk=app.app_id).number_of_items
            try:
                assert int(float(Podio_app_id_check)) == int(float(podio_heroku_check)), f"Heroku has: {podio_heroku_check}, Podio has : {Podio_app_id_check}"
            except AssertionError as msg:
                query = Podio_Item.objects.filter(PARENT__app_id=app.app_id)
                query.delete()
                print(msg)
            add_app_from_podio(request)
    return redirect('POST_collector:hello_page')



@login_required
@csrf_exempt
def refresh_current_items(request):
    items = Podio_Item.objects.filter(app__type_of_application='standard').exclude(Status='Done').exclude(Status='Cancelled')
    print("adding "+str(items.count())+" current podio items (all statuses")
    for item in items:
        request.session['item_id'] = item.item_id
        try:
            add_item(request)
        except Exception as e:
            print('couldnt add item ' + str(e))
    return redirect('POST_collector:hello_page')





'''
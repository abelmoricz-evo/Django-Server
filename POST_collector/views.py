from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from .models import  Podio_Item, Podio_Workspace, Podio_Application, Podio_Hook # , Post
from django.contrib.auth.decorators import login_required
# Create your views here.
import environ
import pandas as pd
from .OLD_pypodio2 import api
import datetime
import re
import json

def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

env = environ.Env()
environ.Env.read_env()
PODIO_client = api.OAuthClient( env('PODIO_CLIENT_ID'),env('PODIO_CLIENT_SECRET'),env('PODIO_UN'),env('PODIO_PW') )
Podio_client_counter = 0

def reload_PODIO_client():
    global Podio_client_counter
    Podio_client_counter += 1
    print("reloaded podio Client for the " + str(Podio_client_counter) + " th time")
    return api.OAuthClient( env('PODIO_CLIENT_ID'),env('PODIO_CLIENT_SECRET'),env('PODIO_UN'),env('PODIO_PW') )


@csrf_exempt # defaults are for item update
def add_item(request):
    print("Started adding item" + str(int(float(request.session['item_id']  ))))
    defaults = {}
    item_id = request.session['item_id']    
    #try: 
    item = ( PODIO_client.Item.find(int(float(item_id)), attributes={'limit':500}) )
    #except:
        #PODIO_client = reload_PODIO_client()
        #item = ( PODIO_client.Item.find(int(float(item_id)), attributes={'limit':500}) )

    #with open('fields.json', 'w') as f:
    #    json.dump(item['fields'], f)

    fields = pd.DataFrame(item['fields'])
    #fields.to_csv('fields.csv')
    
    # updates APPLICATION item total
    items_total = PODIO_client.Item.filter(int(item['app']['app_id']),attributes={'limit':1, 'offset':0})['total']
    Podio_Application.objects.update_or_create( app_id=item['app']['app_id'], defaults={'number_of_items':items_total})     

    defaults['app'] = Podio_Application.objects.get(pk=item['app']['app_id'])
    defaults['link'] = item['link']
    defaults['created_by'] = item['created_by']['name']
    defaults['last_event_on'] = item['last_event_on']

    comments = item['comments']
    if len(comments):
        first_date = (comments[0]['created_on'])
        second_date = item['last_event_on']
        if first_date>second_date:
            print('comment date used')
            defaults['last_event_on'] = first_date
    
        #print(first_date)
        #print(second_date)
        #print ("is latest comment larger than last item edit: " +str(first_date>second_date))

    defaults['created_on'] = pd.to_datetime(item['created_on']) + datetime.timedelta(hours=2)
    defaults['last_event_on'] = pd.to_datetime(item['last_event_on']) + datetime.timedelta(hours=2)

    for text_field in ['Title','Goal','Approach','Constraints and assumptions','Target result description','On-hold/cancellation reason', 'Problem Statement', 'Outcome', 'Notes','File location (Sharepoint/Server)','Podio Best Practices']:
        try:    defaults[text_field.replace(' (Sharepoint/Server)','').replace(' ','_').replace('-','_').replace('/','_')] = (fields[fields['label']==text_field]['values'].iloc[0][0]['value'])
        except: defaults[text_field.replace(' (Sharepoint/Server)','').replace(' ','_').replace('-','_').replace('/','_')] = 'NO '+ text_field

    for date_field in ['Due Date','Start Date']:
        try:    defaults[date_field.replace(' ','_')] = (fields[fields['label']==date_field]['values'].iloc[0][0]['start'])
        except: defaults[date_field.replace(' ','_')] = datetime.datetime(2000,1,1)
    #Team Add is incomplete
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
    
    return_podio_item, created = Podio_Item.objects.update_or_create(item_id=item_id, defaults=defaults)


    try: 
        defaults['PARENT'] = ( fields[fields['label']=='PARENT']['values'].iloc[0][0]['value']['item_id'] )
        return_podio_item.PARENT.clear()
        return_podio_item.PARENT.add(defaults['PARENT'])
    except: defaults['PARENT'] = "NO parent"
#    try:    defaults['PARENT'] = striphtml( fields[fields['label']=='PARENT']['values'].iloc[0][0]['item_id'] )
#    except: defaults['PARENT'] = 'NO '+ 'PARENT'

    print("DONE adding item")


    redirect('POST_collector:hello_page')



@csrf_exempt
def hook_reciever(request):
    print("POST request raw: " + str(request.POST))

    if request.POST['type']=='hook.verify':
        PODIO_client.Hook.validate(request.POST['hook_id'], request.POST['code'])
    
    elif request.POST['type']=='item.update' or request.POST['type']=='item.create':
        request.session['item_id'] = request.POST['item_id']
        add_item(request)

        try:
            print(PODIO_client.Item.update(int(request.POST['item_id']), attributes={'fields': {'podio-best-practices-app': 'https://podio.com/evologic-technologiescom/intranet/apps/podio-best-practices'}}))
        except Exception as e:
            print(e)
            

    elif request.POST['type']=='item.delete':
        try:
            query = Podio_Item.objects.get(pk=request.POST['item_id'])
            items_total = PODIO_client.Item.filter(int(query.app_id),attributes={'limit':1, 'offset':0})['total']
            Podio_Application.objects.update_or_create( app_id=query.app_id, defaults={'number_of_items':items_total})   
            query.delete()
        except Exception as e:
            print(e)

    elif request.POST['type']=='comment.create' or request.POST['type']=='comment.delete':
        request.session['item_id'] = request.POST['item_id']
        add_item(request)
        
    else:
        print("UN CLASSIFIED WEBHOOK TYPE")
    
        
    return HttpResponse("thanks")

@login_required
@csrf_exempt
def hello_page(request):
    applications = Podio_Application.objects.all().order_by('type_of_application')
    num_active_applications = applications.filter(type_of_application='standard').count()
    return render(request, 'POST_collector/base.html', context={ 'apps':applications,
                                                                'num_apps':num_active_applications,
                                                                })







# Redirect to hook_viewer
@login_required
@csrf_exempt
def refresh_workspaces(request):
    spaces = Podio_Workspace.objects.all()
    spaces.delete()

    # GET Podio API spaces for Organization TechSolutions
    spaces = PODIO_client.Org.get_all()
    for space in spaces[0]['spaces']: #parsing non archived spaces 

        if (space['space_id']) in [7237066,7505294,7309056,7316095,7199698,7677577,6831851,7991757,7851231,6588474,6791227,6831858,8063266,]:
            type_of_workspace = "standard"
        else: type_of_workspace = "custom"

        if not space['archived']:
            Podio_Workspace.objects.update_or_create( space_id=space['space_id'], link=space['url'],
                                                        space_name=space['name'], archived=False,
                                                        type_of_workspace=type_of_workspace,
                                                    )
        else:
             Podio_Workspace.objects.update_or_create( space_id=space['space_id'], link=space['url'],
                                                        space_name=space['name'], archived=True,
                                                        type_of_workspace=type_of_workspace,
                                                    )



    return redirect('/')

@login_required
@csrf_exempt
def refresh_applications(request):
    print()
    print("hello from refresh applications")
    print()

    spaces = Podio_Workspace.objects.all()
    all_apps = Podio_Application.objects.all()
    all_apps.delete()
    
    for space in (spaces):
        # Call Podio API to refresh all Applications per workspace
        wsps = PODIO_client.Application.list_in_space(space.space_id)
        for i, wsp in enumerate(wsps):
            items_total = PODIO_client.Item.filter(int(wsp['app_id']),attributes={'limit':1, 'offset':0})['total']
            
    # this will change as standard and custom apps are determined
            type_of_app = "custom"
            #                     | back office                        | Bridge Project Longevitality    | Contracting biohelp              | Contracting CALYXT               | Contracting Globachem             | Contracting KWS                  | Contracting Valent Bioscience     | Finance and Administration          | Grants and Applications           | InfraServ                         | Investor Realations               | R&D                               | Sales
            if (wsp['app_id']) in [27759965,27759966,27759967,27759968,25968882,25968933,25968939,25968945,25286192,25286193,25286194,25286195,27981976,27981977,27981978,27981979,25286144,25286150,25286151,25286152,24864256,24864257,24864259,24864281,26598743,26598744,26598745,26598746,27760977,27760978,27760979,27760980,  27731996,27731997,27731998,27731999,27228215,27228216,27228218,27228219,27751170,27751171,27751172,27751173,27751721,27751722,27751723,27751724, 27742097,27742098,27741424,27741425, ]:
                type_of_app = "standard"
            else: type_of_app = "custom"

            app_space = Podio_Workspace.objects.get(pk=wsp['space_id'])
            Podio_Application.objects.update_or_create( app_id=wsp['app_id'], defaults={
                                                                                        'link':wsp['link'],
                                                                                        'app_name':wsp['config']['name'],
                                                                                        'space':app_space,
                                                                                        'number_of_items':items_total,
                                                                                        'type_of_application':type_of_app,
                                                                                        })    
    return redirect('POST_collector:hello_page')

# without creating hooks
@login_required
@csrf_exempt
def refresh_hooks(request):
    print()
    print("hello from refresh hook")
    print()
    
    applications = Podio_Application.objects.filter(type_of_application='standard')
    
    for app in applications:

        print(app.app_name)
        print(app.type_of_application)
        hook_app = Podio_Application.objects.get(pk=app.app_id)
    
        # API call
        hooks = PODIO_client.Hook.find_all_for('app',app.app_id)
        #abels_hooks_needed = ['item.create', 'item.update', 'item.delete']
        abels_hooks_needed = ['comment.create', 'comment.delete']
        for hook in hooks:
    
            existing_hook, created = Podio_Hook.objects.update_or_create( hook_id=hook['hook_id'], 
                                        defaults= {'url':hook['url'],
                                        'hook_type':hook['type'],
                                        'status':hook['status'],
                                        'app':hook_app,
                                        })
            # if the hook isnt already created then                               
            if hook['url']=='https://evologic-podio.herokuapp.com/POST_collector/hook_reciever':
                if hook['type'] in abels_hooks_needed:
                    abels_hooks_needed.remove(hook['type'])
        # this script actually creates the hooks can be commented if only datamodel for django is needed
        for hook_type in abels_hooks_needed:
            hook = PODIO_client.Hook.create('app', app.app_id, {'url':'https://evologic-podio.herokuapp.com/POST_collector/hook_reciever',
                                                                'type': hook_type})
            print()
    
    return redirect('POST_collector:hello_page')




@login_required
@csrf_exempt
def delete_hooks(request):
    for app in Podio_Application.objects.all():
        print(app.app_name)
        # API call
        hooks = PODIO_client.Hook.find_all_for('app',app.app_id)
        for hook in hooks:
            if hook['url'] == 'https://evologic-podio.herokuapp.com/podio_collect/hook':
                print("Deleting hook")
                PODIO_client.Hook.delete(hook['hook_id'])
    return redirect('/')





@login_required
@csrf_exempt
def add_app_from_podio(request):
    # id = request.GET.get('id')
    id = request.session['app_id']

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

    apps = Podio_Application.objects.filter(type_of_application='standard')

    for app in apps:
        
        if app.app_id:
            print("ADDING APP " + str(app.app_name) + ' wsp: '+str(app.space.space_name))
            request.session['app_id'] = app.app_id
            Podio_app_id_check = PODIO_client.Item.filter(int(float(app.app_id)),attributes={'limit':1, 'offset':0})['total']
            podio_heroku_check = Podio_Application.objects.get(pk=app.app_id).number_of_items

            print("heroku: "+str(podio_heroku_check))
            print("podio: "+str(Podio_app_id_check))



            try:
                assert int(float(Podio_app_id_check)) == int(float(podio_heroku_check)), f"Heroku has: {podio_heroku_check}, Podio has : {Podio_app_id_check}"

            # the errror_message provided by the user gets printed
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
        #add_item(request)
        try:
            print()
            print(item.item_id)
            add_item(request)
        except Exception as e:
            print('couldnt add item')
            print(e)

    return redirect('POST_collector:hello_page')
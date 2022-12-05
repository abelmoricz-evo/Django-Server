from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q

import plotly.express as px
import pandas as pd
import datetime
import re
#from excel_response import ExcelResponse

from POST_collector.models import Podio_Application, Podio_Item, Podio_Workspace


now = timezone.now()
print("NOW: " + str(now))

def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)


def avg(dates):
  any_reference_date = now
  return (sum([any_reference_date-date for date in dates], datetime.timedelta()) / len(dates))


@login_required
@csrf_exempt
def hello_page(request):
    context = {}

    now = timezone.now()
    print("NOW: " + str(now))

    workspaces = Podio_Workspace.objects.all().order_by('type_of_workspace')
    applications = Podio_Application.objects.all().order_by('type_of_application')
    items = Podio_Item.objects.filter(app__type_of_application='standard').exclude(Status='Done').exclude(Status='Cancelled')

    num_active_workspaces = workspaces.filter(type_of_workspace='standard').count()
    num_active_applications = applications.filter(type_of_application='standard').count()
    num_active_items = items.count()


    return render(request, 'standardized_view/base.html', context={'wsps':workspaces, 'apps':applications,
                                                                'items':items, #'hooks':hooks,
                                                                'num_wsps': num_active_workspaces,
                                                                'num_apps':num_active_applications,
                                                                #'num_hooks':num_active_hooks,
                                                                'num_items':num_active_items,
                                                                })




    return render(request, '', context=context)


@login_required
@csrf_exempt
def home_simple(request):
    responsible = list(Podio_Item.objects.all().distinct().values_list('Responsible', flat=True))
    accountables = list(Podio_Item.objects.all().distinct().values_list('Accountable', flat=True))
    
    first_people = ['Alexey Kopchinskiy','Nadine Ullmann','Yuriy Sobanov','Christoph Moser', 'Anna Bartalos','Edgard Dietrich', \
            'Paul Ruschitzka','Alejandro del Barrio','Mohsen Hosseini','Simon Dlabaja', 'Mara Kraft','Angela Pasquel de Debloc','Jan Slonski','Markus Teindl', 'Michael Loev', 'Leonhard Zelger', 'Tiziano Benocci','Viktoriya Stoyanova', 'Tara Mayer',\
            'Bahar Cekici','Rebekka Leitner','Conrad Reichelt','Stefanie Bammer','Jose Ramon Jeronimo Linan','Anna Oberprieler', \
            'Wieland Reichelt','Markus Brillmann','Salmena Keshk','Judith Mirasol','Saleh Akrami','Abel Moricz', 'Samantha Morellini','Ana Mileusnic','Philipp Rittershaus', 'Gerald Schaufler','Dr. Stefan Neumann'  ]   
    
    people = first_people + responsible + accountables
    people = list(dict.fromkeys(people)) #removes duplicates from list
    #print(people)
    people_totals = {}
    standard_items = Podio_Item.objects.filter(app__type_of_application="standard")
    for name in people:
        
        person_items =  standard_items.filter(Q(Responsible=name) | Q(Accountable=name)).exclude(Status='Done').exclude(Status='Cancelled')#.exclude(Status='On Hold')
        
        
        item_count = person_items.distinct().count()
        on_hold_items = person_items.filter(Status='On Hold').distinct().count()

        if item_count:
            team = "NO TEAM"
            if people.index(name) < 6:
                team = "Alejandro's Team"
            elif people.index(name) < 19:
                team = "Markus' Team"
            elif people.index(name) < 25:
                team = "Paul's Team"
            elif people.index(name) < 37:
                team = "Wieland's Team"

            avg_since_last_event = (avg(list(person_items.values_list('last_event_on', flat=True))))
            items_older_than_2_weeks = person_items.filter(last_event_on__lte=datetime.datetime.now() - datetime.timedelta(days=14)).exclude(Status='Done').exclude(Status='Cancelled').exclude(Status='On Hold').distinct().count()
            #on_hold_items = person_items.filter(Status='On Hold').distinct().count()
            if item_count-on_hold_items != 0:
                people_totals['https://evologic-podio.herokuapp.com/standardized_view/home_simple/'+name.replace(' ','+')] = [team, name, item_count, items_older_than_2_weeks, on_hold_items, round(items_older_than_2_weeks/(item_count-on_hold_items), 2) , str(avg_since_last_event).split(',')[0]]
            else:
                people_totals['https://evologic-podio.herokuapp.com/standardized_view/home_simple/'+name.replace(' ','+')] = [team, name, item_count, items_older_than_2_weeks, on_hold_items, round(items_older_than_2_weeks/(item_count+1), 2) , str(avg_since_last_event).split(',')[0]]


    #people_totals.sort_values()




    






    wsps = standard_items.values_list('app__space__space_name', flat=True).distinct()
    df_columns = ['wsp']
    statuses = standard_items.values_list('Status', flat=True).distinct()
    for status in statuses:
        df_columns.append(status)
    


    wdotg_df = pd.DataFrame(columns = df_columns)
    for wsp in wsps:
        df_row = {'wsp':wsp}
        for status in statuses:
            df_row[status] = standard_items.filter(Status=status).filter(app__space__space_name=wsp).count()
        wdotg_df = pd.concat( [wdotg_df, pd.DataFrame(df_row, index=[0])] )
    wdotg_df['ACTIVE ITEMS TOTAL'] = wdotg_df['NO Status'] + wdotg_df['Planned'] + wdotg_df['New'] + wdotg_df['Approved'] + wdotg_df['In Progress'] + wdotg_df['Revision'] + wdotg_df['On Hold']
    wdotg_df = wdotg_df[[ 'wsp', 'NO Status', 'Planned', 'New', 'Approved', 'In Progress', 'Revision', 'On Hold', 'ACTIVE ITEMS TOTAL', 'Done', 'Cancelled' ]]

    wdotg_df.sort_values(inplace=True, by=['ACTIVE ITEMS TOTAL'], ascending=False)

    wdotg_df.loc["Total"] = wdotg_df.sum()
    wdotg_df.iloc[-1,0] = "TOTAL"
    print()
    print(wdotg_df.iloc[-1,0])
    print()
    

    








    data_canada = px.data.gapminder().query("country == 'Canada'")
    fig = px.bar(data_canada, x='year', y='pop')
    graph = fig.to_html(full_html=False)



    return render(  request,'standardized_view/simple_summary.html', {
                    'people':people, 'people_totals':people_totals, 'graph':graph,
                    'df':wdotg_df.to_html(index=False),
                    })


@login_required
@csrf_exempt
def home_simple_name(request,name):

    # EXCLUDING workspaces
    all_items = Podio_Item.objects.filter(app__type_of_application='standard')
    
    spaces = Podio_Workspace.objects.filter(type_of_workspace='standard')
    
    applications = Podio_Application.objects.filter(type_of_application='standard')



    all_items = all_items.exclude(Status='Done').exclude(Status='Cancelled')
    
    graph_df = []
    space_totals = {}
    if name != "TOTAL":
        name = name.replace('+',' ')
        for s in applications:
            
            space_totals[s.app_id] = all_items.filter(app__app_id=s.app_id) \
                                            .filter(Q(Responsible=name)|Q(Accountable=name)) \
                                            .order_by('Status')
        for s in spaces:
            df_row = {}
            df_row['value'] = all_items.filter(Q(Responsible=name)|Q(Accountable=name)) \
                                        .filter(app__space__space_id=s.space_id).count()
            df_row['name'] =  s.space_name
            graph_df.append(df_row)

        #saves a list of all items locally
        
              
        all_items = all_items.filter(Q(Responsible=name) | Q(Accountable=name)).distinct().count()
    
    else:   # shows all responsible and accountable    
        for s in applications:
            space_totals[s.app_id] = all_items.filter(app__app_id=s.app_id).order_by('Status')  
        
        for s in spaces:
            df_row = {}
            df_row['value'] = all_items.filter(app__space__space_id=s.space_id).count()
            #df_row['value'] = all_items.filter(Title='ToDo').count()
            df_row['name'] =  s.space_name
            graph_df.append(df_row)

        #print('printing excel')
        #df = pd.DataFrame(list(all_items.all().values()))
        #df.to_excel('ALL_STANDARD_ITEMS.xlsx')

        all_items = all_items.distinct().count()  

        
    #df = px.data.gapminder().query("year == 2007").query("continent == 'Europe'")
    df = pd.DataFrame(graph_df)
    df.to_excel('debug_graph.xlsx')    
    
    df.sort_values(by='value', inplace=True)
    fig = px.bar(df, x='value', y='name', title='Active Items/ Workspace')

    graph = fig.to_html(full_html=False)#, default_height=500, default_width=700)

    return render(  request,'standardized_view/simple_summary_person.html', 
                            {   'applications':applications, 'spaces':spaces, 
                                'space_totals':space_totals, 'name':name,
                                'total_podio_items':all_items,
                                'graph':graph,
                    })




@login_required
@csrf_exempt
def download_all_items(request):
    #df = pd.DataFrame(list(Podio_Item.objects.filter(app__type_of_application='standard').values('item_id', 'link', 'last_event_on', 'created_on', 'created_by',
    all_items = Podio_Item.objects.filter(app__type_of_application='standard').values('item_id', 'link', 'last_event_on', 'created_on', 'created_by',
       'last_updated_on_heroku', 'app_id', 'Title', 'Title_clean', 'Due_Date',
       'Estimated_hours', 'Goal', 'Status', 'Approach',
       'Constraints_and_assumptions', 'Target_result_description',
       'On_hold_cancellation_reason', 'Problem_Statement', 'Responsible',
       'Accountable', 'Start_Date', 'Outcome', 'Notes', 'Team',
       'Podio_Best_Practices', 'File_location', 'old_podio_item_id','app__app_name', 'app__space__space_name')
    #print(Podio_Item.objects.select_related('app__space'))
    

    return ExcelResponse(all_items)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=all_podio_items.xlsx'
    xlsx_data = pd.read_excel('all_podio_items.xlsx')
    response.write(xlsx_data)
    return response
    
    return redirect('/standardized_view/home_simple')

@login_required
def IR(request):
    context = {}

    IR_items = Podio_Item.objects.filter(app__space__space_id=6588474)

    subprojects = IR_items.filter(app__app_id=27751172)
    tasks = IR_items.filter(app__app_id=27751171)
    todos = IR_items.filter(app__app_id=27751170)


    df = pd.DataFrame()
    index_counter = 0
    for i in subprojects:
        df.loc[index_counter, 'level0_id'] = i.item_id
        df.loc[index_counter, 'level0_title'] = i.Title_clean
        df.loc[index_counter, 'level0_link'] = i.link
        df.loc[index_counter, 'level0_status'] = str(i.Status)
        index_counter += 1
    
    print("first df done")

    ddf = pd.DataFrame()
    index_counter = 0
    for i in tasks:
        ddf.loc[index_counter, 'level1_id'] = i.item_id
        ddf.loc[index_counter, 'level1_title'] = i.Title_clean
        ddf.loc[index_counter, 'level1_link'] = i.link
        ddf.loc[index_counter, 'level1_status'] = str(i.Status)
        
        try:
            ddf.loc[index_counter, 'level0_id'] = i.PARENT.all()[0].item_id
        except:
            ddf.loc[index_counter, 'level1_id'] = 0000
        index_counter += 1


    df = pd.merge(df,ddf, how='outer')
    print("second merge done")

    
    dddf = pd.DataFrame()
    index_counter = 0
    for i in todos:
        dddf.loc[index_counter, 'level2_id'] = i.item_id
        dddf.loc[index_counter, 'level2_title'] = i.Title_clean
        dddf.loc[index_counter, 'level2_link'] = i.link

        dddf.loc[index_counter, 'level2_status'] = str(i.Status)
        try:
            dddf.loc[index_counter, 'level1_id'] = i.PARENT.all()[0].item_id
        except:
            dddf.loc[index_counter, 'level1_id'] = 0000
        index_counter += 1
    df = pd.merge(df,dddf, how='outer')

    print('last merge done saving file')

    context['h'] = df.to_html(escape=False)
    df.to_excel('HIEARCHY.xlsx')
    
    print("file saved")

    return render(  request,'standardized_view/IR.html', context)

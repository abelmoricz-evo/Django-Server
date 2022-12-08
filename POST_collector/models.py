
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Podio_Workspace(models.Model):
    TYPE_CHOICES = (('standard', 'Contains Standard'), ('custom', 'Custom WSP'),)

    space_id = models.CharField(max_length=200, primary_key=True)
    link = models.CharField(max_length=400, blank=True)
    space_name = models.CharField(max_length=400, blank=True)
    archived = models.BooleanField()
    last_updated_on_heroku = models.DateTimeField(auto_now=True)

    type_of_workspace = models.CharField(max_length=10, choices=TYPE_CHOICES, default='custom')

    def __str__(self):
        return "ARCHIVED: " + str(self.archived) + " | " + self.space_name + " | " + self.space_id + " | " + self.link  + " | " + str(self.last_updated_on_heroku)


class Podio_Application(models.Model):  
    TYPE_CHOICES = (('standard', 'Standard'), ('custom', 'Custom'),)
    
    space = models.ForeignKey(Podio_Workspace, on_delete=models.CASCADE) # expresses one-to-many relationship
    link = models.CharField(max_length=400, blank=True)
    app_name = models.CharField(max_length=400, blank=True)
    app_id = models.CharField(max_length=400, blank=True, primary_key=True)
    number_of_items = models.CharField(max_length=400, blank=True)
    type_of_application = models.CharField(max_length=400, choices=TYPE_CHOICES, default='custom')
    last_updated_on_heroku = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type_of_application +" | " + self.app_name + " | " + self.app_id + " | " + self.type_of_application + " | " + self.link + " | " + self.space_id


class Podio_Hook(models.Model):
    hook_id = models.CharField(max_length=400, blank=True, primary_key=True)
    url = models.CharField(max_length=400, blank=True)
    hook_type = models.CharField(max_length=400, blank=True)
    status = models.CharField(max_length=400, blank=True)
    
    app = models.ForeignKey(Podio_Application, on_delete=models.CASCADE) # expresses one-to-many relationship
    
    def __str__(self):
        return self.app.app_name + " | " + self.hook_type + " | " + self.url


class Podio_Item(models.Model):
    STATUS_CHOICES = (
        ('-', 'NO STATUS'),
        ('planned', 'Planned'),
        ('new', 'New'),
        ('approved', 'Approved'),
        ('in progress', 'In Progress'),
        ('revision', 'Revision'),
        ('done', 'Done'),
        ('on hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    )

    # Level 1 data
    item_id = models.CharField(max_length=200, primary_key=True)
    link = models.CharField(max_length=400, blank=True)
    last_event_on = models.DateTimeField(blank=True,null=True)
    created_on = models.DateTimeField(blank=True,null=True)
    created_by = models.CharField(max_length=400, blank=True)


    # Abels fields for django organization
    last_updated_on_heroku = models.DateTimeField(auto_now=True)
    app = models.ForeignKey(Podio_Application, on_delete=models.CASCADE) # expresses one-to-many relationship

    
    #Standard fields
    Title = models.CharField(max_length=1600, blank=True) 
    Title_clean = models.CharField(max_length=1600, blank=True, null=True) 
    Due_Date = models.DateTimeField(null=True,blank=True)
    Estimated_hours = models.CharField(max_length=12800, blank=True) 
    Goal = models.CharField(max_length=102400, blank=True) 
    Status = models.CharField(max_length=11,
                              choices=STATUS_CHOICES,
                              default='-')
    Approach = models.CharField(max_length=102400, blank=True) 
    Constraints_and_assumptions = models.CharField(max_length=102400, blank=True) 
    Target_result_description = models.CharField(max_length=102400, blank=True) 
    On_hold_cancellation_reason = models.CharField(max_length=102400, blank=True) 
    Problem_Statement = models.CharField(max_length=102400, blank=True) 
    Responsible = models.CharField(max_length=1600, blank=True) 
    Accountable = models.CharField(max_length=1600, blank=True) 
    Start_Date = models.DateTimeField(blank=True,null=True)
    Outcome = models.CharField(max_length=102400, blank=True) 
    Notes = models.CharField(max_length=102400, blank=True) 
    Team = models.CharField(max_length=6400, blank=True) 
    File_location = models.CharField(max_length=6400, blank=True) 
    Podio_Best_Practices = models.CharField(max_length=6400, blank=True) 
    File_location = models.CharField(max_length=12800, blank=True) 
    old_podio_item_id = models.CharField(max_length=1600, blank=True) 
    
    PARENT = models.ManyToManyField('self', related_name='Parent', symmetrical=False)

    #for sales stuff
    '''
    organization_sales = models.CharField(max_length=1600, blank=True) 
    organization_id_sales = models.CharField(max_length=1600, blank=True) 
    organization_ranking_sales = models.CharField(max_length=1600, blank=True) 
    sales_call_date = models.DateTimeField(blank=True,null=True)
    '''

    def __str__(self):
        return self.item_id + " -- " + self.Title + " -- " + self.Status + " -- " + self.link





'''
class SPACE(models.Model):
    space_id = models.CharField(max_length=200, primary_key=True)
    link = models.CharField(max_length=400, blank=True)
    space_name = models.CharField(max_length=400, blank=True)

    def __str__(self):
        return self.space_name + " | " + self.space_id + " | " + self.link

class APP(models.Model):  
    space_id = models.CharField(max_length=200)
    link = models.CharField(max_length=400, blank=True)
    app_name = models.CharField(max_length=400, blank=True)
    app_id = models.CharField(max_length=400, blank=True, primary_key=True)
    number_of_items = models.CharField(max_length=400, blank=True)
    
    @property
    def standard_app(self):
        if self.space_id not in ['7854110', '7732451', '7532647', '7382926', '6831854','7716662', '6588475', '7000315', '7532646', '7405673', '7806885', '7237063']:
            if self.app_id not in ['24994978','24994980','24994983','25767602','25767603','27435018','27478608','27448961','27478609','27688195','27391876','24003832','24004696','25888861','25888862',\
                '23742883','23742882','26989898','27220204','24257784','24315732','24315764','24315864','26036957','22818026','22845621','22863123','27004921','27004922','27575419'\
                    '23664452','23649891','23664455','23664696','23669580','23669600']:
                return "standard"
            else:
                return ""
        else:
            return ""

    def __str__(self):
        return self.app_name + " | " + self.app_id + " | " + self.link + " | " + self.space_id

class HOOK(models.Model):
    hook_id = models.CharField(max_length=400, blank=True, primary_key=True)
    url = models.CharField(max_length=400, blank=True)
    hook_type = models.CharField(max_length=400, blank=True)
    status = models.CharField(max_length=400, blank=True)
    app_id = models.CharField(max_length=400, blank=True)
    
    def __str__(self):
        return self.app_name + " | " + self.app_id + " | " + self.link + " | " + self.space_id
'''
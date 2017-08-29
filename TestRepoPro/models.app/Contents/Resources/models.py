from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.utils import timezone


class TestRepoUserManager(BaseUserManager):
    """
    Custom User Manager Class
    """
    def create_user(self, first_name, last_name, email, password, role):
        if not email:
            raise ValueError("Email is required to create a user")
        
        now = timezone.now()        
        cuser = self.model(email=email, first_name=first_name,
                                                        last_name=last_name, is_staff=False,
                            is_active=True, is_superuser=False,
                                                        date_joined=now, last_login=now,)
        cuser.set_password(password)
        cuser.save(self._db)
        return cuser
    
    def create_superuser(self,  first_name , last_name , email, password, role ):
        u = self.create_user(first_name, last_name, email, password, role)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u
        

class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User Class
    """
    first_name = models.CharField( max_length=25 )
    last_name = models.CharField( max_length=25 )    
    email = models.EmailField( verbose_name='email address', max_length=25, unique=True, db_index = True )    
    date_joined = models.DateTimeField( 'date joined', default=timezone.now )
    is_staff = models.BooleanField( 'staff status',  default=False,  help_text='Determines if user can access the admin site' )
    is_active = models.BooleanField( default = True )
    is_admin = models.BooleanField( default = True )
    role = models.CharField( max_length=25 )
    mgr_id = models.CharField( max_length= 10)
    
    objects = TestRepoUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name' , 'last_name', 'role']
    
    def __unicode__(self):
        return self.email
    
    class Meta:
        db_table = "users" 
    
    
class Projects( models.Model ):
    #pid = models.AutoField( primary_key = True )
    pid = models.CharField( primary_key = True, max_length=10 )
    project_name = models.CharField( max_length= 30, unique = True )
    staging_tp = models.CharField( max_length=25 )
    stag_tpid = models.CharField( max_length=25 )
    production_tp = models.CharField( max_length=25 )
    prod_tpid = models.CharField( max_length=25 )    
    userid = models.ForeignKey(User, db_column='userid' )   
    
    def __unicode__(self):
        return self.project_name
    
    class Meta:
        db_table = "projects"
        


class ProjectStats( models.Model ):
    pid = models.ForeignKey( Projects, db_column='pid')
    tp_mode = models.CharField( max_length = 50 )
    build_id = models.CharField( max_length = 75, blank = True, null = True )
    tc_count = models.IntegerField( blank = True, null = True )
    tc_pass_count = models.IntegerField( blank = True, null = True )
    tc_fail_count = models.IntegerField( blank = True, null = True )
    tc_nr_count = models.IntegerField( blank = True, null = True )
    tc_block_count = models.IntegerField( blank = True, null = True )
        
    def __unicode__(self):
        return self.pid
    
    class Meta:
        db_table = "project_stats"
        
        
class UseCases( models.Model ):
    pid = models.ForeignKey( Projects, db_column = "pid" )
    uc_id = models.CharField( primary_key = True, max_length=15 )
    usecase_name = models.CharField( max_length= 50 )
    
    def __unicode__(self):
        return self.usecase_name
    
    class Meta:
        db_table = "usecases"
        
        
class UseCaseStats( models.Model ):
    uc_id = models.ForeignKey( UseCases, db_column = "uc_id" )
    tp_mode = models.CharField( max_length = 50 ) 
    tc_count = models.IntegerField( blank = True, null = True )
    tc_passed =  models.IntegerField( blank = True, null = True )
    tc_failed = models.IntegerField( blank = True, null = True )
    tc_not_run = models.IntegerField( blank = True, null = True )
    tc_blocked = models.IntegerField( blank = True, null = True )
    
    def __unicode__(self):
        return self.uc_id
    
    class Meta:
        db_table = "usecase_stats"
        


class TestCases( models.Model ):
    uc_id = models.ForeignKey( UseCases, db_column="uc_id" )
    tc_id = models.CharField( primary_key = True, max_length = 15 )
    testcase_name = models.CharField( max_length = 75 )
    
    def __unicode__(self):
        return self.testcase_name
    
    class Meta:
        db_table = "testcases"
        


class TestCaseStats( models.Model ):
    tc_id = models.ForeignKey( TestCases, db_column="tc_id" )
    tp_mode = models.CharField( max_length = 50 )
    status = models.CharField( max_length = 1 )
    exec_time = models.CharField( max_length = 30 )
    message = models.CharField( max_length = 255, blank = True, null = True )
    bug_id = models.CharField( max_length = 10, blank = True, null = True )
    
    def __unicode__( self ):
        return self.tc_id
    
    class Meta:
        db_table = "testcase_stats"
        
        
        
class BugSummary( models.Model ):
    bug_id = models.CharField( primary_key = True, max_length = 15 )
    summary = models.CharField( max_length = 255 )
    issue_type = models.CharField( max_length = 15 )
    status = models.CharField( max_length = 15 )
    components = models.CharField( max_length = 100, blank = True, null = True )
    urgency = models.CharField( max_length = 20, blank = True, null = True )
    priority = models.CharField( max_length = 20, blank = True, null = True )
    assignee = models.CharField( max_length = 75, blank = True, null = True )
    qe = models.CharField( max_length = 75, blank = True, null = True )
    fix_versions = models.CharField( max_length = 100, blank = True, null = True )
    environment = models.CharField( max_length = 25, blank = True, null = True )
    sys_env = models.CharField( max_length = 25, blank = True, null = True )
    reporter = models.CharField( max_length = 75, blank = True, null = True )
    
    def __unicode__(self):
        return self.bug_id
    
    class Meta:
        db_table = "bug_summary"
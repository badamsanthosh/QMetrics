from django.shortcuts import render_to_response, redirect, HttpResponse
from django.template import RequestContext
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView
from django.db import connection
# Debug Utils
import pdb
import traceback
import logging
#log = logging.getLogger(__name__)
logging.getLogger('django.request').setLevel(logging.ERROR)
#Importing ModelForms
from TestRepoPro.forms import AuthenticationForm, RegistrationForm, ProjectDetails
# Importing Testlink modules 
from TestRepoPro.lib.testlink.testlink_api import testlinkAPI
from TestRepoPro.lib.testlink.testlink_parser import TestlinkParser
from TestRepoPro.models import  *
tl = testlinkAPI()
tp = TestlinkParser()
# Importin JIRA Modules
#from TestRepoPro.lib.jira.jira_parser import JiraParser
#jira = JiraParser()

@login_required
def index(request):    
    return render_to_response('dashboard.html', { 'user' : request.user } )


@login_required
def staging( request ):    
    tot_project_stats = _getTotalProjectStatsByMode( "staging" )    
    return render_to_response('staging.html', { 'user' : request.user, 'tot_project_stats' : tot_project_stats } )
    
        
@login_required
def production( request ):
    tot_project_stats = _getTotalProjectStatsByMode( "production" )
    return render_to_response('production.html', { 'user' : request.user, 'tot_project_stats' : tot_project_stats } )


@login_required
def stagingUseCaseStats( request ):
    project_name = request.GET.get( 'project_name' )    
    pid = request.GET.get( 'pid' )
    tot_uc_stats, build_id  = _getTotalUseCaseStatsByMode( pid, "staging" )    
    return render_to_response('usecase_stag_stats.html', {'user' : request.user, 'project_name' : project_name, 'pid' : pid,'tot_uc_stats' : tot_uc_stats, 'build_id' : build_id  } )



@login_required
def productionUseCaseStats( request ):
    project_name = request.GET.get( 'project_name' )
    pid = request.GET.get( 'pid' )
    tot_uc_stats, build_id  = _getTotalUseCaseStatsByMode( pid, "production" )    
    return render_to_response('usecase_prod_stats.html', {'user' : request.user, 'project_name': project_name, 'pid' : pid ,'tot_uc_stats' : tot_uc_stats, 'build_id' : build_id  } )



@login_required
def stagingTestCaseStats( request ):
    project_name = request.GET.get( 'project_name' )
    usecase_name = request.GET.get( 'usecase_name' )
    pid = request.GET.get( 'pid' )
    #pdb.set_trace()
    uc_id = str( request.GET.get( 'uc_id' ) )
    tc_mode = str( request.GET.get( 'tc_mode' ) )
    tot_tc_stats = _getTotalTestCaseStatsByMode(uc_id, 'staging', tc_mode)
    print "ABC:", tot_tc_stats
    return render_to_response('testcase_stag_stats.html', {'user' : request.user, 'project_name': project_name, 'pid' : pid ,'tot_tc_stats' : tot_tc_stats, 'usecase_name'  : usecase_name } )



@login_required
def productionTestCaseStats( request ):
    project_name = request.GET.get( 'project_name' )
    usecase_name = request.GET.get( 'usecase_name' )
    pid = request.GET.get( 'pid' )
    uc_id = request.GET.get( 'uc_id' )
    tc_mode = request.GET.get( 'tc_mode' )
    tot_tc_stats = _getTotalTestCaseStatsByMode(uc_id, 'production', tc_mode)
    return render_to_response('testcase_prod_stats.html', {'user' : request.user, 'project_name': project_name, 'pid' : pid ,'tot_tc_stats' : tot_tc_stats, 'usecase_name'  : usecase_name } )



@login_required
def testcaseStats( request ):    
    project_name = request.GET.get( 'project_name' )
    usecase_name = request.GET.get( 'usecase_name' )
    usecase_id = request.GET.get( 'uc_id' )
    test_plan =  Projects.objects.get( project_name= project_name ).staging_tp
    testplan_id = tl.getTestPlanIDByProjectName( project_name ,  test_plan )
    if 'tc_data' in request.session:
        testcases_data = request.session[ 'tc_data' ]
    else:
        testcases_data = tp.getTestCaseData( testplan_id )
    tc_data_by_ucid = []
    for each_tc_data in  testcases_data:
        if each_tc_data['tc_usecaseid'] == usecase_id:
            tc_data_by_ucid.append( each_tc_data )
    
    return render_to_response('testcase_stats.html', { 'user' : request.user, 'usecase_name' : usecase_name, 'tc_data': tc_data_by_ucid,  'project_name' : project_name } )
    


@login_required
def projects(request):
    p_obj = Projects.objects.filter( userid = str(request.user.id) ).order_by( 'project_name' ) 
    projects_list = [ { 'project_name':each.project_name, 'staging_tp': each.staging_tp, 'production_tp': each.production_tp } for each in p_obj ]
    
    return render_to_response('projects.html', { 'user' : request.user, 'projects_list' : projects_list} )


def addUser( request ):
    context = RequestContext( request )
    if request.method == 'POST':
        return render_to_response( 'add_user.html' , context )
    else:
        return render_to_response('add_user.html', {'user' : request.user } )
    

"""
def editProject( UpdateView ):
    model = Projects
    form_class = ProjectDetails
    return render_to_response(' edit_project.html' )
"""

"""
@login_required
def bugReports( request ):    
    latest_version = jira.getCurrentRelease()
    issue_stats_by_project_version = jira.getIssueCountsByProjectByVersion( latest_version )
        
    components = [ 'Ad Status', 'AdLens Misc', 'api', 'Bulksheets', 'Click Data', 'Reports Fetcher', 'RulesBasedBidding', 'Sync' ]
    
    components_res = []
    for each_component in components:
        #issues_res = jira.getIssuesByComponentPerVersion( fix_version = latest_version, component = each_component )
        issues_res = _getIssuesByComponentPerVersion( latest_version, each_component )
        components_res.append( issues_res )
        #print components_res
    return render_to_response( 'bug_reports.html', { 'user' : request.user, 'issue_stats':  issue_stats_by_project_version, 'version':  latest_version, 'components_res' : components_res } )



def bugsList( request ):    
    latest_version = jira.getCurrentRelease()
    component = request.GET.get( 'component' )
    
    filter = {}
    if 'urgency' in request.GET:
        urgency = request.GET.get( 'urgency' )
        filter[ 'name' ] = 'Urgency'
        filter[ 'value' ] = urgency
        issues_list = jira.getIssues( fix_version = latest_version, component = component, urgency = urgency )
        
    elif 'status'  in request.GET:
        status = request.GET.get( 'status' )
        filter[ 'name' ] = 'Status'
        filter[ 'value' ] = status
        issues_list = jira.getIssues( fix_version = latest_version, component = component, status = status )
        
    data = jira.getIssuesListData( issues_list )
    if data:
        issues_data = data['data'  ]
    else:
        issues_data = []
    
    return render_to_response('bugs_list.html', { 'issues_data'  : issues_data, 'component' : component, 'filter' : filter } )
"""
    

@login_required
def reports(request):
    return render_to_response('reports.html', {'user' : request.user } )



@login_required
def home(request):
    #tlink_data = tl.getInfo()
    return render_to_response('home.html', {'user' : request.user, 'tlink_data' : "Hi" } )



@login_required
def forms(request):
    return render_to_response('forms.html', {'user' : request.user } )



@login_required
def timeline(request):
    return render_to_response('timeline.html', {'user' : request.user } )



def login( request ):
    """
    Login in View
    """    
    context = RequestContext(request)    
    if request.method == 'POST':
        form = AuthenticationForm( data = request.POST )        
        
        if form.is_valid():            
            user = authenticate( email = request.POST['email'], password = request.POST['password'] )            
            if user is not None:
                if user.is_active:
                    django_login(request, user)
                    #return render_to_response( 'dashboard.html' , {'user': user }, context_instance = RequestContext( request ) )
                    return redirect('/TestRepoPro/dashboard')
                else:                    
                    return HttpResponse("Your QADashBoardPro account is disabled.")
            else:
                return render_to_response( 'login.html' , {'invalid': True }, context_instance = RequestContext( request ) )                
                #return HttpResponse("Invalid login details supplied.")
        else:
            return render_to_response( 'login.html' , {'invalid': True }, context_instance = RequestContext( request ) )
            #log.info("Form Not Validated")
    else:        
        return render_to_response( 'login.html' , {}, context)
 
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Security Web Views <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

@login_required
def scan_report( request ):
    context = RequestContext( request )
    host_high_level_info = []
    last_five_exec_results = []
    scan_type=''
    curr_sec_exec = []
    curr_exec_ts = ''
    scan_info_db = []

    scan_type = request.GET.get( 'scan_type' )
    
    sec_exec_info = SecurityTestExecInfo.objects.filter( scan_type = scan_type ).order_by( '-exec_ts' )
    if sec_exec_info:
        curr_sec_exec = sec_exec_info[0]
        #pdb.set_trace()
        scan_id = curr_sec_exec.exec_id
        #curr_exec_ts = curr_sec_exec.exec_ts
        scan_info_db = SecurityTestExecInfo.objects.filter( exec_id = scan_id )
    
    for each_host_scan in scan_info_db:
        host_info = {}
        st_id = int( each_host_scan.st_id )

        host_open_port_services = SecurityOpenPortServices.objects.filter( st_id = st_id )

        host_name = each_host_scan.host_name
        
        host_info[ 'st_id' ] = st_id
        host_info[ 'name' ] = host_name
        host_info[ 'open_ports_count' ] = host_open_port_services.count()
        host_info[ 'critical' ] = each_host_scan.critical
        host_info[ 'high' ] = each_host_scan.high
        host_info[ 'medium' ] = each_host_scan.medium
        host_info[ 'low' ] = each_host_scan.low
        host_info[ 'info' ] = each_host_scan.info

        host_high_level_info.append( host_info )

    latest_exec_res_query = """ SELECT MAX(exec_ts) as exec_ts, SUM(critical) as critical, SUM(high) as high, SUM(medium) as medium, SUM(low) as low, SUM(info) as info  FROM sec_test_exec WHERE scan_type='%s' GROUP BY exec_id ORDER BY exec_ts DESC LIMIT 5 """ % ( scan_type )
    cursor = connection.cursor()        
    cursor.execute( latest_exec_res_query )
    exec_results = list ( cursor.fetchall() )
    exec_results = exec_results[::-1]
    records_count = len( exec_results )
    for each_res in exec_results:
        temp_list = []
        ts = str( each_res[0] )
        temp_list.append( ts[ :ts.index(":")+3 ] )
        for i in range(1,6):
            temp_list.append( int( each_res[i] ) )
        last_five_exec_results.append( temp_list )
    curr_exec_ts = last_five_exec_results[ records_count-1 ][0]

    return render_to_response('scan_report.html', { 'user' : request.user, 'host_high_level_info' : host_high_level_info, 'report_name':scan_type+" Report", 'scan_type': scan_type, 'curr_exec_ts':curr_exec_ts, 'last_five_exec_results':last_five_exec_results } )



@login_required
def full_scan_report( request ):
    context = RequestContext( request )
    #pdb.set_trace()
    report_name = request.GET.get( 'scan_type' )+"_report.html"
    return render_to_response( report_name , {}, context)




@login_required
def host_scan_report( request ):
    st_id = request.GET.get( 'st_id' )
    host_open_ports = []
    port_service_info = SecurityOpenPortServices.objects.filter( st_id = st_id )
    for each_port in port_service_info:
        ps_dict = {}
        ps_dict[ 'port' ] = each_port.port_num
        ps_dict[ 'proto' ] = each_port.proto
        ps_dict[ 'service' ] = each_port.service_name

        host_open_ports.append( ps_dict )

    host_vul_info = []
    vul_info = SecurityVulInfo.objects.filter( st_id = st_id )
    for each_vul_info in vul_info:
        vul_dict = {}
        vul_dict['family'] = each_vul_info.family
        vul_dict['name'] = each_vul_info.name
        vul_dict['severity'] = each_vul_info.severity
        vul_dict['plugin_id'] = each_vul_info.plugin_id
        vul_dict['count'] = each_vul_info.count


        host_vul_info.append( vul_dict )

    return render_to_response( 'host_scan_report.html' , { 'user' : request.user, 'host_open_ports': host_open_ports, 'host_vul_info': host_vul_info } )



@login_required
def scan_report_bytype( request ):
    st_id = request.GET.get( 'st_id' )
    report_type = request.GET.get( 'type' )
    value = request.GET.get( 'value' )

    port_service_info = []
    severity_type_info = []

    if report_type == 'port':
        db_res = SecurityOpenPortServices.objects.filter( st_id = st_id )
        port_set = True

        for each_res in db_res:
            ps_dict = {}
            ps_dict[ 'port' ] = each_res.port_num
            ps_dict[ 'proto' ] = each_res.proto
            ps_dict[ 'service' ] = each_res.service_name

            port_service_info.append( ps_dict )


    elif report_type == 'severity':
        db_res = SecurityVulInfo.objects.filter( st_id = st_id, severity = value )
        port_set=False

        for each_res in db_res:
            st_dict = {}
            st_dict['family'] = each_res.family
            st_dict['name'] = each_res.name
            st_dict['severity'] = each_res.severity
            st_dict['plugin_id'] = each_res.plugin_id
            st_dict['count'] = each_res.count

            severity_type_info.append( st_dict )         

    return render_to_response( 'report_by_type.html' , { 'user' : request.user, 'port_service_info': port_service_info, 'severity_type_info': severity_type_info, 'report_type':report_type, 'port_set': port_set } )


def test( request ):
    return render_to_response("test_video_interstitial.html", {} )


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ End of Page views ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def register( request ):
    """
    User Registration View
    """
    if request.method == 'POST':
        form = RegistrationForm( data = request.POST )
        if form.is_valid():
            user = form.save()
            return redirect('/TestRepo/')
        
    else:
        form = RegistrationForm()
        
    return render_to_response( 'register.html', {'form': form }, context_instance = RequestContext(request) )



def addProject( request ):
    context = RequestContext( request )
    projects_info = tp.getProjectsList()
    project_list = projects_info.values()
    project_list_db = [ each[ 'project_name' ] for each in Projects.objects.values('project_name') ]
    
    for each_project in project_list:
        if each_project in project_list_db:
            project_list.remove( each_project )
    
    if request.method == 'POST':
        form = ProjectDetails( data = request.POST )
        project_name = form.data['project_name']
        staging_tp = form.data['staging_tp']
        production_tp = form.data['production_tp']
        
        project_id = tl.getProjectIDByName( project_name )        
        test_plans = tp.getTestplansByProjectID( project_id )
        
        stag_tpid = test_plans[ staging_tp ]
        prod_tpid = test_plans[ production_tp ]
            
        
        if ( staging_tp in test_plans  and production_tp in test_plans ):            
            if form.is_valid():
                    Projects.objects.create( project_name = project_name, staging_tp=staging_tp, stag_tpid = stag_tpid, production_tp=production_tp, prod_tpid = prod_tpid, pid = project_id, userid= User.objects.get(id = request.user.id ) )              
                    return render_to_response( 'add_project_status.html' , {'project_list' : project_list, 'status': True ,'message' : "Project successfully Added."}, context )
            else:
                    log.info( form.errors )
                    return render_to_response( 'add_project_status.html' , {'project_list' : project_list, 'status': False ,'message' : " Invalid form data"}, context)
        else:
            return render_to_response( 'add_project_status.html' , {'project_list' : project_list, 'status': False ,'message' : " Testplans provided does not exist in testlink" }, context)
           
    else:
        return render_to_response( 'add_project.html' , { 'project_list' : project_list  }, context )
    
  
    
def runSync( request ):
    context = RequestContext( request )
    p_obj = Projects.objects.filter()
    projects_info = [ {'pid' : str( each.pid ), 'project_name' : str( each.project_name ),  'staging_tp' : str( each.staging_tp ), 'production_tp' : str( each.production_tp ) } for each in p_obj if each.project_name in ['ProDashBoards'] ]
    #pdb.set_trace()
    stag = True
    prod = True
    
    for each_project in projects_info:
        project_name = each_project['project_name']
        project_id = each_project[ 'pid' ]
        staging_tp = each_project[ 'staging_tp' ]
        production_tp = each_project[ 'production_tp' ]        
        
        if stag:
            #Update Staging Stats
            res_stag_pro = _setProjectStats( project_name, staging_tp, "staging"  )
            res_stag_uc, stag_tc_data = _setUseCaseStats( project_id, project_name, staging_tp, "staging"  )
            res_stag_tc = _setTestCaseStats( stag_tc_data, "staging" )
        
        if prod:
            #Update Production Stats
            res_prod_pro = _setProjectStats( project_name, production_tp, "production"  )
            res_prod_uc, prod_tc_data = _setUseCaseStats( project_id, project_name, production_tp, "production"  )
            res_prod_tc = _setTestCaseStats( prod_tc_data, "production"  )
         
        if ( res_stag_pro and  res_prod_pro and res_stag_uc and res_prod_uc and res_stag_tc and res_prod_tc ):
            message = "Staging and Production stats successfully updated"
        else:
            message = "Staging and Production update failed"    
    
    return render_to_response( 'run_sync.html' , { 'message' : message  }, context )


"""
def syncBugs( request ):
    context = RequestContext( request )
    
    latest_version = jira.getCurrentRelease()
    issues_list = jira.getIssues( fix_version = latest_version )
    
    total_issues_data = []
    for each_issue in issues_list:
        issue_info = jira.getIssueInfo( each_issue )
        total_issues_data.append( issue_info )
        
    print total_issues_data
    
    res = _setBugSummary( total_issues_data )
    
    if res:
        message = "Bug Summary successfully Updated"
    else:
        message = "Bug Summary updation failed"
    
    return render_to_response( 'sync_bugs.html' , { 'user' : request.user, 'message' : message  }, context )
"""


def logout( request ):    
    #Log Out Here
    django_logout(request)
    if 'tc_data' in request.session:
        del request.session['tc_data']
    return redirect('/TestRepoPro/')


"""
Utility Functions
"""

def _setProjectStats( project_name, test_plan, tp_mode):
    #project_stats = tp.getProjectStats( project_name,  test_plan )
    try:
        project_stats = tp.getProjectStats( project_name,  test_plan )
        #pdb.set_trace()
        if project_stats:
            ps_obj = ProjectStats.objects.filter( pid = project_stats['pid'], tp_mode = tp_mode )      
            if ps_obj:
                ps_obj.update( build_id = project_stats[ 'build_id' ], tc_count = project_stats['tc_count'], tc_pass_count = project_stats['tc_pass_count'], tc_fail_count = project_stats['tc_fail_count'], tc_nr_count = project_stats['tc_nr_count'], tc_block_count = project_stats['tc_block_count'] )
            else:
                ProjectStats.objects.create( pid = Projects.objects.get( pid = project_stats['pid'] ),  tp_mode = tp_mode, build_id = project_stats[ 'build_id' ], tc_count = project_stats['tc_count'], tc_pass_count = project_stats['tc_pass_count'], tc_fail_count = project_stats['tc_fail_count'], tc_nr_count = project_stats['tc_nr_count'], tc_block_count = project_stats['tc_block_count']   )
            
            log.info("Project Stats successfully updated for project: "+project_name+"  with Testplan: "+ test_plan)
            return True
        else:
            return False
    except:        
        log.info("Project Stats update failed for project: "+project_name+"  with Testplan: "+ test_plan+"\n"+traceback.format_exc())
        return False



def _getProjectStats( project_name, tp_mode ):
    try:
        cursor = connection.cursor()        
        cursor.execute( "SELECT pid,project_name,tc_count,tc_pass_count,tc_fail_count,tc_nr_count,tc_block_count from projects JOIN project_stats USING (pid) WHERE project_name = %s AND tp_mode = %s ;", [ project_name, tp_mode ]  )
        res = list ( cursor.fetchall()[0] )
        project_dict = {}
        project_dict['pid'] = res[0]
        project_dict['name'] = res[1]
        project_dict['tc_count'] = res[2]
        project_dict['tc_pass_count'] = res[3]
        project_dict['tc_fail_count'] = res[4]
        project_dict['tc_nr_count'] = res[5]
        project_dict['tc_block_count'] = res[6]
        cursor.close()
        return project_dict
    except:
        connection._rollback()
        return False
    

    
def _getTotalProjectStatsByMode( mode ):
    p_obj = Projects.objects.filter()
    projects_db = [ {'pid' : each.pid, 'project_name' : each.project_name } for each in p_obj ]
    tot_project_stats = []
    for each_project in projects_db:  
        project_stats = _getProjectStats( each_project[ 'project_name' ], mode )
        if project_stats:
            tot_project_stats.append( project_stats )
    return tot_project_stats



def _setUseCaseStats( project_id, project_name, test_plan, tp_mode ):
    try:        
        uc_data, tc_data = tp.getExecStats( project_name, test_plan )        
        #pdb.set_trace()
        for each_uc in uc_data:
            uc_id = each_uc['id' ]
            uc_obj = UseCases.objects.filter( uc_id = uc_id )     
            if not uc_obj:
                UseCases.objects.create( pid = Projects.objects.get( pid = project_id  ), uc_id = uc_id, usecase_name = each_uc['name'] )
                
            ucs_obj = UseCaseStats.objects.filter( uc_id = uc_id, tp_mode = tp_mode )
            if  ucs_obj:
                ucs_obj.update( tc_count = each_uc[ 'total' ], tc_passed = each_uc[ 'pass' ], tc_failed = each_uc['fail' ], tc_not_run = each_uc[ 'not_run' ], tc_blocked = each_uc[ 'blocked' ]   )
            else:
                UseCaseStats.objects.create(  uc_id = UseCases.objects.get( uc_id = uc_id  ),tp_mode = tp_mode, tc_count = each_uc[ 'total' ], tc_passed = each_uc[ 'pass' ], tc_failed = each_uc['fail'], tc_not_run = each_uc[ 'not_run' ], tc_blocked = each_uc[ 'blocked'  ]  )
        
        log.info("UseCase Stats successfully updated for project: "+project_name+"  with Testplan: "+ test_plan )
        
        return True, tc_data
    except:
        log.info("UseCase Stats update failed for project: "+project_name+"  with Testplan: "+ test_plan+"\n"+traceback.format_exc() )
        return False, False



def _getTotalUseCaseStatsByMode( pid, tp_mode ):
    try:        
        cursor = connection.cursor()        
        cursor.execute( " SELECT uc_id, usecase_name, tc_count, tc_passed, tc_failed, tc_not_run, tc_blocked  FROM usecases  JOIN usecase_stats  USING (uc_id) WHERE pid = %s AND tp_mode = %s ; ", [ pid, tp_mode ]  )
        res_data = list ( cursor.fetchall() )
        tot_uc_stats = []
        for each_res in res_data:
            uc_dict = {}
            uc_dict['uc_id'] = each_res[0]
            uc_dict['uc_name'] = each_res[1]
            uc_dict['total'] = each_res[2]
            uc_dict['pass'] = each_res[3]
            uc_dict['fail'] = each_res[4]
            uc_dict['not_run'] = each_res[5]
            uc_dict['blocked'] = each_res[6]
            tot_uc_stats.append( uc_dict )
        #Get Build ID    
        build_id_res = ProjectStats.objects.filter( pid = pid , tp_mode = tp_mode ).values()
        if build_id_res:
            build_id = build_id_res[0]['build_id'].strip()
        else:
            build_id = ''
            
        return tot_uc_stats, build_id
    
    except:
        log.info( traceback.format_exc() )
        connection._rollback()
        cursor.close()
        return False
    


def _setTestCaseStats( tc_data, tp_mode ):
    try:                        
        for each_tc in tc_data:
            tc_id = each_tc[ 'tc_id'  ]                       
            tc_obj = TestCases.objects.filter( tc_id = tc_id )     
            if not tc_obj:
                TestCases.objects.create(  uc_id = UseCases.objects.get( uc_id = each_tc[ 'tc_usecaseid' ]  ), tc_id = tc_id, testcase_name = each_tc['name'] )
                
            tcs_obj = TestCaseStats.objects.filter( tc_id = tc_id, tp_mode = tp_mode )
            if  tcs_obj:
                tcs_obj.update( status = each_tc[ 'status' ], exec_time = each_tc[ 'execution_ts' ], message = each_tc['tc_message'], bug_id = each_tc[ 'bug_id' ]  )
            else:
                TestCaseStats.objects.create(  tc_id = TestCases.objects.get( tc_id = tc_id ), tp_mode = tp_mode , status = each_tc[ 'status' ], exec_time = each_tc[ 'execution_ts' ], message = each_tc[ 'tc_message' ], bug_id = each_tc[ 'bug_id'  ]  )
        
        log.info("TestCase Stats successfully updated")
        
        return True
    except:
        log.info("TestCase Stats updation failed"+"\n"+traceback.format_exc())
        return False



def _getTestCaseStats( tc_id, tp_mode, tc_mode ):
    try:
        cursor = connection.cursor()
        if tc_mode == 'all':
            query_string = "SELECT tc_id, testcase_name, status, exec_time, message, bug_id FROM testcases JOIN testcase_stats USING (tc_id) WHERE tc_id = %s AND tp_mode = %s " % ( tc_id, tp_mode )
        else:
            query_string = "SELECT tc_id, testcase_name, status, exec_time, message, bug_id FROM testcases JOIN testcase_stats WHERE tc_id = %s AND tp_mode = %s AND  status = %"  % ( tc_id, tp_mode, tc_mode )
        cursor.execute( query_string  )
        res = list ( cursor.fetchall()[0] )
        tc_dict = {}
        tc_dict['tc_id'] = res[0]
        tc_dict['tc_name'] = res[1]
        tc_dict['status'] = res[2]
        tc_dict['exec_time'] = res[3]
        tc_dict['message'] = res[4]
        tc_dict['bug_id'] = res[5]       
        cursor.close()
        return tc_dict
    except:
        connection._rollback()
        log.info( "Unable to get TestCaseStats"+"\n"+traceback.format_exc() )
        return False
    


def _getTotalTestCaseStatsByMode( uc_id, tp_mode, tc_mode ):
    try:        
        cursor = connection.cursor()             
        if tc_mode == 'all':
            cursor.execute( "SELECT tc_id,testcase_name,status,exec_time,message,bug_id FROM testcases JOIN testcase_stats USING (tc_id) WHERE uc_id = %s  AND tp_mode = %s ; " , [ uc_id, tp_mode ] )
        else:
            cursor.execute( "SELECT tc_id,testcase_name,status,exec_time,message,bug_id FROM testcases JOIN testcase_stats USING (tc_id) WHERE uc_id = %s  AND tp_mode = %s AND  status = %s  ;" , [ uc_id, tp_mode, tc_mode ] )
        
        res_data = list ( cursor.fetchall() )        
        tot_tc_stats = []
        for each_res in res_data:
            tc_dict = {}
            tc_dict['tc_id'] = each_res[0]
            tc_dict['tc_name'] = each_res[1]
            tc_dict['status'] = each_res[2]
            tc_dict['exec_time'] = each_res[3]
            tc_dict['message'] = each_res[4]
            tc_dict['bug_id'] = each_res[5]
            tot_tc_stats.append( tc_dict )
        
        cursor.close()
        return tot_tc_stats
    except:
        log.info( "Unable to get Total TestCase statistics"+"\n"+ traceback.format_exc() )
        connection._rollback()
        cursor.close()
        return False
    

    
def _setBugSummary( total_issues_data ):
    try:
        # Update bugs summar data from JIRA to QADashBoardPro database
        for each_issue_data in total_issues_data:
            bug_id = each_issue_data[ 'bug_id' ]
            
            bs_obj = BugSummary.objects.filter( bug_id = bug_id )     
            if not bs_obj:
                BugSummary.objects.create(  bug_id = bug_id, summary = each_issue_data[ 'summary'  ], issue_type = each_issue_data[ 'issue_type'  ], status = each_issue_data[ 'status' ], components = each_issue_data[ 'components' ], urgency = each_issue_data[ 'urgency'  ], priority = each_issue_data[ 'priority' ], assignee = each_issue_data[ 'assignee' ], qe = each_issue_data[ 'qe' ], fix_versions = each_issue_data[ 'fix_versions'  ], environment = each_issue_data[ 'environment' ], sys_env = each_issue_data[ 'sys_env' ], reporter = each_issue_data[ 'reporter'  ] )
            else:
                bs_obj.update( summary = each_issue_data[ 'summary'  ], issue_type = each_issue_data[ 'issue_type'  ], status = each_issue_data[ 'status' ], components = each_issue_data[ 'components' ], urgency = each_issue_data[ 'urgency'  ], priority = each_issue_data[ 'priority' ], assignee = each_issue_data[ 'assignee' ], qe = each_issue_data[ 'qe' ], fix_versions = each_issue_data[ 'fix_versions'  ], environment = each_issue_data[ 'environment' ], sys_env = each_issue_data[ 'sys_env' ], reporter = each_issue_data[ 'reporter'  ]  )

        return True
            
    except:
        log.info( "Bug Summary Updation failed with traceback"+ "\n" + traceback.format_exc() )
        return False
    


def _getIssueCountsByProjectByVersion( fix_version ):
    try:
        issue_stats = {}
        
        p1_count = BugSummary.objects.filter( urgency__contains = 'P1' , fix_versions__contains = fix_version  ).count()
        issue_stats[ 'p1' ] = p1_count
        p2_count = BugSummary.objects.filter( urgency__contains = 'P2' , fix_versions__contains = fix_version  ).count()
        issue_stats[ 'p2' ] = p2_count
        new_count = BugSummary.objects.filter( status__contains = 'New' , fix_versions__contains = fix_version  ).count()
        issue_stats[ 'new' ] = new_count
        in_prog_count = BugSummary.objects.filter( status__contains = 'In Progress' , fix_versions__contains = fix_version  ).count()
        issue_stats[ 'in_prog' ] = in_prog_count
        resolved_count = BugSummary.objects.filter( status__contains = 'Resolved' , fix_versions__contains = fix_version  ).count()
        issue_stats[ 'resolved' ] = resolved_count        
        verify_closed_count = BugSummary.objects.filter( status__in = (  'Verified', 'Closed'  ), fix_versions__contains = fix_version  ).count()
        issue_stats[ 'verify_closed' ] = verify_closed_count
        
        issue_stats
        
    except:
        log.info( "Loading Bug Summary failed with traceback"+ "\n" + traceback.format_exc()  )
        return False

    
def _getIssuesByComponentPerVersion( fix_version , component ):
    try:
        issues_res = {}
        issues_res[ 'name' ] = component
        
        p1_bugs_obj = BugSummary.objects.filter( urgency__contains = 'P1' , components__contains = component , fix_versions__contains = fix_version  )
        p2_bugs_obj = BugSummary.objects.filter( urgency__contains = 'P2' , components__contains = component , fix_versions__contains = fix_version  )
        
    except:
        log.info( "Loading Bug Summary failed with traceback"+ "\n" + traceback.format_exc() )
        return False
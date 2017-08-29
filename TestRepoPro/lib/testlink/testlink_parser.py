from testlink_api import testlinkAPI
import traceback
import sys, pdb
import logging
log = logging.getLogger(__name__)

class TestlinkParser:
    
    def __init__(self ):
        self.client = testlinkAPI()        
    
     
    def getProjectsList(self):
        res = self.client.getProjects()
        projects_list = {}
        for each_project in res:
            if each_project['is_public'] == '1':
                projects_list[ each_project['id'] ] = each_project['name' ]              
        return projects_list
    
    
    def getTestplansByProjectID( self,  project_id ):
        get_test_plans =  self.client.getProjectTestPlans( project_id )            
        test_plans = {}
        for each in get_test_plans:            
            if each['is_public'] == '1':
                test_plans[ each['name'] ] = each['id']                
        return test_plans
    
        
    def getProjectStats( self, project_name, test_plan ): 
        try:       
            project_stats = {}
            pid = self.client.getProjectIDByName( project_name )
            testplan_id = self.client.getTestPlanIDByProjectName( project_name ,  test_plan )
            res = self.client.getLatestBuildForTestPlan( project_name, testplan_id )[ 'build_name'  ]
            if res:
                build_id = res.strip()
            else:
                build_id = ''
            tot_for_testplan = self.client.getTotalsForTestPlan( testplan_id )
            project_stats[ 'pid' ] = pid
            project_stats[ 'name' ] = project_name
            project_stats[ 'build_id' ] = build_id
            project_stats[ 'tc_count' ] = int ( tot_for_testplan [ 'total' ][ 0 ][ 'qty'  ] )
            project_stats[ 'tc_pass_count' ] = int ( tot_for_testplan['with_tester' ][0][ 'p' ][ 'exec_qty' ] )
            project_stats[ 'tc_fail_count' ] = int ( tot_for_testplan['with_tester' ][0][ 'f' ][ 'exec_qty' ] )
            project_stats[ 'tc_nr_count' ] = int ( tot_for_testplan['with_tester' ][0][ 'n' ][ 'exec_qty' ] )
            project_stats[ 'tc_block_count' ] = int ( tot_for_testplan['with_tester' ][0][ 'b' ][ 'exec_qty' ] )        
            return project_stats
        except:
            print traceback.format_exc()
            return {}
            
        
     
        
    def getExecStats(self, project_name, test_plan):
        try:
            client = self.client
            testplan_id = client.getTestPlanIDByProjectName(project_name, test_plan)
            project_id = client.getProjectIDByName(project_name)
            usecase_data = self.getUseCaseData( project_id, testplan_id,   )            
            testcase_data = self.getTestCaseData( project_id, testplan_id)           
            usecase_stats = self.getUseCaseStats( project_id, usecase_data, testcase_data)            
            return usecase_stats, testcase_data
        
        except:
            print >> sys.stderr, traceback.format_exc()
            
     
            
    def getTestCaseData(self, project_id, testplan_id):
        try:
            client = self.client
            tc_data = []
            testcases_data = client.getCasesForTestPlanByTestPlanID( testplan_id )
            for each_tc in testcases_data.keys():
                tc_info = testcases_data[each_tc]
                tc = {}
                tc_id = tc_info[0]['tc_id']
                testsuite_id = client.getTestCase(tc_id)[0]['testsuite_id']                
                exec_res = client.getLastExecutionResult( testplan_id, tc_id )[0]
                tc['pid'] = project_id
                tc['tc_usecaseid'] = testsuite_id
                tc['tc_id'] = tc_id
                tc['name'] = tc_info[0]['tcase_name']                
                if exec_res['id'] != -1:
                    execution_notes = exec_res['notes']
                    execution_ts = exec_res['execution_ts']
                    tc['tc_message'] = execution_notes
                    tc['execution_ts'] = execution_ts
                    tc['status'] = exec_res['status']
                    exec_id =  exec_res['id']
                    bug_id = client.getTestCaseBugIdForExec(exec_id)
                    if bug_id:
                        tc['bug_id'] = str(bug_id)
                    else:
                        tc['bug_id'] = ''
                else:
                    tc['tc_message'] = "TestCase not executed. Please check"
                    tc['execution_ts'] = ''
                    tc['bug_id'] = ''
                    tc['status'] = 'n'

                tc_data.append(tc)

            return tc_data

        except:
            print >> sys.stderr, traceback.format_exc()
            
     
            
    def getUseCaseStats(self, project_id, usecase_data, testcase_data):        
        uc_stats = {}
        uc_data = []
        for each_tc in testcase_data:
            uc_id = each_tc[ 'tc_usecaseid' ]
            if not uc_stats.has_key( uc_id ):
                uc_stats[ uc_id ] = {}
                uc_stats[ uc_id ]['pid'] = project_id
                uc_stats[ uc_id ][ 'id' ] = uc_id
                uc_stats[ uc_id ][ 'pass' ] =  uc_stats[ uc_id ][ 'fail' ] = uc_stats[ uc_id ][ 'blocked' ] = uc_stats[ uc_id ][ 'not_run' ] = 0
                uc_stats[ uc_id ][ 'name' ] = ''
                uc_stats[ uc_id ][ 'total'] = 0

            if each_tc[ 'status' ] == 'p':
                uc_stats[ uc_id ][ 'pass' ] += 1
            elif each_tc[ 'status' ] == 'f':
                uc_stats[ uc_id ][ 'fail' ] += 1
            elif  each_tc[ 'status' ] == 'b':
                uc_stats[ uc_id ][ 'blocked' ] += 1
            else:
                uc_stats[ uc_id ][ 'not_run' ] += 1

            uc_stats[ uc_id ][ 'name' ] = usecase_data[ uc_id ]
            uc_stats[ uc_id ][ 'total' ] += 1
            
        for each_uc in uc_stats:
            uc_data.append( uc_stats[each_uc] )
        return uc_data
    
    
    
    def getUseCaseData( self, project_id, testplan_id ):
        try:
            client = self.client
            root_nodes = []
            ts_data = client.getTestSuitesForTestPlan( testplan_id, True)            
            for each_ts in ts_data:
                if each_ts['parent_id'] == project_id:
                    root_nodes.append(each_ts)
            self.uc_name = ''
            self.uc_data = {}
            self.parseTestSuites(root_nodes, ts_data, project_id )  
            return self.uc_data
        except:
            print >> sys.stderr, traceback.format_exc()
            
    
    
    def parseTestSuites(self, ts_nodes, ts_data, project_id):
        for each_data in ts_nodes:
            if each_data['parent_id'] == project_id:
                self.uc_name = ''
                
            self.uc_name += each_data['name']+"_"        
            node_data = self.getNodesList( each_data['id'], ts_data )            
            if not node_data:
                self.uc_name = self.uc_name.strip('_')
                self.uc_data[ each_data['id'] ] = self.uc_name
                self.uc_name = self.uc_name[:self.uc_name.rfind('_')]+'_'                
            else:
                self.parseTestSuites(node_data, ts_data, project_id)
        
        index = self.uc_name.strip('_').rfind('_')
        self.uc_name = self.uc_name[:index]+'_'
    
    
    
    def getNodesList(self, node_id, ts_data):
        node_list = []
        for each in ts_data:
            if each['parent_id'] == node_id:
                node_list.append( each )
        return node_list
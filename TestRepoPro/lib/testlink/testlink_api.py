import sys
import xmlrpclib
import ConfigParser, os, re
from xml.dom.minidom import parse
import paramiko
import urllib

# Testlink Version : 1.9.7
SERVER_URL = "http://localhost:8888/testlink-1.9.13/lib/api/xmlrpc/v1/xmlrpc.php"
DEV_KEY = "<DEV_KEY>"


class testlinkAPI:

      def __init__(self):
          self.server = xmlrpclib.Server(SERVER_URL)
          self.devKey = DEV_KEY
          self.usecases = {}
          self.usecase_ind = 0
          self.usecase_name = ""
          

      def getInfo(self):
          return self.server.tl.about()

      def ping(self):
          return self.server.tl.ping() 
          
      def echo(self, message):
            return self.server.tl.repeat({'str':message})         

      def createBuild(self, planID, buildName, buildNotes):
          args = {'devKey':self.devKey, 'testplanid':str(planID), 'buildname':buildName, 'buildnotes':buildNotes}
          return self.server.tl.createBuild(args)

      def getTestCaseBugIdForExec(self, exec_id):
          """
          args = {'devKey':self.devKey,'executionid':exec_id}
          tc_bug_info = self.server.tl.getTestCaseBugInfoForExec(args)
          bug_id = ""
          if tc_bug_info:
             for each_bug in tc_bug_info:
                 bug_id = bug_id+each_bug['bug_id']+","
             return bug_id.rstrip(',')             
          else:
             pass
          """
          return ""  

      def updateTestCase(self, tcid, tpid, buildID, status, msg=None):
        if status == 'p':
            args = {"devKey":self.devKey, "testcaseid":tcid, "testplanid":tpid, 'buildid':buildID, "status":status}

        else:
            latestExecInfo = self.getLastExecutionResult(tpid,tcid)            
            exec_id = int( latestExecInfo[0]['id'])
            bug_id = self.getTestCaseBugIdForExec(exec_id)
            if bug_id:
               args = {"devKey":self.devKey, "testcaseid":tcid, "testplanid":tpid, 'buildid':buildID, "status":status, "notes":msg, "bugid":bug_id}
            else:
               args = {"devKey":self.devKey, "testcaseid":tcid, "testplanid":tpid, 'buildid':buildID, "status":status, "notes":msg}
    
        return self.server.tl.reportTCResult(args)
              


      def getTestCaseIDByName(self, testCaseName = None, testSuiteName = None, testcasePath = None, project_id = None, testplan_id = None):
      # TestCase Path Format: <TestSuite-1>_<TestSuite-2>_ ... <TestSuite-X>:<TestCaseName>
          if testcasePath:
             if project_id and testplan_id:
                uc_info = self.getUseCasesForTestPlan(project_id,testplan_id)
                tc_id = uc_info[testcasePath]
                return tc_id

             else:                
                return False
          elif testCaseName and testSuiteName:               
               args = {"devKey":self.devKey, "testcasename":testCaseName, "testsuitename":testSuiteName}                  
               return self.server.tl.getTestCaseIDByName(args)[0]['id']

          else:
               print "Test Case Name and TestSuite Name need to be passed"
               return False

      
              
      def getCasesForTestPlan(self, projectName, planName):
          args = {'devKey':self.devKey, 'testprojectname':str(projectName), 'testplanname':str(planName)}
          testplans = self.server.tl.getTestPlanByName(args)
          for testplan in testplans:
              if testplan['name'] == planName:
                 testplanid = testplan['id']
          args = {'devKey':self.devKey, 'testplanid':str(testplanid)}
          return self.server.tl.getTestCasesForTestPlan(args)    


            
      def getCasesForTestPlanByTestPlanID(self, testplanid):  
          args = {'devKey':self.devKey, 'testplanid':str(testplanid)}
          return self.server.tl.getTestCasesForTestPlan(args)    


          
      def getCasesForTestSuite(self, testProjectID, testSuiteID):
          args = {'devKey':self.devKey, "testprojectid":testProjectID, 'testsuiteid':testSuiteID}
          return self.server.tl.getCasesForTestSuite(args)          



      def getTestSuiteByID(self, testSuiteID):
          args = {'devKey':self.devKey, "testsuiteid":testSuiteID}
          return self.server.tl.getTestSuiteByID(args)                    


      def getTestCaseVersion(self, tcid):
          args = {'devKey':self.devKey, 'testcaseid':tcid}
          return self.server.tl.getTestCase(args)[0]['version']

      
      def getTestCase(self, tc_id):
          args = {'devKey':self.devKey, 'testcaseid':tc_id}
          return self.server.tl.getTestCase(args)


      def getTestCasePriority(self, tcid):
          args = {'devKey':self.devKey, 'testcaseid':tcid}
          return self.server.tl.getTestCase(args)[0]['importance']  

      
      def getProjects(self):
          args = {'devKey':self.devKey}
          return self.server.tl.getProjects(args)

      
      def getProjectIDByName(self, projectName, tot_info = False ):
          args = {'devKey':self.devKey, "testprojectname":projectName}
          projects = self.server.tl.getProjects(args)
          result = -1
          for project in projects:
              if (project['name'] == projectName):
                  if not tot_info:
                      result = project['id']
                  else:
                      result = project
          return result

      
      def getProjectTestPlans(self, testProjectID):
              args = {"devKey":self.devKey, "testprojectid":testProjectID}
              return self.server.tl.getProjectTestPlans(args)

      
      def getTestPlanIDByProjectName(self, project_name, test_plan):
          args = {"devKey":self.devKey, "testprojectname":project_name, "testplanname":test_plan}
          testplan = self.server.tl.getTestPlanByName(args)[0]
          return testplan['id']


      def getFirstLevelTestSuitesForTestProject(self, projectID):        
              args = {'devKey':self.devKey, "testprojectid":projectID}
              return self.server.tl.getFirstLevelTestSuitesForTestProject(args)              


      def getTestSuitesForTestPlan(self, testplanid, internalFlag = None):
          args = {'devKey':self.devKey, "testplanid":testplanid}
          testsuites = self.server.tl.getTestSuitesForTestPlan(args)
          if internalFlag:
             return testsuites
          return [testsuite['id'] for testsuite in testsuites]


      def getTestSuitesForTestSuite(self, testsuiteid):
          args = {'devKey':self.devKey,'testsuiteid':testsuiteid}
          testsuites = self.server.tl.getTestSuitesForTestSuite(args)
          return testsuites


      def prepareUseCasesForTestSuite(self, testsuite, testcases, mg_script=None):
          self.usecase_name += testsuite['name'] + "_"
          self.testsuiteid = testsuite['id']
          testsuites = self.getTestSuitesForTestSuite(self.testsuiteid)
          if testsuites:
             for testsuite in testsuites:
                 if testsuite == 'node_type_id':
                    testsuite = {'name':testsuites['name'], 'id':testsuites['id']}
                    break
                 self.prepareUseCasesForTestSuite(testsuites[testsuite], testcases, mg_script)
             self.usecase_name = '_'.join(self.usecase_name.rstrip('_').split('_')[:-1]) + "_"
          elif mg_script:
               self.usecases[self.testsuiteid] = self.usecase_name.rstrip('_')
               self.usecase_name = '_'.join(self.usecase_name.rstrip('_').split('_')[:-1]) + "_"
          else :
              testcasesOfTestSuite = self.getTestCasesForTestSuite(self.testsuiteid)
              for testcase in testcasesOfTestSuite:
                  if testcase['id'] in testcases:
                     self.usecases[self.usecase_name.rstrip('_') + ':' + testcase['name']] = testcase['id']
              self.usecase_name = '_'.join(self.usecase_name.rstrip('_').split('_')[:-1]) + "_"

          
      
      #This method is to get usecases for sync project alone
      def getUseCasesForTestPlan(self, project_id, testplan_id, mg_script = None):
          testsuites = self.getFirstLevelTestSuitesForTestProject(project_id)
          testcasesForTestplan = self.getCasesForTestPlanByTestPlanID(testplan_id)
          testcases = []
          testcaseids = []          
          for testcase in testcasesForTestplan:
              testcases.append(testcasesForTestplan[testcase][0]['tc_id'])
          for testsuite in testsuites:              
              self.usecase_name = ""
              self.prepareUseCasesForTestSuite(testsuite, testcases, mg_script)
              self.usecase_ind += 1
          return self.usecases


      def getTestCasesForTestSuite(self, testsuiteid):
          args={'devKey':self.devKey,'testsuiteid':testsuiteid}
          testcases = self.server.tl.getTestCasesForTestSuite(args)
          return testcases


      def getLastExecutionResult(self, testplan_id, tcid):
          args={'devKey':self.devKey,'testplanid':testplan_id,'testcaseid':tcid}
          lastExecRes = self.server.tl.getLastExecutionResult(args)
          return lastExecRes



      def getTotalsForTestPlan(self, testplan_id):
          args={'devKey':self.devKey,'testplanid':testplan_id}
          total_test_plan = self.server.tl.getTotalsForTestPlan(args)
          return total_test_plan



      def getTestCaseCustomFieldDesignValue(self, tcid, version, projectID, customField):
          args = {"devKey":self.devKey, "testcaseid":tcid, "version":version, "testprojectid":projectID,"customfieldname":customField}
          return self.server.tl.getTestCaseCustomFieldDesignValue(args) 


          
      def getTestCaseCustomFields(self, tcid, version, projectID):
          args = {"devKey":self.devKey, "testcaseid":tcid, "version":version, "testprojectid":projectID}
          customfields = self.server.tl.getTestCaseCustomFields(args)
          return [customfields[customfield] for customfield in customfields]



      def updateCustomField(self, tcid, projectID, customfieldlabel, cf_value):         
          args = {"devKey":self.devKey, "customfieldname":str(customfieldlabel), "customfieldvalue":str(cf_value), "tc_id":int(tcid)}
          result = self.server.tl.updateCustomField(args)



      def getLatestBuildForTestPlan(self, projectName, testplan_id):
          args = {"devKey":self.devKey, "testplanid": testplan_id}
          buildName = self.server.tl.getLatestBuildForTestPlan(args)
          if type(buildName) is list and buildName[0]['code']:
             return None
          else:            
             return {'build_name':buildName['name'], 'buildID':buildName['id']}


          
      def getBuildName(self, environment):          
          if environment == 'staging':
             url = "https://opsconsole-test.efrontier.com/adlens-version.cgi"
          elif environment == 'production':
             url = "https://opsconsole.efrontier.com/adlens-version.cgi"

          buildName = urllib.urlopen(url).read()
          return buildName



      def createNewBuild(self, projectName, testplan_id, environment):
          #environment values will be 'staging' or 'production'
          stagingBuild = self.getBuildName(environment)
          args_dict = self.getLatestBuildForTestPlan(projectName, testplan_id)
          if args_dict:
             latestTLBuild = args_dict['build_name']
             if stagingBuild != latestTLBuild:
                args = {"devKey":self.devKey, "testplanid":testplan_id, "buildname":stagingBuild, "buildnotes": "Release "+stagingBuild}
                self.server.tl.createBuild(args)
                print "Created new build: %s" %stagingBuild
             else: 
                print "Staging build is same as the latest TL build and no new build is created"

          else:
              args = {"devKey":self.devKey, "testplanid":testplan_id, "buildname":"First Build", "buildnotes": "First Build"}
              self.server.tl.createBuild(args)
              print "Created new build"


      def createTestSuite(self, testsuite_name, project_id):
          args = { "devKey":self.devKey, "testsuitename": testsuite_name, "testprojectid": project_id }
          testsuiteresult = self.server.tl.createTestSuite(args)
          return testsuiteresult[0]['id']

      def createTestCase(self, project_id, testsuite_id, testcase_name, summary, author_login, steps, execution_type):
          args = { "devKey":self.devKey, "testprojectid": project_id, "testsuiteid": testsuite_id, "testcasename": testcase_name, "summary": summary, "authorlogin": author_login, "steps": steps, "executiontype": execution_type }
          res = self.server.tl.createTestCase(args)
          return res

      def createTestProject(self, testproject_name, testcase_prefix_name, project_desc, active, public):
          args = { "devKey":self.devKey, "testprojectname": testproject_name, "testcaseprefix": testcase_prefix_name, "notes": project_desc, "active": active, "public": public }
          self.server.tl.createTestProject(args)



if __name__ == '__main__':
   client = testlinkAPI()
   print client.getBuildName('production')

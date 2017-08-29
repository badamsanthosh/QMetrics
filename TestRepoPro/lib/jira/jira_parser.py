from jira.client import JIRA
import sys, urllib, traceback, pdb

custom_fields_dict = { 'urgency'  : 'customfield_13419' , 'qe' : 'customfield_12801', 'sys_env' : 'customfield_14905'  }

class JiraParser:
    
    def __init__(self):
        ### Connect to JIRA ###
        self.jira = JIRA( options,  basic_auth = ( username, pwd ), oauth = None )
        
        
    def getCurrentRelease(self, url):
        stag_build = urllib.urlopen(url).read()[:5]
        version_name = stag_build[:2]+'.'+stag_build[2:4]+'.'+stag_build[4]
        return version_name
           
            
    
    def getIssueCountsByProjectByVersion(self, version ):
        try:
            jira = self.jira
            issue_stats = {}
                    
            p1_issues = self.getIssues( fix_version = version, urgency = 'P1 - Hot/Critical' )
            issue_stats['p1'] = len( p1_issues )
            
            p2_issues = self.getIssues( fix_version = version, urgency = 'P2 - High' )
            issue_stats['p2'] = len( p2_issues )
            
            new = self.getIssues( fix_version = version, status = 'New'  )
            issue_stats['new'] = len( new )
            
            in_prog = self.getIssues( fix_version = version, status = 'In Progress'  )
            issue_stats['in_prog'] = len( in_prog )            
            
            resolved = self.getIssues( fix_version = version, status = 'Resolved'  )
            issue_stats['resolved'] = len( resolved )
            
            verify_closed = self.getIssues( fix_version = version, status = "Closed', 'Verified"  )
            issue_stats['verify_closed'] = len( verify_closed )
            
            return issue_stats
        
        except:
            print traceback.format_exc()
            
            
        
    def getIssuesByComponentPerVersion(self, fix_version, component ):
        try: 
            issue_stats = {}
            issue_stats['name'] = component
            p1_issues = self.getIssues( fix_version = fix_version, component = component, urgency = 'P1 - Hot/Critical'  )
            issue_stats['p1'] = len( p1_issues  )
            
            p2_issues = self.getIssues( fix_version = fix_version, component = component, urgency = 'P2 - High' )
            issue_stats['p2'] = len( p2_issues  )
            
            new = self.getIssues( fix_version = fix_version, component = component, status = 'New'  )
            issue_stats['new'] = len( new  )
            
            in_prog = self.getIssues( fix_version = fix_version, component = component, status = 'In Progress'  )
            issue_stats['in_prog'] = len( in_prog  )
             
            resolved = self.getIssues( fix_version = fix_version, component = component, status = 'Resolved'  )
            issue_stats['resolved'] = len( resolved  )
            
            verify_closed = self.getIssues( fix_version = fix_version, component = component, status = "Closed', 'Verified"  )
            issue_stats['verify_closed'] = len( verify_closed  )            
            
            return issue_stats
        
        except:
            print >>sys.stderr, traceback.format_exc()
        
        
            
    def getIssues( self, fix_version = None , status = None , urgency = None, component = None ):
        try:
            jira = self.jira
            
            jql_str = " project = AMO AND "
            
            if fix_version:
                jql_str += " fixVersion = "+ fix_version
                
            if status:
                jql_str += " AND status in " +" ('" + status +"') "
            
            if component:
                jql_str += " AND component in "+"('" + component + "') "
                
            if urgency:
                jql_str += " AND Urgency in " +" ('" + urgency +"') "
                
            #pdb.set_trace()
            issue_res = jira.search_issues( jql_str = jql_str )
            
            if  issue_res:
                return issue_res
            else:
                return[]
                
        except:
            print >> sys.stderr, traceback.format_exc()


            
    def getIssuesListData( self, issues_list ):
        try:
            if issues_list:
                tot_issues_data = {}
                tot_issues_data[ 'count' ] = len( issues_list )
                
                issue_data = []
                for each_issue in issues_list:
                    issue_stats = {}
                    issue_stats[ 'id' ] = each_issue.key
                    issue_stats['summary' ] = each_issue.fields.summary
                    issue_stats[ 'priority' ] = each_issue.fields.priority.name
                    issue_stats[ 'status' ] = each_issue.fields.status.name
                    issue_data.append(issue_stats  )
                
                tot_issues_data[ 'data' ] = issue_data
                
                return tot_issues_data
            else:
                return False
        
        except:
            print >> sys.stderr, traceback.format_exc()
            
    
    
    def getIssueInfo(self, issue_obj ):
        try:
            issue_info = {}
            
            issue_info[ 'bug_id' ] = issue_obj.key
            issue_info[ 'summary' ] = issue_obj.fields.summary
            issue_info[ 'issue_type' ] =  issue_obj.fields.issuetype.name
            issue_info[ 'components' ] = self.getComponents( issue_obj )
            issue_info[ 'urgency' ] = self.getCustomFieldValue( 'urgency', issue_obj )
            issue_info[ 'priority' ] = issue_obj.fields.priority.name
            issue_info[ 'assignee' ] = issue_obj.fields.assignee.name
            issue_info[ 'qe' ] = self.getCustomFieldValue( 'qe', issue_obj )
            issue_info[ 'fix_versions' ] = self.getFixVersions( issue_obj )
            issue_info[ 'environment' ] = issue_obj.fields.environment
            issue_info[ 'sys_env' ] = self.getCustomFieldValue( 'sys_env', issue_obj )
            issue_info[ 'reporter' ] = issue_obj.fields.reporter.name
            issue_info[ 'status' ] = issue_obj.fields.status.name
            
            return issue_info
            
        except:
            print >> sys.stderr, traceback.format_exc()
            
            
    def getComponents( self, issue_obj ):
        try:
            components = []
            components_list = issue_obj.fields.components
            
            if components_list:
                for each_component in components_list:
                    components.append( each_component.name )                    
                return  ','.join( components  )
            else:
                return ''
            
        except:
            print >> sys.stderr, traceback.format_exc()
            
            
    def getFixVersions( self, issue_obj ):
        try:
            fix_versions = []
            fix_versions_list = issue_obj.fields.fixVersions
            
            if fix_versions_list:
                for each_fix_version in fix_versions_list:
                    fix_versions.append( each_fix_version.name )                    
                return  ','.join( fix_versions  )
            else:
                return ''
            
        except:
            print >> sys.stderr, traceback.format_exc()
            
            
    def getCustomFieldValue( self, name, issue_obj ):
        try:
            custom_field_id = custom_fields_dict[ name ]
            custom_field_obj = getattr( issue_obj.fields, custom_field_id )            
            
            if hasattr( custom_field_obj, 'value' ):
                return custom_field_obj.value
            elif hasattr( custom_field_obj, 'name' ):
                return custom_field_obj.name
            else:
                return ''
            
        except:
            print >> sys.stderr, traceback.format_exc()
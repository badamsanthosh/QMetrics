from django import forms
from TestRepoPro.models import Projects


class ProjectDetails( forms.ModelForm ):
    project_name = forms.CharField(widget=forms.widgets.TextInput, label="Project Name:", required = True )    
    staging_tp = forms.CharField(widget=forms.widgets.TextInput, label="Pre Release:", required = True )
    production_tp = forms.CharField(widget=forms.widgets.TextInput, label="Post Release:", required = True )
    
    class Meta:
        model = Projects
        fields = [ 'project_name',  'staging_tp', 'production_tp' ]
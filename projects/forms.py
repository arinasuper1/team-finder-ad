from django import forms
from projects.models import Project
from constants.validations import validation_github_url


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']
        widgets = {
            'status': forms.Select(choices=Project.status)
        }
    
    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        return validation_github_url(url)
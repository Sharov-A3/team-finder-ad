from django import forms

from users.utils import is_github_url

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "Ссылка на GitHub",
            "status": "Статус",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "status": forms.Select(choices=Project.STATUS_CHOICES),
        }

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url", "").strip()
        if not url:
            return url
        if not is_github_url(url):
            raise forms.ValidationError("Ссылка должна вести на GitHub (https://github.com/...).")
        return url

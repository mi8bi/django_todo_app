from django import forms
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from datetime import date, timedelta
from .models import Task, Category


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "title",
            "category",
            "progress",
            "description",
            "start_date",
            "due_date",
            "status",
            "priority",
        ]
        widgets = {
            "progress": forms.Select(choices=[(i, f"{i} %") for i in range(0, 101, 10)]),
            "start_date": forms.DateInput(
                attrs={"type": "date", "min": date.today().isoformat()}
            ),
            "due_date": forms.DateInput(
                attrs={"type": "date", "min": date.today().isoformat()}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].required = True

    def clean_start_date(self):
        start_date = self.cleaned_data.get("start_date")
        if start_date < now() - timedelta(days=1):
            raise ValidationError("Due date cannot be in the past.")
        return start_date

    def clean_due_date(self):
        due_date = self.cleaned_data.get("due_date")
        if due_date < now() - timedelta(days=1):
            raise ValidationError("Due date cannot be in the past.")
        return due_date

    def clean_progress(self):
        progress = self.cleaned_data.get("progress")
        if progress is not None and progress < 0:
            raise ValidationError("進捗率は0以上で入力してください。")
        return progress

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        due_date = cleaned_data.get("due_date")
        if start_date and due_date and start_date > due_date:
            raise ValidationError("The scheduled start date is past the deadline.")
        return cleaned_data


class TaskSearchForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "category", "status", "priority"]

    def __init__(self, *args, **kwargs):
        super(TaskSearchForm, self).__init__(*args, **kwargs)
        self.fields["title"].required = False
        self.fields["category"].required = False
        self.fields["status"].required = False
        self.fields["priority"].required = False


class TaskBulkDeleteForm(forms.Form):
    tasks = forms.ModelMultipleChoiceField(
        queryset=Task.objects.all(), widget=forms.CheckboxSelectMultiple
    )


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["title"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "カテゴリ名"})
        }


class TaskUpdateForm(TaskForm):
    class Meta(TaskForm.Meta):
        widgets = TaskForm.Meta.widgets.copy()
        widgets["start_date"] = forms.DateInput(attrs={"type": "date"})
        widgets["due_date"] = forms.DateInput(attrs={"type": "date"})

    def clean_start_date(self):
        start_date = self.cleaned_data.get("start_date")
        # 更新時は過去日も許容
        return start_date

    def clean_due_date(self):
        due_date = self.cleaned_data.get("due_date")
        # 更新時は過去日も許容
        return due_date

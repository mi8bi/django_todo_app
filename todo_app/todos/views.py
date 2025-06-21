from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import (
    CreateView,
    UpdateView,
    DeleteView,
    FormMixin,
)
from django.contrib.auth.mixins import LoginRequiredMixin

from . import forms, models


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "todos/home.html"


class BoardView(LoginRequiredMixin, TemplateView):
    template_name = "todos/task_board.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_set = models.Task.objects.filter(user=self.request.user)
        context["notCompletedTasks"] = query_set.filter(
            status=models.Status.NOT_COMPLETED
        )
        context["progressTasks"] = query_set.filter(status=models.Status.PROGRESS)
        context["completedTasks"] = query_set.filter(status=models.Status.COMPLETED)
        return context

    def post(self, request):
        # TODO: バリデーションチェック
        task_id = request.POST.get("taskId", "")
        status = request.POST.get("status", models.Status.NOT_COMPLETED)
        is_updated = (
            models.Task.objects.filter(user=self.request.user)
            .filter(id__exact=task_id)
            .update(status=status)
        )

        if is_updated:
            return HttpResponse(status=200)
        return HttpResponse(status=404)


class GanttView(LoginRequiredMixin, TemplateView):
    template_name = "todos/task_gantt.html"


class GanttDataView(LoginRequiredMixin, View):
    def get(self, request):
        tasks = models.Task.objects.filter(user=self.request.user)
        tasks_gant = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "start_date": task.start_date,
                "due_date": task.due_date,
                "progress": task.progress,
            }
            for task in tasks
        ]
        return JsonResponse(tasks_gant, safe=False)


class TaskListView(LoginRequiredMixin, FormMixin, ListView):
    model = models.Task
    paginate_by = 10
    form_class = forms.TaskBulkDeleteForm
    success_url = reverse_lazy("todos:task_list")

    def get_queryset(self):
        queryset = models.Task.objects.filter(user=self.request.user)

        # 検索フォームの処理
        search_params = self.request.session.get("search_params", {})
        priority_query = search_params.get("priority", "")
        status_query = search_params.get("status", "")
        title_query = search_params.get("title", "")
        category_query = search_params.get("category", "")
        if priority_query:
            queryset = queryset.filter(priority__exact=priority_query)
        if status_query:
            queryset = queryset.filter(status__exact=status_query)
        if title_query:
            queryset = queryset.filter(title__icontains=title_query)
        if category_query:
            queryset = queryset.filter(category__id=category_query)

        # ソートの処理
        sort_by = self.request.GET.get("sort", "id")
        order = self.request.GET.get("order", "asc")
        if order == "desc":
            sort_by = f"-{sort_by}"

        queryset = queryset.order_by(sort_by)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ソート条件
        context["sort_by"] = self.request.GET.get("sort", "id")
        context["order"] = self.request.GET.get("order", "asc")
        context["today"] = now()
        # 検索
        context["search_form"] = forms.TaskSearchForm(
            self.request.session.get("search_params", {})
        )
        return context

    def post(self, request):
        # 検索フォームのデータをsessionに保存
        if "search_action" in request.POST:
            if request.POST["search_action"] == "search":
                request.session["search_params"] = {
                    "status": request.POST.get("status", ""),
                    "priority": request.POST.get("priority", ""),
                    "title": request.POST.get("title", ""),
                    "category": request.POST.get("category", ""),
                }
            elif request.POST["search_action"] == "clear":
                request.session["search_params"] = {
                    "status": "",
                    "priority": "",
                    "title": "",
                    "category": "",
                }

        # 削除処理
        form = self.get_form()
        if "tasks" not in request.POST:
            return redirect("todos:task_list")
        if not form.is_valid():
            return self.form_invalid(form)
        tasks = form.cleaned_data["tasks"]
        tasks.delete()
        return self.form_valid(form)


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = models.Task
    form_class = forms.TaskForm
    template_name_suffix = "_add_form"
    success_url = reverse_lazy("todos:task_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            return redirect("todos:task_list")
        return super(TaskCreateView, self).post(request, *args, **kwargs)

    def get_success_url(self):
        next_page = self.request.GET.get("next_page", "1")
        return f"{reverse("todos:task_list")}?page={next_page}"


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Task
    form_class = forms.TaskForm
    template_name_suffix = "_update_form"

    # TODO: formがinvalidateしたときに画面遷移が意図通りにいかない
    def get_success_url(self):
        referer_url = self.request.POST.get("referer-url", "")
        if referer_url:
            return referer_url
        return reverse("todos:task_list")


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Task
    template_name_suffix = "_confirm_delete"
    success_url = reverse_lazy("todos:task_list")


class TaskCategoryJsonView(LoginRequiredMixin, View):
    def get(self, request):
        tasks = models.Task.objects.filter(user=self.request.user)
        task_categories = [
            {
                "task_title": task.title,
                "category_title": (task.category.title if task.category else "なし"),
            }
            for task in tasks
        ]
        return JsonResponse(task_categories, safe=False)

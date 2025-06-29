from django.urls import path

from . import views

app_name = "todos"

urlpatterns = [
    path("task/list", views.TaskListView.as_view(), name="task_list"),
    path("task/add/", views.TaskCreateView.as_view(), name="task_add"),
    path("task/<int:pk>/update", views.TaskUpdateView.as_view(), name="task_update"),
    path("task/<int:pk>/delete", views.TaskDeleteView.as_view(), name="task_delete"),
    path("home/", views.HomeView.as_view(), name="home"),
    path("home/bar-chart", views.TaskCategoryJsonView.as_view(), name="task_category"),
    path("board/", views.BoardView.as_view(), name="board"),
    path("board/update", views.BoardView.as_view(), name="board_update"),
    path("gantt/", views.GanttView.as_view(), name="gantt"),
    path("gantt/get", views.GanttDataView.as_view(), name="gantt_get"),
    path("category/", views.CategoryListView.as_view(), name="category_list"),
    path("category/add/", views.CategoryCreateView.as_view(), name="category_add"),
]

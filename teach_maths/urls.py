from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.__register, name="register"),
    path("login/", views.__login_view, name="login"),
    path("logout/", views.__logout_view, name="logout"),
    path("users/", views.__user_list, name="user_list"),
    path("protected/", views.__protected_view, name="protected"),
    path("all_tasks/", views.__all_tasks, name="all_tasks"),
    path("add_task/", views.__add_task, name="add_task"),
    path("task/<int:task_id>/", views.__view_task, name="view_task"),
    path("edit_task/<int:task_id>", views.__edit_task, name="edit_task"),
    path("delete_task/<int:task_id>/", views.__delete_task,
         name="delete_task"),
    path("calculator/", views.__calculator_view, name="calculator"),
    path("edit_profile/", views.__edit_profile, name="edit_profile"),
    path(
        "student_task_view/<int:task_id>/",
        views.__student_task_view,
        name="student_task_view",
    ),
    path("all_results/", views.__all_results_view, name="all_results"),
    path("delete_user/<int:user_id>/", views.DeleteUserView.as_view(),
         name="delete_user"),
    path("all_results/", views.__all_results_view, name="all_results_view"),
    path("results/<int:task_id>/", views.__results, name="results"),
    path(
        "view_student_results/<int:user_id>/",
        views.__view_student_results,
        name="view_student_results",
    ),
]

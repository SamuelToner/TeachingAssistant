from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('users/', views.user_list, name='user_list'),
    path('protected/', views.protected_view, name='protected'),
    path('all_tasks/', views.all_tasks, name='all_tasks'),
    path('add_task/', views.add_task, name='add_task'),
    path('task/<int:task_id>/', views.view_task, name='view_task'),
    path('edit_task/<int:task_id>', views.edit_task, name='edit_task'),
    path('delete_task/<int:task_id>/', views.__delete_task,
         name='delete_task'),
    path('calculator/', views.calculator_view, name='calculator'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('student_task_view/<int:task_id>/', views.student_task_view,
         name='student_task_view'),
    path('all_results/', views.all_results_view, name='all_results'),
    path('delete_user/<int:user_id>/', views.DeleteUserView.as_view(),
         name='delete_user_view'),
    path('view_student_results/<int:user_id>/', views.view_student_results,
         name='view_student_results'),
    ]

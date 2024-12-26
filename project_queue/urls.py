from django.urls import path
from online_queue import views
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password, name='change_password'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('my-queue/', views.my_queue_view, name='my_queue'),
    path('leave-queue/<int:position_id>/', views.leave_queue, name='leave_queue'),
    path('join_queue/', views.join_queue, name='join_queue'),
    path('get_subjects_for_teacher/', views.get_subjects_for_teacher, name='get_subjects_for_teacher'),
    path('get_tasks_for_subject/', views.get_tasks_for_subject, name='get_tasks_for_subject'),
    path('get_students_for_group/', views.get_students_for_group, name='get_students_for_group'),
]

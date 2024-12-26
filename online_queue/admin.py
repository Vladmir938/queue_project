from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Group, Subject, Task, Queue, Result, GroupSubject, StudentGroup, SubjectTeacher


class GroupSubjectInline(admin.TabularInline):
    model = GroupSubject
    extra = 1  # Количество пустых строк для добавления новых записей


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [GroupSubjectInline]  # Добавляем связь группы с предметами через Inline


# Расширяем админку User, чтобы добавить отчество и скрыть пароль
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'patronymic', 'is_student', 'is_teacher', 'is_password_changed')
    list_filter = ('is_student', 'is_teacher', 'is_password_changed')
    search_fields = ('username', 'patronymic')
    ordering = ('username',)

    # Убираем пароль из отображения
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональные данные', {'fields': ('first_name', 'last_name', 'patronymic', 'email')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
        ('Другие', {'fields': ('last_login', 'date_joined', 'is_student', 'is_teacher', 'is_password_changed')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'patronymic', 'is_student', 'is_teacher')}
        ),
    )
    # Используем стандартный подход для ManyToMany поля
    filter_horizontal = ('groups',)


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'description', 'files')
    list_filter = ('subject',)
    search_fields = ('name', 'subject__name')


class QueueAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'task', 'file_address', 'created_at')
    list_filter = ('subject', 'task')
    search_fields = ('student__username', 'subject__name', 'task__name')
    date_hierarchy = 'created_at'


class ResultAdmin(admin.ModelAdmin):
    list_display = ('queue', 'user', 'result', 'description')
    list_filter = ('result',)
    search_fields = ('queue__student__username', 'user__username', 'result')


class StudentGroupAdmin(admin.ModelAdmin):
    list_display = ('user', 'group')
    search_fields = ('user__username', 'group__name')


class SubjectTeacherAdmin(admin.ModelAdmin):
    list_display = ('subject', 'teacher')
    search_fields = ('subject__name', 'teacher__username')


# Регистрируем модели в админке
admin.site.register(User, CustomUserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Queue, QueueAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(StudentGroup, StudentGroupAdmin)
admin.site.register(SubjectTeacher, SubjectTeacherAdmin)

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    patronymic = models.CharField(max_length=150, blank=True, null=True, verbose_name="Patronymic")
    is_student = models.BooleanField(default=False, verbose_name="Студент")
    is_teacher = models.BooleanField(default=False, verbose_name="Преподаватель")
    is_password_changed = models.BooleanField(default=False, verbose_name="Пароль изменен")

    # Связи, которые ранее были у Student
    groups = models.ManyToManyField('Group', through='StudentGroup', verbose_name="Группы", related_name="students")
    queue_results = models.ManyToManyField('Queue', through='Result', verbose_name="Результаты проверки", related_name="students")

    # Связи, которые ранее были у Teacher
    subjects = models.ManyToManyField('Subject', through='SubjectTeacher', verbose_name="Предметы", related_name="teachers")

    def __str__(self):
        return f"{self.username} ({'Преподаватель' if self.is_teacher else 'Студент'})"


class Group(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название группы")
    subjects = models.ManyToManyField('Subject', through='GroupSubject', related_name='groups', verbose_name='Предметы')

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название предмета")

    def __str__(self):
        return self.name


class Task(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название задания")
    description = models.TextField(verbose_name="Описание задания")
    files = models.FileField(upload_to='tasks/', blank=True, null=True, verbose_name="Файлы")
    # Указываем related_name для поля subject, чтобы избежать конфликта с полем tasks в Subject
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Предмет", related_name='task_subjects')

    def __str__(self):
        return self.name


class Queue(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Студент", related_name="queues")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Предмет", related_name="queues")
    file_address = models.FileField(upload_to='queue_files/', verbose_name="Файл задания")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name="Задание", related_name="queues")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время постановки")

    def __str__(self):
        return f"Очередь: {self.student} ({self.task})"


class Result(models.Model):
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE, related_name="results")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="result_entries")
    result = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.queue} - {self.result}"


class GroupSubject(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name="Группа")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Предмет")

    class Meta:
        unique_together = ['group', 'subject']  # Уникальная связь между группой и предметом

    def __str__(self):
        return f"{self.group.name} - {self.subject.name}"


class StudentGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Студент", related_name="student_groups")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name="Группа", related_name="student_groups")


class SubjectTeacher(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Предмет", related_name="subject_teachers")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Преподаватель", related_name="subject_teachers")


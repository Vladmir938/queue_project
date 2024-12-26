from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from online_queue.models import Subject, Task, Group, User, SubjectTeacher, StudentGroup, Queue


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Если пароль еще не был изменен, перенаправляем на страницу смены пароля
            if not user.is_password_changed:
                return redirect('change_password')
            return redirect('dashboard')
        else:
            messages.error(request, "Неверный логин или пароль.")

    return render(request, 'login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def change_password(request):
    if request.method == 'POST':
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        if new_password == confirm_password:
            request.user.set_password(new_password)
            request.user.is_password_changed = True  # Помечаем, что пароль был изменен
            request.user.save()
            messages.success(request, "Пароль успешно изменен!")
            return redirect('dashboard')
        else:
            messages.error(request, "Пароли не совпадают.")
    return render(request, 'change_password.html')


@login_required
def dashboard_view(request):
    user = request.user

    # Проверяем роль пользователя
    is_teacher = user.is_teacher
    is_student = user.is_student

    # Инициализация фильтров
    selected_teacher_id = request.GET.get('teacher')
    selected_subject_id = request.GET.get('subject')
    selected_task_id = request.GET.get('task')
    selected_student_id = request.GET.get('student')
    selected_group_id = request.GET.get('group')

    # Инициализируем данные для фильтров
    teachers = User.objects.filter(is_teacher=True)
    subjects = Subject.objects.none()
    tasks = Task.objects.none()
    groups = Group.objects.all()
    students = User.objects.filter(is_student=True)
    queue = None

    if is_teacher:
        if selected_teacher_id:
            teacher = User.objects.get(id=selected_teacher_id)
            subjects = teacher.subjects.all()

            if selected_subject_id:
                tasks = Task.objects.filter(subject_id=selected_subject_id)

        if selected_subject_id:
            queue = Queue.objects.filter(subject_id=selected_subject_id).order_by('created_at')

        if selected_task_id:
            queue = Queue.objects.filter(task_id=selected_task_id).order_by('created_at')

    elif is_student:
        student_groups = user.groups.all()

        if selected_teacher_id:
            teacher = User.objects.get(id=selected_teacher_id)
            subjects = teacher.subjects.filter(groups__in=student_groups).distinct()

            if selected_subject_id:
                tasks = Task.objects.filter(subject_id=selected_subject_id)

        else:
            subjects = Subject.objects.filter(groups__in=student_groups).distinct()
            tasks = Task.objects.filter(subject__groups__in=student_groups).distinct()

        if selected_subject_id:
            queue = Queue.objects.filter(subject_id=selected_subject_id).order_by('created_at')

        if selected_task_id:
            queue = Queue.objects.filter(task_id=selected_task_id).order_by('created_at')

    # Добавляем позиции в очереди
    queue_with_position = []
    if queue:
        for index, item in enumerate(queue, start=1):
            item.position = index
            queue_with_position.append(item)

    context = {
        'is_teacher': is_teacher,
        'is_student': is_student,
        'teachers': teachers,
        'subjects': subjects,
        'tasks': tasks,
        'groups': groups,
        'students': students,
        'queue': queue_with_position,
        'selected_teacher_id': selected_teacher_id,
        'selected_subject_id': selected_subject_id,
        'selected_task_id': selected_task_id,
        'selected_student_id': selected_student_id,
        'selected_group_id': selected_group_id
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'queue_table.html', {'queue': queue_with_position})
    return render(request, 'dashboard.html', context)


@login_required
def queue_view(request):
    return render(request, 'queue.html')


@login_required
def get_subjects_for_teacher(request):
    teacher_id = request.GET.get('teacher_id')
    if teacher_id:
        subjects = Subject.objects.filter(teachers__id=teacher_id)
        subject_data = [{'id': subject.id, 'name': subject.name} for subject in subjects]
        return JsonResponse({'subjects': subject_data})
    return JsonResponse({'subjects': []})


@login_required
def get_tasks_for_subject(request):
    subject_id = request.GET.get('subject_id')
    if subject_id:
        tasks = Task.objects.filter(subject_id=subject_id)
        task_data = [{'id': task.id, 'name': task.name} for task in tasks]
        return JsonResponse({'tasks': task_data})
    return JsonResponse({'tasks': []})


@login_required
def my_queue_view(request):
    """Отображение позиций студента в очереди."""
    user = request.user
    teachers = User.objects.filter(is_teacher=True)
    # Получаем группы, в которых состоит студент
    student_groups = user.groups.all()

    # Фильтруем очереди по предметам, связанным с этими группами
    all_queue_positions = (
        Queue.objects.filter(subject__groups__in=student_groups)
        .select_related('subject', 'task', 'student')
        .order_by('subject', 'task', 'created_at')
    )

    # Рассчитываем позиции относительно всех работ группы для каждого задания
    grouped_positions = {}
    for position in all_queue_positions:
        # Создаем группу по предмету и заданию
        key = (position.subject, position.task)
        if key not in grouped_positions:
            grouped_positions[key] = []
        grouped_positions[key].append(position)

    # Для каждого задания считаем позицию студента среди всех работ группы
    for positions in grouped_positions.values():
        positions.sort(key=lambda p: p.created_at)  # Сортируем по времени постановки
        for idx, position in enumerate(positions, start=1):
            if position.student == user:
                position.position_in_group = idx

    # Получаем только работы текущего студента, но с позициями
    student_queue_positions = [
        pos for positions in grouped_positions.values() for pos in positions if pos.student == user
    ]

    context = {
        'queue_positions': student_queue_positions,  # Передаем в шаблон только работы студента
        'teachers': teachers
    }
    return render(request, 'my_queue.html', context)


@login_required
def leave_queue(request, position_id):
    """Удаление позиции студента из очереди."""
    position = get_object_or_404(Queue, id=position_id, student=request.user)

    if request.method == 'POST':
        position.delete()
        return redirect('my_queue')

    return HttpResponseForbidden("Нельзя удалять чужие позиции.")


def join_queue(request):
    if request.method == 'POST':
        teacher = User.objects.get(id=request.POST['teacher'])
        subject = Subject.objects.get(id=request.POST['subject'])
        task = Task.objects.get(id=request.POST['task'])
        file = request.FILES['file']

        # Добавляем запись в очередь
        Queue.objects.create(
            student=request.user,
            subject=subject,
            task=task,
            file_address=file
        )

    return redirect('my_queue')


def get_students_for_group(request):
    group_id = request.GET.get('group_id')
    if group_id:
        students = User.objects.filter(groups__id=group_id, is_student=True)
        student_list = [
            {'id': student.id, 'last_name': student.last_name, 'first_name': student.first_name, 'patronymic': student.patronymic}
            for student in students
        ]
        return JsonResponse({'students': student_list})
    return JsonResponse({'students': []})


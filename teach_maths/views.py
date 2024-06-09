
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import UserRegisterForm, EditProfileForm
from .models import Task, QuestionAnswer, Result
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import Group, User
from django.views import View
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Prefetch
from .forms import CalculatorForm


class DeleteTaskView(UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self):
        task = get_object_or_404(Task, id=self.kwargs['task_id'])
        return self.request.user.groups.filter(name='Teacher').exists()

    def handle_no_permission(self):
        return render(self.request, 'protected.html')

    def get(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        return render(request, 'delete_task.html', {'task': task})

    def post(self, request, task_id):  # Change this line
        task = get_object_or_404(Task, id=task_id)
        task.delete()
        return redirect('all_tasks')


class DeleteUserView(UserPassesTestMixin, View):
    raise_exception = True

    def test_func(self):
        return Group.objects.get(name='teacher') \
            in self.request.user.groups.all()

    def handle_no_permission(self):
        return render(self.request, 'protected.html')

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        return render(request, 'delete_user.html', {'user': user})

    def post(self, request, user_id):  # Change this line
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return redirect('user_list')


def index(request):
    return render(request, 'index.html')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f'You are now logged in as {username}.')
                return redirect('index')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have successfully logged out.')
    return redirect('index')


def user_list(request):
    users = User.objects.all()
    is_teacher = request.user.groups.filter(name='teacher').exists()
    return render(request, 'users.html', {'users': users,
                                          'is_teacher': is_teacher})


def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = EditProfileForm(instance=request.user)
        args = {'form': form}
        return render(request, 'edit_profile.html', args)


def protected_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'protected.html')


def some_view(request):
    # Your view logic here...

    is_teacher = request.user.groups.filter(name='teacher').exists()
    context = {
        'is_teacher': is_teacher,
        # Other context variables...
    }
    return render(request, 'base.html', context)


# Create your views here.
def all_tasks(request):
    tasks = Task.objects.all()
    return render(request, 'all_tasks.html', {'tasks': tasks})


def add_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        questions = request.POST.getlist('question')
        answers = request.POST.getlist('answer')

        if title and questions and answers:
            task = Task(title=title)
            task.save()

            for question, answer in zip(questions, answers):
                if question and answer:  # Ensure question and answer are not empty
                    qa = QuestionAnswer(task=task, question=question, answer=answer)
                    qa.save()

            return redirect('view_task', task_id=task.id)

    return render(request, 'add_task.html')


@login_required
def view_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    is_teacher = request.user.groups.filter(name='teacher').exists()
    return render(request, 'view_task.html', {
        'task': task,
        'is_teacher': is_teacher,
    })


def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    question_answers = QuestionAnswer.objects.filter(task=task)
    if request.method == 'POST':
        title = request.POST.get('title')
        questions = request.POST.getlist('question')
        answers = request.POST.getlist('answer')
        # Update the task record
        task.title = title
        task.save()
        # Update the QuestionAnswer records
        for qa, question, answer in zip(question_answers, questions, answers):
            qa.question = question
            qa.answer = answer
            qa.save()
        # Redirect to the view_post page
        return redirect('view_task', task_id=task.id)
    return render(request, 'edit_task.html', {'task': task, 'question_answers': question_answers})


def __delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.delete()
        return redirect('all_tasks')
    return render(request, 'delete_task.html', {'task': task})


@login_required
def student_task_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    question_answers = QuestionAnswer.objects.filter(task=task)
    if request.method == 'POST':
        student_answers = request.POST.getlist('answer')
        qa_results = []
        for qa, student_answer in zip(question_answers, student_answers):
            result_text = 'Correct' if qa.answer.lower() == student_answer.lower() else 'Incorrect'
            qa_results.append({
                'question': qa.question,
                'result': result_text
            })
            # Save the result to the database
            Result.objects.create(
                task=task,
                student=request.user,
                question=qa.question,
                student_answer=student_answer,
                result=result_text
            )
        return render(request, 'student_task_results.html', {'qa_results': qa_results, 'task': task})
    return render(request, 'student_task_view.html', {'task': task, 'question_answers': question_answers})


def results(question_answers, results):
    qa_results = []
    for qa, result in zip(question_answers, results):
        qa_results.append({
            'question': qa.question,
            'result': result
        })
    return render(request, 'student_task_results.html', {'qa_results': qa_results, 'task': task})


@login_required
def all_results_view(request):
    # Get all tasks with their related results for the current user
    tasks_with_results = Task.objects.prefetch_related(
        Prefetch(
            'result_set',
            queryset=Result.objects.filter(student=request.user),
            to_attr='user_results'
        )
    )
    return render(request, 'all_results.html', {'tasks_with_results': tasks_with_results})


@login_required
def view_student_results(request, user_id):
    # Get all tasks with their related results for the specified user
    tasks_with_results = Task.objects.prefetch_related(
        Prefetch(
            'result_set',
            queryset=Result.objects.filter(student_id=user_id),
            to_attr='user_results'
        )
    )
    student = User.objects.get(id=user_id)
    return render(request, 'all_results.html', {'tasks_with_results': tasks_with_results, 'student': student})


def calculator_view(request):
    result = None
    if request.method == 'POST':
        form = CalculatorForm(request.POST)
        if form.is_valid():
            operand1 = form.cleaned_data.get('operand1')
            operator = form.cleaned_data.get('operator')
            operand2 = form.cleaned_data.get('operand2')

            if operator == '+':
                result = operand1 + operand2
            elif operator == '-':
                result = operand1 - operand2
            elif operator == '*':
                result = operand1 * operand2
            elif operator == '/':
                if operand2 != 0:
                    result = operand1 / operand2
                else:
                    result = 'Error: Division by zero'
    else:
        form = CalculatorForm()

    return render(request, 'calculator.html', {'form': form, 'result': result})

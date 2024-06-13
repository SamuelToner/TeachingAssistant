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
from django.db.models import Prefetch
from .forms import CalculatorForm
from django.http import HttpRequest, HttpResponse


class DeleteTaskView(UserPassesTestMixin, View):
    """
    View for deleting a task. Only accessible to users in the 'Teacher' group.
    """

    raise_exception = True

    def test_func(self) -> bool:
        """
        Check if the current user is in the 'Teacher' group.
        """
        task = get_object_or_404(Task, id=self.kwargs["task_id"])
        return self.request.user.groups.filter(name="Teacher").exists()

    def handle_no_permission(self) -> HttpResponse:
        """
        Render the 'protected.html' template if the user does not
        have permission.
        """
        return render(self.request, "protected.html")

    def get(self, request: HttpRequest, task_id: int) -> HttpResponse:
        """
        Render the 'delete_task.html' template for the given task.
        """
        task = get_object_or_404(Task, id=task_id)
        return render(request, "delete_task.html", {"task": task})

    def post(self, request: HttpRequest, task_id: int) -> HttpResponse:
        """
        Delete the given task and redirect to 'all_tasks'.
        """
        task = get_object_or_404(Task, id=task_id)
        task.delete()
        return redirect("all_tasks")


class DeleteUserView(UserPassesTestMixin, View):
    """
    View for deleting a user. Only accessible to users in the 'Teacher' group.
    """

    raise_exception = True

    def test_func(self) -> bool:
        """
        Check if the current user is in the 'Teacher' group.
        """
        return Group.objects.get(name="teacher")\
            in self.request.user.groups.all()

    def handle_no_permission(self) -> HttpResponse:
        """
        Render the 'protected.html' template if the user does not have
        permission.
        """
        return render(self.request, "protected.html")

    def get(self, request: HttpRequest, user_id: int) -> HttpResponse:
        """
        Render the 'delete_user.html' template for the given user.
        """
        user = get_object_or_404(User, id=user_id)
        return render(request, "delete_user.html", {"user": user})

    def post(self, request: HttpRequest, user_id: int) -> HttpResponse:
        """
        Delete the given user and redirect to 'user_list'.
        """
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return redirect("user_list")


# Welcome page after login
def index(request):
    return render(request, "index.html")


def __register(request):
    """
    View for user registration. If the form is valid,
    a new user is created and the user is redirected to the login page.
    Otherwise, the registration form is rendered.
    """
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Account created for {username}!")
            return redirect("login")
    else:
        form = UserRegisterForm()
    return render(request, "register.html", {"form": form})


def __login_view(request):
    """
    View for user login. If the form is valid and the user is authenticated,
    the user is logged in and redirected to the index page.
    Otherwise, an error message is displayed and the login form is rendered.
    """
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("index")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def __logout_view(request):
    """
    View for user logout. The user is logged out and
    redirected to the index page.
    """
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("index")


def __user_list(request):
    """
    View for displaying a list of all users. The list of users and a flag
    indicating whether the current user is a teacher are passed to the
    template.
    """
    users = User.objects.all()
    is_teacher = request.user.groups.filter(name="teacher").exists()
    return render(request, "users.html", {"users": users,
                                          "is_teacher": is_teacher})


def __edit_profile(request: HttpRequest) -> HttpResponse:
    """
    View for editing the profile of the current user. If the form is valid,
    the changes are saved and the user is redirected to the index.
    Otherwise, the form is rendered with the current user's
    data.
    """
    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = EditProfileForm(instance=request.user)
        args = {"form": form}
        return render(request, "edit_profile.html", args)


def __protected_view(request):
    """
    View for a protected page. If the user is not authenticated,
    they are redirected to the login page.
    Otherwise, the 'protected.html' template is rendered.
    """
    if not request.user.is_authenticated:
        return redirect("login")  # Redirect if user is not authenticated
    return render(request, "protected.html")


def __all_tasks(request):
    """
    View for displaying all tasks. The 'all_tasks.html'
    template is rendered with all tasks passed to it.
    """
    tasks = Task.objects.all()  # Get all tasks
    return render(request, "all_tasks.html", {"tasks": tasks})


def __add_task(request):
    """
    View for adding a task. If the form is valid,
    a new task is created along with its associated questions and answers.
    The user is then redirected to the view task page. Otherwise,
    the 'add_task.html' template is rendered.
    """
    if request.method == "POST":
        title = request.POST.get("title")
        questions = request.POST.getlist("question")
        answers = request.POST.getlist("answer")

        if title and questions and answers:
            task = Task(title=title)
            task.save()

            for question, answer in zip(questions, answers):
                if question and answer:  # Ensure question and answer not empty
                    qa = QuestionAnswer(task=task, question=question,
                                        answer=answer)
                    qa.save()

            return redirect("view_task", task_id=task.id)

    return render(request, "add_task.html")


@login_required
def __view_task(request, task_id):
    """
    View for a task. The 'view_task.html' template is rendered with the
    task and a flag indicating whether the current user is a teacher.
    """
    task = get_object_or_404(Task, pk=task_id)
    is_teacher = request.user.groups.filter(name="teacher").exists()
    return render(
        request,
        "view_task.html",
        {
            "task": task,
            "is_teacher": is_teacher,
        },
    )


def __edit_task(request, task_id):
    """
    View for editing a task. If the form is valid,
    the task and its associated questions and answers are updated.
    The user is then redirected to the view task page.
    Otherwise, the 'edit_task.html' template is rendered.
    """
    task = get_object_or_404(Task, id=task_id)
    question_answers = QuestionAnswer.objects.filter(task=task)
    if request.method == "POST":
        title = request.POST.get("title")
        questions = request.POST.getlist("question")
        answers = request.POST.getlist("answer")
        # Update the task record
        task.title = title
        task.save()
        # Update the QuestionAnswer records
        for qa, question, answer in zip(question_answers, questions, answers):
            qa.question = question
            qa.answer = answer
            qa.save()
        # Redirect to the view_post page
        return redirect("view_task", task_id=task.id)
    return render(
        request, "edit_task.html", {"task": task,
                                    "question_answers": question_answers}
    )


def __delete_task(request, task_id):
    """
    View for deleting a task. If the request method is POST,
    the task is deleted and the user is redirected to 'all_tasks'.
    Otherwise, the 'delete_task.html' template is rendered.
    """
    task = get_object_or_404(Task, id=task_id)
    if request.method == "POST":
        task.delete()
        return redirect("all_tasks")
    return render(request, "delete_task.html", {"task": task})


@login_required
def __student_task_view(request: HttpRequest, task_id: int) -> HttpResponse:
    """
    View for a student to view a task and submit answers.
    The student's answers are saved to the database and the
    'student_task_results.html' template is rendered, showing the student's
    results.
    """
    task = get_object_or_404(Task, id=task_id)
    question_answers = QuestionAnswer.objects.filter(task=task)
    if request.method == "POST":
        student_answers = request.POST.getlist("answer")
        qa_results = []
        for qa, student_answer in zip(question_answers, student_answers):
            result_text = (
                "Correct"
                if qa.answer.lower() == student_answer.lower()
                else "Incorrect"
            )
            qa_results.append({"question": qa.question, "result": result_text})
            # Save the result to the database
            Result.objects.create(
                task=task,
                student=request.user,
                question=qa.question,
                student_answer=student_answer,
                result=result_text,
            )
        return render(
            request,
            "student_task_results.html",
            {"qa_results": qa_results, "task": task},
        )
    return render(
        request,
        "student_task_view.html",
        {"task": task, "question_answers": question_answers},
    )


def __results(request, task, question_answers, results):
    """
    Function for creating a list of results for a task.
    The 'student_task_results.html' template is rendered with the
    results and the task.
    """
    qa_results = []
    for qa, result in zip(question_answers, results):
        qa_results.append({"question": qa.question, "result": result})
    return render(
        request, "student_task_results.html", {"qa_results": qa_results,
                                               "task": task}
    )


@login_required
def __all_results_view(request):
    """
    View for displaying all results for the current user.
    The 'all_results.html' template is rendered with all tasks
    and their related results.
    """
    tasks_with_results = Task.objects.prefetch_related(
        Prefetch(
            "result_set",
            queryset=Result.objects.filter(student=request.user),
            to_attr="user_results",
        )
    )
    return render(
        request, "all_results.html", {"tasks_with_results": tasks_with_results}
    )


@login_required
def __view_student_results(request, user_id):
    """
    View for displaying all results for a specified user.
    The 'all_results.html' template is rendered with all tasks and
    their related results for the user.
    """
    tasks_with_results = Task.objects.prefetch_related(
        Prefetch(
            "result_set",
            queryset=Result.objects.filter(student_id=user_id),
            to_attr="user_results",
        )
    )
    student = User.objects.get(id=user_id)
    return render(
        request,
        "all_results.html",
        {"tasks_with_results": tasks_with_results, "student": student},
    )


def __calculator_view(request):
    """
    View for a calculator. If the form is valid, a calculation is
    performed based on the form data and the result is displayed.
    Otherwise, the 'calculator.html' template is rendered with the form.
    """
    result = None
    if request.method == "POST":
        form = CalculatorForm(request.POST)
        if form.is_valid():
            operand1 = form.cleaned_data.get("operand1")
            operator = form.cleaned_data.get("operator")
            operand2 = form.cleaned_data.get("operand2")

            if operator == "+":
                result = operand1 + operand2
            elif operator == "-":
                result = operand1 - operand2
            elif operator == "*":
                result = operand1 * operand2
            elif operator == "/":
                if operand2 != 0:
                    result = operand1 / operand2
                else:
                    result = "Error: Division by zero"
    else:
        form = CalculatorForm()

    return render(request, "calculator.html", {"form": form, "result": result})

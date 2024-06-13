from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User, Group
from .models import Task, QuestionAnswer, Result
from .views import results


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.teacher_group = Group.objects.create(
            name="teacher"
        )  # Create 'Teacher' group here
        self.teacher_user = User.objects.create_user(
            username="teacher", password="password"
        )
        self.teacher_user.groups.add(self.teacher_group)
        self.task = Task.objects.create(title="Test Task")
        self.qa = QuestionAnswer.objects.create(
            task=self.task, question="Test Question", answer="Test Answer"
        )

    def test_delete_task_view(self):
        self.client.login(username="teacher", password="password")
        response = self.client.get(reverse("delete_task", args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "delete_task.html")

    def test_delete_user_view(self):
        self.client.login(username="teacher", password="password")
        response = self.client.get(reverse("delete_user", args=[self.teacher_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "delete_user.html")

    def test_all_tasks_view(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("all_tasks"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "all_tasks.html")

    def test_add_task_view(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.post(
            reverse("add_task"),
            {
                "title": "New Task",
                "question": ["Question 1", "Question 2"],
                "answer": ["Answer 1", "Answer 2"],
            },
        )
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertTrue(
            Task.objects.filter(title="New Task").exists()
        )  # Check if new task was created

    def test_view_task_view(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("view_task", args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "view_task.html")

    def test_edit_task_view(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.post(
            reverse("edit_task", args=[self.task.id]),
            {
                "title": "Updated Task",
                "question": ["Updated Question"],
                "answer": ["Updated Answer"],
            },
        )
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.task.refresh_from_db()
        self.assertEqual(
            self.task.title, "Updated Task"
        )  # Check if task title was updated
        self.qa.refresh_from_db()
        self.assertEqual(
            self.qa.question, "Updated Question"
        )  # Check if question was updated
        self.assertEqual(
            self.qa.answer, "Updated Answer"
        )  # Check if answer was updated

    def test_calculator_view_GET(self):
        response = self.client.get("/calculator/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "calculator.html")

    def test_student_task_view_GET(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("student_task_view", args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student_task_view.html")

    def test_student_task_view_POST_correct_answer(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.post(
            reverse("student_task_view", args=[self.task.id]),
            {"answer": ["Test Answer"]},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student_task_results.html")
        result = Result.objects.filter(task=self.task, student=self.user).first()
        self.assertEqual(result.result, "Correct")

    def test_student_task_view_POST_incorrect_answer(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.post(
            reverse("student_task_view", args=[self.task.id]),
            {"answer": ["Wrong Answer"]},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student_task_results.html")
        result = (
            Result.objects.filter(task=self.task, student=self.user)
            .order_by("-id")
            .first()
        )
        self.assertEqual(result.student_answer, "Wrong Answer")
        self.assertEqual(result.result, "Incorrect")

    def test_all_results_view(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("all_results_view"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "all_results.html")

    def test_view_student_results(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("view_student_results", args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "all_results.html")

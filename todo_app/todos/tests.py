from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Category, Task
from django.urls import reverse

settings.SECRET_KEY = "a-test-secret-key"


class CategoryViewTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            "user1", "user1@test.com", "password"
        )
        self.user2 = User.objects.create_user(
            "user2", "user2@test.com", "password"
        )
        self.category1 = Category.objects.create(title="User1 Category", user=self.user1)
        self.category2 = Category.objects.create(title="User2 Category", user=self.user2)

    def test_category_list_isolation(self):
        self.client.login(username="user1", password="password")
        response = self.client.get(reverse("todos:category_list"))
        self.assertContains(response, "User1 Category")
        self.assertNotContains(response, "User2 Category")

    def test_category_edit_isolation(self):
        self.client.login(username="user1", password="password")
        response = self.client.get(
            reverse("todos:category_edit", kwargs={"pk": self.category2.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_category_delete_isolation(self):
        self.client.login(username="user1", password="password")
        response = self.client.get(
            reverse("todos:category_delete", kwargs={"pk": self.category2.pk})
        )
        self.assertEqual(response.status_code, 404)


class TaskFormTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            "user1", "user1@test.com", "password"
        )
        self.user2 = User.objects.create_user(
            "user2", "user2@test.com", "password"
        )
        self.category1 = Category.objects.create(title="User1 Category", user=self.user1)
        self.category2 = Category.objects.create(title="User2 Category", user=self.user2)

    def test_task_form_category_queryset(self):
        self.client.login(username="user1", password="password")
        response = self.client.get(reverse("todos:task_add"))
        form = response.context["form"]
        self.assertIn(self.category1, form.fields["category"].queryset)
        self.assertNotIn(self.category2, form.fields["category"].queryset)

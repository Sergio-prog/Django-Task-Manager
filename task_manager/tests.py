import random
import uuid
from typing import Any

from django.test import TestCase

from task_manager.models import CustomUser, Task

# Create your tests here.
# TODO: Write tests

DEFAULT_PASSWORD = "L5Kr72Xb8i"
DEFAULT_TEST_USER = {"email": "example@example.com", "password": DEFAULT_PASSWORD, "username": "TestUser"}


def generate_user_data():
    return {
        "email": f"exampla{random.randint(1, 1000000)}@gmail.com",
        "password": DEFAULT_PASSWORD,
        "username": f"TestUser{random.randint(1, 1000000)}",
    }


def create_new_user(client, user_data: dict[str, str] | None = None):
    if not user_data:
        user_data = generate_user_data()

    response = client.post("/api/auth/signup/", data=user_data)
    response_body = response.json()

    return response_body


def generate_headers(access_token: str):
    return {"Authorization": "Bearer " + access_token}


class AuthorizationTest(TestCase):
    def test_register_function(self):
        response = self.client.post("/api/auth/signup/", data=DEFAULT_TEST_USER)
        response_body = response.json()

        self.assertEqual(response.status_code, 201)

        self.assertIsNotNone(response_body.get("tokens"))
        self.assertIsNotNone(response_body.get("user"))
        self.assertIsNotNone(response_body["tokens"].get("access_token"))

        self.assertEqual(CustomUser.objects.first().username, "TestUser")
        self.assertEqual(CustomUser.objects.first().email, "example@example.com")

    def test_register_with_simple_password(self):
        test_user_data = {"email": "example@example.com", "password": "12345678", "username": "TestUser"}

        error = {"password": ["This password is too common.", "This password is entirely numeric."]}
        response = self.client.post("/api/auth/signup/", data=test_user_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), error)

    def test_register_already_registered_user(self):
        response1 = self.client.post("/api/auth/signup/", data=DEFAULT_TEST_USER)
        self.assertEqual(response1.status_code, 201)

        error = {"username": ["This field must be unique."], "email": ["This field must be unique."]}
        response2 = self.client.post("/api/auth/signup/", data=DEFAULT_TEST_USER)
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(response2.json(), error)

    def test_refresh_token(self):
        response = self.client.post("/api/auth/signup/", data=DEFAULT_TEST_USER)
        response_body = response.json()

        self.assertEqual(response.status_code, 201)
        tokens = response_body["tokens"]
        refresh_token = tokens["refresh_token"]
        access_token = tokens["access_token"]

        refresh_data = {
            "refresh": refresh_token,
            "access": access_token,
        }

        response_refresh = self.client.post("/api/auth/refresh/", data=refresh_data)
        response_refresh_body = response_refresh.json()

        self.assertEqual(response_refresh.status_code, 200)
        self.assertNotEqual(response_refresh_body["access"], access_token)
        self.assertNotEqual(response_refresh_body["refresh"], refresh_token)

    def test_get_user(self):
        user = create_new_user(self.client)
        get_user_response = self.client.get("/api/users/", headers=generate_headers(user["tokens"]["access_token"]))
        get_user = get_user_response.json()

        self.assertEqual(get_user_response.status_code, 200)
        self.assertEqual(get_user, user["user"])

    # def test_refresh_token_with_token_another_user(self):
    #     fake_user = create_new_user(self.client)
    #
    #     true_user_response = self.client.post("/api/auth/signup/", data=DEFAULT_TEST_USER)
    #     true_user = true_user_response.json()
    #
    #     fake_data = {
    #         "refresh": fake_user["tokens"]["refresh_token"],
    #         "access": true_user["tokens"]["access_token"],
    #     }
    #
    #     response_refresh = self.client.post(
    #         "/api/auth/refresh/",
    #         data=fake_data
    #     )
    #     new_access = response_refresh.json()["access"]
    #
    #     headers = generate_headers(new_access)
    #     user = self.client.get("/api/users/", headers=headers).json()
    #     self.assertEqual(user["username"], true_user["user"]["username"])

    def test_login(self):
        user_data = generate_user_data()
        new_user = create_new_user(self.client, user_data)

        login_user = self.client.post("/api/auth/login/", data=user_data)
        login_user_body = login_user.json()

        self.assertEqual(login_user.status_code, 200)
        self.assertNotEqual(new_user["tokens"]["access_token"], login_user_body["access"])
        self.assertNotEqual(new_user["tokens"]["refresh_token"], login_user_body["refresh"])

    def test_login_to_undefined_account(self):
        new_user = create_new_user(self.client)

        login_to_undefined_user = self.client.post("/api/auth/login/", data=generate_user_data())
        login_user_data = login_to_undefined_user.json()

        self.assertEqual(login_to_undefined_user.status_code, 401)
        self.assertEqual(login_user_data, {"detail": "No active account found with the given credentials"})


class TasksTest(TestCase):
    def create_task(self, client, task_data: dict, access_token: str):
        headers = generate_headers(access_token)

        new_task = self.client.post("/api/tasks/", data=task_data, headers=headers)

        return new_task

    def create_task_shorter(self):
        new_user = create_new_user(self.client)

        access_token = new_user["tokens"]["access_token"]
        task_data = {
            "assigned_to_username": new_user["user"]["username"],
            "title": "Just a test task",
            "body": "Do not read this body. This is a test.",
            # "category_id": "",
            "priority": 0,
        }

        new_task = self.create_task(self.client, task_data, access_token)
        task_body = new_task.json()

        return task_body, access_token

    @staticmethod
    def compare_two_dicts(first: dict, second: dict):
        keys = first.keys()
        ...

    def test_create_new_task(self):
        new_user = create_new_user(self.client)

        access_token = new_user["tokens"]["access_token"]
        task_data = {
            "assigned_to_username": new_user["user"]["username"],
            "title": "Just a test task",
            "body": "Do not read this body. This is a test.",
            # "category_id": "",
            "priority": 0,
        }

        new_task = self.create_task(self.client, task_data, access_token)
        task_body = new_task.json()

        self.assertEqual(new_task.status_code, 201)
        self.assertEqual(task_body["title"], task_data["title"])
        self.assertEqual(task_body["body"], task_data["body"])
        self.assertEqual(task_body["priority"], task_data["priority"])

    def test_get_tasks(self):
        new_user = create_new_user(self.client)

        access_token = new_user["tokens"]["access_token"]
        task_data = {
            "assigned_to_username": new_user["user"]["username"],
            "title": "Just a test task",
            "body": "Do not read this body. This is a test.",
            # "category_id": "",
            "priority": 0,
        }

        headers = generate_headers(access_token)

        new_task = self.client.post("/api/tasks/", data=task_data, headers=headers)
        new_task2 = self.client.post("/api/tasks/", data=task_data, headers=headers)
        task_body = [new_task.json(), new_task2.json()]

        tasks_by_user = self.client.get("/api/tasks/", headers=headers)
        tasks_body = tasks_by_user.json()

        self.assertEqual(tasks_by_user.status_code, 200)
        self.assertEqual(len(tasks_body), 2)
        self.assertEqual(tasks_body, task_body)

    def test_create_category_and_task_with_it(self):
        new_user = create_new_user(self.client)

        access_token = new_user["tokens"]["access_token"]
        headers = generate_headers(access_token)

        category_data = {"name": "Test category"}

        new_category = self.client.post("/api/categories/", data=category_data, headers=headers)
        category_body = new_category.json()

        self.assertEqual(new_category.status_code, 201)

        expected_result = {
            **category_data,
            "id": category_body["id"],
            "creator": {
                "first_name": "",
                "last_name": "",
                "username": new_user["user"]["username"],
                "email": new_user["user"]["email"],
            },
        }
        self.assertEqual(category_body, expected_result)

        task_data = {
            "assigned_to_username": new_user["user"]["username"],
            "title": "Just a test task",
            "body": "Do not read this body. This is a test.",
            "category_id": int(category_body["id"]),
            "priority": 0,
        }

        new_task = self.client.post("/api/tasks/", data=task_data, headers=headers)
        new_task_body = new_task.json()
        self.assertEqual(new_task.status_code, 201)
        self.assertEqual(new_task_body["category"]["id"], category_body["id"])

    def test_complete_task(self):
        task_body, token = self.create_task_shorter()
        headers = generate_headers(token)

        expected_task = task_body
        expected_task["completed"] = True

        completed_task = self.client.post("/api/tasks/complete/", data={"task_id": task_body["id"]}, headers=headers)
        completed_task_body = completed_task.json()

        self.assertEqual(completed_task.status_code, 201)
        self.assertEqual(completed_task_body["completed"], expected_task["completed"])

        task_search = Task.objects.first()
        self.assertEqual(task_search.completed, True)

    def test_complete_task_two_times(self):
        pass

    def test_get_task(self):
        task_body, token = self.create_task_shorter()
        headers = generate_headers(token)

        get_task = self.client.get(f"/api/tasks/{task_body['id']}/", headers=headers)
        get_task_body = get_task.json()

        self.assertEqual(get_task.status_code, 200)
        self.assertEqual(get_task_body, task_body)

    def test_delete_task(self):
        task_body, token = self.create_task_shorter()
        headers = generate_headers(token)

        get_task = self.client.delete(f"/api/tasks/{task_body['id']}/", headers=headers)

        self.assertEqual(get_task.status_code, 200)
        task_search = Task.objects.all()
        self.assertEqual(len(task_search), 0)

    def test_update_task(self):
        task_body, token = self.create_task_shorter()
        headers = generate_headers(token)

        new_task = {**task_body, "priority": 2}

        completed_task = self.client.patch(
            f"/api/tasks/{task_body['id']}/", content_type="application/json", data=new_task, headers=headers
        )
        completed_task_body = completed_task.json()

        self.assertEqual(completed_task.status_code, 200)
        self.assertEqual(completed_task_body["priority"], new_task["priority"])

        task_search = Task.objects.first()
        self.assertEqual(int(task_search.priority), 2)

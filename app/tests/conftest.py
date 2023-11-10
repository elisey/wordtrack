import pytest
from django.contrib.auth.models import User
from django.db import connections
from django.test import Client


@pytest.fixture(scope="session")
def django_db_setup(django_db_blocker):
    with django_db_blocker.unblock():
        for alias in connections:
            connection = connections[alias]
            connection.creation.create_test_db(verbosity=1)
            connection.close()


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="testpassword")


@pytest.fixture
def logged_client(client, user):
    client.login(username="testuser", password="testpassword")
    return client

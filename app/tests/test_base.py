import datetime

import pytest
from django.urls import reverse

from app.models import Word


def test_dummy():
    assert 1 == 1


@pytest.mark.django_db
def test_index(logged_client):
    response = logged_client.get(reverse("index"))

    assert response.status_code == 200
    assert "Word Track" in response.content.decode("utf-8")


@pytest.mark.django_db
def test_random_word(logged_client, user):
    response = logged_client.get(reverse("get_word"))
    assert response.status_code == 404

    Word.objects.create(
        user_id=user.pk,
        native="native",
        foreign="foreign",
        status="NEW",
        last_repeated=datetime.date.today(),
        repeat_on=datetime.date.today(),
        learning_stage=0,
        repetition_period=0,
        next_repetition_direction="TO_NATIVE",
        group="some group",
    )
    response = logged_client.get(reverse("get_word"))
    assert response.status_code == 200
    assert response.json() == {
        "word_id": 1,
        "native": "native",
        "foreign": "foreign",
        "inverted": False,
        "repetition_period": 0,
        "commands": [
            {"text": "Не помню", "command_id": "LEARNING_HARD"},
            {"text": "Помню", "command_id": "LEARNING_NORMAL"},
            {"text": "Я его выучил", "command_id": "LEARNING_KNOW"},
            {"text": "Я его знаю, напомнить через месяц", "command_id": "LEARNING_AFTER_MONTH"},
            {"text": "Удалить", "command_id": "LEARNING_DELETE"},
        ],
    }

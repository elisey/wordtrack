import dataclasses
import json
import logging
import random

import pydantic
from django.conf import settings
from django.http import (
    FileResponse,
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import render
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET

from app.service import word_example
from app.service.commands import Command as CommandModel
from app.service.commands import Commands, apply_command
from app.service.learning_history import add_history_event
from app.service.speech import SpeechStorage
from app.service.today_page import get_today_page
from app.service.word import AlreadyExistsError, WordPicker


@require_GET
@cache_control(max_age=60 * 60 * 24, immutable=True, public=True)  # one day
def favicon(_: HttpRequest) -> FileResponse:
    """
    Serve favicon.

    from https://adamj.eu/tech/2022/01/18/how-to-add-a-favicon-to-your-django-site/
    """
    file = (settings.BASE_DIR / "data" / "favicon.png").open("rb")
    return FileResponse(file)


def index(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return HttpResponseRedirect("admin/login/?next=/")
    return render(request, "index.html")


def add_word_page(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return HttpResponseRedirect("admin/login/?next=/add_word")
    return render(request, "add_word.html")


class Command(pydantic.BaseModel):
    text: str
    command_id: str


class GetWordResponse(pydantic.BaseModel):
    word_id: int
    native: str
    foreign: str
    inverted: bool
    repetition_period: int
    commands: list[Command]


def get_word(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to access this page.")
    user_id = request.user.pk
    word_picker = WordPicker()

    if word := word_picker.get_word_for_learning(user_id):
        commands = Commands().create_commands(word)
        commands_response = [Command(text=command.text, command_id=command.command.value) for command in commands]
        inverted = word.is_inverted
    else:
        word = word_picker.get_any_word(user_id)
        commands_response = []
        inverted = random.choice([True, False, False])

    body = GetWordResponse(
        word_id=word.word_id,
        native=word.native,
        foreign=word.foreign,
        inverted=inverted,
        repetition_period=word.repetition_period,
        commands=commands_response,
    )

    return JsonResponse(body.model_dump())


class SendWordRequest(pydantic.BaseModel):
    word_id: int
    command_id: str


def send_answer(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to access this page.")

    user_id = request.user.pk
    body_str = request.body.decode("utf-8")
    body = json.loads(body_str)
    logging.info(body)
    data = SendWordRequest(**body)

    command = CommandModel(data.command_id)
    word_picker = WordPicker()
    word = word_picker.get_by_id(data.word_id, user_id)
    if word is None:
        return HttpResponse("Invalid word id", status=400)

    apply_command(command, word)
    word.save()
    add_history_event(user_id, data.word_id, command)
    return HttpResponse()


def add_word(request: HttpRequest) -> HttpResponse:
    if request.method != "POST":
        return HttpResponse("Invalid method", status=405)
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to access this page.")

    native = request.POST.get("native")
    foreign = request.POST.get("foreign")
    group = request.POST.get("group")

    if not native or not foreign or group is None:
        return HttpResponse("Both native and foreign parameters are required.", status=400)

    try:
        WordPicker().create_new(request.user.pk, native, foreign, group).save()
    except AlreadyExistsError:
        return HttpResponse("Word already exists.", status=400)

    return HttpResponseRedirect("add_word")


def get_audio(request: HttpRequest, word_id: int) -> HttpResponse:
    if request.method != "GET":
        return HttpResponse("Invalid method", status=405)
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to access this page.")

    word = WordPicker().get_by_id(word_id, request.user.pk)
    if word is None:
        return HttpResponse("Invalid word id", status=400)

    assert word.word_id

    audio_file = SpeechStorage(settings.AUDIO_FILES_DIR).get_audio(word.word_id, word.foreign)

    return HttpResponse(content=audio_file, content_type="audio/mp3")


def get_example(request: HttpRequest, word_id: int) -> HttpResponse:
    if request.method != "GET":
        return HttpResponse("Invalid method", status=405)
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to access this page.")

    word = WordPicker().get_by_id(word_id, request.user.pk)
    if word is None:
        return HttpResponse("Invalid word id", status=400)

    assert word.word_id

    result = word_example.get_example(word.foreign)
    if result is None:
        return HttpResponse("Error get an example", status=503)
    return HttpResponse(result)


def today_text(request: HttpRequest) -> HttpResponse:
    if request.method != "GET":
        return HttpResponse("Invalid method", status=405)
    if not request.user.is_authenticated:
        return HttpResponseRedirect("admin/login/?next=/today")
    today_page = get_today_page(request.user.pk)
    if today_page is None:
        return HttpResponse("Error generate the text", status=400)
    context = dataclasses.asdict(today_page)
    return render(request, "today.html", context)

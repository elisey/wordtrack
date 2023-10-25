import json

import pydantic
from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import render

from app.service import word_example
from app.service.commands import Command as CommandModel
from app.service.commands import Commands, apply_command
from app.service.speech import SpeechStorage
from app.service.word import AlreadyExists, ExerciseDirection, Status, WordPicker


def index(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to access this page.")
    return render(request, "index.html")


def add_word_page(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to access this page.")
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
    word_picker = WordPicker()
    word = word_picker.get_word_for_learning(request.user.pk)

    if not word:
        return HttpResponse("Done.")

    commands = Commands().create_commands(word)

    commands_response = []
    for command in commands:
        commands_response.append(Command(text=command.text, command_id=command.command.value))
    inverted = False
    if (word.status == Status.LEARN and word.learning_stage == 2) or (
        word.status == Status.REPEAT and word.next_repetition_direction == ExerciseDirection.TO_NATIVE
    ):
        inverted = True
    body = GetWordResponse(
        word_id=word.id,
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

    body_str = request.body.decode("utf-8")
    body = json.loads(body_str)
    print(body)
    data = SendWordRequest(**body)

    command = CommandModel(data.command_id)
    word_picker = WordPicker()
    word = word_picker.get_by_id(data.word_id, request.user.pk)
    if word is None:
        return HttpResponse("Invalid word id", status=400)

    apply_command(command, word)
    word.save()
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
    except AlreadyExists:
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

    assert word.id

    audio_file = SpeechStorage(settings.AUDIO_FILES_DIR).get_audio(word.id, word.foreign)

    return HttpResponse(content=audio_file, content_type="audio/mp3")


def get_example(request: HttpRequest, word_id: int) -> HttpResponse:
    if request.method != "GET":
        return HttpResponse("Invalid method", status=405)
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to access this page.")

    word = WordPicker().get_by_id(word_id, request.user.pk)
    if word is None:
        return HttpResponse("Invalid word id", status=400)

    assert word.id

    result = word_example.get_example(word.foreign)
    if result is None:
        return HttpResponse("Error get an example", status=503)
    return HttpResponse(result)

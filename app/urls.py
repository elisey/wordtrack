from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("add_word", views.add_word_page, name="add_word_page"),
    path("random_word", views.get_word, name="get_word"),
    path("send_answer", views.send_answer, name="send_answer"),
    path("word", views.add_word, name="add word"),
]

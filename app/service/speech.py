import pathlib

from google_speech import Speech  # type:ignore[import-untyped]


class SpeechStorage:
    def __init__(self, storage_pass: pathlib.Path) -> None:
        self._storage_pass = storage_pass

    def get_audio(self, item_id: int, word: str) -> bytes:
        file_path = self._generate_file_path(item_id)

        data = self._try_get_file(file_path)
        if not data:
            data = self._download_speech(word)
            self._save_file(file_path, data)
        return data

    def _generate_file_path(self, item_id: int) -> pathlib.Path:
        file_name = str(item_id) + ".mp3"
        return self._storage_pass / file_name

    def _try_get_file(self, file_path: pathlib.Path) -> bytes | None:
        if file_path.is_file():
            return file_path.read_bytes()
        return None

    def _download_speech(self, word: str) -> bytes:
        speech = Speech(word, "nl")

        data = bytearray()
        for segment in speech:
            d = segment.getAudioData()
            data = data + d
        return bytes(data)

    def _save_file(self, file_path: pathlib.Path, data: bytes) -> None:
        with open(file_path, "wb") as f:
            f.write(data)

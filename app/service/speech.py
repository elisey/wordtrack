import pathlib
import subprocess

from google_speech import Speech  # type:ignore[import-untyped]


class SpeechStorage:
    def play_audio(self, item_id: int, word: str) -> None:
        file_name = str(item_id) + ".mp3"
        data = self.try_get_file(file_name)
        if not data:
            data = self.download_speech(word)
            self._save_file(item_id, data)
        self.play(data)

    def try_get_file(self, file_name: str) -> bytes | None:
        path = pathlib.Path(__file__).parent / "data"

        file_path = path / file_name
        if file_path.is_file():
            return file_path.read_bytes()
        return None

    def download_speech(self, word: str) -> bytes:
        speech = Speech(word, "nl")

        data = bytearray()
        for segment in speech:
            d = segment.getAudioData()
            data = data + d
        return data

    def _save_file(self, item_id: int, data: bytes) -> None:
        path = pathlib.Path(__file__).parent / "data"
        file_name = str(item_id) + ".mp3"
        file_path = path / file_name
        with open(file_path, "wb") as f:
            f.write(data)

    def play(self, audio_data: bytes) -> None:
        cmd = ["sox", "-q", "-t", "mp3", "-"]

        cmd.extend(("-d", "trim", "0.1", "reverse", "trim", "0.07", "reverse"))  # "trim", "0.25", "-0.1"

        with subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL) as p:
            p.communicate(input=audio_data)
            if p.returncode != 0:
                raise RuntimeError()

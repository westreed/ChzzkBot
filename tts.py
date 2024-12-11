import os
from logging import getLogger

from google.cloud import texttospeech

from config import get_env
from manager import ConnectionManager

_log = getLogger(__name__)


def parsing_message(content: str) -> str:
    import re

    pattern = r'{:(.*?):}'
    matches = re.findall(pattern, content)
    if matches:
        for pat in matches:
            t = "{:" + pat + ":}"
            content = content.replace(t, "")

    return content.strip()


async def create_tts(user_id: str, content: str, manager: ConnectionManager) -> bool:
    gender = get_env("tts_gender") or "FEMALE"
    content = parsing_message(content)
    if content == "":
        return False

    client = texttospeech.TextToSpeechClient()
    text_length = len(content)
    max_length = 200 if get_env("tts_max_length") is None else int(get_env("tts_max_length"))

    if text_length > max_length:
        return False

    input_text = texttospeech.SynthesisInput(text=content)
    gender_info = {
        "MALE": {
            "name": "ko-KR-Neural2-C",
            "ssml_gender": texttospeech.SsmlVoiceGender.MALE,
            "pitch": 1.2
        },
        "FEMALE": {
            "name": "ko-KR-Neural2-A",
            "ssml_gender": texttospeech.SsmlVoiceGender.FEMALE,
            "pitch": 2.0
        }
    }

    # 오디오 설정 (예제에서는 한국어, 남성C)
    voice = texttospeech.VoiceSelectionParams(
        language_code="ko-KR",
        name=gender_info[gender]["name"],
        ssml_gender=gender_info[gender]["ssml_gender"],
    )

    speed = 1.5 if get_env("tts_speaking_rate") is None else float(get_env("tts_speaking_rate"))
    if get_env("tts_dynamic_speaking") == "true":
        thresholds = [(0.2, 0.0), (0.4, 0.2), (0.6, 0.4), (0.8, 0.6), (1.0, 1.0)]
        for threshold, addv in thresholds:
            value_at = max_length*threshold
            if text_length <= value_at:
                speed = min(addv+speed, 4.0)
                break

    pitch = gender_info[gender]["pitch"] if get_env("tts_pitch") is None else float(get_env("tts_pitch"))
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=speed,
        pitch=pitch
    )

    print(f"speed: {speed}, pitch: {pitch}")
    try:
        response = client.synthesize_speech(
            request={"input": input_text, "voice": voice, "audio_config": audio_config}
        )
    except Exception as e:
        _log.error(f"tts error: {e}")
        return False

    await manager.broadcast_tts(response.audio_content)
    return True

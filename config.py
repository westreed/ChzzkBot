import json
import os
import sys
from logging import getLogger

from utils import get_abs_path

_log = getLogger(__name__)


def is_blank(data: dict, key: str):
    if not data.get(key):
        return True
    return False


def load_config():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            data = json.loads(f.read())
            if is_blank(data, "channel_id"):
                raise NameError("config.json에서 'channel_id' 항목이 비어있거나 존재하지 않습니다.")
            os.environ["channel_id"] = data.get("channel_id")

            if is_blank(data, "google_json"):
                raise NameError("config.json에서 'google_json' 항목이 비어있거나 존재하지 않습니다.")
            google_api_path = get_abs_path(data.get("google_json"))
            if not os.path.exists(google_api_path):
                raise FileExistsError(f"config.json의 'google_json'에서 명시한 파일이 존재하지 않습니다! ({google_api_path})")
            _log.info(f"Google API Path: {google_api_path}")
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_api_path

            os.environ["is_login"] = "false"
            if not is_blank(data, "login"):
                login_data = data["login"]
                if not is_blank(login_data, "nid_aut") and not is_blank(login_data, "nid_ses"):
                    os.environ["is_login"] = "true"
                    os.environ["nid_aut"] = login_data.get("nid_aut")
                    os.environ["nid_ses"] = login_data.get("nid_ses")

            if not is_blank(data, "tts_option"):
                tts_data = data["tts_option"]
                if not is_blank(tts_data, "gender"):
                    tts_gender: str = tts_data.get("gender")
                    tts_gender = tts_gender.upper()
                    if tts_gender not in ["MALE", "FEMALE"]:
                        raise TypeError("config.json에서 gender는 'MALE' 혹은 'FEMALE'만 가능합니다.")
                    os.environ["tts_gender"] = tts_gender

                if not is_blank(tts_data, "speaking_rate"):
                    tts_speaking_rate = tts_data.get("speaking_rate")
                    float_speaking_rate = float(tts_speaking_rate)
                    if float_speaking_rate < 0.25 or float_speaking_rate > 4.00:
                        raise ValueError("config.json에서 speaking_rate는 0.25 ~ 4.00 사이의 값만 가질 수 있습니다.")
                    os.environ["tts_speaking_rate"] = str(tts_speaking_rate)

                if not is_blank(tts_data, "dynamic_speaking"):
                    tts_dynamic_speaking: str = tts_data.get("dynamic_speaking")
                    if tts_dynamic_speaking.lower() == "true":
                        os.environ["tts_dynamic_speaking"] = "true"
                    else:
                        os.environ["tts_dynamic_speaking"] = "false"

                if not is_blank(tts_data, "pitch"):
                    tts_pitch = tts_data.get("pitch")
                    float_pitch = float(tts_pitch)
                    if float_pitch < -20.00 or float_pitch > 20.00:
                        raise ValueError("config.json에서 pitch는 -20.00 ~ 20.00 사이의 값만 가질 수 있습니다.")
                    os.environ["tts_pitch"] = str(tts_pitch)

                if not is_blank(tts_data, "max_length"):
                    tts_max_length = tts_data.get("max_length")
                    int_max_length = min(int(tts_max_length), 100)
                    os.environ["tts_max_length"] = str(int_max_length)

                if not is_blank(tts_data, "volume"):
                    tts_volume = tts_data.get("volume")
                    float_volume = min(float(tts_volume), 1.0)
                    os.environ["tts_volume"] = str(float_volume)
                else:
                    os.environ["tts_volume"] = "1.0"

    except Exception as e:
        _log.error(e)
        input("Press Enter to exit...")
        sys.exit(1)


def get_env(key: str):
    return os.environ.get(key)


if __name__ == "__main__":
    load_config()

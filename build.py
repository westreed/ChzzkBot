import os
import shutil
import subprocess
import zipfile
from zipfile import ZipFile

readme_content = """config.json 가이드

# channel_id

적용하고자 하는 방송의 채널 ID를 작성해야 합니다. 라이브 방송으로 들어가서, 방송주소를 보면 https://chzzk.naver.com/live/{채널ID} 이런 형식인데 live/ 뒤에 있는 값이 본인의 채널 ID입니다.
 
# login

로그인을 위해서는 치지직에 로그인된 브라우저에서 관리자도구 - 애플리케이션 - 쿠키에서 [NID_AUT], [NID_SES] 쿠키 정보가 필요합니다.
자세한 정보는 깃허브에 있습니다.

# google_json

google tts api를 사용하기 위해, 다운로드 받았던 json 파일을 Chzzk TTS BOT.exe가 있는 폴더 안으로 옮기고 해당 json 파일명을 작성합니다.

# tts option
- gender: "MALE", "FEMALE" 둘중 하나 선택
- speaking_rate: 0.25 ~ 4.00 (default: 1.00)
- dynamic_speaking: "true" or "false", 설정할 경우 채팅 내용이 길수록 빠르게 읽어줍니다.
- pitch: -20.00 ~ 20.00 (default: 0.00)
- max_length: 허용하고 싶은 채팅의 최대 길이, 최대 100자 (default: 100)
"""

confing_json = """{
    "channel_id": "",
    "login": {
        "nid_aut": "",
        "nid_ses": ""
    },
    "google_json": "",
    "tts_option": {
        "gender": "FEMALE",
        "speaking_rate": 1,
        "dynamic_speaking": "true",
        "pitch": 1,
        "max_length": 200
    }
}"""


def build(spec_name: str):
    try:
        venv_cmd = "./venv/Scripts/pyinstaller"
        subprocess.run([venv_cmd, spec_name])
        return
    except:
        pass

    try:
        global_cmd = "pyinstaller"
        subprocess.run([global_cmd, spec_name])
        return
    except:
        pass

    raise EnvironmentError(f"pyinstaller가 설치되어 있지 않습니다.")


def zip_folder(zipf: ZipFile, temp_path: str, folder_path: str):
    rel_path = os.path.join(temp_path, folder_path)
    for root, dirs, files in os.walk(rel_path):
        for file in files:
            # 파일의 전체 경로
            file_path = os.path.join(root, file)
            # 파일을 ZIP에 추가하되, ZIP 내부 경로는 루트 폴더에서의 상대 경로로 설정
            arcname = os.path.join(folder_path, file)
            zipf.write(file_path, arcname)



def compress():
    temp_path = "chzzk-bot"
    output_path = "output"

    readme_name = "README.txt"
    zip_name = "chzzk-tts-bot.zip"
    config_name = "config.json"
    build_name = "ChzzkBot.exe"

    if not os.path.exists(temp_path):
        os.mkdir(temp_path)

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    # copy build file
    shutil.copytree(f"static", f"{temp_path}/static")
    shutil.copytree(f"templates", f"{temp_path}/templates")
    shutil.copy(f"dist/{build_name}", f"{temp_path}/{build_name}")

    # create README.txt
    with open(f"{temp_path}/{readme_name}", "w", encoding="utf-8") as f:
        f.write(readme_content)

    with open(f"{temp_path}/{config_name}", "w", encoding="utf-8") as f:
        f.write(confing_json)

    # compress
    with ZipFile(f"{output_path}/{zip_name}", 'w', zipfile.ZIP_DEFLATED) as zipf:
        zip_folder(zipf, temp_path, "static")
        zip_folder(zipf, temp_path, "templates")
        zipf.write(f"{temp_path}/{build_name}", arcname=build_name)
        zipf.write(f"{temp_path}/{readme_name}", arcname=readme_name)
        zipf.write(f"{temp_path}/{config_name}", arcname=config_name)

    # remove temp
    shutil.rmtree(temp_path, onerror=lambda x: print(x))


if __name__ == "__main__":
    build("app.spec")
    compress()

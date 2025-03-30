import os
import zipfile
import subprocess
import re
import shutil

EXE_NAME = "염색도우미.exe"
DIST_FOLDER_NAME = "염색도우미"
DIST_DIR = os.path.join("dist", DIST_FOLDER_NAME)
TXT_NAME = "사용법.txt"
ICON_NAME = "icon.png"
SPEC_NAME = "염색도우미.spec"

# VERSION 문자열 추출 함수
def extract_version():
    with open("main.py", encoding="utf-8") as f:
        for line in f:
            match = re.search(r'VERSION\s*=\s*["\'](.+?)["\']', line)
            if match:
                return match.group(1)
    return "v0.0.0"

VERSION = extract_version()
OUTPUT_ZIP = f"{DIST_FOLDER_NAME}_{VERSION}.zip"

# 1. PyInstaller 빌드 실행
print(f"[빌드] PyInstaller 실행 중... (버전: {VERSION})")
subprocess.run(["pyinstaller", "--noconfirm", SPEC_NAME], check=True)

# 2. 빌드 확인
if not os.path.exists(DIST_DIR):
    raise FileNotFoundError(f"{DIST_DIR} 빌드 실패. .spec 파일 확인 필요")

# 3. 사용법.txt 및 기타 리소스 복사
for file in [TXT_NAME, ICON_NAME]:
    if os.path.exists(file):
        shutil.copy(file, os.path.join(DIST_DIR, file))

# 4. 압축 생성
print(f"[패킹] {OUTPUT_ZIP} 압축 생성 중...")
with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, _, files in os.walk(DIST_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, os.path.dirname(DIST_DIR))
            zipf.write(full_path, arcname=rel_path)

print(f"✅ 빌드 및 압축 완료: {OUTPUT_ZIP}")

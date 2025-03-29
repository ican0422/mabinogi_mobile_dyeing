import os
import zipfile
import subprocess

EXE_NAME = "염색도우미.exe"
TXT_NAME = "사용법.txt"
OUTPUT_ZIP = "염색도우미.zip"

# 1. PyInstaller 빌드 실행
print("[빌드] PyInstaller 실행 중...")
subprocess.run(["pyinstaller", "염색도우미.spec"], check=True)

# 2. dist 폴더 확인 및 파일 경로 설정
exe_path = os.path.join("dist", EXE_NAME)
txt_path = TXT_NAME

if not os.path.exists(exe_path):
    raise FileNotFoundError(f"{exe_path} 빌드 실패. .spec 확인 필요")
if not os.path.exists(txt_path):
    raise FileNotFoundError(f"{txt_path} 파일이 존재하지 않습니다")

# 3. zip 생성
print(f"[패킹] {OUTPUT_ZIP} 압축 생성 중...")
with zipfile.ZipFile(OUTPUT_ZIP, "w") as zipf:
    zipf.write(exe_path, arcname=EXE_NAME)
    zipf.write(txt_path, arcname=TXT_NAME)

print(f"✅ 빌드 및 압축 완료: {OUTPUT_ZIP}")

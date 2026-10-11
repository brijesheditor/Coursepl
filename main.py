import os
import asyncio
import time
import re
from datetime import datetime
from config import *
from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

# --- AES Encryption ---
def aes_encrypt_auto_prefix(data: str) -> str:
    try:
        key = b'ThisIsASecretKey'
        cipher = AES.new(key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
        encrypted_data = base64.b64encode(cipher.iv + ct_bytes).decode('utf-8')
        return encrypted_data
    except Exception as e:
        return data

# --- Player URL Generator ---
def get_player_url(url: str) -> str:
    if "drm" in url and "playlist.m3u8" in url:
        encrypted = aes_encrypt_auto_prefix(url)
        return f"https://itsgolu-v1player.vercel.app/?url={encrypted}"
    elif 'zip' in url:
        return f'https://video.pablocoder.eu.org/appx-zip?url={url}'
    elif 'brightcove' in url:
        bcov = 'bcov_auth=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3Mjg3MDIyMDYsImNvbiI6eyJpc0FkbWluIjpmYWxzZSwiYXVzZXIiOiJVMFZ6TkdGU2NuQlZjR3h5TkZwV09FYzBURGxOZHowOSIsImlkIjoiT0dweFpuWktabVl3WVdwRlExSXJhV013WVdvMlp6MDkiLCJmaXJzdF9uYW1lIjoiU0hCWVJFc3ZkbVJ0TVVSR1JqSk5WamN3VEdoYVp6MDkiLCJlbWFpbCI6ImNXbE5NRTVoTUd4NloxbFFORmx4UkhkWVV6bFhjelJTWWtwSlVVcHNSM0JDVTFKSWVGQXpRM2hsT0QwPSIsInBob25lIjoiYVhReWJ6TTJkWEJhYzNRM01uQjZibEZ4ZGxWR1p6MDkiLCJhdmF0YXIiOiJLM1ZzY1M4elMwcDBRbmxrYms4M1JEbHZla05pVVQwOSIsInJlZmVycmFsX2NvZGUiOiJla3RHYjJoYWRtcENXSFo0YTFsV2FEVlBaM042ZHowOSIsImRldmljZV90eXBlIjoiYW5kcm9pZCIsImRldmljZV92ZXJzaW9uIjoidXBwZXIgdGhhbiAzMSIsImRldmljZV9tb2RlbCI6IlhpYW9NaSBNMjAwN0oxN0MiLCJyZW1vdGVfYWRkciI6IjQ0LjIyMi4yNTMuODUifX0.k_419KObeIVpLO6BqHcg8MpnvEwDgm54UxPnY7rTUEu_SIjOaE7FOzez5NL9LS7LdI_GawTeibig3ILv5kWuHhDqAvXiM8sQpTkhQoGEYybx8JRFmPw_fyNsiwNxTZQ4P4RSF9DgN_yiQ61aFtYpcfldT0xG1AfamXK4JlneJpVOJ8aG_vOLm6WkiY-XG4PCj5u4C3iyur0VM1-j-EhwHmNXVCiCz5weXDsv6ccV6SqNW2j_Cbjia16ghgX61XeIyyEkp07Nyrp7GN4eXuxxHeKcoBJB-YsQ0OopSWKzOQNEjlGgx7b54BkmU8PbiwElYgMGpjRT9bLTf3EYnTJ_wA'
        return url.split("bcov_auth")[0] + bcov
    elif 'utkarsh' in url:
        return url
    else:
        return f'https://itsgolu-v1player.vercel.app/?url={url}'

client = Client("itsgolu_html_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@client.on_message(filters.command("start") & filters.private)
async def start_command(_, message: Message):
    await message.reply_text(
        f"🎐 **Welcome {message.from_user.first_name}!**\n"
        "✨ **TXT ➝ HTML Bot** ✨\n"
        "📌 **Features:**\n"
        "• Pro Sidebar Layout\n"
        "• Fixed Grid & Index\n"
        "• In-App Player (No new tab)\n"
        "• Smart Search\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🎨 **Themes:**\n"
        "🔓 /modern → Pro Sidebar (Fixed)\n"
        "🔓 /neumorphic → Soft Grey\n"
        "🔓 /brutalist → Bold & Raw\n"
        "🔓 /glassmorphism → Glass Effect\n"
        "🔓 /cyberpunk → Neon Tech\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "👑 By: [ITsGOlU](https://t.me/ITSGOLU_OFFICIAL)"
    )

@client.on_message(filters.command("neumorphic") & filters.private)
async def cmd_neumorphic(client, message: Message): await process_txt_to_html(client, message, "neumorphic")
@client.on_message(filters.command("brutalist") & filters.private)
async def cmd_brutalist(client, message: Message): await process_txt_to_html(client, message, "brutalist")
@client.on_message(filters.command("modern") & filters.private)
async def cmd_modern(client, message: Message): await process_txt_to_html(client, message, "modern")
@client.on_message(filters.command("glassmorphism") & filters.private)
async def cmd_glassmorphism(client, message: Message): await process_txt_to_html(client, message, "glassmorphism")
@client.on_message(filters.command("cyberpunk") & filters.private)
async def cmd_cyberpunk(client, message: Message): await process_txt_to_html(client, message, "cyberpunk")

async def process_txt_to_html(client: Client, message: Message, theme: str):
    user_id = message.from_user.id
    await message.reply(f"🕹️ **Generating `{theme}`...**\n📤 Please send `.txt` file.")
    try:
        msg: Message = await client.listen(user_id, timeout=300)
    except asyncio.TimeoutError:
        await message.reply("⏰ Timeout!")
        return

    if not msg.document or not msg.document.file_name.endswith(".txt"):
        await msg.reply("❌ Only `.txt` files allowed.")
        return

    file_path = await msg.download()
    # Fix Filename
    original_name = msg.document.file_name.replace(".txt", "")
    output_path = f"{original_name}_{user_id}.html" 
    await msg.reply("⏳ Processing...")

    try:
        if theme == "neumorphic": await extract_links_neumorphic(file_path, output_path)
        elif theme == "brutalist": await extract_links_brutalist(file_path, output_path)
        elif theme == "modern": await extract_links_modern_dark(file_path, output_path)
        elif theme == "glassmorphism": await extract_links_glassmorphism(file_path, output_path)
        elif theme == "cyberpunk": await extract_links_cyberpunk(file_path, output_path) # FIXED TYPO
        else: raise ValueError("Invalid theme")

        await msg.reply_document(document=output_path, file_name=f"{original_name}.html", caption=f"✅ Theme: `{theme}` | By ITsGOlU")
    except Exception as e:
        await msg.reply(f"❌ Error: `{str(e)}`")
    finally:
        for f in [file_path, output_path]:
            if os.path.exists(f): os.remove(f)

# --- Common Parsing ---
def parse_line(line):
    line = line.strip()
    if ':' not in line: return None
    title_part, url = line.split(':', 1)
    title_part = title_part.strip()
    url = url.strip()
    
    subject = "General"
    category = None
    clean_title = title_part

    matches = re.findall(r'\[([^\]]+)\]|\(([^)]+)\)', title_part)
    if matches:
        subject = matches[0][0] if matches[0][0] else matches[0][1]
        subject = subject.strip()
        if len(matches) > 1:
            category = matches[1][0] if matches[1][0] else matches[1][1]
            category = category.strip()
        clean_title = re.sub(r'\[([^\]]+)\]|\(([^)]+)\)', '', title_part).strip()

    is_pdf = '.pdf' in url.lower()
    is_image = any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp'])
    
    return {
        "subject": subject,
        "category": category,
        "title": clean_title,
        "url": url,
        "is_pdf": is_pdf,
        "is_image": is_image
    }

# --- Common JS (Modal Player & Search) ---
COMMON_JS = """
<script>
    // Tab Switching
    function showContent(tabName) {
        document.querySelectorAll('.content-section').forEach(s=>s.classList.remove('active'));
        document.querySelectorAll('.nav-item, .tab').forEach(t=>t.classList.remove('active'));
        document.getElementById(tabName).classList.add('active');
        if(event && event.target) event.target.classList.add('active');
        
        // Update breadcrumbs
        const breadcrumb = document.querySelector('.breadcrumb span.active');
        if(breadcrumb) breadcrumb.textContent = tabName.charAt(0).toUpperCase() + tabName.slice(1);
    }
    
    // Toggle Folders (Subjects)
    function toggleVideos(subject) {
        const el = document.getElementById(subject);
        const icon = el.previousElementSibling.querySelector('.fa-chevron-down');
        if(el.classList.toggle('active')){
            icon.style.transform = 'rotate(180deg)';
        } else {
            icon.style.transform = 'rotate(0deg)';
        }
    }

    // --- SEARCH LOGIC ---
    function searchContent() {
        var input = document.getElementById('searchInput');
        var filter = input.value.toLowerCase();
        var items = document.querySelectorAll('.searchable-item');
        var subjects = document.querySelectorAll('.subject-card');

        // Reset all visibility first
        subjects.forEach(sub => sub.style.display = '');

        items.forEach(function(item) {
            var text = item.textContent || item.innerText;
            if (text.toLowerCase().indexOf(filter) > -1) {
                item.style.display = ""; // Show item
            } else {
                item.style.display = "none"; // Hide item
            }
        });

        // Smart Hide: If a subject has no visible items, hide subject too
        subjects.forEach(function(subject) {
            var listId = subject.getAttribute('onclick').match(/'([^']+)'/)[1];
            var list = document.getElementById(listId);
            var visibleItems = list.querySelectorAll('.searchable-item[style=""]');
            var hasVisibleItems = false;
            
            visibleItems.forEach(function(i) {
                if(i.offsetParent !== null) hasVisibleItems = true;
            });

            if (filter !== "" && !hasVisibleItems && subject.textContent.toLowerCase().indexOf(filter) === -1) {
                subject.style.display = "none";
            } else if (filter === "") {
                subject.style.display = ""; 
            }
        });
    }

    // --- VIDEO PLAYER MODAL ---
    function openPlayer(url) {
        document.getElementById('playerModal').style.display = "flex";
        document.getElementById('videoFrame').src = url;
    }
    function closePlayer() {
        document.getElementById('playerModal').style.display = "none";
        document.getElementById('videoFrame').src = "";
    }

    // PDF Viewer
    function openPdf(url) {
        document.getElementById('pdfModal').style.display = "flex";
        document.getElementById('pdfFrame').src = "https://mozilla.github.io/pdf.js/web/viewer.html?file=" + encodeURIComponent(url);
    }
    function closePdf() {
        document.getElementById('pdfModal').style.display = "none";
        document.getElementById('pdfFrame').src = "";
    }
    
    // Mobile Sidebar
    function toggleSidebar() {
        document.getElementById('sidebar').classList.toggle('active');
    }
</script>
"""

COMMON_PLAYER_MODAL = """
<div id="playerModal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.9);z-index:9999;align-items:center;justify-content:center;">
    <div style="position:absolute;top:20px;right:20px;z-index:10000;">
        <button onclick="closePlayer()" style="background:#ef4444;color:white;border:none;padding:10px 20px;border-radius:8px;cursor:pointer;font-size:18px;font-weight:bold;">✕ Close Player</button>
    </div>
    <iframe id="videoFrame" style="width:100%;height:100%;border:none;max-width:1200px;max-height:80vh;" allowfullscreen></iframe>
</div>
"""

COMMON_PDF_MODAL = """
<div id="pdfModal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.95);z-index:9999;flex-direction:column;align-items:center;justify-content:center;">
    <button onclick="closePdf()" style="position:absolute;top:20px;right:20px;z-index:10000;background:#ef4444;color:white;border:none;padding:10px 20px;border-radius:8px;cursor:pointer;font-weight:bold;">✕ Close PDF</button>
    <iframe id="pdfFrame" style="width:95%;height:95%;border:none;background:white;"></iframe>
</div>
"""

# --- THEME 1: MODERN DARK (FIXED SIDEBAR & LAYOUT) ---
async def extract_links_modern_dark(input_file, output_file):
    video_links_by_subject = {}
    pdf_links = []
    image_links = []
    
    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            data = parse_line(line)
            if not data: continue
            if data['is_pdf']: pdf_links.append(data)
            elif data['is_image']: image_links.append(data)
            else:
                sub = data['subject']
                if sub not in video_links_by_subject: video_links_by_subject[sub] = []
                video_links_by_subject[sub].append(data)

    total_videos = sum(len(v) for v in video_links_by_subject.values())
    total_pdfs = len(pdf_links)
    total_images = len(image_links)

    # Fixed CSS for Grid and Sidebar
    html_content = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>ITsGOlU Viewer</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><style>
        :root {{ --primary: #6366f1; --primary-dark: #4f46e5; --secondary: #ec4899; --bg-main: #0f172a; --bg-secondary: #1e293b; --bg-card: #1e293b; --text-primary: #f1f5f9; --text-secondary: #94a3b8; --border: #334155; --sidebar-width: 260px; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg-main); color: var(--text-primary); }}
        
        /* Sidebar */
        .sidebar {{ position: fixed; left: 0; top: 0; width: var(--sidebar-width); height: 100vh; background: var(--bg-secondary); border-right: 1px solid var(--border); padding: 20px; overflow-y: auto; transition: transform 0.3s ease; z-index: 100; }}
        .sidebar-header {{ margin-bottom: 30px; }}
        .logo {{ font-size: 1.5rem; font-weight: 800; color: white; text-decoration: none; display: ab flex; align-items: center; gap: 10px; }} /* Fixed Brand */
        .logo i {{ color: var(--primary); }} 
        .stats-sidebar {{ display: flex; flex-direction: column; gap: 12px; margin-bottom: 25px; }}
        .stat-card {{ background: linear-gradient(135deg, var(--primary), var(--secondary)); padding: 15px; border-radius: 12px; display: flex; align-items: center; gap: 12px; }}
        .stat-icon {{ font-size: 1.8rem; opacity: 0.9; color: white; }}
        .stat-info {{ flex: 1; }}
        .stat-num {{ font-size: 1.5rem; font-weight: 700; color: white; }}
        .stat-label {{ font-size: 0.75rem; color: rgba(255,255,255,0.8); text-transform: uppercase; }}
        .menu {{ list-style: none; }}
        .menu-item {{ padding: 12px 15px; border-radius: 10px; margin-bottom: 5px; cursor: pointer; transition: all 0.3s; display: flex; align-items: center; gap: 12px; color: var(--text-secondary); }}
        .menu-item:hover, .menu-item.active {{ background: var(--bg-card); color: var(--primary); }}
        
        /* Main Content */
        .main-content {{ margin-left: var(--sidebar-width); padding: 30px; min-height: 100vh; }} /* Fixed Margin */
        .top-bar {{ background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 15px; padding: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; gap: 20px; flex-wrap: wrap; }}
        .breadcrumb {{ display: flex; gap: 8px; align-items: center; color: var(--text-secondary); font-size: 1.1rem; font-weight: 600; }}
        .search-container {{ flex: 1; max-width: 400px; }}
        #searchInput {{ width: 100%; padding: 12px 45px 12px 20px; border: 1px solid var(--border); border-radius: 25px; background: var(--bg-card); color: var(--text-primary); outline: none; }}
        #searchInput:focus {{ border-color: var(--primary); }}
        
        /* Grid & Cards */
        .content-section {{ display: none; }}
        .content-section.active {{ display: block; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }} /* Fixed Grid */
        .subject-card {{ background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; cursor: pointer; transition: all 0.3s; display: flex; justify-content: space-between; align-items: center; }}
        .subject-card:hover {{ transform: translateY(-3px); border-color: var(--primary); }}
        .subject-title {{ font-size: 1.1rem; font-weight: 600; color: var(--text-primary); }}
        .subject-count {{ background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; border-radius: 20px; padding: 4px 12px; font-size: 0.8rem; font-weight: 600; }}
        .video-grid {{ display: none; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }} /* Corrected Video Grid */
        .video-grid.active {{ display: grid; }}
        
        /* Video Card with Player Button */
        .card {{ background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 15px; display: flex; align-items: center; gap: 15px; text-decoration: none; color: var(--text-primary); transition: all 0.3s; position: relative; }}
        .card:hover {{ border-color: var(--primary); transform: translateY(-3px); }}
        .card-icon {{ width: 36px; height: 36px; background: linear-gradient(135deg, var(--primary), var(--secondary)); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; flex-shrink: 0; }}
        .card-content {{ flex: 1; overflow: hidden; }}
        .card-title {{ font-weight: 500; font-size: 0.95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .card-meta {{ color: var(--text-secondary); font-size: 0.75rem; }}
        .play-btn {{ background: var(--primary); color: white; padding: 5px 10px; border-radius: 6px; font-size: 0.8rem; cursor: pointer; border: none; }}
        .pdf-btn {{ background: var(--secondary); color: white; padding: 5px 10px; border-radius: 6px; font-size: 0.8rem; cursor: pointer; border: none; }}
        
        /* Mobile */
        .mobile-toggle {{ display: none; position: fixed; bottom: 20px; right: 20px; width: 50px; height: 50px; background: linear-gradient(135deg, var(--primary), var(--secondary)); border-radius: 50%; align-items: center; justify-content: center; color: white; font-size: 1.3rem; cursor: pointer; z-index: 101; }}
        @media (max-width: 968px) {{ .sidebar {{ transform: translateX(-100%); }} .sidebar.active {{ transform: translateX(0); }} .main-content {{ margin-left: 0; }} .mobile-toggle {{ display: flex; }} }}
    </style></head><body>
    <div class="sidebar" id="sidebar">
        <div class="sidebar-header"><a href="#" class="logo"><i class="fas fa-code"></i> ITsGOlU</a></div> <!-- Fixed Brand Name -->
        <div class="stats-sidebar">
            <div class="stat-card"><div class="stat-icon"><i class="fas fa-video"></i></div><div class="stat-info"><div class="stat-num">{total_videos}</div><div class="stat-label">Videos</div></div></div>
            <div class="stat-card"><div class="stat-icon"><i class="fas fa-file-pdf"></i></div><div class="stat-info"><div class="stat-num">{total_pdfs}</div><div class="stat-label">PDFs</div></div></div>
            <div class="stat-card"><div class="stat-icon"><i class="fas fa-image"></i></div><div class="stat-info"><div class="stat-num">{total_images}</div><div class="stat-label">Images</div></div></div>
        </div>
        <ul class="menu">
            <li class="menu-item active" onclick="showContent('videos')"><i class="fas fa-play"></i> Videos</li>
            <li class="menu-item" onclick="showContent('pdfs')"><i class="fas fa-file-pdf"></i> PDFs</li>
            <li class="menu-item" onclick="showContent('images')"><i class="fas fa-image"></i> Images</li>
        </ul>
    </div>
    <div class="mobile-toggle" onclick="toggleSidebar()"><i class="fas fa-bars"></i></div>
    <div class="main-content">
        <div class="top-bar">
            <div class="breadcrumb"><span class="active">Videos</span></div>
            <div class="search-container"><input type="text" id="searchInput" placeholder="Search content..." onkeyup="searchContent()"></div>
        </div>
        
        <section id="videos" class="content-section active"><div class="grid">"""
    for sub, vids in video_links_by_subject.items():
        html_content += f'<div class="subject-card" onclick="toggleVideos(\'{sub}\')"><div class="subject-title">{sub}</div><div class="subject-count"><span style="margin-right:5px">{len(vids)}</span><i class="fas fa-chevron-down" style="font-size:0.8rem;transition:0.3s"></i></div></div><div id="{sub}" class="video-grid">'
        for v in vids: 
            p_url = get_player_url(v['url'])
            cat = f"• {v['category']}" if v['category'] else ""
            html_content += f'<div class="card searchable-item"><div class="card-icon"><i class="fas fa-play"></i></div><div class="card-content"><div class="card-title">{v["title"]}</div><div class="card-meta">Video {cat}</div></div><button class="play-btn" onclick="openPlayer(\'{p_url}\')">▶ Play</button></div>'
        html_content += '</div>'
    html_content += """</div></section>
        
        <section id="pdfs" class="content-section"><div class="grid">"""
    for p in pdf_links:
        html_content += f'<div class="card searchable-item"><div class="card-icon"><i class="fas fa-file-pdf"></i></div><div class="card-content"><div class="card-title">{p["title"]}</div><div class="card-meta">PDF Document</div></div><button class="pdf-btn" onclick="openPdf(\'{p["url"]}\')">View</button></div>'
    html_content += """</div></section>
        
        <section id="images" class="content-section"><div class="grid">"""
    for i in image_links:
        html_content += f'<a href="{i["url"]}" target="_blank" class="card searchable-item"><div class="card-icon"><i class="fas fa-image"></i></div><div class="card-content"><div class="card-title">{i["title"]}</div><div class="card-meta">Image</div></div></a>'
    html_content += f"""</div></section>
    </div>
    {COMMON_PLAYER_MODAL}{COMMON_PDF_MODAL}{COMMON_JS}
    </body></html>"""
    with open(output_file, 'w', encoding='utf-8') as file: file.write(html_content)

# --- THEME 2: NEUMORPHIC ---
async def extract_links_neumorphic(input_file, output_file):
    video_links_by_subject = {}
    pdf_links = []
    image_links = []
    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            data = parse_line(line)
            if not data: continue
            if data['is_pdf']: pdf_links.append(data)
            elif data['is_image']: image_links.append(data)
            else:
                sub = data['subject']
                if sub not in video_links_by_subject: video_links_by_subject[sub] = []
                video_links_by_subject[sub].append(data)
    total_videos = sum(len(v) for v in video_links_by_subject.values())
    
    html_content = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>ITsGOlU</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"><style>
        :root {{ --bg: #e0e5ec; --card: #e0e5ec; --text: #4a5568; --accent: #6c5ce7; --shadow-light: #ffffff; --shadow-dark: #a3b1c6; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }}
        body {{ background: var(--bg); color: var(--text); padding: 20px; min-height: 100vh; }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        h1 {{ font-size: 2.5rem; color: var(--accent); }}
        #searchInput {{ width: 100%; max-width: 400px; padding: 15px 25px; border-radius: 50px; border: none; outline: none; background: var(--card); box-shadow: 6px 6px 12px var(--shadow-dark), -6px -6px 12px var(--shadow-light); color: var(--text); margin-bottom: 20px; }}
        .tabs {{ display: flex; justify-content: center; gap: 20px; margin-bottom: 30px; }}
        .tab {{ padding: 10px 25px; border-radius: 15px; cursor: pointer; font-weight: 600; background: var(--card); box-shadow: 5px 5px 10px var(--shadow-dark), -5px -5px 10px var(--shadow-light); transition: 0.3s; }}
        .tab.active {{ box-shadow: inset 5px 5px 10px var(--shadow-dark), inset -5px -5px 10px var(--shadow-light); color: var(--accent); }}
        .content {{ display: none; }}
        .content.active {{ display: block; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 25px; }}
        .subject {{ padding: 20px; border-radius: 20px; cursor: pointer; margin-bottom: 20px; background: var(--card); box-shadow: 8px 8px 16px var(--shadow-dark), -8px -8px 16px var(--shadow-light); }}
        .video-list {{ display: none; grid-column: 1 / -1; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
        .video-list.active {{ display: grid; }}
        .card {{ padding: 20px; border-radius: 15px; background: var(--card); box-shadow: 6px 6px 12px var(--shadow-dark), -6px -6px 12px var(--shadow-light); transition: 0.3s; display: flex; align-items: center; gap: 15px; text-decoration: none; color: inherit; }}
        .card:hover {{ box-shadow: inset 4px 4px 8px var(--shadow-dark), inset -4px -4px 8px var(--shadow-light); }}
        .card i {{ font-size: 1.5rem; color: var(--accent); }}
        .pdf-btn {{ margin-left: auto; padding: 5px 10px; background: var(--accent); color: white; border: none; border-radius: 10px; cursor: pointer; }}
    </style></head><body><div class="container">
        <div class="header"><h1>ITsGOlU</h1><input type="text" id="searchInput" placeholder="🔍 Search..." onkeyup="searchContent()"></div>
        <div class="tabs"><div class="tab active" onclick="showContent('videos')">Videos</div><div class="tab" onclick="showContent('pdfs')">PDFs</div><div class="tab" onclick="showContent('images')">Images</div></div>
        <div id="videos" class="content active"><div class="grid">"""
    for sub, vids in video_links_by_subject.items():
        html_content += f'<div class="subject" onclick="toggleVideos(\'{sub}\')"><h3>{sub}</h3></div><div id="{sub}" class="video-list">'
        for v in vids: 
            p_url = get_player_url(v['url'])
            html_content += f'<a href="{p_url}" target="_blank" class="card searchable-item"><i class="fas fa-play-circle"></i><span>{v["title"]}</span></a>'
        html_content += '</div>'
    html_content += """</div></div><div id="pdfs" class="content"><div class="grid">"""
    for p in pdf_links:
        html_content += f'<div class="card searchable-item"><i class="fas fa-file-pdf"></i><span>{p["title"]}</span><button class="pdf-btn" onclick="openPdf(\'{p["url"]}\')">View</button></div>'
    html_content += """</div></div><div id="images" class="content"><div class="grid">"""
    for i in image_links:
        html_content += f'<a href="{i["url"]}" target="_blank" class="card searchable-item"><i class="fas fa-image"></i><span>{i["title"]}</span></a>'
    html_content += f"""</div></div></div>{COMMON_PDF_MODAL}{COMMON_JS}</body></html>"""
    with open(output_file, 'w', encoding='utf-8') as file: file.write(html_content)

# --- THEME 3: BRUTALIST ---
async def extract_links_brutalist(input_file, output_file):
    video_links_by_subject = {}
    pdf_links = []
    image_links = []
    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            data = parse_line(line)
            if not data: continue
            if data['is_pdf']: pdf_links.append(data)
            elif data['is_image']: image_links.append(data)
            else:
                sub = data['subject']
                if sub not in video_links_by_subject: video_links_by_subject[sub] = []
                video_links_by_subject[sub].append(data)
    
    html_content = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>BRUTALIST</title><link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap" rel="stylesheet"><style>
        *{{margin:0;padding:0;box-sizing:border-box;font-family:'Space Mono',monospace;}}
        body{{background:#000;color:#fff;padding:20px;}}
        .container{{max-width:1100px;margin:0 auto;border:5px solid #fff;padding:20px;}}
        h1{{font-size:3rem;text-transform:uppercase;letter-spacing:-2px;margin-bottom:20px;text-align:center;}}
        #searchInput{{width:100%;background:#000;border:2px solid #fff;color:#fff;padding:15px;font-size:1.2rem;margin-bottom:20px;font-family:'Space Mono';}}
        .tabs{{display:flex;gap:10px;margin-bottom:30px;flex-wrap:wrap;}}
        .tab{{background:#fff;color:#000;padding:10px 20px;border:2px solid #fff;cursor:pointer;font-weight:bold;text-transform:uppercase;}}
        .tab.active{{background:#000;color:#fff;}}
        .content{{display:none;}}
        .content.active{{display:block;}}
        .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px;}}
        .card{{background:#fff;color:#000;padding:20px;border:2px solid #fff;text-decoration:none;display:block;}}
        .subject{{background:transparent;border:3px solid #fff;padding:20px;margin-bottom:20px;cursor:pointer;text-transform:uppercase;font-size:1.5rem;font-weight:bold;}}
        .video-list{{display:none;grid-column:1/-1;}}
        .video-list.active{{display:grid;}}
        .pdf-btn{{display:block;margin-top:10px;background:#000;color:#fff;padding:5px;border:2px solid #fff;cursor:pointer;text-align:center;}}
    </style></head><body><div class="container">
        <h1>BRUTALIST // DATA</h1>
        <input type="text" id="searchInput" placeholder="SEARCH_DATA..." onkeyup="searchContent()">
        <div class="tabs"><div class="tab active" onclick="showContent('videos')">VIDEOS</div><div class="tab" onclick="showContent('pdfs')">PDFS</div><div class="tab" onclick="showContent('images')">IMAGES</div></div>
        <div id="videos" class="content active"><div class="grid">"""
    for sub, vids in video_links_by_subject.items():
        html_content += f'<div class="subject" onclick="toggleVideos(\'{sub}\')">{sub}</div><div id="{sub}" class="video-list">'
        for v in vids: 
            p_url = get_player_url(v['url'])
            html_content += f'<a href="{p_url}" target="_blank" class="card searchable-item">> {v["title"]}</a>'
        html_content += '</div>'
    html_content += """</div></div><div id="pdfs" class="content"><div class="grid">"""
    for p in pdf_links:
        html_content += f'<div class="card searchable-item">> {p["title"]}<div class="pdf-btn" onclick="openPdf(\'{p["url"]}\')">[ VIEW PDF ]</div></div>'
    html_content += """</div></div><div id="images" class="content"><div class="grid">"""
    for i in image_links:
        html_content += f'<a href="{i["url"]}" target="_blank" class="card searchable-item">> {i["title"]}</a>'
    html_content += f"""</div></div></div>{COMMON_PDF_MODAL}{COMMON_JS}</body></html>"""
    with open(output_file, 'w', encoding='utf-8') as file: file.write(html_content)

# --- THEME 4: GLASSMORPHISM ---
async def extract_links_glassmorphism(input_file, output_file):
    video_links_by_subject = {}
    pdf_links = []
    image_links = []
    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            data = parse_line(line)
            if not data: continue
            if data['is_pdf']: pdf_links.append(data)
            elif data['is_image']: image_links.append(data)
            else:
                sub = data['subject']
                if sub not in video_links_by_subject: video_links_by_subject[sub] = []
                video_links_by_subject[sub].append(data)

    html_content = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Glass</title><link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;600&display=swap" rel="stylesheet"><style>
        body{{margin:0;padding:0;background:linear-gradient(45deg,#1a1a2e,#16213e);background-attachment:fixed;color:#fff;font-family:'Poppins',sans-serif;min-height:100vh;}}
        .container{{max-width:1100px;margin:0 auto;padding:20px;}}
        .glass{{background:rgba(255,255,255,0.05);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.1);border-radius:15px;}}
        h1{{text-align:center;margin-bottom:20px;}}
        #searchInput{{width:100%;padding:15px;border-radius:30px;background:rgba(255,255,255,0.1);border:none;color:#fff;margin-bottom:20px;outline:none;}}
        .tabs{{display:flex;justify-content:center;gap:15px;margin-bottom:30px;}}
        .tab{{padding:10px 25px;border-radius:20px;cursor:pointer;background:rgba(255,255,255,0.1);transition:0.3s;}}
        .tab.active{{background:#ff0055;}}
        .content{{display:none;}}
        .content.active{{display:block;}}
        .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px;}}
        .card{{padding:20px;text-decoration:none;color:#fff;display:block;transition:0.3s;}}
        .card:hover{{background:rgba(255,255,255,0.1);}}
        .subject{{padding:20px;cursor:pointer;margin-bottom:15px;font-weight:bold;}}
        .video-list{{display:none;grid-column:1/-1;}}
        .video-list.active{{display:grid;}}
        .pdf-btn{{float:right;color:#ff0055;font-weight:bold;cursor:pointer;border:none;background:none;}}
    </style></head><body><div class="container">
        <div class="glass" style="padding:20px;margin-bottom:20px;"><h1>Glass View</h1></div>
        <div class="glass" style="padding:15px;margin-bottom:20px;"><input type="text" id="searchInput" placeholder="🔍 Search..." onkeyup="searchContent()"></div>
        <div class="tabs"><div class="tab active" onclick="showContent('videos')">Videos</div><div class="tab" onclick="showContent('pdfs')">PDFs</div><div class="tab" onclick="showContent('images')">Images</div></div>
        <div id="videos" class="content active"><div class="grid">"""
    for sub, vids in video_links_by_subject.items():
        html_content += f'<div class="glass subject" onclick="toggleVideos(\'{sub}\')">{sub}</div><div id="{sub}" class="video-list">'
        for v in vids: 
            p_url = get_player_url(v['url'])
            html_content += f'<a href="{p_url}" target="_blank" class="glass card searchable-item">▶ {v["title"]}</a>'
        html_content += '</div>'
    html_content += """</div></div><div id="pdfs" class="content"><div class="grid">"""
    for p in pdf_links:
        html_content += f'<div class="glass card searchable-item">📄 {p["title"]}<button class="pdf-btn" onclick="openPdf(\'{p["url"]}\')">View PDF</button></div>'
    html_content += """</div></div><div id="images" class="content"><div class="grid">"""
    for i in image_links:
        html_content += f'<a href="{i["url"]}" target="_blank" class="glass card searchable-item">🖼️ {i["title"]}</a>'
    html_content += f"""</div></div></div>{COMMON_PDF_MODAL}{COMMON_JS}</body></html>"""
    with open(output_file, 'w', encoding='utf-8') as file: file.write(html_content)

# --- THEME 5: CYBERPUNK ---
async def extract_links_cyberpunk(input_file, output_file):
    video_links_by_subject = {}
    pdf_links = []
    image_links = []
    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            data = parse_line(line)
            if not data: continue
            if data['is_pdf']: pdf_links.append(data)
            elif data['is_image']: image_links.append(data)
            else:
                sub = data['subject']
                if sub not in video_links_by_subject: video_links_by_subject[sub] = []
                video_links_by_subject[sub].append(data)

    html_content = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>CYBERPUNK</title><link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&display=swap" rel="stylesheet"><style>
        body{{background:#050505;color:#00ff41;font-family:'Orbitron',sans-serif;padding:20px;}}
        .container{{max-width:1100px;margin:0 auto;border:2px solid #00ff41;box-shadow:0 0 10px #00ff41;padding:20px;}}
        h1{{text-align:center;color:#00ff41;text-shadow:0 0 5px #00ff41;}}
        #searchInput{{width:100%;background:#000;border:2px solid #00ff41;color:#00ff41;padding:15px;margin-bottom:20px;font-family:'Orbitron';}}
        .tabs{{display:flex;gap:20px;margin-bottom:30px;}}
        .tab{{border:2px solid #00ff41;padding:10px 20px;cursor:pointer;transition:0.3s;}}
        .tab.active{{background:#00ff41;color:#000;}}
        .content{{display:none;}}
        .content.active{{display:block;}}
        .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px;}}
        .card{{border:1px solid #00ff41;padding:15px;text-decoration:none;color:#00ff41;display:block;transition:0.3s;}}
        .card:hover{{background:rgba(0,255,65,0.1);}}
        .subject{{font-size:1.2rem;margin-bottom:20px;padding:10px;border-bottom:1px solid #00ff41;cursor:pointer;}}
        .video-list{{display:none;grid-column:1/-1;}}
        .video-list.active{{display:grid;}}
        .pdf-btn{{display:block;margin-top:10px;color:#ff0055;border:1px solid #ff0055;padding:5px;text-align:center;cursor:pointer;}}
    </style></head><body><div class="container">
        <h1>CYBER_VAULT</h1>
        <input type="text" id="searchInput" placeholder="SEARCH_SYSTEM..." onkeyup="searchContent()">
        <div class="tabs"><div class="tab active" onclick="showContent('videos')">VIDEOS</div><div class="tab" onclick="showContent('pdfs')">PDFS</div><div class="tab" onclick="showContent('images')">IMAGES</div></div>
        <div id="videos" class="content active"><div class="grid">"""
    for sub, vids in video_links_by_subject.items():
        html_content += f'<div class="subject" onclick="toggleVideos(\'{sub}\')">> {sub}</div><div id="{sub}" class="video-list">'
        for v in vids: 
            p_url = get_player_url(v['url'])
            html_content += f'<a href="{p_url}" target="_blank" class="card searchable-item">> {v["title"]}</a>'
        html_content += '</div>'
    html_content += """</div></div><div id="pdfs" class="content"><div class="grid">"""
    for p in pdf_links:
        html_content += f'<div class="card searchable-item">> {p["title"]}<div class="pdf-btn" onclick="openPdf(\'{p["url"]}\')">[VIEW_DOC]</div></div>'
    html_content += """</div></div><div id="images" class="content"><div class="grid">"""
    for i in image_links:
        html_content += f'<a href="{i["url"]}" target="_blank" class="card searchable-item">> {i["title"]}</a>'
    html_content += f"""</div></div></div>{COMMON_PDF_MODAL}{COMMON_JS}</body></html>"""
    with open(output_file, 'w', encoding='utf-8') as file: file.write(html_content)

if __name__ == "__main__":
    print("✅ Bot is starting...")
    client.run()

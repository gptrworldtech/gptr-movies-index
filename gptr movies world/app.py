import os
import time
import re
from flask import Flask, request, jsonify, render_template_string
from DrissionPage import ChromiumPage, ChromiumOptions

app = Flask(__name__)

# --- 1. THE UI (Glassmorphism Design) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GPTR Movies Downloader</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #00f2ff;
            --secondary: #bd00ff;
            --danger: #ff4757;
            --bg-dark: #090919;
            --glass: rgba(255, 255, 255, 0.05);
            --border: rgba(255, 255, 255, 0.1);
        }
        body {
            background-color: var(--bg-dark);
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(189, 0, 255, 0.2) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(0, 242, 255, 0.15) 0%, transparent 40%);
            color: white;
            font-family: 'Outfit', sans-serif;
            margin: 0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }
        .header { text-align: center; margin-top: 30px; animation: fadeInDown 1s ease; }
        .logo { width: 160px; filter: drop-shadow(0 0 20px rgba(0, 242, 255, 0.4)); transition: transform 0.3s; margin-bottom: 10px; }
        .logo:hover { transform: scale(1.05) rotate(2deg); }
        h1 { font-size: 2.2rem; margin: 10px 0 30px 0; background: linear-gradient(90deg, #ffffff, var(--primary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; }
        
        .search-container { background: var(--glass); backdrop-filter: blur(12px); padding: 8px; border-radius: 50px; border: 1px solid var(--border); display: flex; width: 90%; max-width: 700px; box-shadow: 0 15px 35px rgba(0,0,0,0.3); transition: 0.3s; }
        .search-container:focus-within { border-color: var(--primary); box-shadow: 0 0 25px rgba(0, 242, 255, 0.2); }
        input { flex: 1; background: transparent; border: none; padding: 15px 25px; color: white; font-size: 1.1rem; outline: none; font-family: 'Outfit', sans-serif; }
        .search-btn { background: linear-gradient(135deg, var(--secondary), var(--primary)); border: none; padding: 0 40px; border-radius: 40px; color: white; font-weight: 600; font-size: 1rem; cursor: pointer; transition: 0.3s; }
        .search-btn:hover { transform: translateY(-2px); }

        .info-wrapper {
            width: 85%;
            max-width: 650px;
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin-top: 25px;
        }
        .tips-box {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border);
            border-radius: 15px;
            padding: 15px 25px;
            text-align: left;
            animation: fadeInUp 0.8s ease;
        }
        .tips-title { color: var(--primary); font-weight: 700; margin-bottom: 8px; font-size: 0.9rem; }
        .tips-list { margin: 0; padding-left: 20px; color: #cbd5e1; font-size: 0.85rem; line-height: 1.5; }
        .tips-list li span { color: #fff; font-weight: 500; }

        .notice-box {
            background: rgba(255, 71, 87, 0.05);
            border: 1px solid rgba(255, 71, 87, 0.2);
            border-radius: 15px;
            padding: 15px 25px;
            text-align: left;
            animation: fadeInUp 1s ease;
        }
        .notice-title { color: var(--danger); font-weight: 700; margin-bottom: 8px; font-size: 0.9rem; display: flex; align-items: center; gap: 8px; }
        .notice-list { margin: 0; padding-left: 20px; color: #ffcccb; font-size: 0.85rem; line-height: 1.5; }

        #results { width: 95%; max-width: 1000px; margin-top: 30px; display: grid; grid-template-columns: 1fr; gap: 15px; padding-bottom: 50px; }
        
        .card { 
            background: linear-gradient(145deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02)); 
            border: 1px solid var(--border); 
            border-radius: 16px; 
            padding: 15px 20px; 
            transition: all 0.3s ease; 
            display: grid; 
            grid-template-columns: 50px 1fr auto; 
            align-items: center;
            gap: 20px;
        }
        .card:hover { transform: translateY(-5px); border-color: var(--primary); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        
        .card-icon { 
            font-size: 1.5rem; color: var(--primary); 
            display: flex; justify-content: center; align-items: center;
            background: rgba(0, 242, 255, 0.1);
            width: 50px; height: 50px; border-radius: 12px;
        }
        
        .title { 
            font-size: 1rem; font-weight: 500; color: #fff; 
            line-height: 1.4; margin-bottom: 8px;
            word-wrap: break-word;
        }
        
        .meta-tags { display: flex; flex-wrap: wrap; gap: 6px; }
        .tag { font-size: 0.75rem; padding: 3px 8px; border-radius: 4px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
        
        .tag-tel { background: rgba(189, 0, 255, 0.2); color: #eebbff; border: 1px solid rgba(189, 0, 255, 0.3); }
        .tag-tam { background: rgba(255, 100, 100, 0.2); color: #ffcccc; border: 1px solid rgba(255, 100, 100, 0.3); }
        .tag-hin { background: rgba(255, 165, 0, 0.2); color: #ffeebb; border: 1px solid rgba(255, 165, 0, 0.3); }
        .tag-multi { background: linear-gradient(45deg, #bd00ff, #00f2ff); color: white; border: none; }
        .tag-quality { background: rgba(0, 242, 255, 0.15); color: #ccfcff; border: 1px solid rgba(0, 242, 255, 0.3); }
        .tag-size { background: rgba(255, 215, 0, 0.15); color: #fff5cc; border: 1px solid rgba(255, 215, 0, 0.3); }

        .download-btn { 
            padding: 10px 20px; border-radius: 10px; border: 1px solid var(--primary); 
            background: rgba(0, 242, 255, 0.05); color: var(--primary); font-weight: 600; 
            cursor: pointer; transition: 0.3s; white-space: nowrap; font-size: 0.9rem;
        }
        .download-btn:hover { background: var(--primary); color: #000; }
        
        .loader { display: none; margin: 30px auto; border: 3px solid rgba(255,255,255,0.1); border-top: 3px solid var(--primary); border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; }
        .status-text { color: #94a3b8; margin-top: 10px; font-size: 0.9rem; text-align: center; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        @keyframes fadeInDown { from { opacity: 0; transform: translateY(-30px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

        @media (max-width: 600px) {
            .card { grid-template-columns: 1fr; text-align: center; gap: 15px; }
            .card-icon { margin: 0 auto; }
            .meta-tags { justify-content: center; }
            .info-wrapper { width: 95%; }
        }
    </style>
</head>
<body>
    <div class="header">
        <img src="https://ik.imagekit.io/kff5oshkqj/low%20semi%20logo%20med%20png-modified%20(1).webp?updatedAt=1763525747370" alt="GPTR Logo" class="logo">
        <h1>GPTR Movies Downloader</h1>
    </div>

    <div class="search-container">
        <input type="text" id="query" placeholder="Enter movie name..." onkeypress="handleEnter(event)">
        <button class="search-btn" onclick="searchMovies()"><i class="fa-solid fa-search"></i></button>
    </div>

    <div class="info-wrapper">
        <div class="tips-box">
            <div class="tips-title"><i class="fa-solid fa-lightbulb"></i> Pro Tips:</div>
            <ul class="tips-list">
                <li>Check Google for spelling (e.g., <span>Devara</span> not Devarra).</li>
                <li>If searching fails, try again immediately.</li>
                <li>For Series: Use <span>Name S01E01</span>.</li>
                <li>Add Year: <span>RRR 2022</span>.</li>
            </ul>
        </div>

        <div class="notice-box">
            <div class="notice-title"><i class="fa-solid fa-triangle-exclamation"></i> Important Notice:</div>
            <ul class="notice-list">
                <li>Resume support is not available.</li>
                <li>Stable internet connection required.</li>
                <li>Use a download manager (IDM/FDM) for better experience.</li>
            </ul>
        </div>
    </div>

    <div id="loader" class="loader"></div>
    <div id="status" class="status-text"></div>
    <div id="results"></div>

    <script>
        function handleEnter(e) { if(e.key === 'Enter') searchMovies(); }

        function generateTags(title, size) {
            let tagsHtml = "";
            const t = title.toLowerCase();

            if(t.includes('tel') || t.includes('telugu')) tagsHtml += `<span class="tag tag-tel">TELUGU</span>`;
            if(t.includes('hin') || t.includes('hindi')) tagsHtml += `<span class="tag tag-hin">HINDI</span>`;
            if(t.includes('tam') || t.includes('tamil')) tagsHtml += `<span class="tag tag-tam">TAMIL</span>`;
            if(t.includes('kan') || t.includes('kannada')) tagsHtml += `<span class="tag tag-lang" style="color:#FFF;">KAN</span>`;
            if(t.includes('mal') || t.includes('malayalam')) tagsHtml += `<span class="tag tag-lang" style="color:#FFF;">MAL</span>`;
            if(t.includes('eng') || t.includes('english')) tagsHtml += `<span class="tag tag-lang" style="color:#FFF;">ENG</span>`;
            
            if(t.includes('multi') || t.includes('dual') || t.includes('pan')) tagsHtml += `<span class="tag tag-multi">MULTI AUDIO</span>`;
            
            if(t.includes('4k') || t.includes('2160p')) tagsHtml += `<span class="tag tag-quality">4K UHD</span>`;
            else if(t.includes('1080p')) tagsHtml += `<span class="tag tag-quality">1080p</span>`;
            else if(t.includes('720p')) tagsHtml += `<span class="tag tag-quality">720p</span>`;

            if(size && size !== "Unknown") {
                tagsHtml += `<span class="tag tag-size">💾 ${size}</span>`;
            }
            return tagsHtml;
        }

        async function searchMovies() {
            const query = document.getElementById('query').value;
            if(!query) return alert("Please enter a name!");
            
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = "";
            document.getElementById('loader').style.display = "block";
            document.getElementById('status').innerText = "🔍 Scanning SCLOUD Library...";
            
            try {
                const res = await fetch(`/api/search?q=${query}`);
                const data = await res.json();
                
                document.getElementById('loader').style.display = "none";
                document.getElementById('status').innerText = `✅ Found ${data.count} movies!`;
                
                if(data.count === 0) {
                    resultsDiv.innerHTML = "<p style='text-align:center;color:#fff;'>No results found. Try again.</p>";
                    return;
                }

                data.results.forEach((movie, index) => {
                    const card = document.createElement('div');
                    card.className = 'card';
                    card.style.animationDelay = `${index * 0.05}s`;
                    const badges = generateTags(movie.title, movie.size);
                    card.innerHTML = `
                        <div class="card-icon"><i class="fa-solid fa-film"></i></div>
                        <div class="card-content">
                            <div class="title">${movie.title}</div>
                            <div class="meta-tags">${badges}</div>
                        </div>
                        <button class="download-btn" onclick="getLink(this, '${movie.url}')">
                            <i class="fa-solid fa-cloud-arrow-down"></i> Download
                        </button>
                    `;
                    resultsDiv.appendChild(card);
                });
            } catch (err) {
                document.getElementById('loader').style.display = "none";
                document.getElementById('status').innerText = "❌ Connection Error.";
            }
        }

        async function getLink(btn, url) {
            const originalHTML = btn.innerHTML;
            btn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Getting Link...`;
            btn.style.opacity = "0.7";
            try {
                const res = await fetch(`/api/get-link?url=${encodeURIComponent(url)}`);
                const data = await res.json();
                if(data.success) {
                    btn.innerHTML = `<i class="fa-solid fa-check"></i> Open!`;
                    btn.style.background = "#00f2ff";
                    btn.style.color = "#000";
                    window.location.href = data.direct_download_link;
                } else {
                    btn.innerHTML = `Failed`;
                    alert("Failed: " + data.error);
                    btn.innerHTML = originalHTML;
                }
            } catch (err) { alert("Error: " + err); btn.innerHTML = originalHTML; }
        }
    </script>
</body>
</html>
"""

# --- 2. BACKEND LOGIC ---
BASE_URL = "https://scloudx.lol"

def get_browser():
    co = ChromiumOptions()
    # IMPORTANT: Headless MUST be True for Cloud Deployment (Render)
    co.headless(True)
    co.set_argument('--no-sandbox')
    co.set_argument('--disable-gpu')
    try: return ChromiumPage(co)
    except: return None

def search_logic(query):
    page = get_browser()
    if not page: return []
    try:
        page.get(BASE_URL)
        if page.wait.ele_displayed('tag:input', timeout=15):
            page.ele('tag:input').input(query)
            time.sleep(0.5)
            page.actions.type('\n')
            
            if page.wait.ele_displayed('css:a[href^="/file/"]', timeout=20):
                results = []
                links = page.eles('css:a[href^="https://scloudx.lol/file/"]') or page.eles('css:a[href^="/file/"]')
                for link in links:
                    try:
                        url = link.link
                        title = link.text or link.raw_text
                        size = "Unknown"
                        try:
                            parent = link.parent(2)
                            if parent:
                                text_content = parent.text
                                size_match = re.search(r'(\d+(\.\d+)?\s*(GB|MB))', text_content, re.IGNORECASE)
                                if size_match: size = size_match.group(0)
                        except: pass
                        if url and "/file/" in url:
                            if not any(r['url'] == url for r in results):
                                results.append({"title": title, "url": url, "size": size})
                    except: continue
                page.quit()
                return results
        page.quit()
        return []
    except:
        try: page.quit()
        except: pass
        return []

def extract_link_logic(file_url):
    page = get_browser()
    if not page: return None
    try:
        page.get(BASE_URL)
        time.sleep(2)
        page.get(file_url)
        if page.wait.ele_displayed('text:Download', timeout=30):
            btn = page.ele('.btn-danger') or page.ele('text:Download File') or page.ele('text:Download')
            if btn:
                link = btn.link if btn.tag == 'a' else (btn.parent('tag:a').link if btn.parent('tag:a') else None)
                if link:
                    page.quit()
                    return link
        page.quit()
        return None
    except:
        try: page.quit()
        except: pass
        return None

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/search')
def api_search():
    query = request.args.get('q')
    return jsonify({"count": 0, "results": []}) if not query else jsonify({"count": len(res:=search_logic(query)), "results": res})

@app.route('/api/get-link')
def api_get_link():
    url = request.args.get('url')
    if not url: return jsonify({"error": "No URL"}), 400
    link = extract_link_logic(url)
    return jsonify({"success": True, "direct_download_link": link}) if link else jsonify({"success": False, "error": "Not found"}), 404

if __name__ == '__main__':
    # Get port from environment variable (Required for Render)
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 GPTR CLOUD APP RUNNING ON PORT {port}")
    app.run(host='0.0.0.0', port=port)
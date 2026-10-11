const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// CORS Proxy route for .m3u8 playlists and video segments
app.get('/proxy', async (req, res) => {
    const targetUrl = req.query.url;
    if (!targetUrl) return res.status(400).send('URL missing');

    try {
        const isM3u8 = targetUrl.includes('.m3u8');
        const response = await axios({
            method: 'get',
            url: targetUrl,
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Referer': 'https://web.classplusapp.com/',
                'Origin': 'https://web.classplusapp.com'
            },
            responseType: isM3u8 ? 'text' : 'stream'
        });

        res.setHeader('Access-Control-Allow-Origin', '*');

        if (isM3u8) {
            let m3u8Content = response.data;
            const baseUrl = targetUrl.substring(0, targetUrl.lastIndexOf('/') + 1);

            const lines = m3u8Content.split('\n');
            const rewrittenLines = lines.map(line => {
                line = line.trim();
                if (line && !line.startsWith('#')) {
                    let absoluteSegmentUrl = line.startsWith('http') ? line : baseUrl + line;
                    return `/proxy?url=${encodeURIComponent(absoluteSegmentUrl)}`;
                } else if (line.startsWith('#EXT-X-MAP:URI=')) {
                    return line.replace(/URI="([^"]+)"/, (match, uri) => {
                        let absUri = uri.startsWith('http') ? uri : baseUrl + uri;
                        return `URI="/proxy?url=${encodeURIComponent(absUri)}"`;
                    });
                }
                return line;
            });

            res.setHeader('Content-Type', 'application/vnd.apple.mpegurl');
            res.send(rewrittenLines.join('\n'));
        } else {
            response.data.pipe(res);
        }
    } catch (error) {
        res.status(500).send('Proxy error: ' + error.message);
    }
});

// Front-end Interface
app.get('/', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html lang="hi">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Classplus Video & PDF Player</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
        </head>
        <body class="bg-slate-900 text-white min-h-screen p-4 md:p-8">
            <div class="max-w-6xl mx-auto">
                <header class="text-center mb-8">
                    <h1 class="text-3xl font-bold text-indigo-400 mb-2">Classplus Secure Video & PDF Player</h1>
                    <p class="text-slate-400">Apni .txt file upload karein, videos proxy ke zariye chalengi.</p>
                </header>

                <div class="bg-slate-800 border-2 border-dashed border-slate-700 rounded-xl p-6 text-center mb-8">
                    <input type="file" id="fileInput" accept=".txt" class="block w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-500 cursor-pointer mx-auto"/>
                </div>

                <div id="playerSection" class="hidden bg-slate-800 rounded-xl p-4 mb-8 shadow-lg">
                    <h2 id="nowPlayingTitle" class="text-lg font-semibold text-indigo-300 mb-3">Video Play ho rahi hai...</h2>
                    <div class="relative w-full aspect-video bg-black rounded-lg overflow-hidden">
                        <video id="videoPlayer" controls class="w-full h-full"></video>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-slate-800 rounded-xl p-5 shadow-md">
                        <h2 class="text-xl font-bold text-emerald-400 mb-4 flex items-center justify-between">
                            <span>Videos (.m3u8)</span>
                            <span id="videoCount" class="text-xs bg-emerald-900 text-emerald-300 px-2.5 py-1 rounded-full">0</span>
                        </h2>
                        <div id="videoList" class="space-y-3 max-h-[400px] overflow-y-auto pr-2">
                            <p class="text-slate-500 text-sm">File upload karein...</p>
                        </div>
                    </div>

                    <div class="bg-slate-800 rounded-xl p-5 shadow-md">
                        <h2 class="text-xl font-bold text-amber-400 mb-4 flex items-center justify-between">
                            <span>PDF Notes</span>
                            <span id="pdfCount" class="text-xs bg-amber-900 text-amber-300 px-2.5 py-1 rounded-full">0</span>
                        </h2>
                        <div id="pdfList" class="space-y-3 max-h-[400px] overflow-y-auto pr-2">
                            <p class="text-slate-500 text-sm">File upload karein...</p>
                        </div>
                    </div>
                </div>
            </div>

            <script>
                const fileInput = document.getElementById('fileInput');
                const videoList = document.getElementById('videoList');
                const pdfList = document.getElementById('pdfList');
                const videoCount = document.getElementById('videoCount');
                const pdfCount = document.getElementById('pdfCount');
                const playerSection = document.getElementById('playerSection');
                const videoPlayer = document.getElementById('videoPlayer');
                const nowPlayingTitle = document.getElementById('nowPlayingTitle');
                let hls = null;

                fileInput.addEventListener('change', function(event) {
                    const file = event.target.files[0];
                    if (!file) return;
                    const reader = new FileReader();
                    reader.onload = function(e) { parseData(e.target.result); };
                    reader.readAsText(file);
                });

                function parseData(text) {
                    const lines = text.split('\\n');
                    let videos = [], pdfs = [];
                    lines.forEach(line => {
                        const httpIndex = line.indexOf('http');
                        if (httpIndex !== -1) {
                            const title = line.substring(0, httpIndex).replace(/[:\\-]+$/, '').trim();
                            const url = line.substring(httpIndex).trim();
                            if (url.includes('.m3u8') || url.includes('.mp4')) {
                                videos.push({ title, url });
                            } else if (url.includes('.pdf')) {
                                pdfs.push({ title, url });
                            }
                        }
                    });
                    renderVideos(videos);
                    renderPdfs(pdfs);
                }

                function renderVideos(videos) {
                    videoCount.textContent = videos.length;
                    if (videos.length === 0) { videoList.innerHTML = '<p class="text-slate-500 text-sm">Koi video nahi mili.</p>'; return; }
                    videoList.innerHTML = '';
                    videos.forEach((item) => {
                        const div = document.createElement('div');
                        div.className = "bg-slate-700/50 hover:bg-slate-700 p-3 rounded-lg flex items-center justify-between transition cursor-pointer";
                        div.innerHTML = \`<span class="text-sm font-medium text-slate-200 truncate mr-2">\${item.title}</span><button class="bg-indigo-600 hover:bg-indigo-500 text-white text-xs px-3 py-1.5 rounded shrink-0">Play</button>\`;
                        div.querySelector('button').addEventListener('click', () => { playVideo(item.url, item.title); });
                        videoList.appendChild(div);
                    });
                }

                function renderPdfs(pdfs) {
                    pdfCount.textContent = pdfs.length;
                    if (pdfs.length === 0) { pdfList.innerHTML = '<p class="text-slate-500 text-sm">Koi PDF nahi mili.</p>'; return; }
                    pdfList.innerHTML = '';
                    pdfs.forEach((item) => {
                        const div = document.createElement('div');
                        div.className = "bg-slate-700/50 hover:bg-slate-700 p-3 rounded-lg flex items-center justify-between transition";
                        div.innerHTML = \`<span class="text-sm font-medium text-slate-200 truncate mr-2">\${item.title}</span><a href="\${item.url}" target="_blank" class="bg-amber-600 hover:bg-amber-500 text-white text-xs px-3 py-1.5 rounded shrink-0">Open PDF</a>\`;
                        pdfList.appendChild(div);
                    });
                }

                function playVideo(url, title) {
                    playerSection.classList.remove('hidden');
                    nowPlayingTitle.textContent = "Playing: " + title;
                    window.scrollTo({ top: 0, behavior: 'smooth' });

                    const proxyUrl = '/proxy?url=' + encodeURIComponent(url);

                    if (Hls.isSupported()) {
                        if (hls) { hls.destroy(); }
                        hls = new Hls();
                        hls.loadSource(proxyUrl);
                        hls.attachMedia(videoPlayer);
                        hls.on(Hls.Events.MANIFEST_PARSED, () => { videoPlayer.play(); });
                    } else if (videoPlayer.canPlayType('application/vnd.apple.mpegurl')) {
                        videoPlayer.src = proxyUrl;
                        videoPlayer.addEventListener('loadedmetadata', () => { videoPlayer.play(); });
                    }
                }
            </script>
        </body>
        </html>
    `);
});

app.listen(PORT, () => {
    console.log('Server is running on port ' + PORT);
});

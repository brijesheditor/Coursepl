const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html lang="hi">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Classplus Playlist Generator</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-slate-900 text-white min-h-screen p-4 md:p-8">
            <div class="max-w-4xl mx-auto">
                <header class="text-center mb-8">
                    <h1 class="text-3xl font-bold text-indigo-400 mb-2">Classplus Playlist Generator</h1>
                    <p class="text-slate-400">Apni .txt file upload karein aur VLC Playlist download karke saari videos ek sath chalayein.</p>
                </header>

                <div class="bg-slate-800 border-2 border-dashed border-slate-700 rounded-xl p-6 text-center mb-8">
                    <input type="file" id="fileInput" accept=".txt" class="block w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-500 cursor-pointer mx-auto"/>
                </div>

                <!-- Download Playlist Button Section -->
                <div id="playlistSection" class="hidden mb-6 text-center">
                    <button id="downloadBtn" class="bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 px-6 rounded-xl shadow-lg transition flex items-center justify-center mx-auto gap-2">
                        📥 Download VLC Playlist (.m3u)
                    </button>
                    <p class="text-xs text-slate-400 mt-2">Is file ko download karke VLC ya MX Player me open karein.</p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- Videos List -->
                    <div class="bg-slate-800 rounded-xl p-5 shadow-md">
                        <h2 class="text-xl font-bold text-emerald-400 mb-4 flex items-center justify-between">
                            <span>Videos (.m3u8)</span>
                            <span id="videoCount" class="text-xs bg-emerald-900 text-emerald-300 px-2.5 py-1 rounded-full">0</span>
                        </h2>
                        <div id="videoList" class="space-y-3 max-h-[450px] overflow-y-auto pr-2">
                            <p class="text-slate-500 text-sm">Pehle .txt file upload karein...</p>
                        </div>
                    </div>

                    <!-- PDFs List -->
                    <div class="bg-slate-800 rounded-xl p-5 shadow-md">
                        <h2 class="text-xl font-bold text-amber-400 mb-4 flex items-center justify-between">
                            <span>PDF Notes</span>
                            <span id="pdfCount" class="text-xs bg-amber-900 text-amber-300 px-2.5 py-1 rounded-full">0</span>
                        </h2>
                        <div id="pdfList" class="space-y-3 max-h-[450px] overflow-y-auto pr-2">
                            <p class="text-slate-500 text-sm">Pehle .txt file upload karein...</p>
                        </div>
                    </div>
                </div>
            </div>

            <script>
                let globalVideos = [];
                const fileInput = document.getElementById('fileInput');
                const videoList = document.getElementById('videoList');
                const pdfList = document.getElementById('pdfList');
                const videoCount = document.getElementById('videoCount');
                const pdfCount = document.getElementById('pdfCount');
                const playlistSection = document.getElementById('playlistSection');
                const downloadBtn = document.getElementById('downloadBtn');

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
                    globalVideos = videos;
                    if(videos.length > 0) {
                        playlistSection.classList.remove('hidden');
                    }
                    renderVideos(videos);
                    renderPdfs(pdfs);
                }

                downloadBtn.addEventListener('click', () => {
                    if (globalVideos.length === 0) return;
                    let m3uContent = "#EXTM3U\\n";
                    globalVideos.forEach(v => {
                        m3uContent += \`#EXTINF:-1,\${v.title}\\n\${v.url}\\n\`;
                    });
                    const blob = new Blob([m3uContent], { type: 'audio/x-mpegurl' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'classplus_playlist.m3u';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                });

                function renderVideos(videos) {
                    videoCount.textContent = videos.length;
                    if (videos.length === 0) {
                        videoList.innerHTML = '<p class="text-slate-500 text-sm">Koi video nahi mili.</p>';
                        return;
                    }
                    videoList.innerHTML = '';
                    videos.forEach((item) => {
                        const div = document.createElement('div');
                        div.className = "bg-slate-700/50 p-2.5 rounded-lg flex items-center justify-between gap-2";
                        div.innerHTML = \`
                            <span class="text-xs font-medium text-slate-200 truncate">\${item.title}</span>
                            <button onclick="navigator.clipboard.writeText('\${item.url}'); alert('Link copied!');" class="bg-indigo-600 hover:bg-indigo-500 text-white text-[10px] py-1 px-2.5 rounded shrink-0 font-semibold">Copy</button>
                        \`;
                        videoList.appendChild(div);
                    });
                }

                function renderPdfs(pdfs) {
                    pdfCount.textContent = pdfs.length;
                    if (pdfs.length === 0) {
                        pdfList.innerHTML = '<p class="text-slate-500 text-sm">Koi PDF nahi mili.</p>';
                        return;
                    }
                    pdfList.innerHTML = '';
                    pdfs.forEach((item) => {
                        const div = document.createElement('div');
                        div.className = "bg-slate-700/50 p-2.5 rounded-lg flex items-center justify-between gap-2";
                        div.innerHTML = \`
                            <span class="text-xs font-medium text-slate-200 truncate">\${item.title}</span>
                            <a href="\${item.url}" target="_blank" class="bg-amber-600 hover:bg-amber-500 text-white text-[10px] py-1 px-2.5 rounded shrink-0 font-semibold">Open PDF</a>
                        \`;
                        pdfList.appendChild(div);
                    });
                }
            </script>
        </body>
        </html>
    `);
});

app.listen(PORT, () => {
    console.log('Server is running on port ' + PORT);
});

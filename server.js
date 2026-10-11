const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// Front-end Interface with fixed VLC Android URI scheme
app.get('/', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html lang="hi">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Classplus VLC Streamer</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-slate-900 text-white min-h-screen p-4 md:p-8">
            <div class="max-w-4xl mx-auto">
                <header class="text-center mb-8">
                    <h1 class="text-3xl font-bold text-indigo-400 mb-2">Classplus VLC Streamer</h1>
                    <p class="text-slate-400">Apni .txt file upload karein aur videos ko direct VLC Player me chalayein.</p>
                </header>

                <div class="bg-slate-800 border-2 border-dashed border-slate-700 rounded-xl p-6 text-center mb-8">
                    <input type="file" id="fileInput" accept=".txt" class="block w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-500 cursor-pointer mx-auto"/>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- Videos List -->
                    <div class="bg-slate-800 rounded-xl p-5 shadow-md">
                        <h2 class="text-xl font-bold text-emerald-400 mb-4 flex items-center justify-between">
                            <span>Videos (.m3u8)</span>
                            <span id="videoCount" class="text-xs bg-emerald-900 text-emerald-300 px-2.5 py-1 rounded-full">0</span>
                        </h2>
                        <div id="videoList" class="space-y-3 max-h-[500px] overflow-y-auto pr-2">
                            <p class="text-slate-500 text-sm">Pehle .txt file upload karein...</p>
                        </div>
                    </div>

                    <!-- PDFs List -->
                    <div class="bg-slate-800 rounded-xl p-5 shadow-md">
                        <h2 class="text-xl font-bold text-amber-400 mb-4 flex items-center justify-between">
                            <span>PDF Notes</span>
                            <span id="pdfCount" class="text-xs bg-amber-900 text-amber-300 px-2.5 py-1 rounded-full">0</span>
                        </h2>
                        <div id="pdfList" class="space-y-3 max-h-[500px] overflow-y-auto pr-2">
                            <p class="text-slate-500 text-sm">Pehle .txt file upload karein...</p>
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
                    if (videos.length === 0) {
                        videoList.innerHTML = '<p class="text-slate-500 text-sm">Koi video nahi mili.</p>';
                        return;
                    }
                    videoList.innerHTML = '';
                    videos.forEach((item) => {
                        // Fix for Android VLC scheme by removing https:// from the URI trigger
                        const cleanUrlForVlc = item.url.replace(/^https?:\\/\\//, '');
                        const div = document.createElement('div');
                        div.className = "bg-slate-700/50 p-3 rounded-lg flex flex-col gap-2";
                        div.innerHTML = \`
                            <span class="text-sm font-medium text-slate-200">\${item.title}</span>
                            <div class="flex gap-2">
                                <a href="vlc://\${cleanUrlForVlc}" class="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white text-xs py-1.5 px-3 rounded text-center font-semibold">Play in VLC</a>
                                <button onclick="navigator.clipboard.writeText('\${item.url}'); alert('Link copied!');" class="bg-indigo-600 hover:bg-indigo-500 text-white text-xs py-1.5 px-3 rounded font-semibold">Copy Link</button>
                            </div>
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
                        div.className = "bg-slate-700/50 p-3 rounded-lg flex items-center justify-between";
                        div.innerHTML = \`
                            <span class="text-sm font-medium text-slate-200 truncate mr-2">\${item.title}</span>
                            <a href="\${item.url}" target="_blank" class="bg-amber-600 hover:bg-amber-500 text-white text-xs py-1.5 px-3 rounded shrink-0">Open PDF</a>
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

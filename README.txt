STUDYVAULT PLUS
Phone-friendly static player for TXT / JSON / direct video URLs / PDF.

DEPLOY:
1) Extract ZIP on Android.
2) GitHub > New repository > StudyVault (Public).
3) Upload index.html and commit.
4) Settings > Pages > Deploy from branch > main > /(root) > Save.
5) Open the Pages URL and upload your TXT/JSON, or paste a direct URL.

Render Static Site alternative:
- Connect the same GitHub repository
- Build command: leave blank
- Publish directory: .
- Deploy.

Supported inputs:
- TXT lines: Lecture title:https://example.com/master.m3u8
- Direct links in plain text
- JSON objects/arrays with url, link, src, videoUrl, video_url, fileUrl, streamUrl, playUrl, downloadUrl fields.
- HLS .m3u8, direct MP4/WebM, and PDF URLs.

IMPORTANT:
The player uses hls.js for HLS playback. HLS resources must be accessible from the browser and the host must permit CORS GET requests. It does not bypass DRM, authorization, expired signatures, or provider restrictions. Use course links/materials you are authorized to access. A static GitHub Pages website cannot fix a stream server that denies browser playback.

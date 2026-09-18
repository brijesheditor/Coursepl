let player;

document.addEventListener('DOMContentLoaded', () => {
  shaka.polyfill.installAll();
  if (shaka.Player.isBrowserSupported()) {
    const video = document.getElementById('video');
    player = new shaka.Player(video);
    player.addEventListener('error', (e) => console.error('Shaka Player Error:', e.detail));
  } else {
    alert('Aapka browser video player support nahi karta.');
  }
});

async function playDRMStream() {
  const mpdUrl = document.getElementById('mpdUrl').value.trim();
  const keyPair = document.getElementById('keyPair').value.trim();

  if (!mpdUrl) {
    alert('Kripya MPD URL enter karein.');
    return;
  }

  let clearKeysObj = {};
  if (keyPair && keyPair.includes(':')) {
    const [kid, key] = keyPair.split(':');
    clearKeysObj[kid.trim()] = key.trim();
  }

  player.configure({
    drm: { clearKeys: clearKeysObj }
  });

  try {
    await player.load(mpdUrl);
    document.getElementById('videoTitle').innerText = 'Playing Stream';
  } catch (err) {
    console.error('Error loading stream:', err);
    alert('Stream load nahi ho saki. Token ya Link expire ho sakti hai.');
  }
}

function switchTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
  
  document.getElementById(tabId).classList.add('active');
  event.target.classList.add('active');
}


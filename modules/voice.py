"""
Voice Assistant Module — Speech Input & Text-to-Speech Output
Modul 4: Interaksi Suara (Web Speech API via Streamlit Components)
"""

import streamlit as st
import streamlit.components.v1 as components
from modules.utils import CARD_CSS


# ─── Web Speech API HTML component ──────────────────────────────────────────────
VOICE_INPUT_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { margin: 0; font-family: 'Segoe UI', sans-serif; background: transparent; }
  .voice-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    padding: 12px;
  }
  .mic-btn {
    width: 64px; height: 64px;
    border-radius: 50%;
    border: none;
    font-size: 28px;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 4px 14px rgba(37,99,235,0.3);
  }
  .mic-btn.idle    { background: linear-gradient(135deg,#2563EB,#7C3AED); color: white; }
  .mic-btn.listening { background: linear-gradient(135deg,#DC2626,#F59E0B); color: white; animation: pulse 1s infinite; }
  @keyframes pulse {
    0%,100% { box-shadow: 0 4px 14px rgba(220,38,38,0.4); }
    50%      { box-shadow: 0 4px 28px rgba(220,38,38,0.8); }
  }
  .status-text {
    font-size: 13px; color: #64748B; text-align: center;
    min-height: 18px;
  }
  .transcript-box {
    width: 100%; max-width: 420px;
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 14px;
    color: #1E293B;
    min-height: 44px;
    display: none;
  }
  .copy-btn {
    background: #2563EB; color: white;
    border: none; border-radius: 8px;
    padding: 8px 20px; font-size: 13px;
    cursor: pointer; display: none;
  }
  .copy-btn:hover { background: #1D4ED8; }
  .lang-select {
    border: 1px solid #E2E8F0; border-radius: 8px;
    padding: 6px 10px; font-size: 13px; color: #374151;
  }
  .not-supported { color: #DC2626; font-size: 13px; text-align: center; padding: 12px; }
</style>
</head>
<body>
<div class="voice-container">
  <select class="lang-select" id="langSelect">
    <option value="id-ID">🇮🇩 Bahasa Indonesia</option>
    <option value="en-US">🇺🇸 English (US)</option>
    <option value="en-GB">🇬🇧 English (UK)</option>
  </select>
  <button class="mic-btn idle" id="micBtn" onclick="toggleMic()">🎤</button>
  <div class="status-text" id="statusText">Tekan tombol mikrofon untuk mulai</div>
  <div class="transcript-box" id="transcriptBox"></div>
  <button class="copy-btn" id="copyBtn" onclick="sendTranscript()">✅ Gunakan Teks Ini</button>
</div>

<script>
let recognition = null;
let isListening = false;
let finalTranscript = '';

function checkSupport() {
  return ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window);
}

function initRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  const lang = document.getElementById('langSelect').value;
  recognition.lang = lang;
  recognition.continuous = false;
  recognition.interimResults = true;

  recognition.onstart = function() {
    isListening = true;
    document.getElementById('micBtn').className = 'mic-btn listening';
    document.getElementById('micBtn').textContent = '⏹️';
    document.getElementById('statusText').textContent = '🔴 Sedang mendengarkan...';
    finalTranscript = '';
  };

  recognition.onresult = function(event) {
    let interim = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      if (event.results[i].isFinal) {
        finalTranscript += event.results[i][0].transcript;
      } else {
        interim += event.results[i][0].transcript;
      }
    }
    const display = finalTranscript || interim;
    const box = document.getElementById('transcriptBox');
    box.style.display = 'block';
    box.textContent = display;
  };

  recognition.onerror = function(event) {
    stopListening();
    document.getElementById('statusText').textContent = '⚠️ Error: ' + event.error;
  };

  recognition.onend = function() {
    stopListening();
    if (finalTranscript.trim()) {
      document.getElementById('copyBtn').style.display = 'inline-block';
      document.getElementById('statusText').textContent = '✅ Selesai. Klik tombol untuk menggunakan teks.';
    }
  };
}

function stopListening() {
  isListening = false;
  document.getElementById('micBtn').className = 'mic-btn idle';
  document.getElementById('micBtn').textContent = '🎤';
  if (!finalTranscript) {
    document.getElementById('statusText').textContent = 'Tekan tombol mikrofon untuk mulai';
  }
}

function toggleMic() {
  if (!checkSupport()) {
    document.getElementById('statusText').textContent = '❌ Browser tidak mendukung Speech Recognition';
    return;
  }
  if (isListening) {
    recognition.stop();
  } else {
    initRecognition();
    recognition.start();
  }
}

function sendTranscript() {
  if (finalTranscript.trim()) {
    // Send to Streamlit via query param technique
    window.parent.postMessage({
      type: 'voice_transcript',
      text: finalTranscript.trim()
    }, '*');
    document.getElementById('statusText').textContent = '📤 Teks dikirim ke asisten!';
    document.getElementById('copyBtn').style.display = 'none';
    setTimeout(() => {
      document.getElementById('transcriptBox').style.display = 'none';
      document.getElementById('statusText').textContent = 'Tekan tombol mikrofon untuk mulai';
      finalTranscript = '';
    }, 2000);
  }
}

// Check browser support on load
if (!checkSupport()) {
  document.querySelector('.voice-container').innerHTML =
    '<div class="not-supported">❌ Browser ini tidak mendukung Web Speech API.<br>Gunakan Chrome atau Edge untuk fitur suara.</div>';
}
</script>
</body>
</html>
"""

TTS_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0">
<script>
function speakText(text, lang) {{
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  const utt = new SpeechSynthesisUtterance(text);
  utt.lang = lang || 'id-ID';
  utt.rate = 0.9;
  utt.pitch = 1.0;
  utt.volume = 1.0;
  // Pick best voice
  const voices = window.speechSynthesis.getVoices();
  const preferred = voices.find(v => v.lang === utt.lang);
  if (preferred) utt.voice = preferred;
  window.speechSynthesis.speak(utt);
}}
// Auto-speak on load
window.onload = function() {{
  setTimeout(() => speakText({text!r}, {lang!r}), 300);
}};
</script>
</body>
</html>
"""


def render_voice_input(key: str = "voice_input", height: int = 220) -> None:
    """Embed the voice input component."""
    components.html(VOICE_INPUT_HTML, height=height, scrolling=False)


def text_to_speech_html(text: str, lang: str = "id-ID") -> None:
    """Trigger browser TTS for the given text."""
    html = TTS_HTML_TEMPLATE.format(text=text, lang=lang)
    components.html(html, height=0, scrolling=False)


def render_voice_settings():
    """Voice settings & test page."""
    st.markdown(CARD_CSS, unsafe_allow_html=True)

    st.markdown("### 🎤 Pengaturan & Uji Coba Suara")

    st.markdown(
        """<div class='info-card'>
        <div class='card-header'>ℹ️ Tentang Fitur Suara</div>
        <b>Input Suara (Speech-to-Text)</b>: Menggunakan Web Speech API bawaan browser.
        Tersedia di Google Chrome, Microsoft Edge, dan browser modern berbasis Chromium.<br><br>
        <b>Output Suara (Text-to-Speech)</b>: Menggunakan Speech Synthesis API. Mendukung
        Bahasa Indonesia dan Bahasa Inggris.<br><br>
        <span class='badge badge-amber'>⚠️ Untuk input suara, pastikan kamu mengizinkan akses mikrofon saat browser meminta izin.</span>
        </div>""",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 🎙️ Uji Coba Input Suara")
        st.markdown("Klik tombol mikrofon di bawah dan bicara. Teks akan muncul secara real-time.")
        render_voice_input(key="settings_voice", height=230)

    with col2:
        st.markdown("#### 🔊 Uji Coba Output Suara (TTS)")

        tts_lang = st.selectbox(
            "Pilih Bahasa",
            options=["id-ID", "en-US", "en-GB"],
            format_func=lambda x: {
                "id-ID": "🇮🇩 Bahasa Indonesia",
                "en-US": "🇺🇸 English (US)",
                "en-GB": "🇬🇧 English (UK)",
            }.get(x, x),
        )

        tts_text = st.text_area(
            "Teks untuk diucapkan",
            value=(
                "Selamat datang di Holiday Planner! "
                "Itinerary liburanmu sudah siap. "
                "Hari pertama dimulai pukul delapan pagi."
            ),
            height=100,
        )

        if st.button("🔊 Putar Suara", type="primary", use_container_width=True):
            text_to_speech_html(text=tts_text, lang=tts_lang)
            st.success("🔊 Memutar suara... Pastikan volume perangkat menyala!")

    st.divider()

    st.markdown("#### ⚙️ Pengaturan Global Suara")
    c1, c2 = st.columns(2)
    with c1:
        enabled = st.toggle(
            "🔊 Aktifkan Voice Assistant",
            value=st.session_state.get("voice_enabled", True),
        )
        st.session_state.voice_enabled = enabled
    with c2:
        auto_read = st.toggle(
            "🤖 Baca otomatis setiap rekomendasi asisten",
            value=st.session_state.get("voice_auto_read", False),
        )
        st.session_state.voice_auto_read = auto_read

    if enabled:
        st.success("✅ Voice Assistant aktif — tombol 🎤 tersedia di seluruh aplikasi.")
    else:
        st.info("🔇 Voice Assistant dinonaktifkan. Beralih ke mode teks saja.")

    st.markdown(
        """<div class='info-card' style='margin-top:16px'>
        <div class='card-header'>📌 Cara Menggunakan Suara di Seluruh Aplikasi</div>
        <ol style='font-size:13px;color:#374151;margin:8px 0;padding-left:18px'>
          <li>Buka modul mana pun (Itinerary, Keberangkatan, Backup Darurat)</li>
          <li>Scroll ke bawah — temukan komponen <b>🎤 Ucapkan Pertanyaan</b></li>
          <li>Klik tombol mikrofon, izinkan akses mikrofon jika diminta</li>
          <li>Ucapkan pertanyaan atau perintah kamu dengan jelas</li>
          <li>Teks hasil akan muncul — klik <b>Gunakan Teks Ini</b> untuk kirim ke asisten</li>
        </ol>
        <b>Contoh perintah suara:</b><br>
        <span class='badge badge-blue'>"Hari ini Tanah Lot tutup, carikan alternatif"</span>
        <span class='badge badge-blue'>"Pesawat jam 7 pagi, hotel 45 menit dari bandara"</span>
        <span class='badge badge-blue'>"Tampilkan jadwal hari ke-2"</span>
        </div>""",
        unsafe_allow_html=True,
    )

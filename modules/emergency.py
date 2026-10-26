"""
Dynamic Itinerary & Emergency Backup Module
Modul 3: Real-time Rescheduling & Backup Viral Destination
"""

import streamlit as st
from datetime import datetime
from modules.utils import (
    CARD_CSS,
    rearrange_day,
    get_destinations,
    VIRAL_BACKUP_DESTINATIONS,
    format_activity_row,
    get_transport_icon,
    fmt_duration,
)


def render_emergency_module():
    st.markdown(CARD_CSS, unsafe_allow_html=True)

    st.markdown(
        """<div class='emergency-banner'>
        <b>🚨 Backup Darurat & Dynamic Rescheduling</b><br>
        <span style='font-size:13px'>
        Tempat tujuan tiba-tiba tutup? Jangan panik dan jangan balik ke penginapan!
        Laporkan ke asisten dan kami langsung carikan alternatif terbaik + susun ulang jadwal harimu seketika.
        </span>
        </div>""",
        unsafe_allow_html=True,
    )

    # Check if itinerary exists
    if not st.session_state.get("itinerary"):
        st.warning(
            "⚠️ Belum ada itinerary aktif. Buat itinerary dulu di menu **Susun Itinerary** ya!"
        )
        if st.button("📋 Buat Itinerary Sekarang", type="primary"):
            st.session_state.active_module = "itinerary"
            st.rerun()
        # Allow demo mode without itinerary
        st.markdown("---")
        st.markdown("#### 🎭 Atau coba Demo Mode di bawah ini:")
        _render_demo_mode()
        return

    itin = st.session_state.itinerary

    tab_report, tab_view = st.tabs(
        ["🚨 Laporkan Tempat Tutup", "📋 Lihat Itinerary Hari Ini (Setelah Revisi)"]
    )

    with tab_report:
        _render_report_form(itin)

    with tab_view:
        _render_revised_itinerary(itin)


def _render_report_form(itin: dict):
    st.markdown("### 📢 Tempat Tutup? Laporkan di sini!")

    # Select day
    day_options = [f"Hari {d['day_number']} — {d['label']}" for d in itin["days"]]
    sel_day = st.selectbox(
        "🗓️ Kamu sedang di hari ke berapa?",
        options=range(len(day_options)),
        format_func=lambda i: day_options[i],
        key="emerg_day_sel",
    )

    day_data = itin["days"][sel_day]
    activities = day_data["activities"]

    # Show non-buffer activities (real destinations)
    real_activities = [a for a in activities if not a.get("is_buffer")]
    if not real_activities:
        st.info("Tidak ada destinasi di hari ini.")
        return

    activity_names = [a["name"] for a in real_activities]
    closed_name = st.selectbox(
        "🔒 Destinasi mana yang TUTUP / tidak bisa dikunjungi?",
        options=activity_names,
        key="closed_dest_sel",
    )

    current_time = st.time_input(
        "🕐 Jam berapa sekarang?",
        value=datetime.now().replace(second=0, microsecond=0).time(),
    )

    reason = st.selectbox(
        "📋 Alasan tidak bisa dikunjungi",
        options=[
            "Tutup mendadak (tidak sesuai Google)",
            "Antrean terlalu panjang",
            "Cuaca buruk / ditutup sementara",
            "Harga tiket naik drastis",
            "Sudah pernah dikunjungi / bosan",
            "Alasan lainnya",
        ],
    )

    col1, col2 = st.columns(2)
    with col1:
        report_btn = st.button(
            "🚀 Carikan Alternatif & Susun Ulang!", type="primary", use_container_width=True
        )
    with col2:
        if st.button("🔄 Reset Perubahan Hari Ini", use_container_width=True):
            key = f"revised_day_{sel_day}"
            if key in st.session_state:
                del st.session_state[key]
            st.success("✅ Itinerary hari ini dikembalikan ke rencana awal.")
            st.rerun()

    if report_btn:
        city = itin["city"]
        destination_pool = get_destinations(city) + VIRAL_BACKUP_DESTINATIONS

        # Filter out already-scheduled destinations
        scheduled_names = {a["name"].replace("⭐ ", "") for a in activities}
        backup_pool = [d for d in destination_pool if d["name"] not in scheduled_names and d["name"] != closed_name.replace("⭐ ", "")]

        with st.spinner("🔍 Mencari destinasi alternatif terbaik..."):
            import time; time.sleep(0.8)  # UX feedback
            new_activities = rearrange_day(
                day_activities=activities,
                closed_activity_name=closed_name,
                backup_pool=backup_pool,
                current_time_str=current_time.strftime("%H:%M"),
            )

        # Save revised day
        revised_key = f"revised_day_{sel_day}"
        st.session_state[revised_key] = new_activities
        # Also update main itinerary
        st.session_state.itinerary["days"][sel_day]["activities"] = new_activities

        # Find the newly added backup activity
        backup_added = next(
            (a for a in new_activities if a.get("is_backup")), None
        )

        # Success banner
        st.markdown(
            f"""<div class='emergency-banner'>
            <b>✅ Itinerary berhasil diperbarui!</b><br>
            <span style='font-size:13px'>
            🔒 <b>{closed_name}</b> telah dihapus dari jadwal.<br>
            📍 Destinasi pengganti telah ditambahkan ke jadwalmu.
            </span>
            </div>""",
            unsafe_allow_html=True,
        )

        if backup_added:
            transport_icons = " ".join(
                get_transport_icon(t) for t in backup_added.get("transport", [])[:3]
            )
            st.markdown(
                f"""<div class='info-card'>
                <div class='card-header'>⭐ Destinasi Pengganti Viral</div>
                <div class='card-title'>{backup_added['name']}</div>
                <div style='margin-top:8px'>
                  <span class='badge badge-purple'>📂 {backup_added['category']}</span>
                  <span class='badge badge-blue'>⏱️ {fmt_duration(backup_added['duration'])}</span>
                  <span class='badge badge-green'>🕐 {backup_added['time']} – {backup_added['end_time']}</span>
                </div>
                <div style='margin-top:10px;font-size:13px;color:#374151'>{transport_icons} {backup_added.get('tip','')}</div>
                </div>""",
                unsafe_allow_html=True,
            )

        # Mood booster message
        mood_messages = [
            "😎 Jangan biarkan satu tempat tutup merusak hari liburanmu. Let's go!",
            "🎉 Destinasi pengganti sudah siap! Kadang perubahan rencana justru bikin kenangan terbaik.",
            "💪 Adventure traveler sejati selalu punya plan B. Kamu siap!",
            "✨ Great explorers never stay in the hotel. Let's discover something new!",
        ]
        import random
        st.success(random.choice(mood_messages))
        st.rerun()


def _render_revised_itinerary(itin: dict):
    st.markdown("### 📋 Itinerary Hari Ini (Kondisi Terkini)")

    day_options = [f"Hari {d['day_number']} — {d['label']}" for d in itin["days"]]
    sel_day = st.selectbox(
        "🗓️ Pilih hari",
        options=range(len(day_options)),
        format_func=lambda i: day_options[i],
        key="emerg_view_day",
    )

    day_data = itin["days"][sel_day]
    activities = day_data["activities"]

    is_revised = any(a.get("is_backup") for a in activities)
    has_removed = f"revised_day_{sel_day}" in st.session_state

    if is_revised:
        st.markdown(
            "<span class='badge badge-amber'>⚠️ Itinerary Telah Direvisi</span>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<span class='badge badge-green'>✅ Itinerary Original</span>",
            unsafe_allow_html=True,
        )

    rows_html = "".join(format_activity_row(a) for a in activities)
    st.markdown(
        f"<div class='timeline-wrap'>{rows_html}</div>", unsafe_allow_html=True
    )

    if is_revised:
        st.info(
            "🌟 Item bertanda ⭐ adalah destinasi pengganti yang baru ditambahkan. "
            "Jadwal telah dioptimalkan agar flow harimu tetap menyenangkan!"
        )


def _render_demo_mode():
    """Demo mode without an active itinerary."""
    st.markdown("### 🎭 Demo: Simulasi Tempat Tutup")

    sample_itinerary = [
        {"time": "08:00", "end_time": "08:30", "name": "☕ Sarapan & Persiapan", "duration": 0.5,
         "category": "Rutinitas", "tip": "", "transport": [], "is_buffer": True},
        {"time": "08:30", "end_time": "10:30", "name": "Tanah Lot Temple", "duration": 2.0,
         "category": "Budaya", "tip": "Datang sore hari untuk sunset terbaik.",
         "transport": ["taxi", "sewa_motor"], "open": "07:00", "close": "19:00", "is_buffer": False},
        {"time": "10:55", "end_time": "13:25", "name": "Ubud Monkey Forest", "duration": 1.5,
         "category": "Alam", "tip": "Jaga barang bawaan dari monyet.",
         "transport": ["taxi", "sewa_mobil"], "open": "08:30", "close": "18:00", "is_buffer": False},
        {"time": "13:25", "end_time": "14:25", "name": "🍽️ Makan Siang", "duration": 1.0,
         "category": "Kuliner", "tip": "Coba kuliner lokal!", "transport": [], "is_buffer": True},
        {"time": "14:25", "end_time": "16:55", "name": "Tegallalang Rice Terrace", "duration": 1.5,
         "category": "Alam", "tip": "Pagi hari cahaya terbaik untuk foto.",
         "transport": ["taxi", "sewa_motor"], "open": "08:00", "close": "18:00", "is_buffer": False},
    ]

    if "demo_activities" not in st.session_state:
        st.session_state.demo_activities = sample_itinerary.copy()

    st.markdown("**Itinerary Demo (Hari 1 - Bali):**")
    rows_html = "".join(format_activity_row(a) for a in st.session_state.demo_activities)
    st.markdown(f"<div class='timeline-wrap'>{rows_html}</div>", unsafe_allow_html=True)

    real = [a for a in st.session_state.demo_activities if not a.get("is_buffer")]
    closed = st.selectbox(
        "🔒 Simulasi: destinasi mana yang tutup?",
        options=[a["name"] for a in real],
        key="demo_closed",
    )

    if st.button("🚀 Simulasi Backup Plan!", type="primary", use_container_width=True):
        backup_pool = VIRAL_BACKUP_DESTINATIONS + [
            {
                "name": "Pantai Kuta",
                "avg_visit_hours": 2.5,
                "category": "Pantai",
                "tip": "Hindari siang hari, terlalu panas.",
                "transport": ["taxi", "ojek_online"],
            },
            {
                "name": "Seminyak Beach",
                "avg_visit_hours": 2.5,
                "category": "Pantai",
                "tip": "Area beach clubs populer.",
                "transport": ["taxi", "ojek_online"],
            },
        ]
        scheduled = {a["name"] for a in st.session_state.demo_activities}
        pool = [b for b in backup_pool if b["name"] not in scheduled]

        new_acts = rearrange_day(
            day_activities=st.session_state.demo_activities,
            closed_activity_name=closed,
            backup_pool=pool,
            current_time_str=datetime.now().strftime("%H:%M"),
        )
        st.session_state.demo_activities = new_acts
        st.success(f"✅ Demo berhasil! **{closed}** digantikan dengan destinasi baru.")
        st.rerun()

    if st.button("🔄 Reset Demo", use_container_width=True):
        st.session_state.demo_activities = sample_itinerary.copy()
        st.rerun()

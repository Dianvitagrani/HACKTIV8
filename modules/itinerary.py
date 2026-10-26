"""
Pre-Holiday Module — Itinerary Planning
Modul 1: Penyusunan Itinerary Cerdas
"""

import streamlit as st
from datetime import datetime, date, timedelta
from modules.utils import (
    build_itinerary,
    get_destinations,
    DESTINATION_DB,
    CARD_CSS,
    format_activity_row,
    fmt_duration,
    get_transport_icon,
    VIRAL_BACKUP_DESTINATIONS,
)

INTERESTS_OPTIONS = [
    "Pantai", "Alam", "Budaya", "Sejarah", "Hiburan", "Belanja", "Kuliner"
]

CITY_OPTIONS = list(DESTINATION_DB.keys())

def render_itinerary_module():
    st.markdown(CARD_CSS, unsafe_allow_html=True)

    # ── Sub-tabs ──────────────────────────────────────────────────────────────────
    tab_plan, tab_view = st.tabs(["📋 Buat Itinerary", "📅 Lihat Itinerary"])

    with tab_plan:
        _render_planner_form()

    with tab_view:
        _render_itinerary_viewer()


def _render_planner_form():
    st.markdown("### 🗺️ Detail Perjalanan")
    st.markdown("Isi informasi di bawah untuk menyusun itinerary cerdas hari per hari.")

    with st.form("itinerary_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            city = st.selectbox(
                "📍 Kota / Destinasi Utama",
                options=[c.title() for c in CITY_OPTIONS],
                help="Pilih kota tujuan liburanmu",
            )
        with c2:
            travelers = st.number_input(
                "👥 Jumlah Wisatawan",
                min_value=1, max_value=50, value=2,
                help="Termasuk kamu sendiri",
            )

        c3, c4 = st.columns(2)
        with c3:
            today = date.today()
            start_date = st.date_input(
                "📅 Tanggal Mulai Liburan",
                value=today + timedelta(days=7),
                min_value=today,
                help="Hari pertama tiba di destinasi",
            )
        with c4:
            end_date = st.date_input(
                "📅 Tanggal Selesai Liburan",
                value=today + timedelta(days=10),
                min_value=today + timedelta(days=1),
                help="Hari terakhir / hari kepulangan",
            )

        st.markdown("**🎯 Minat / Kategori Wisata** *(opsional)*")
        interests_selected = []
        cols = st.columns(len(INTERESTS_OPTIONS))
        for i, interest in enumerate(INTERESTS_OPTIONS):
            with cols[i]:
                if st.checkbox(interest, key=f"int_{interest}"):
                    interests_selected.append(interest)

        c5, c6 = st.columns(2)
        with c5:
            start_time = st.time_input(
                "⏰ Jam Mulai Aktivitas Harian",
                value=datetime.strptime("08:00", "%H:%M").time(),
            )
        with c6:
            end_time = st.time_input(
                "🌙 Jam Selesai Aktivitas Harian",
                value=datetime.strptime("21:00", "%H:%M").time(),
            )

        submitted = st.form_submit_button(
            "🚀 Susun Itinerary Sekarang!", type="primary", use_container_width=True
        )

    if submitted:
        if end_date <= start_date:
            st.error("⚠️ Tanggal selesai harus setelah tanggal mulai!")
            return

        num_days = (end_date - start_date).days + 1
        with st.spinner("⚙️ Menyusun itinerary cerdas untukmu..."):
            itinerary = build_itinerary(
                city=city,
                num_days=num_days,
                start_date=start_date.strftime("%Y-%m-%d"),
                travelers=travelers,
                interests=interests_selected,
                start_time_daily=start_time.strftime("%H:%M"),
                end_time_daily=end_time.strftime("%H:%M"),
            )

        st.session_state.itinerary = itinerary
        st.session_state.trip_info = {
            "destination": city,
            "start_date": start_date.strftime("%d %b %Y"),
            "end_date": end_date.strftime("%d %b %Y"),
            "travelers": travelers,
            "num_days": num_days,
        }
        st.session_state.active_module = "itinerary"
        st.success(f"✅ Itinerary {num_days} hari untuk {city} berhasil disusun!")
        st.rerun()


def _render_itinerary_viewer():
    if not st.session_state.get("itinerary"):
        st.markdown(
            """<div class='info-card' style='text-align:center;padding:40px'>
            <div style='font-size:48px'>🗓️</div>
            <div style='font-weight:700;font-size:18px;margin:12px 0'>Belum ada itinerary</div>
            <div style='color:#64748B'>Buat itinerary baru di tab <b>Buat Itinerary</b> terlebih dahulu.</div>
            </div>""",
            unsafe_allow_html=True,
        )
        return

    itin = st.session_state.itinerary
    info = st.session_state.trip_info

    # Trip summary banner
    st.markdown(
        f"""<div class='info-card'>
        <div class='card-header'>✈️ Trip Summary</div>
        <div class='card-title'>📍 {itin['city'].title()}</div>
        <div style='margin-top:8px'>
          <span class='badge badge-blue'>📅 {info.get('start_date')} → {info.get('end_date')}</span>
          <span class='badge badge-green'>👥 {itin['travelers']} orang</span>
          <span class='badge badge-purple'>🗓️ {itin['total_days']} hari</span>
        </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Day selector
    day_options = [f"Hari {d['day_number']} — {d['label']}" for d in itin["days"]]
    selected_day_idx = st.selectbox(
        "🗓️ Pilih Hari",
        options=range(len(day_options)),
        format_func=lambda i: day_options[i],
        key="day_selector",
    )
    st.session_state.current_day = selected_day_idx + 1

    day_data = itin["days"][selected_day_idx]
    _render_day_card(day_data)


def _render_day_card(day: dict):
    activities = day["activities"]

    st.markdown(
        f"""<div class='info-card'>
        <div class='card-header'>Jadwal Harian</div>
        <div class='card-title'>{day['label']}</div>
        <div style='margin-top:6px'>
          <span class='badge badge-blue'>📍 {sum(1 for a in activities if not a.get('is_buffer'))} destinasi</span>
          <span class='badge badge-green'>⏱️ {len(activities)} aktivitas</span>
        </div>
        </div>""",
        unsafe_allow_html=True,
    )

    rows_html = "".join(format_activity_row(a) for a in activities)
    st.markdown(
        f"<div class='timeline-wrap'>{rows_html}</div>", unsafe_allow_html=True
    )

    # Transport legend
    all_transports = set()
    for a in activities:
        for t in a.get("transport", []):
            all_transports.add(t)
    if all_transports:
        icons_html = " ".join(
            f"<span>{get_transport_icon(t)} {t.replace('_', ' ').title()}</span>"
            for t in sorted(all_transports)
        )
        st.markdown(
            f"<div class='info-card' style='font-size:13px'><span class='card-header'>🚗 Moda Transportasi Hari Ini</span><br>{icons_html}</div>",
            unsafe_allow_html=True,
        )

    # Quick tips
    with st.expander("💡 Tips & Catatan Hari Ini"):
        for act in activities:
            if act.get("tip") and not act.get("is_buffer"):
                st.markdown(f"- **{act['name']}**: {act['tip']}")
            if act.get("open") and act.get("close") and not act.get("is_buffer"):
                st.markdown(
                    f"  &nbsp;&nbsp;🕐 Jam buka: **{act['open']}** – **{act['close']}**"
                )

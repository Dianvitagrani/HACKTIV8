"""
Departure Time Management Module — H-1 & Hari-H
Modul 2: Manajemen Waktu Keberangkatan
"""

import streamlit as st
from datetime import datetime, timedelta
from modules.utils import (
    CARD_CSS,
    get_traffic_multiplier,
    parse_time,
    add_minutes,
    fmt_time,
)

# ─── Constants ───────────────────────────────────────────────────────────────────
# Indonesian airport buffer recommendations (minutes)
AIRPORT_BUFFERS = {
    "domestic": {
        "checkin_close":   45,   # check-in closes before departure
        "security_queue":  20,   # security screening
        "gate_walk_min":   10,   # min gate walking time
        "gate_walk_max":   25,   # max gate walking time
        "boarding_close":  15,   # boarding gate closes before departure
        "ideal_arrival":   90,   # ideal airport arrival before departure
        "safe_arrival":   120,   # safe (recommended) airport arrival
        "hero_arrival":   150,   # panic-free "hero" arrival
    },
    "international": {
        "checkin_close":   60,
        "security_queue":  35,
        "gate_walk_min":   15,
        "gate_walk_max":   40,
        "boarding_close":  20,
        "ideal_arrival":  150,
        "safe_arrival":   180,
        "hero_arrival":   240,
    },
}

def get_airport_buffer(flight_type: str) -> dict:
    return AIRPORT_BUFFERS.get(flight_type, AIRPORT_BUFFERS["domestic"])


def compute_hm1_recommendations(
    departure_time_str: str,
    hotel_to_airport_minutes: int,
    flight_type: str = "domestic",
) -> dict:
    """
    Compute H-1 wake-up & leave recommendations.
    Returns rich dict with all timestamps.
    """
    buf = get_airport_buffer(flight_type)
    dep = parse_time(departure_time_str)

    safe_airport_arrival   = dep - timedelta(minutes=buf["safe_arrival"])
    ideal_airport_arrival  = dep - timedelta(minutes=buf["ideal_arrival"])
    hero_airport_arrival   = dep - timedelta(minutes=buf["hero_arrival"])

    # Recommended leave time = safe arrival - travel duration
    rec_leave_safe  = safe_airport_arrival  - timedelta(minutes=hotel_to_airport_minutes)
    rec_leave_ideal = ideal_airport_arrival - timedelta(minutes=hotel_to_airport_minutes)
    rec_leave_hero  = hero_airport_arrival  - timedelta(minutes=hotel_to_airport_minutes)

    # Wake-up: 60 min before leaving (shower, pack, breakfast)
    wake_safe  = rec_leave_safe  - timedelta(minutes=60)
    wake_ideal = rec_leave_ideal - timedelta(minutes=60)

    # Traffic multiplier on the recommended departure hour
    traffic = get_traffic_multiplier(rec_leave_safe.hour)
    adjusted_travel = int(hotel_to_airport_minutes * traffic["multiplier"])
    rec_leave_traffic = safe_airport_arrival - timedelta(minutes=adjusted_travel)
    wake_traffic = rec_leave_traffic - timedelta(minutes=60)

    return {
        "departure_time": fmt_time(dep),
        "flight_type": flight_type,
        "hotel_to_airport_minutes": hotel_to_airport_minutes,
        "traffic": traffic,
        "adjusted_travel_minutes": adjusted_travel,
        # Tiers
        "hero": {
            "wake": fmt_time(wake_ideal - timedelta(minutes=30)),
            "leave": fmt_time(rec_leave_hero),
            "airport_arrival": fmt_time(hero_airport_arrival),
            "label": "🏆 Mode Hero (Santai Banget)",
            "status": "green",
            "desc": f"Tiba di bandara {buf['hero_arrival']} menit sebelum departure. Super aman!",
        },
        "recommended": {
            "wake": fmt_time(wake_safe),
            "leave": fmt_time(rec_leave_traffic),
            "airport_arrival": fmt_time(safe_airport_arrival),
            "label": "✅ Rekomendasi Asisten",
            "status": "green",
            "desc": f"Memperhitungkan kondisi lalu lintas '{traffic['label']}'. Waktu terbaik!",
        },
        "ideal": {
            "wake": fmt_time(wake_ideal),
            "leave": fmt_time(rec_leave_ideal),
            "airport_arrival": fmt_time(ideal_airport_arrival),
            "label": "⚡ Mode Ideal (Tepat Waktu)",
            "status": "amber",
            "desc": f"Tiba {buf['ideal_arrival']} menit sebelum departure. Masih oke asal tidak ada hambatan.",
        },
    }


def analyze_departure_hariH(
    flight_date: str,
    departure_time_str: str,
    gate_number: str,
    hotel_to_airport_minutes: int,
    flight_type: str = "domestic",
    current_time_str: str = None,
) -> dict:
    """
    Hari-H analysis: compare H-1 recs vs current traffic,
    calculate gate walking time, assess if still feasible.
    """
    if current_time_str is None:
        current_time_str = datetime.now().strftime("%H:%M")

    buf = get_airport_buffer(flight_type)
    dep = parse_time(departure_time_str)
    now = parse_time(current_time_str)

    # Current traffic
    traffic = get_traffic_multiplier(now.hour)
    actual_travel = int(hotel_to_airport_minutes * traffic["multiplier"])

    # Gate walk (based on gate number heuristic)
    gate_walk = _estimate_gate_walk(gate_number)

    # Earliest should-leave time right now
    airport_arrival_needed = dep - timedelta(
        minutes=buf["boarding_close"] + buf["security_queue"] + gate_walk
    )
    leave_now_latest = airport_arrival_needed - timedelta(minutes=actual_travel)

    minutes_until_must_leave = (leave_now_latest - now).total_seconds() / 60
    minutes_until_departure  = (dep - now).total_seconds() / 60

    # Status
    if minutes_until_must_leave > 60:
        status = "ok"
        status_label = "✅ Masih Sangat Aman"
        status_cls = "status-ok"
        advice = "Kamu masih punya waktu santai. Pastikan semua barang sudah di-pack!"
    elif minutes_until_must_leave > 20:
        status = "warning"
        status_label = "⚠️ Segera Bersiap"
        status_cls = "status-warn"
        advice = f"Sebaiknya berangkat dalam {int(minutes_until_must_leave)} menit ke depan!"
    elif minutes_until_must_leave > 0:
        status = "urgent"
        status_label = "🚨 Harus Berangkat SEKARANG!"
        status_cls = "status-danger"
        advice = "Tinggalkan hotel segera. Setiap menit sangat berharga!"
    else:
        status = "danger"
        status_label = "❌ Sangat Mepet / Kemungkinan Telat"
        status_cls = "status-danger"
        advice = "Segera hubungi airline. Pertimbangkan taksi ekspres atau ojek online."

    return {
        "flight_date": flight_date,
        "departure_time": fmt_time(dep),
        "gate": gate_number,
        "now": fmt_time(now),
        "traffic": traffic,
        "actual_travel_minutes": actual_travel,
        "gate_walk_minutes": gate_walk,
        "leave_latest": fmt_time(leave_now_latest),
        "airport_arrival_needed": fmt_time(airport_arrival_needed),
        "minutes_until_must_leave": max(0, int(minutes_until_must_leave)),
        "minutes_until_departure": max(0, int(minutes_until_departure)),
        "status": status,
        "status_label": status_label,
        "status_cls": status_cls,
        "advice": advice,
    }


def _estimate_gate_walk(gate_str: str) -> int:
    """Estimate walking time (minutes) to gate from security exit."""
    if not gate_str:
        return 15
    gate_str = gate_str.upper().strip()
    # International terminals tend to be farther
    if any(c in gate_str for c in ["D", "E", "F"]):
        return 20
    if any(c in gate_str for c in ["C"]):
        return 15
    # Domestic closer gates
    try:
        num = int("".join(filter(str.isdigit, gate_str)))
        if num > 20:
            return 18
        elif num > 10:
            return 12
        return 8
    except ValueError:
        return 12


# ─── Streamlit UI ────────────────────────────────────────────────────────────────
def render_departure_module():
    st.markdown(CARD_CSS, unsafe_allow_html=True)

    tab_hm1, tab_harih = st.tabs(["🌙 H-1 Keberangkatan", "🛫 Hari-H Analisis Ulang"])

    with tab_hm1:
        _render_hm1_tab()

    with tab_harih:
        _render_harih_tab()


def _render_hm1_tab():
    st.markdown("### 🌙 Rekomendasi Waktu Berangkat (H-1)")
    st.markdown(
        "<div class='info-card'><b>💡 Kenapa H-1?</b> Banyak orang Indonesia suka 'mepet'. "
        "Asisten ini menghitung waktu bangun & berangkat yang ideal agar kamu tiba di bandara "
        "dengan nyaman tanpa drama panik!</div>",
        unsafe_allow_html=True,
    )

    with st.form("hm1_form"):
        c1, c2 = st.columns(2)
        with c1:
            dep_time = st.time_input(
                "✈️ Jam Keberangkatan (Departure Time)",
                value=datetime.strptime("07:00", "%H:%M").time(),
            )
        with c2:
            flight_type = st.radio(
                "🌐 Jenis Penerbangan",
                options=["domestic", "international"],
                format_func=lambda x: "🇮🇩 Domestik" if x == "domestic" else "🌍 Internasional",
                horizontal=True,
            )

        hotel_dist = st.slider(
            "🏨 Perkiraan Jarak Hotel → Bandara (menit normal)",
            min_value=10, max_value=120, value=30, step=5,
            help="Waktu tempuh tanpa lalu lintas",
        )

        submitted = st.form_submit_button("⏰ Hitung Waktu Ideal", type="primary", use_container_width=True)

    if submitted:
        result = compute_hm1_recommendations(
            departure_time_str=dep_time.strftime("%H:%M"),
            hotel_to_airport_minutes=hotel_dist,
            flight_type=flight_type,
        )
        _render_hm1_result(result)

    # Show persisted result
    if "hm1_result" in st.session_state:
        _render_hm1_result(st.session_state.hm1_result)


def _render_hm1_result(result: dict):
    st.session_state.hm1_result = result
    traffic = result["traffic"]
    traffic_cls = {"red": "badge-red", "amber": "badge-amber", "green": "badge-green"}.get(
        traffic["color"], "badge-blue"
    )

    st.markdown(
        f"""<div class='info-card'>
        <div class='card-header'>Kondisi Lalu Lintas Terprediksi</div>
        <span class='badge {traffic_cls}'>{traffic['label']}</span>
        <span class='badge badge-blue'>🚗 Jarak normal: {result['hotel_to_airport_minutes']} mnt</span>
        <span class='badge badge-amber'>🕐 Estimasi dengan traffic: {result['adjusted_travel_minutes']} mnt</span>
        </div>""",
        unsafe_allow_html=True,
    )

    tiers = ["hero", "recommended", "ideal"]
    tier_data = [result[t] for t in tiers]
    cols = st.columns(3)

    for col, tier, key in zip(cols, tier_data, tiers):
        with col:
            cls = "status-ok" if tier["status"] == "green" else "status-warn"
            st.markdown(
                f"""<div class='dep-card {cls}'>
                <div style='font-size:12px;font-weight:600;margin-bottom:8px'>{tier['label']}</div>
                <div class='dep-label'>⏰ Bangun</div>
                <div class='dep-time'>{tier['wake']}</div>
                <div class='dep-label' style='margin-top:8px'>🚗 Berangkat</div>
                <div style='font-size:22px;font-weight:700;color:#0F172A'>{tier['leave']}</div>
                <div class='dep-label' style='margin-top:8px'>🛬 Tiba Bandara</div>
                <div style='font-size:18px;font-weight:600;color:#374151'>{tier['airport_arrival']}</div>
                <div style='font-size:11px;margin-top:10px;color:#374151'>{tier['desc']}</div>
                </div>""",
                unsafe_allow_html=True,
            )

    st.info(
        f"✈️ Jam Keberangkatan: **{result['departure_time']}** | "
        f"Penerbangan: **{'Domestik' if result['flight_type'] == 'domestic' else 'Internasional'}**"
    )


def _render_harih_tab():
    st.markdown("### 🛫 Analisis Hari-H (Real-time)")
    st.markdown(
        "<div class='info-card'><b>🔄 Analisis Ulang</b>: Asisten membandingkan kondisi lalu lintas "
        "saat ini dengan rekomendasi kemarin, memperhitungkan waktu jalan menuju gate, "
        "dan memastikan kamu masih bisa catch your flight!</div>",
        unsafe_allow_html=True,
    )

    with st.form("harih_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            flight_date = st.date_input("📅 Tanggal Penerbangan", value=datetime.today())
        with c2:
            dep_time = st.time_input(
                "✈️ Departure Time",
                value=datetime.strptime("10:00", "%H:%M").time(),
            )
        with c3:
            gate = st.text_input("🚪 Nomor Gate", value="B12", placeholder="Contoh: A5, C22, D01")

        c4, c5 = st.columns(2)
        with c4:
            current_time = st.time_input(
                "🕐 Waktu Sekarang (Real-time)",
                value=datetime.now().replace(second=0, microsecond=0).time(),
                help="Otomatis terisi waktu saat ini",
            )
        with c5:
            hotel_dist = st.slider("🏨 Jarak Hotel → Bandara (mnt normal)", 10, 120, 30, 5)

        flight_type = st.radio(
            "🌐 Jenis Penerbangan",
            options=["domestic", "international"],
            format_func=lambda x: "🇮🇩 Domestik" if x == "domestic" else "🌍 Internasional",
            horizontal=True,
        )

        submitted = st.form_submit_button(
            "🔍 Analisis Sekarang", type="primary", use_container_width=True
        )

    if submitted:
        analysis = analyze_departure_hariH(
            flight_date=flight_date.strftime("%d %B %Y"),
            departure_time_str=dep_time.strftime("%H:%M"),
            gate_number=gate,
            hotel_to_airport_minutes=hotel_dist,
            flight_type=flight_type,
            current_time_str=current_time.strftime("%H:%M"),
        )
        _render_harih_result(analysis)

    if "harih_result" in st.session_state:
        _render_harih_result(st.session_state.harih_result)


def _render_harih_result(r: dict):
    st.session_state.harih_result = r
    traffic = r["traffic"]
    traffic_cls = {"red": "badge-red", "amber": "badge-amber", "green": "badge-green"}.get(
        traffic["color"], "badge-blue"
    )

    # Status banner
    st.markdown(
        f"""<div class='dep-card {r['status_cls']}'>
        <div style='font-size:20px;font-weight:700'>{r['status_label']}</div>
        <div style='font-size:14px;margin-top:6px'>{r['advice']}</div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Details grid
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""<div class='info-card'>
            <div class='card-header'>⏰ Waktu Saat Ini</div>
            <div class='dep-time'>{r['now']}</div>
            <div class='dep-label'>Penerbangan: {r['departure_time']}</div>
            <div class='dep-label'>Gate: <b>{r['gate']}</b></div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""<div class='info-card'>
            <div class='card-header'>🚗 Kondisi Traffic Sekarang</div>
            <span class='badge {traffic_cls}'>{traffic['label']}</span>
            <div style='margin-top:8px'>
              <div class='dep-label'>Waktu tempuh perjalanan</div>
              <div style='font-size:22px;font-weight:700'>{r['actual_travel_minutes']} mnt</div>
            </div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""<div class='info-card'>
            <div class='card-header'>🚶 Walking ke Gate {r['gate']}</div>
            <div style='font-size:22px;font-weight:700'>{r['gate_walk_minutes']} mnt</div>
            <div class='dep-label' style='margin-top:8px'>⚠️ Batas akhir berangkat</div>
            <div style='font-size:20px;font-weight:700;color:#DC2626'>{r['leave_latest']}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    # Countdown info
    if r["minutes_until_must_leave"] > 0:
        st.markdown(
            f"""<div class='info-card'>
            <div style='text-align:center'>
              <div class='dep-label'>⏳ Sisa waktu sebelum HARUS berangkat</div>
              <div style='font-size:42px;font-weight:800;color:#2563EB'>{r['minutes_until_must_leave']} menit</div>
              <div style='color:#64748B;font-size:13px'>Waktu keberangkatan pesawat dalam {r['minutes_until_departure']} menit</div>
            </div>
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.error("⏰ Kamu sudah melewati batas waktu aman! Segera hubungi airline atau counter check-in.")

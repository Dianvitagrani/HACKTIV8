"""
Hotel Recommendation Module
Rekomendasi penginapan strategis berdasarkan kedekatan ke itinerary.
"""

import streamlit as st
from modules.utils import (
    CARD_CSS,
    recommend_hotels,
    get_hotels,
    fmt_price,
    fmt_duration,
    HOTEL_DB,
)

STAR_MAP = {1: "⭐", 2: "⭐⭐", 3: "⭐⭐⭐", 4: "⭐⭐⭐⭐", 5: "⭐⭐⭐⭐⭐"}
CITY_OPTIONS = list(HOTEL_DB.keys())


def _strategic_label(avg_min: float) -> tuple[str, str]:
    """Return (label, badge_class) based on average travel time."""
    if avg_min <= 20:
        return "🏆 Sangat Strategis", "badge-green"
    elif avg_min <= 35:
        return "✅ Strategis", "badge-blue"
    elif avg_min <= 55:
        return "⚡ Cukup Strategis", "badge-amber"
    else:
        return "🚗 Perlu Perjalanan Jauh", "badge-red"


def _coverage_label(pct: int) -> tuple[str, str]:
    if pct >= 80:
        return f"📍 Menjangkau {pct}% destinasi", "badge-green"
    elif pct >= 50:
        return f"📍 Menjangkau {pct}% destinasi", "badge-amber"
    else:
        return f"📍 Menjangkau {pct}% destinasi", "badge-red"


def render_hotel_module():
    st.markdown(CARD_CSS, unsafe_allow_html=True)

    # Extra hotel card CSS
    st.markdown(
        """<style>
        .hotel-card{background:white;border-radius:14px;padding:20px;border:1px solid #E2E8F0;
            margin:10px 0;box-shadow:0 1px 4px rgba(0,0,0,.06);transition:box-shadow .2s}
        .hotel-rank{width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#2563EB,#7C3AED);
            color:white;font-weight:700;font-size:14px;display:flex;align-items:center;
            justify-content:center;flex-shrink:0}
        .hotel-name{font-size:17px;font-weight:700;color:#0F172A}
        .hotel-area{font-size:13px;color:#64748B}
        .hotel-price{font-size:15px;font-weight:700;color:#2563EB}
        .score-bar-wrap{background:#F1F5F9;border-radius:99px;height:8px;overflow:hidden;margin:6px 0}
        .score-bar{height:8px;border-radius:99px;background:linear-gradient(90deg,#22C55E,#2563EB)}
        .dest-chip{display:inline-block;background:#F8FAFC;border:1px solid #E2E8F0;
            border-radius:8px;padding:3px 8px;font-size:11px;color:#374151;margin:2px}
        .dest-chip-fast{background:#DCFCE7;border-color:#86EFAC;color:#15803D}
        .dest-chip-med{background:#FEF3C7;border-color:#FCD34D;color:#92400E}
        .dest-chip-slow{background:#FEE2E2;border-color:#FCA5A5;color:#DC2626}
        </style>""",
        unsafe_allow_html=True,
    )

    # ── Header info box ────────────────────────────────────────────────────────
    st.markdown(
        """<div class='info-card' style='border-left:4px solid #2563EB'>
        <b>🏨 Cara Kerja Rekomendasi Strategis</b><br>
        <span style='font-size:13px;color:#374151'>
        Sistem membaca <b>seluruh destinasi di itinerary kamu</b>, lalu menghitung
        rata-rata waktu tempuh dari setiap penginapan ke semua destinasi tersebut.
        Penginapan dengan rata-rata tempuh terpendek <b>dan</b> cakupan destinasi terluas
        mendapat peringkat tertinggi — bukan sekadar yang paling murah atau paling mewah.
        </span>
        </div>""",
        unsafe_allow_html=True,
    )

    # ── Two modes: with itinerary or standalone ────────────────────────────────
    has_itinerary = bool(st.session_state.get("itinerary"))

    if has_itinerary:
        _render_with_itinerary()
    else:
        _render_standalone()


# ─── Mode 1: Itinerary already exists ────────────────────────────────────────────
def _render_with_itinerary():
    itin  = st.session_state.itinerary
    info  = st.session_state.trip_info
    city  = itin["city"]

    st.markdown(
        f"""<div class='info-card'>
        <div class='card-header'>Trip Aktif</div>
        <div class='card-title'>📍 {city.title()}</div>
        <span class='badge badge-blue'>📅 {info.get('start_date')} → {info.get('end_date')}</span>
        <span class='badge badge-purple'>🗓️ {info.get('num_days')} hari</span>
        <span class='badge badge-green'>👥 {info.get('travelers')} orang</span>
        </div>""",
        unsafe_allow_html=True,
    )

    # Filter controls
    with st.expander("⚙️ Filter Penginapan", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            stars_min = st.select_slider(
                "⭐ Minimal Bintang",
                options=[1, 2, 3, 4, 5],
                value=1,
                format_func=lambda x: STAR_MAP[x],
            )
        with c2:
            budget_options = {
                "Semua harga": None,
                "s/d Rp 500rb": 500_000,
                "s/d Rp 1 juta": 1_000_000,
                "s/d Rp 2 juta": 2_000_000,
                "s/d Rp 5 juta": 5_000_000,
            }
            budget_label = st.selectbox("💰 Budget Maks / Malam", list(budget_options.keys()))
            budget_max = budget_options[budget_label]
        with c3:
            sort_by = st.radio(
                "📊 Urut Berdasarkan",
                options=["🏆 Paling Strategis", "💰 Harga Termurah", "⭐ Bintang Tertinggi"],
                index=0,
            )

    results = recommend_hotels(city, itin, budget_max=budget_max, stars_min=stars_min)

    if sort_by == "💰 Harga Termurah":
        results.sort(key=lambda h: h["price_min"])
    elif sort_by == "⭐ Bintang Tertinggi":
        results.sort(key=lambda h: -h["stars"])

    if not results:
        st.warning("⚠️ Tidak ada penginapan yang cocok dengan filter kamu. Coba perlonggar filter.")
        return

    st.markdown(f"#### 🏨 {len(results)} Penginapan Ditemukan")
    _render_hotel_list(results, show_travel_detail=True)


# ─── Mode 2: No itinerary yet — standalone search ────────────────────────────────
def _render_standalone():
    st.warning(
        "⚠️ Belum ada itinerary aktif. Hasil rekomendasi akan menampilkan semua penginapan "
        "tanpa analisis waktu tempuh personal. Buat itinerary dulu untuk hasil terbaik!"
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        city = st.selectbox(
            "📍 Pilih Kota",
            options=[c.title() for c in CITY_OPTIONS],
        )
    with col2:
        stars_min = st.select_slider(
            "⭐ Minimal Bintang",
            options=[1, 2, 3, 4, 5],
            value=1,
            format_func=lambda x: STAR_MAP[x],
        )

    hotels = [h for h in get_hotels(city) if h["stars"] >= stars_min]

    if st.button("🏨 Tampilkan Penginapan", type="primary"):
        st.session_state["standalone_hotels"] = hotels
        st.session_state["standalone_city"]   = city

    if "standalone_hotels" in st.session_state:
        _render_hotel_list(st.session_state["standalone_hotels"], show_travel_detail=False)

    st.divider()
    if st.button("➕ Buat Itinerary Sekarang untuk Rekomendasi Akurat", type="primary", use_container_width=True):
        st.session_state.active_module = "itinerary"
        st.rerun()


# ─── Hotel card renderer ─────────────────────────────────────────────────────────
def _render_hotel_list(hotels: list, show_travel_detail: bool = True):
    for rank, hotel in enumerate(hotels, 1):
        _render_hotel_card(hotel, rank, show_travel_detail)


def _render_hotel_card(hotel: dict, rank: int, show_travel_detail: bool):
    strat_label, strat_cls = _strategic_label(hotel.get("avg_travel_minutes", 999))
    cov_label, cov_cls     = _coverage_label(hotel.get("coverage_pct", 0))

    # Score bar width (100% = best, inversely proportional to strategic_score)
    score = hotel.get("strategic_score", 999)
    bar_width = max(5, min(100, int(100 - (score / 150) * 100)))

    facilities_html = " ".join(
        f"<span style='background:#F1F5F9;border-radius:6px;padding:2px 8px;"
        f"font-size:11px;color:#374151;margin:2px;display:inline-block'>{f}</span>"
        for f in hotel.get("facilities", [])
    )

    # Build travel-time chips for matched destinations
    dest_chips_html = ""
    if show_travel_detail and hotel.get("matched_destinations"):
        chips = []
        for dest_name, minutes in hotel["matched_destinations"]:
            if minutes <= 20:
                cls = "dest-chip dest-chip-fast"
            elif minutes <= 40:
                cls = "dest-chip dest-chip-med"
            else:
                cls = "dest-chip dest-chip-slow"
            chips.append(f"<span class='{cls}'>{dest_name} · {minutes} mnt</span>")
        dest_chips_html = "".join(chips)

    avg_travel_html = ""
    if show_travel_detail and hotel.get("avg_travel_minutes") is not None:
        avg = hotel["avg_travel_minutes"]
        mx  = hotel.get("max_travel_minutes", avg)
        avg_travel_html = f"""
        <div style='margin-top:12px'>
          <div style='font-size:11px;color:#64748B;margin-bottom:4px'>
            📊 Skor Strategis (lebih penuh = lebih baik)
          </div>
          <div class='score-bar-wrap'>
            <div class='score-bar' style='width:{bar_width}%'></div>
          </div>
          <div style='display:flex;justify-content:space-between;font-size:11px;color:#64748B'>
            <span>⌀ tempuh: <b>{avg} mnt</b></span>
            <span>maks: <b>{mx} mnt</b></span>
            <span>
              <span class='badge {cov_cls}' style='font-size:10px'>{cov_label}</span>
            </span>
          </div>
        </div>
        <div style='margin-top:10px;font-size:12px;font-weight:600;color:#374151;margin-bottom:4px'>
          🗺️ Waktu Tempuh ke Destinasi Itinerary:
        </div>
        <div>{dest_chips_html if dest_chips_html else '<span style="font-size:12px;color:#94A3B8">Tidak ada data tempuh untuk destinasi itinerary ini.</span>'}</div>
        """

    col_rank, col_body = st.columns([1, 11])
    with col_rank:
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, str(rank))
        st.markdown(
            f"<div style='text-align:center;padding-top:22px;font-size:20px'>{medal}</div>",
            unsafe_allow_html=True,
        )

    with col_body:
        st.markdown(
            f"""<div class='hotel-card'>
            <div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px'>
              <div>
                <div class='hotel-name'>{hotel['name']}</div>
                <div class='hotel-area'>📍 {hotel['area']} &nbsp;·&nbsp; {STAR_MAP.get(hotel['stars'], '')}</div>
              </div>
              <div style='text-align:right'>
                <div class='hotel-price'>{fmt_price(hotel['price_min'])} – {fmt_price(hotel['price_max'])}</div>
                <div style='font-size:11px;color:#64748B'>per malam</div>
              </div>
            </div>
            <div style='margin-top:8px'>
              <span class='badge {strat_cls}'>{strat_label}</span>
            </div>
            <div style='margin-top:10px;font-size:12px;color:#374151'>
              💡 {hotel.get('tip', '')}
            </div>
            <div style='margin-top:8px'>{facilities_html}</div>
            {avg_travel_html}
            </div>""",
            unsafe_allow_html=True,
        )

    with col_body:
        with st.expander(f"📋 Detail Lengkap — {hotel['name']}"):
            if show_travel_detail and hotel.get("matched_destinations"):
                st.markdown("**🗺️ Tabel Waktu Tempuh ke Setiap Destinasi**")
                rows = []
                for d, m in hotel["matched_destinations"]:
                    if m <= 20:
                        status = "🟢 Sangat Dekat"
                    elif m <= 40:
                        status = "🟡 Terjangkau"
                    else:
                        status = "🔴 Perlu Waktu"
                    rows.append({"Destinasi": d, "Waktu Tempuh (menit)": m, "Status": status})

                if rows:
                    import pandas as pd
                    df = pd.DataFrame(rows)
                    st.dataframe(df, use_container_width=True, hide_index=True)

            st.markdown("**🏨 Fasilitas:**")
            for f in hotel.get("facilities", []):
                st.markdown(f"- {f}")

            if show_travel_detail:
                st.markdown(
                    f"**📊 Ringkasan Strategis:**  \n"
                    f"Rata-rata waktu tempuh: **{hotel.get('avg_travel_minutes')} menit**  \n"
                    f"Waktu tempuh terlama: **{hotel.get('max_travel_minutes')} menit**  \n"
                    f"Cakupan destinasi: **{hotel.get('coverage_pct')}%**"
                )

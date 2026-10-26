"""
Shared utilities, constants, and mock data for Holiday Planner.
"""

from datetime import datetime, timedelta

# ─── Transport modes ─────────────────────────────────────────────────────────────
TRANSPORT_ICONS = {
    "taxi": "🚕",
    "ojek_online": "🛵",
    "bus": "🚌",
    "kereta": "🚆",
    "mrt": "🚇",
    "lrt": "🚈",
    "jalan_kaki": "🚶",
    "sepeda": "🚲",
    "sewa_motor": "🏍️",
    "sewa_mobil": "🚗",
    "kapal": "⛴️",
    "shuttle": "🚐",
}

def get_transport_icon(mode: str) -> str:
    return TRANSPORT_ICONS.get(mode.lower(), "🚗")

# ─── Sample destination database ────────────────────────────────────────────────
DESTINATION_DB = {
    "bali": [
        {
            "name": "Tanah Lot Temple",
            "avg_visit_hours": 2.0,
            "open": "07:00", "close": "19:00",
            "category": "Budaya",
            "tip": "Datang sore hari untuk sunset terbaik.",
            "transport": ["taxi", "sewa_motor", "ojek_online"],
            "backup_for": ["pantai"],
        },
        {
            "name": "Pantai Kuta",
            "avg_visit_hours": 2.5,
            "open": "06:00", "close": "22:00",
            "category": "Pantai",
            "tip": "Hindari siang hari, terlalu panas.",
            "transport": ["taxi", "ojek_online", "sewa_motor"],
            "backup_for": ["pantai", "outdoor"],
        },
        {
            "name": "Ubud Monkey Forest",
            "avg_visit_hours": 1.5,
            "open": "08:30", "close": "18:00",
            "category": "Alam",
            "tip": "Jaga barang bawaan dari monyet.",
            "transport": ["taxi", "sewa_mobil"],
            "backup_for": ["alam", "outdoor"],
        },
        {
            "name": "Tegallalang Rice Terrace",
            "avg_visit_hours": 1.5,
            "open": "08:00", "close": "18:00",
            "category": "Alam",
            "tip": "Pagi hari cahaya terbaik untuk foto.",
            "transport": ["taxi", "sewa_motor"],
            "backup_for": ["alam"],
        },
        {
            "name": "Seminyak Beach",
            "avg_visit_hours": 2.5,
            "open": "06:00", "close": "22:00",
            "category": "Pantai",
            "tip": "Area beach clubs populer, cocok untuk sunset.",
            "transport": ["taxi", "ojek_online"],
            "backup_for": ["pantai"],
        },
        {
            "name": "Pura Besakih",
            "avg_visit_hours": 2.0,
            "open": "08:00", "close": "17:00",
            "category": "Budaya",
            "tip": "Bawa sarung, tersedia sewaan di pintu masuk.",
            "transport": ["taxi", "sewa_mobil"],
            "backup_for": ["budaya"],
        },
        {
            "name": "Nusa Dua Beach",
            "avg_visit_hours": 3.0,
            "open": "06:00", "close": "20:00",
            "category": "Pantai",
            "tip": "Air lebih tenang, cocok untuk snorkeling.",
            "transport": ["taxi", "sewa_mobil"],
            "backup_for": ["pantai"],
        },
        {
            "name": "Waterbom Bali",
            "avg_visit_hours": 4.0,
            "open": "09:00", "close": "18:00",
            "category": "Hiburan",
            "tip": "Datang pagi untuk menghindari antrian.",
            "transport": ["taxi", "ojek_online"],
            "backup_for": ["hiburan"],
        },
        {
            "name": "Pasar Seni Sukawati",
            "avg_visit_hours": 1.5,
            "open": "08:00", "close": "18:00",
            "category": "Belanja",
            "tip": "Tawar-menawar harga adalah hal biasa.",
            "transport": ["taxi", "sewa_motor"],
            "backup_for": ["belanja"],
        },
        {
            "name": "Uluwatu Temple",
            "avg_visit_hours": 2.0,
            "open": "09:00", "close": "21:00",
            "category": "Budaya",
            "tip": "Tonton Kecak Dance saat sunset (mulai 18:00).",
            "transport": ["taxi", "sewa_motor"],
            "backup_for": ["budaya"],
        },
    ],
    "yogyakarta": [
        {
            "name": "Candi Borobudur",
            "avg_visit_hours": 3.0,
            "open": "06:00", "close": "17:00",
            "category": "Sejarah",
            "tip": "Sunrise tour tersedia mulai 04:30.",
            "transport": ["bus", "taxi", "sewa_motor"],
            "backup_for": ["sejarah", "budaya"],
        },
        {
            "name": "Candi Prambanan",
            "avg_visit_hours": 2.5,
            "open": "06:00", "close": "17:00",
            "category": "Sejarah",
            "tip": "Sore hari lebih sejuk untuk eksplorasi.",
            "transport": ["bus", "taxi", "sewa_motor"],
            "backup_for": ["sejarah"],
        },
        {
            "name": "Kraton Yogyakarta",
            "avg_visit_hours": 2.0,
            "open": "08:30", "close": "14:00",
            "category": "Budaya",
            "tip": "Tutup hari Jumat. Perhatikan jadwal pertunjukan.",
            "transport": ["becak", "taxi", "jalan_kaki"],
            "backup_for": ["budaya", "sejarah"],
        },
        {
            "name": "Malioboro Street",
            "avg_visit_hours": 2.5,
            "open": "08:00", "close": "22:00",
            "category": "Belanja",
            "tip": "Belanja batik & oleh-oleh khas Jogja.",
            "transport": ["jalan_kaki", "becak", "taxi"],
            "backup_for": ["belanja"],
        },
        {
            "name": "Pantai Parangtritis",
            "avg_visit_hours": 2.5,
            "open": "06:00", "close": "18:00",
            "category": "Pantai",
            "tip": "Ombak besar, hindari berenang terlalu jauh.",
            "transport": ["bus", "taxi"],
            "backup_for": ["pantai"],
        },
        {
            "name": "Hutan Pinus Mangunan",
            "avg_visit_hours": 2.0,
            "open": "07:00", "close": "17:00",
            "category": "Alam",
            "tip": "Pagi hari ada kabut indah untuk foto.",
            "transport": ["taxi", "sewa_motor"],
            "backup_for": ["alam"],
        },
    ],
    "jakarta": [
        {
            "name": "Kota Tua Jakarta",
            "avg_visit_hours": 3.0,
            "open": "09:00", "close": "20:00",
            "category": "Sejarah",
            "tip": "Museum Fatahillah wajib dikunjungi.",
            "transport": ["mrt", "bus", "ojek_online"],
            "backup_for": ["sejarah", "budaya"],
        },
        {
            "name": "Ancol Dreamland",
            "avg_visit_hours": 4.0,
            "open": "07:00", "close": "22:00",
            "category": "Hiburan",
            "tip": "Banyak wahana, siapkan biaya ekstra.",
            "transport": ["bus", "taxi", "ojek_online"],
            "backup_for": ["hiburan"],
        },
        {
            "name": "Grand Indonesia Mall",
            "avg_visit_hours": 3.0,
            "open": "10:00", "close": "22:00",
            "category": "Belanja",
            "tip": "Terhubung langsung dengan MRT Bundaran HI.",
            "transport": ["mrt", "taxi", "ojek_online"],
            "backup_for": ["belanja", "indoor"],
        },
        {
            "name": "TMII (Taman Mini Indonesia Indah)",
            "avg_visit_hours": 4.0,
            "open": "07:00", "close": "20:00",
            "category": "Budaya",
            "tip": "Sangat luas, gunakan kereta mini di dalam.",
            "transport": ["bus", "taxi"],
            "backup_for": ["budaya", "alam"],
        },
    ],
    "lombok": [
        {
            "name": "Pantai Kuta Lombok",
            "avg_visit_hours": 2.5,
            "open": "06:00", "close": "18:00",
            "category": "Pantai",
            "tip": "Berbeda dengan Kuta Bali — lebih sepi dan eksotis.",
            "transport": ["taxi", "sewa_motor"],
            "backup_for": ["pantai"],
        },
        {
            "name": "Gili Trawangan",
            "avg_visit_hours": 5.0,
            "open": "00:00", "close": "23:59",
            "category": "Pantai",
            "tip": "Tidak ada kendaraan bermotor, sewa sepeda.",
            "transport": ["kapal", "sepeda"],
            "backup_for": ["pantai"],
        },
        {
            "name": "Gunung Rinjani Base Camp",
            "avg_visit_hours": 6.0,
            "open": "07:00", "close": "17:00",
            "category": "Alam",
            "tip": "Perlu guide resmi dan persiapan fisik.",
            "transport": ["taxi", "sewa_motor"],
            "backup_for": ["alam"],
        },
    ],
}

# Generic fallback destinations (viral spots)
VIRAL_BACKUP_DESTINATIONS = [
    {
        "name": "Kafe Instagrammable Terdekat",
        "avg_visit_hours": 1.5,
        "category": "Kuliner",
        "tip": "Cek Google Maps filter 'Highly Rated' di area kamu.",
        "transport": ["ojek_online", "jalan_kaki"],
    },
    {
        "name": "Pasar Malam / Night Market Lokal",
        "avg_visit_hours": 2.0,
        "category": "Kuliner",
        "tip": "Coba street food lokal yang autentik.",
        "transport": ["jalan_kaki", "ojek_online"],
    },
    {
        "name": "Taman Kota / Ruang Hijau",
        "avg_visit_hours": 1.5,
        "category": "Alam",
        "tip": "Cocok untuk bersantai dan foto-foto.",
        "transport": ["jalan_kaki", "ojek_online"],
    },
    {
        "name": "Museum Terdekat",
        "avg_visit_hours": 2.5,
        "category": "Budaya",
        "tip": "Alternatif saat cuaca buruk atau tempat outdoor tutup.",
        "transport": ["taxi", "ojek_online"],
    },
]

def get_destinations(city: str) -> list:
    """Return destination list for a city (case-insensitive)."""
    key = city.lower().strip()
    for k, v in DESTINATION_DB.items():
        if k in key or key in k:
            return v
    # Return generic if city not found
    return DESTINATION_DB.get("bali", [])

def get_city_key(city: str) -> str:
    city = city.lower().strip()
    for k in DESTINATION_DB:
        if k in city or city in k:
            return k
    return "bali"

# ─── Traffic analysis (mock) ─────────────────────────────────────────────────────
TRAFFIC_CONDITIONS = {
    "pagi_rush": {"label": "Pagi Sibuk (07:00–09:00)", "multiplier": 1.7, "color": "red"},
    "siang":     {"label": "Siang Normal (09:00–16:00)", "multiplier": 1.2, "color": "amber"},
    "sore_rush": {"label": "Sore Sibuk (16:00–19:00)", "multiplier": 1.8, "color": "red"},
    "malam":     {"label": "Malam Lancar (19:00–06:00)", "multiplier": 0.9, "color": "green"},
}

def get_traffic_multiplier(departure_hour: int) -> dict:
    if 7 <= departure_hour < 9:
        return TRAFFIC_CONDITIONS["pagi_rush"]
    elif 9 <= departure_hour < 16:
        return TRAFFIC_CONDITIONS["siang"]
    elif 16 <= departure_hour < 19:
        return TRAFFIC_CONDITIONS["sore_rush"]
    else:
        return TRAFFIC_CONDITIONS["malam"]

# ─── Time helpers ────────────────────────────────────────────────────────────────
def parse_time(t: str) -> datetime:
    """Parse HH:MM string to today's datetime."""
    h, m = map(int, t.split(":"))
    now = datetime.now()
    return now.replace(hour=h, minute=m, second=0, microsecond=0)

def add_minutes(dt: datetime, minutes: int) -> datetime:
    return dt + timedelta(minutes=minutes)

def fmt_time(dt: datetime) -> str:
    return dt.strftime("%H:%M")

def fmt_duration(hours: float) -> str:
    h = int(hours)
    m = int((hours - h) * 60)
    if h > 0 and m > 0:
        return f"{h} jam {m} menit"
    elif h > 0:
        return f"{h} jam"
    return f"{m} menit"

# ─── Itinerary builder ───────────────────────────────────────────────────────────
def build_itinerary(
    city: str,
    num_days: int,
    start_date: str,
    travelers: int,
    interests: list,
    start_time_daily: str = "08:00",
    end_time_daily: str = "21:00",
) -> dict:
    """Build a full day-by-day itinerary."""
    destinations = get_destinations(city)
    
    # Filter by interests if provided
    if interests:
        filtered = [d for d in destinations if d["category"].lower() in [i.lower() for i in interests]]
        if len(filtered) >= num_days * 2:
            destinations = filtered

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    
    itinerary = {"city": city, "days": [], "total_days": num_days, "travelers": travelers}
    used = set()
    dest_index = 0

    for day_num in range(1, num_days + 1):
        day_date = start_dt + timedelta(days=day_num - 1)
        day_label = day_date.strftime("%A, %d %B %Y")
        
        current_time = parse_time(start_time_daily)
        end_time = parse_time(end_time_daily)
        activities = []

        # Add 30-min breakfast buffer at start
        breakfast_end = add_minutes(current_time, 30)
        activities.append({
            "time": fmt_time(current_time),
            "end_time": fmt_time(breakfast_end),
            "name": "☕ Sarapan & Persiapan",
            "duration": 0.5,
            "category": "Rutinitas",
            "tip": "Siapkan perlengkapan hari ini.",
            "transport": [],
            "is_buffer": True,
        })
        current_time = breakfast_end

        while current_time < end_time:
            # Pick next destination
            while dest_index < len(destinations) and destinations[dest_index]["name"] in used:
                dest_index += 1
            if dest_index >= len(destinations):
                dest_index = 0  # wrap around

            dest = destinations[dest_index]
            visit_hours = dest["avg_visit_hours"]
            visit_minutes = int(visit_hours * 60)
            travel_minutes = 25  # avg travel to next destination

            end_activity = add_minutes(current_time, visit_minutes)
            if end_activity > end_time:
                break

            activities.append({
                "time": fmt_time(current_time),
                "end_time": fmt_time(end_activity),
                "name": dest["name"],
                "duration": visit_hours,
                "category": dest["category"],
                "tip": dest["tip"],
                "transport": dest["transport"],
                "open": dest.get("open", "-"),
                "close": dest.get("close", "-"),
                "is_buffer": False,
            })
            used.add(dest["name"])
            dest_index += 1
            current_time = add_minutes(end_activity, travel_minutes)  # 25 min travel

            # Lunch break around 12:00–13:30
            h = current_time.hour
            if 12 <= h <= 13 and not any(a.get("name", "").startswith("🍽️") for a in activities):
                lunch_end = add_minutes(current_time, 60)
                activities.append({
                    "time": fmt_time(current_time),
                    "end_time": fmt_time(lunch_end),
                    "name": "🍽️ Makan Siang",
                    "duration": 1.0,
                    "category": "Kuliner",
                    "tip": "Coba kuliner lokal khas " + city + "!",
                    "transport": [],
                    "is_buffer": True,
                })
                current_time = lunch_end

        # Dinner buffer
        dinner_start = add_minutes(parse_time(end_time_daily), -90)
        if current_time < dinner_start:
            current_time = dinner_start
        activities.append({
            "time": fmt_time(dinner_start),
            "end_time": fmt_time(add_minutes(dinner_start, 75)),
            "name": "🍜 Makan Malam & Bersantai",
            "duration": 1.25,
            "category": "Kuliner",
            "tip": "Nikmati malam dengan kuliner & suasana lokal.",
            "transport": ["ojek_online", "jalan_kaki"],
            "is_buffer": True,
        })

        itinerary["days"].append({
            "day_number": day_num,
            "date": day_date.strftime("%Y-%m-%d"),
            "label": day_label,
            "activities": activities,
        })

    return itinerary

def rearrange_day(
    day_activities: list,
    closed_activity_name: str,
    backup_pool: list,
    current_time_str: str,
) -> list:
    """Remove closed activity and fill gap with backup destination."""
    current_time = parse_time(current_time_str)
    
    # Find closed activity and remove it
    removed = None
    new_activities = []
    for a in day_activities:
        if a["name"] == closed_activity_name:
            removed = a
        else:
            new_activities.append(a)

    if not removed:
        return day_activities

    # Find available backup
    existing_names = {a["name"] for a in new_activities}
    backup = None
    for b in backup_pool:
        if b["name"] not in existing_names:
            backup = b
            break

    if backup:
        visit_minutes = int(backup["avg_visit_hours"] * 60)
        # Insert backup at removed slot time
        new_slot = {
            "time": removed["time"],
            "end_time": fmt_time(
                add_minutes(parse_time(removed["time"]), visit_minutes)
            ),
            "name": "⭐ " + backup["name"],
            "duration": backup["avg_visit_hours"],
            "category": backup["category"],
            "tip": "📍 BACKUP DESTINASI BARU — " + backup["tip"],
            "transport": backup.get("transport", ["ojek_online"]),
            "open": "08:00",
            "close": "22:00",
            "is_buffer": False,
            "is_backup": True,
        }
        new_activities.append(new_slot)
        # Re-sort by time
        new_activities.sort(key=lambda x: x["time"])

    return new_activities


# ─── Hotel database ──────────────────────────────────────────────────────────────
# Setiap hotel: nama, area, bintang, harga, fasilitas,
# travel_times: {nama_destinasi -> menit_perjalanan_normal}
HOTEL_DB = {
    "bali": [
        {
            "name": "The Layar Private Villas",
            "area": "Seminyak",
            "stars": 5,
            "price_min": 1_800_000,
            "price_max": 4_500_000,
            "facilities": ["kolam renang", "spa", "sarapan included", "wifi", "antar-jemput bandara"],
            "travel_times": {
                "Tanah Lot Temple": 20, "Pantai Kuta": 15, "Ubud Monkey Forest": 50,
                "Tegallalang Rice Terrace": 60, "Seminyak Beach": 5, "Pura Besakih": 90,
                "Nusa Dua Beach": 35, "Waterbom Bali": 20, "Pasar Seni Sukawati": 55,
                "Uluwatu Temple": 40,
            },
            "tip": "Lokasi strategis di jantung Seminyak, dekat beach clubs & restoran fine dining.",
        },
        {
            "name": "Komaneka at Bisma",
            "area": "Ubud",
            "stars": 5,
            "price_min": 2_200_000,
            "price_max": 5_000_000,
            "facilities": ["kolam renang infinity", "spa", "sarapan included", "wifi", "shuttle Ubud"],
            "travel_times": {
                "Tanah Lot Temple": 55, "Pantai Kuta": 65, "Ubud Monkey Forest": 10,
                "Tegallalang Rice Terrace": 15, "Seminyak Beach": 70, "Pura Besakih": 55,
                "Nusa Dua Beach": 75, "Waterbom Bali": 60, "Pasar Seni Sukawati": 10,
                "Uluwatu Temple": 75,
            },
            "tip": "Ideal untuk wisatawan yang fokus di area Ubud & alam pedalaman Bali.",
        },
        {
            "name": "Aloft Bali Seminyak",
            "area": "Seminyak",
            "stars": 4,
            "price_min": 650_000,
            "price_max": 1_200_000,
            "facilities": ["kolam renang", "rooftop bar", "wifi", "gym"],
            "travel_times": {
                "Tanah Lot Temple": 22, "Pantai Kuta": 12, "Ubud Monkey Forest": 48,
                "Tegallalang Rice Terrace": 58, "Seminyak Beach": 7, "Pura Besakih": 88,
                "Nusa Dua Beach": 33, "Waterbom Bali": 18, "Pasar Seni Sukawati": 52,
                "Uluwatu Temple": 38,
            },
            "tip": "Value terbaik di Seminyak — dekat pantai dengan fasilitas bintang 4.",
        },
        {
            "name": "COMO Uma Ubud",
            "area": "Ubud",
            "stars": 5,
            "price_min": 3_000_000,
            "price_max": 7_000_000,
            "facilities": ["spa COMO Shambhala", "kolam renang", "sarapan included", "wifi", "yoga"],
            "travel_times": {
                "Tanah Lot Temple": 52, "Pantai Kuta": 62, "Ubud Monkey Forest": 8,
                "Tegallalang Rice Terrace": 18, "Seminyak Beach": 68, "Pura Besakih": 50,
                "Nusa Dua Beach": 72, "Waterbom Bali": 58, "Pasar Seni Sukawati": 12,
                "Uluwatu Temple": 72,
            },
            "tip": "Pengalaman retreat mewah di tengah hutan Ubud.",
        },
        {
            "name": "Bali Mandira Beach Resort",
            "area": "Legian",
            "stars": 4,
            "price_min": 800_000,
            "price_max": 1_600_000,
            "facilities": ["akses pantai langsung", "kolam renang", "spa", "sarapan included", "wifi"],
            "travel_times": {
                "Tanah Lot Temple": 25, "Pantai Kuta": 10, "Ubud Monkey Forest": 52,
                "Tegallalang Rice Terrace": 62, "Seminyak Beach": 10, "Pura Besakih": 92,
                "Nusa Dua Beach": 30, "Waterbom Bali": 15, "Pasar Seni Sukawati": 55,
                "Uluwatu Temple": 42,
            },
            "tip": "Akses langsung ke pantai Legian — sempurna untuk pantai-lovers.",
        },
        {
            "name": "The Nusa Dua (a St. Regis Resort)",
            "area": "Nusa Dua",
            "stars": 5,
            "price_min": 3_500_000,
            "price_max": 8_000_000,
            "facilities": ["butler service", "kolam renang", "beach access", "spa", "sarapan included", "wifi"],
            "travel_times": {
                "Tanah Lot Temple": 50, "Pantai Kuta": 30, "Ubud Monkey Forest": 65,
                "Tegallalang Rice Terrace": 75, "Seminyak Beach": 35, "Pura Besakih": 95,
                "Nusa Dua Beach": 5, "Waterbom Bali": 35, "Pasar Seni Sukawati": 68,
                "Uluwatu Temple": 20,
            },
            "tip": "Posisi premium di Nusa Dua, dekat Uluwatu & pantai ekslusif.",
        },
        {
            "name": "Guesthouse Jukung Bali",
            "area": "Kuta",
            "stars": 2,
            "price_min": 180_000,
            "price_max": 350_000,
            "facilities": ["wifi", "sarapan included", "parkir motor"],
            "travel_times": {
                "Tanah Lot Temple": 28, "Pantai Kuta": 8, "Ubud Monkey Forest": 55,
                "Tegallalang Rice Terrace": 65, "Seminyak Beach": 14, "Pura Besakih": 95,
                "Nusa Dua Beach": 28, "Waterbom Bali": 12, "Pasar Seni Sukawati": 58,
                "Uluwatu Temple": 40,
            },
            "tip": "Budget-friendly di Kuta, cocok untuk backpacker yang mau dekat aksi.",
        },
    ],
    "yogyakarta": [
        {
            "name": "Tentrem Hotel Yogyakarta",
            "area": "Pusat Kota",
            "stars": 5,
            "price_min": 1_500_000,
            "price_max": 3_500_000,
            "facilities": ["kolam renang", "spa", "sarapan included", "wifi", "concierge"],
            "travel_times": {
                "Candi Borobudur": 45, "Candi Prambanan": 30, "Kraton Yogyakarta": 10,
                "Malioboro Street": 8, "Pantai Parangtritis": 35, "Hutan Pinus Mangunan": 50,
            },
            "tip": "Lokasi terbaik — jalan kaki ke Malioboro, 10 menit ke Kraton.",
        },
        {
            "name": "Hyatt Regency Yogyakarta",
            "area": "Sleman",
            "stars": 5,
            "price_min": 1_800_000,
            "price_max": 4_000_000,
            "facilities": ["kolam renang", "golf", "spa", "sarapan included", "wifi", "shuttle"],
            "travel_times": {
                "Candi Borobudur": 40, "Candi Prambanan": 20, "Kraton Yogyakarta": 20,
                "Malioboro Street": 18, "Pantai Parangtritis": 50, "Hutan Pinus Mangunan": 55,
            },
            "tip": "Resort luas dekat Prambanan & bandara YIA. Cocok untuk keluarga.",
        },
        {
            "name": "Melia Purosani Hotel",
            "area": "Pusat Kota",
            "stars": 4,
            "price_min": 700_000,
            "price_max": 1_400_000,
            "facilities": ["kolam renang", "sarapan included", "wifi", "gym"],
            "travel_times": {
                "Candi Borobudur": 48, "Candi Prambanan": 32, "Kraton Yogyakarta": 8,
                "Malioboro Street": 5, "Pantai Parangtritis": 38, "Hutan Pinus Mangunan": 52,
            },
            "tip": "Sangat dekat Malioboro — favorit wisatawan yang mau belanja & kuliner Jogja.",
        },
        {
            "name": "Omah Cangkringan Villa & Spa",
            "area": "Kaliurang (Lereng Merapi)",
            "stars": 4,
            "price_min": 900_000,
            "price_max": 2_000_000,
            "facilities": ["kolam renang air panas", "spa", "sarapan included", "wifi", "view Merapi"],
            "travel_times": {
                "Candi Borobudur": 65, "Candi Prambanan": 35, "Kraton Yogyakarta": 40,
                "Malioboro Street": 38, "Pantai Parangtritis": 70, "Hutan Pinus Mangunan": 45,
            },
            "tip": "Pengalaman unik di kaki Merapi — kolam air panas alami, view luar biasa.",
        },
        {
            "name": "Greenhost Boutique Hotel",
            "area": "Prawirotaman",
            "stars": 3,
            "price_min": 450_000,
            "price_max": 900_000,
            "facilities": ["kolam renang", "wifi", "rooftop", "restoran"],
            "travel_times": {
                "Candi Borobudur": 50, "Candi Prambanan": 35, "Kraton Yogyakarta": 12,
                "Malioboro Street": 15, "Pantai Parangtritis": 30, "Hutan Pinus Mangunan": 45,
            },
            "tip": "Kawasan seni Prawirotaman — dekat galeri, kafe unik & Pantai Parangtritis.",
        },
    ],
    "jakarta": [
        {
            "name": "The Ritz-Carlton Pacific Place",
            "area": "SCBD / Sudirman",
            "stars": 5,
            "price_min": 3_000_000,
            "price_max": 8_000_000,
            "facilities": ["spa", "kolam renang", "sarapan included", "wifi", "concierge", "akses mall"],
            "travel_times": {
                "Kota Tua Jakarta": 30, "Ancol Dreamland": 35,
                "Grand Indonesia Mall": 15, "TMII (Taman Mini Indonesia Indah)": 40,
            },
            "tip": "Jantung bisnis Jakarta — akses MRT langsung ke Grand Indonesia.",
        },
        {
            "name": "Hotel Batavia",
            "area": "Kota Tua",
            "stars": 4,
            "price_min": 900_000,
            "price_max": 2_000_000,
            "facilities": ["wifi", "sarapan included", "restoran rooftop", "kolam renang"],
            "travel_times": {
                "Kota Tua Jakarta": 3, "Ancol Dreamland": 15,
                "Grand Indonesia Mall": 35, "TMII (Taman Mini Indonesia Indah)": 50,
            },
            "tip": "Menginap persis di Kota Tua — bangun pagi langsung eksplorasi sejarah!",
        },
        {
            "name": "Ibis Budget Jakarta Cikini",
            "area": "Cikini / Menteng",
            "stars": 2,
            "price_min": 300_000,
            "price_max": 600_000,
            "facilities": ["wifi", "sarapan included", "parkir"],
            "travel_times": {
                "Kota Tua Jakarta": 20, "Ancol Dreamland": 25,
                "Grand Indonesia Mall": 10, "TMII (Taman Mini Indonesia Indah)": 35,
            },
            "tip": "Budget terbaik di tengah kota — akses mudah ke mana saja.",
        },
    ],
    "lombok": [
        {
            "name": "Katamaran Resort & Spa",
            "area": "Senggigi",
            "stars": 4,
            "price_min": 800_000,
            "price_max": 1_800_000,
            "facilities": ["pantai private", "kolam renang", "spa", "sarapan included", "wifi"],
            "travel_times": {
                "Pantai Kuta Lombok": 60, "Gili Trawangan": 30, "Gunung Rinjani Base Camp": 90,
            },
            "tip": "Lokasi terbaik untuk akses ke Gili via speedboat dari Senggigi.",
        },
        {
            "name": "Novotel Lombok Resort & Villas",
            "area": "Kuta Lombok",
            "stars": 4,
            "price_min": 1_200_000,
            "price_max": 2_800_000,
            "facilities": ["kolam renang", "spa", "sarapan included", "wifi", "surf lesson"],
            "travel_times": {
                "Pantai Kuta Lombok": 5, "Gili Trawangan": 90, "Gunung Rinjani Base Camp": 70,
            },
            "tip": "Sempurna untuk pecinta surfing — persis di Kuta Lombok yang eksotis.",
        },
        {
            "name": "Pondok Senaru Cottages",
            "area": "Senaru (Kaki Rinjani)",
            "stars": 2,
            "price_min": 200_000,
            "price_max": 450_000,
            "facilities": ["wifi", "sarapan included", "guide trekking"],
            "travel_times": {
                "Pantai Kuta Lombok": 110, "Gili Trawangan": 100, "Gunung Rinjani Base Camp": 10,
            },
            "tip": "Basecamp ideal untuk pendaki Rinjani — paling dekat ke gerbang trek.",
        },
    ],
}


def get_hotels(city: str) -> list:
    """Return hotel list for a city."""
    key = city.lower().strip()
    for k, v in HOTEL_DB.items():
        if k in key or key in k:
            return v
    return HOTEL_DB.get("bali", [])


def recommend_hotels(
    city: str,
    itinerary: dict,
    budget_max: int = None,
    stars_min: int = 1,
) -> list:
    """
    Score hotels by strategic proximity to all itinerary destinations.
    Lower avg_travel_minutes + higher destination coverage = better strategic score.
    Returns list sorted best-first.
    """
    hotels = get_hotels(city)
    if not hotels:
        return []

    # Collect unique real destination names from entire itinerary
    dest_names = set()
    for day in itinerary.get("days", []):
        for act in day.get("activities", []):
            if not act.get("is_buffer"):
                dest_names.add(act["name"].replace("⭐ ", ""))

    scored = []
    for hotel in hotels:
        if budget_max and hotel["price_min"] > budget_max:
            continue
        if hotel["stars"] < stars_min:
            continue

        travel_map = hotel.get("travel_times", {})
        times, matched = [], []
        for dest in dest_names:
            if dest in travel_map:
                t = travel_map[dest]
                times.append(t)
                matched.append((dest, t))

        if times:
            avg_time   = sum(times) / len(times)
            max_time   = max(times)
            coverage   = len(matched) / max(len(dest_names), 1)
        else:
            avg_time = max_time = 999
            coverage = 0.0

        # Strategic score: lower avg_time * penalised by missing coverage
        score = avg_time * (1 - coverage * 0.25)

        scored.append({
            **hotel,
            "avg_travel_minutes":    round(avg_time, 1),
            "max_travel_minutes":    max_time,
            "coverage_pct":          round(coverage * 100),
            "matched_destinations":  sorted(matched, key=lambda x: x[1]),
            "strategic_score":       round(score, 1),
        })

    # Best strategic score first; stars as tiebreaker
    scored.sort(key=lambda h: (h["strategic_score"], -h["stars"]))
    return scored


def fmt_price(amount: int) -> str:
    """Format integer as Indonesian Rupiah string."""
    return "Rp " + f"{amount:,}".replace(",", ".")



# ─── CSS helpers ─────────────────────────────────────────────────────────────────
CARD_CSS = """
<style>
.info-card{background:white;border-radius:14px;padding:18px 20px;border:1px solid #E2E8F0;margin:8px 0;box-shadow:0 1px 4px rgba(0,0,0,.06)}
.card-header{font-size:12px;font-weight:600;color:#64748B;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px}
.card-title{font-size:17px;font-weight:700;color:#0F172A;margin-bottom:4px}
.badge{display:inline-block;padding:3px 10px;border-radius:99px;font-size:11px;font-weight:600;margin:2px}
.badge-blue{background:#DBEAFE;color:#1D4ED8}
.badge-green{background:#DCFCE7;color:#15803D}
.badge-amber{background:#FEF3C7;color:#B45309}
.badge-red{background:#FEE2E2;color:#DC2626}
.badge-purple{background:#EDE9FE;color:#7C3AED}
.timeline-wrap{border-left:2px solid #E2E8F0;margin-left:10px;padding-left:16px}
.tl-item{position:relative;padding:8px 0}
.tl-dot{position:absolute;left:-22px;top:14px;width:10px;height:10px;border-radius:50%;background:#2563EB;border:2px solid white;box-shadow:0 0 0 2px #2563EB}
.tl-dot-buffer{background:#94A3B8;box-shadow:0 0 0 2px #94A3B8}
.tl-dot-backup{background:#F59E0B;box-shadow:0 0 0 2px #F59E0B}
.tl-time{font-size:11px;font-weight:600;color:#64748B}
.tl-name{font-weight:600;color:#1E293B;font-size:14px}
.tl-detail{font-size:12px;color:#64748B;margin-top:2px}
.dep-card{border-radius:14px;padding:16px 20px;margin:8px 0}
.dep-time{font-size:36px;font-weight:800;color:#0F172A}
.dep-label{font-size:13px;color:#64748B;margin-bottom:4px}
.status-ok{background:#DCFCE7;border:1px solid #86EFAC;color:#15803D}
.status-warn{background:#FEF3C7;border:1px solid #FCD34D;color:#92400E}
.status-danger{background:#FEE2E2;border:1px solid #FCA5A5;color:#DC2626}
.emergency-banner{background:linear-gradient(135deg,#FEF3C7,#FEE2E2);border:1.5px solid #F59E0B;border-radius:12px;padding:14px 18px;margin:8px 0}
.chat-bubble{padding:12px 16px;border-radius:18px;margin:6px 0;max-width:85%;line-height:1.6;font-size:14px}
.chat-user{background:#2563EB;color:white;margin-left:auto;border-bottom-right-radius:4px}
.chat-bot{background:#F1F5F9;color:#1E293B;border:1px solid #E2E8F0;border-bottom-left-radius:4px}
</style>
"""

def format_activity_row(act: dict, show_tip: bool = True) -> str:
    dot_cls = "tl-dot-buffer" if act.get("is_buffer") else ("tl-dot-backup" if act.get("is_backup") else "")
    transport_html = ""
    if act.get("transport"):
        icons = " ".join(get_transport_icon(t) for t in act["transport"][:3])
        transport_html = f"<span style='font-size:13px'>{icons}</span>"
    tip_html = f"<div class='tl-detail'>💡 {act['tip']}</div>" if show_tip and act.get("tip") and not act.get("is_buffer") else ""
    hours_label = fmt_duration(act["duration"]) if act.get("duration") else ""
    return f"""
    <div class='tl-item'>
      <span class='tl-dot {dot_cls}'></span>
      <div class='tl-time'>{act['time']} – {act['end_time']}</div>
      <div class='tl-name'>{act['name']} &nbsp;<span style='font-size:11px;color:#94A3B8'>({hours_label})</span> {transport_html}</div>
      {tip_html}
    </div>"""

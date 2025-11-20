import swisseph as swe
from datetime import datetime, timezone

swe.set_ephe_path(".")

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
}

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

VIM_ORDER = [
    "Ketu", "Venus", "Sun", "Moon", "Mars",
    "Rahu", "Jupiter", "Saturn", "Mercury"
]

VIM_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10,
    "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19,
    "Mercury": 17
}


def to_julian(dt: datetime):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(timezone.utc)

    y, m, d = dt.year, dt.month, dt.day
    h = dt.hour + dt.minute / 60 + dt.second / 3600
    return swe.julday(y, m, d, h)


def planet_positions(dt):
    jd = to_julian(dt)
    pos = {}

    for name, pid in PLANETS.items():
        r = swe.calc_ut(jd, pid)

        lon_raw = r[0]

        # FIX: handle nested tuple ((135.5,), 1)
        if isinstance(lon_raw, tuple):
            lon_raw = lon_raw[0]

        pos[name] = lon_raw % 360

    return pos, jd


def house_data(dt, lat, lon):
    jd = to_julian(dt)
    cusps, ascmc = swe.houses(jd, lat, lon)
    asc = ascmc[0] % 360

    if len(cusps) == 12:
        hc = {i + 1: cusps[i] % 360 for i in range(12)}
    else:
        hc = {i: cusps[i] % 360 for i in range(1, 13)}

    return asc, hc


def sign_from_longitude(lon):
    index = int(lon // 30)
    return SIGNS[index]


def which_house(lon, cusps):
    for i in range(1, 13):
        start = cusps[i]
        end = cusps[1] if i == 12 else cusps[i + 1]

        if start <= end:
            if start <= lon < end:
                return i
        else:
            if lon >= start or lon < end:
                return i

    return 12


def dashas(dt, moon_lon, now=None):
    if now is None:
        now = datetime.now(timezone.utc)

    nak_len = 360 / 27
    idx = int(moon_lon // nak_len)
    start = VIM_ORDER[idx]
    yrs = VIM_YEARS[start]

    used = (moon_lon % nak_len) / nak_len
    rem = (1 - used) * yrs

    elapsed = (now - dt).total_seconds() / 86400 / 365.25

    if elapsed < rem:
        return {"current": start, "remaining": rem - elapsed}

    elapsed -= rem
    i = (idx + 1) % 9

    while True:
        p = VIM_ORDER[i]
        l = VIM_YEARS[p]

        if elapsed < l:
            return {"current": p, "remaining": l - elapsed}

        elapsed -= l
        i = (i + 1) % 9


def compute_chart(dt, lat, lon):
    longitudes, jd = planet_positions(dt)
    asc, cusps = house_data(dt, lat, lon)

    ph = {}
    for p, lng in longitudes.items():
        ph[p] = which_house(lng, cusps)

    moon_lon = longitudes["Moon"]
    moon_sign = sign_from_longitude(moon_lon)

    mars_house = ph["Mars"]
    manglik = mars_house in {1, 2, 4, 7, 8, 12}
    manglik_text = f"Mars is in house {mars_house}. {'Manglik' if manglik else 'Not Manglik'}."

    dasha_info = dashas(dt, moon_lon)

    return {
        "julian": jd,
        "longitudes": longitudes,
        "ascendant": asc,
        "houses": cusps,
        "planet_houses": ph,
        "moon_sign": moon_sign,
        "manglik": {"flag": manglik, "text": manglik_text},
        "dasha": dasha_info
    }

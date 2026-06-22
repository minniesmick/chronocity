import re


def normalize_text(query: str) -> str:
    """
    Normalizes English and Turkish text for rule-based NLP search.

    Examples:
    yüksek -> yuksek
    önce -> once
    gökdelen -> gokdelen
    """

    text = query.lower().strip()

    replacements = {
        "ı": "i",
        "ğ": "g",
        "ü": "u",
        "ş": "s",
        "ö": "o",
        "ç": "c",
        "’": "'",
        "`": "'",
        "´": "'",
    }

    for source, target in replacements.items():
        text = text.replace(source, target)

    return text


def has_turkish_signal(query: str) -> bool:
    """
    Detects whether the query looks Turkish.
    """

    raw_text = query.lower()
    text = normalize_text(query)

    turkish_chars = ["ı", "ğ", "ü", "ş", "ö", "ç"]

    turkish_words = [
        "once",
        "oncesi",
        "sonra",
        "sonrasi",
        "arasi",
        "ile",
        "ve",
        "yuksek",
        "kisa",
        "alti",
        "ustu",
        "bina",
        "binalar",
        "binalari",
        "goster",
        "bul",
        "eski",
        "tarihi",
        "tarihsel",
        "gokdelen",
        "gokdelenler",
        "metre",
        "modern",
        "yeni",
    ]

    return any(char in raw_text for char in turkish_chars) or any(
        word in text for word in turkish_words
    )


def first_group_as_int(match) -> int | None:
    """
    Returns the first non-empty regex group as integer.
    """

    for group in match.groups():
        if group:
            return int(group)

    return None


def parse_query(query: str) -> dict:
    """
    Rule-based multilingual NLP parser.

    Converts English/Turkish natural language text into structured filters.

    Examples:
    - Show tall buildings before 1930
    - 1930dan once yuksek binalari goster
    - 2000 sonrasi modern binalari bul
    - 50 metreden yuksek binalari goster
    - 1900 ile 1950 arasi binalari goster
    """

    text = normalize_text(query)

    filters = {
        "year_min": None,
        "year_max": None,
        "height_min": None,
        "height_max": None,
        "name_contains": None,
        "language_detected": "tr" if has_turkish_signal(query) else "en",
    }

    # ── English year filters ────────────────────────────────────────────────

    # before 1930
    before_match = re.search(r"before\s+(\d{4})", text)
    if before_match:
        filters["year_max"] = int(before_match.group(1))

    # after 2000
    after_match = re.search(r"after\s+(\d{4})", text)
    if after_match:
        filters["year_min"] = int(after_match.group(1))

    # between 1950 and 2000
    between_match = re.search(r"between\s+(\d{4})\s+and\s+(\d{4})", text)
    if between_match:
        filters["year_min"] = int(between_match.group(1))
        filters["year_max"] = int(between_match.group(2))

    # ── Turkish year filters ────────────────────────────────────────────────

    # 1930dan once / 1930'dan once / 1930 den once / 1930 oncesi
    tr_before_match = re.search(
        r"(\d{4})\s*'?\s*(dan|den)\s+once|(\d{4})\s+oncesi",
        text,
    )
    if tr_before_match:
        year = first_group_as_int(tr_before_match)
        if year is not None:
            filters["year_max"] = year

    # 2000den sonra / 2000'den sonra / 2000 sonrasi
    tr_after_match = re.search(
        r"(\d{4})\s*'?\s*(dan|den)\s+sonra|(\d{4})\s+sonrasi",
        text,
    )
    if tr_after_match:
        year = first_group_as_int(tr_after_match)
        if year is not None:
            filters["year_min"] = year

    # 1900 ile 1950 arasi / 1900 ve 1950 arasi / 1900-1950 arasi
    tr_between_match = re.search(
        r"(\d{4})\s+(ile|ve)\s+(\d{4})\s+arasi|(\d{4})\s*-\s*(\d{4})\s+arasi",
        text,
    )
    if tr_between_match:
        numbers = [int(num) for num in re.findall(r"\d{4}", tr_between_match.group(0))]
        if len(numbers) >= 2:
            filters["year_min"] = min(numbers[0], numbers[1])
            filters["year_max"] = max(numbers[0], numbers[1])

    # ── English height filters ──────────────────────────────────────────────

    # higher than 50 / taller than 80 / above 100
    height_min_match = re.search(r"(higher|taller|above)\s+than\s+(\d+)", text)
    if height_min_match:
        filters["height_min"] = int(height_min_match.group(2))

    # lower than 30 / shorter than 20 / below 15
    height_max_match = re.search(r"(lower|shorter|below)\s+than\s+(\d+)", text)
    if height_max_match:
        filters["height_max"] = int(height_max_match.group(2))

    # ── Turkish height filters ──────────────────────────────────────────────

    # 50 metreden yuksek / 50 metre ustu / 50m ustu / 50 den yuksek
    tr_height_min_match = re.search(
        r"(\d+)\s*(metre|meter|m)?\s*'?\s*(den|dan)?\s*(yuksek|ustu|uzun)",
        text,
    )
    if tr_height_min_match:
        filters["height_min"] = int(tr_height_min_match.group(1))

    # 30 metreden kisa / 30 metre alti / 30 dan dusuk
    tr_height_max_match = re.search(
        r"(\d+)\s*(metre|meter|m)?\s*'?\s*(den|dan)?\s*(kisa|alti|dusuk)",
        text,
    )
    if tr_height_max_match:
        filters["height_max"] = int(tr_height_max_match.group(1))

    # ── Semantic shortcuts: English + Turkish ───────────────────────────────

    if any(
        word in text
        for word in [
            "old",
            "historical",
            "historic",
            "heritage",
            "eski",
            "tarihi",
            "tarihsel",
        ]
    ):
        filters["year_max"] = filters["year_max"] or 1950

    if any(
        word in text
        for word in [
            "modern",
            "new",
            "recent",
            "yeni",
            "guncel",
            "son donem",
        ]
    ):
        filters["year_min"] = filters["year_min"] or 2000

    if any(
        word in text
        for word in [
            "tall",
            "high-rise",
            "yuksek",
            "uzun",
        ]
    ):
        filters["height_min"] = filters["height_min"] or 50

    if any(
        word in text
        for word in [
            "skyscraper",
            "gokdelen",
            "gokdelenler",
        ]
    ):
        filters["height_min"] = filters["height_min"] or 100

    return filters


def filter_buildings(buildings: list[dict], filters: dict) -> list[dict]:
    """
    Applies parsed filters to building records.
    """

    results = []

    for building in buildings:
        year = building.get("construction_year")
        height = building.get("height")
        name = building.get("name") or ""

        if filters["year_min"] is not None:
            if year is None or year < filters["year_min"]:
                continue

        if filters["year_max"] is not None:
            if year is None or year > filters["year_max"]:
                continue

        if filters["height_min"] is not None:
            if height is None or height < filters["height_min"]:
                continue

        if filters["height_max"] is not None:
            if height is None or height > filters["height_max"]:
                continue

        if filters["name_contains"]:
            if filters["name_contains"].lower() not in name.lower():
                continue

        results.append(building)

    return results


def build_search_answer(filters: dict, matched_count: int) -> str:
    """
    Creates a simple AI-style explanation.
    Supports English and Turkish answers.

    Turkish answer is ASCII-only to avoid Windows PowerShell encoding issues.
    """

    language = filters.get("language_detected", "en")
    parts = []

    if language == "tr":
        if filters["year_min"] is not None:
            parts.append(f"{filters['year_min']} sonrasinda yapilmis")

        if filters["year_max"] is not None:
            parts.append(f"{filters['year_max']} oncesinde yapilmis")

        if filters["height_min"] is not None:
            parts.append(f"{filters['height_min']} metreden yuksek")

        if filters["height_max"] is not None:
            parts.append(f"{filters['height_max']} metreden alcak")

        if not parts:
            return f"Aramanizla eslesen {matched_count} bina bulundu."

        detail = " ve ".join(parts)
        return f"{detail} {matched_count} bina bulundu."

    if filters["year_min"] is not None:
        parts.append(f"after {filters['year_min']}")

    if filters["year_max"] is not None:
        parts.append(f"before {filters['year_max']}")

    if filters["height_min"] is not None:
        parts.append(f"higher than {filters['height_min']} meters")

    if filters["height_max"] is not None:
        parts.append(f"lower than {filters['height_max']} meters")

    if not parts:
        return f"I found {matched_count} buildings matching your search."

    return f"I found {matched_count} buildings " + " and ".join(parts) + "."
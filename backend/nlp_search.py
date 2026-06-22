import re


def parse_query(query: str) -> dict:
    """
    Rule-based NLP parser.
    Converts natural language search text into structured filters.
    """
    text = query.lower().strip()

    filters = {
        "year_min": None,
        "year_max": None,
        "height_min": None,
        "height_max": None,
        "name_contains": None,
    }

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

    # higher than 50 / taller than 80 / above 100
    height_min_match = re.search(r"(higher|taller|above)\s+than\s+(\d+)", text)
    if height_min_match:
        filters["height_min"] = int(height_min_match.group(2))

    # lower than 30 / shorter than 20 / below 15
    height_max_match = re.search(r"(lower|shorter|below)\s+than\s+(\d+)", text)
    if height_max_match:
        filters["height_max"] = int(height_max_match.group(2))

    # Semantic shortcuts
    if "old" in text or "historical" in text or "historic" in text:
        filters["year_max"] = filters["year_max"] or 1950

    if "modern" in text or "new" in text:
        filters["year_min"] = filters["year_min"] or 2000

    if "tall" in text or "high-rise" in text:
        filters["height_min"] = filters["height_min"] or 50

    if "skyscraper" in text:
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
    Creates a simple AI-style explanation for the user.
    """
    parts = []

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
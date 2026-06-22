from collections import Counter


def calculate_city_stats(city_id: str, buildings: list[dict]) -> dict:
    """
    Bina listesinden şehir istatistikleri üretir.
    """

    heights = [
        b["height"]
        for b in buildings
        if isinstance(b.get("height"), (int, float))
    ]

    years = [
        b["construction_year"]
        for b in buildings
        if isinstance(b.get("construction_year"), int)
    ]

    tall_buildings = [
        b for b in buildings
        if isinstance(b.get("height"), (int, float)) and b["height"] >= 50
    ]

    before_1900 = [
        b for b in buildings
        if isinstance(b.get("construction_year"), int)
        and b["construction_year"] < 1900
    ]

    after_2000 = [
        b for b in buildings
        if isinstance(b.get("construction_year"), int)
        and b["construction_year"] >= 2000
    ]

    decade_counter = Counter()

    for year in years:
        decade = (year // 10) * 10
        decade_counter[f"{decade}s"] += 1

    fastest_growth_decade = None
    decade_distribution = dict(sorted(decade_counter.items()))

    if decade_counter:
        fastest_growth_decade = decade_counter.most_common(1)[0][0]

    average_height = None
    min_height = None
    max_height = None

    if heights:
        average_height = round(sum(heights) / len(heights), 2)
        min_height = round(min(heights), 2)
        max_height = round(max(heights), 2)

    return {
        "city": city_id,
        "total_buildings": len(buildings),
        "buildings_with_height": len(heights),
        "buildings_with_construction_year": len(years),
        "average_height": average_height,
        "min_height": min_height,
        "max_height": max_height,
        "oldest_year": min(years) if years else None,
        "newest_year": max(years) if years else None,
        "buildings_before_1900": len(before_1900),
        "buildings_after_2000": len(after_2000),
        "tall_buildings_50m_plus": len(tall_buildings),
        "fastest_growth_decade": fastest_growth_decade,
        "decade_distribution": decade_distribution,
    }
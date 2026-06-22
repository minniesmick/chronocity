def build_city_comparison(stats_a: dict, stats_b: dict) -> dict:
    """
    Compares two cities using building analytics statistics.
    This endpoint is useful for frontend comparison cards and charts.
    """

    city_a = stats_a.get("city")
    city_b = stats_b.get("city")

    comparison_fields = [
        {
            "metric": "total_buildings",
            "label": "Total Buildings",
            "city_a_value": stats_a.get("total_buildings"),
            "city_b_value": stats_b.get("total_buildings"),
        },
        {
            "metric": "average_height",
            "label": "Average Height",
            "city_a_value": stats_a.get("average_height"),
            "city_b_value": stats_b.get("average_height"),
            "unit": "meters",
        },
        {
            "metric": "max_height",
            "label": "Maximum Height",
            "city_a_value": stats_a.get("max_height"),
            "city_b_value": stats_b.get("max_height"),
            "unit": "meters",
        },
        {
            "metric": "oldest_year",
            "label": "Oldest Construction Year",
            "city_a_value": stats_a.get("oldest_year"),
            "city_b_value": stats_b.get("oldest_year"),
        },
        {
            "metric": "newest_year",
            "label": "Newest Construction Year",
            "city_a_value": stats_a.get("newest_year"),
            "city_b_value": stats_b.get("newest_year"),
        },
        {
            "metric": "tall_buildings_50m_plus",
            "label": "Buildings Taller Than 50m",
            "city_a_value": stats_a.get("tall_buildings_50m_plus"),
            "city_b_value": stats_b.get("tall_buildings_50m_plus"),
        },
        {
            "metric": "buildings_before_1900",
            "label": "Buildings Before 1900",
            "city_a_value": stats_a.get("buildings_before_1900"),
            "city_b_value": stats_b.get("buildings_before_1900"),
        },
        {
            "metric": "buildings_after_2000",
            "label": "Buildings After 2000",
            "city_a_value": stats_a.get("buildings_after_2000"),
            "city_b_value": stats_b.get("buildings_after_2000"),
        },
        {
            "metric": "fastest_growth_decade",
            "label": "Strongest Growth Decade",
            "city_a_value": stats_a.get("fastest_growth_decade"),
            "city_b_value": stats_b.get("fastest_growth_decade"),
        },
    ]

    summary = build_comparison_summary(stats_a, stats_b)

    return {
        "city_a": city_a,
        "city_b": city_b,
        "comparison": comparison_fields,
        "summary": summary,
        "note": "Comparison is generated from GeoJSON building analytics.",
    }


def build_comparison_summary(stats_a: dict, stats_b: dict) -> str:
    """
    Creates a short AI-style comparison summary.
    """

    city_a = format_city_name(stats_a.get("city"))
    city_b = format_city_name(stats_b.get("city"))

    total_a = stats_a.get("total_buildings") or 0
    total_b = stats_b.get("total_buildings") or 0

    avg_a = stats_a.get("average_height") or 0
    avg_b = stats_b.get("average_height") or 0

    tall_a = stats_a.get("tall_buildings_50m_plus") or 0
    tall_b = stats_b.get("tall_buildings_50m_plus") or 0

    if total_a > total_b:
        larger_city_text = f"{city_a} has more buildings in the dataset than {city_b}."
    elif total_b > total_a:
        larger_city_text = f"{city_b} has more buildings in the dataset than {city_a}."
    else:
        larger_city_text = f"{city_a} and {city_b} have the same number of buildings in the dataset."

    if avg_a > avg_b:
        height_text = f"{city_a} has a higher average building height."
    elif avg_b > avg_a:
        height_text = f"{city_b} has a higher average building height."
    else:
        height_text = "Both cities have the same average building height."

    if tall_a > tall_b:
        skyline_text = f"{city_a} has more buildings taller than 50 meters."
    elif tall_b > tall_a:
        skyline_text = f"{city_b} has more buildings taller than 50 meters."
    else:
        skyline_text = "Both cities have the same number of buildings taller than 50 meters."

    return f"{larger_city_text} {height_text} {skyline_text}"


def format_city_name(city_id: str | None) -> str:
    if not city_id:
        return "Unknown City"

    return city_id.replace("-", " ").title()
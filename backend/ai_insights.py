def format_city_name(city_id: str) -> str:
    """
    Converts city id format into readable city name.
    Example:
    new-york -> New York
    istanbul -> Istanbul
    """
    if not city_id:
        return "This city"

    return city_id.replace("-", " ").title()


def build_city_insights(stats: dict) -> dict:
    """
    Creates AI-style insights from city analytics.

    This is rule-based AI logic for now.
    Later, this function can be connected to an LLM API.
    """

    city_id = stats.get("city")
    city = format_city_name(city_id)

    total = stats.get("total_buildings")
    avg_height = stats.get("average_height")
    min_height = stats.get("min_height")
    max_height = stats.get("max_height")
    oldest_year = stats.get("oldest_year")
    newest_year = stats.get("newest_year")
    before_1900 = stats.get("buildings_before_1900")
    after_2000 = stats.get("buildings_after_2000")
    tall = stats.get("tall_buildings_50m_plus")
    fastest_decade = stats.get("fastest_growth_decade")
    decade_distribution = stats.get("decade_distribution", {})

    highlights = []

    if total is not None:
        highlights.append(f"The dataset contains {total} buildings for {city}.")

    if avg_height is not None:
        highlights.append(f"The average building height is {avg_height} meters.")

    if min_height is not None and max_height is not None:
        highlights.append(
            f"Building heights range from {min_height} meters to {max_height} meters."
        )

    if oldest_year is not None and newest_year is not None:
        highlights.append(
            f"Construction years range from {oldest_year} to {newest_year}."
        )

    if fastest_decade:
        highlights.append(
            f"The strongest construction growth appears in the {fastest_decade}."
        )

    if tall is not None:
        highlights.append(f"There are {tall} buildings taller than 50 meters.")

    if before_1900 is not None:
        highlights.append(f"{before_1900} buildings were built before 1900.")

    if after_2000 is not None:
        highlights.append(f"{after_2000} buildings were built after 2000.")

    summary = "Not enough data to generate a detailed insight."

    if total and fastest_decade and oldest_year and newest_year:
        summary = (
            f"{city} shows its strongest building activity in the {fastest_decade}, "
            f"with construction years ranging from {oldest_year} to {newest_year}."
        )

        if tall is not None:
            tall_ratio = round((tall / total) * 100, 2)
            summary += f" Around {tall_ratio}% of buildings are taller than 50 meters."

        if avg_height is not None:
            summary += f" The average building height is {avg_height} meters."

    growth_interpretation = None

    if fastest_decade:
        growth_interpretation = (
            f"The {fastest_decade} can be interpreted as a major growth period "
            f"in this dataset because it has the highest number of recorded construction years."
        )

    height_interpretation = None

    if total and tall is not None:
        tall_ratio = round((tall / total) * 100, 2)

        if tall_ratio >= 25:
            height_interpretation = (
                f"{city} has a strong vertical skyline pattern, because "
                f"{tall_ratio}% of the buildings are taller than 50 meters."
            )
        elif tall_ratio >= 10:
            height_interpretation = (
                f"{city} has a moderate vertical skyline pattern, because "
                f"{tall_ratio}% of the buildings are taller than 50 meters."
            )
        else:
            height_interpretation = (
                f"{city} has a lower vertical density in this dataset, because "
                f"only {tall_ratio}% of the buildings are taller than 50 meters."
            )

    historical_interpretation = None

    if before_1900 is not None and after_2000 is not None:
        if before_1900 > after_2000:
            historical_interpretation = (
                f"The dataset contains more pre-1900 buildings than post-2000 buildings, "
                f"which suggests that the selected area preserves a visible historical layer."
            )
        elif after_2000 > before_1900:
            historical_interpretation = (
                f"The dataset contains more post-2000 buildings than pre-1900 buildings, "
                f"which suggests stronger recent development in the selected area."
            )
        else:
            historical_interpretation = (
                f"The dataset has a balanced number of pre-1900 and post-2000 buildings."
            )

    top_decades = []

    if decade_distribution:
        sorted_decades = sorted(
            decade_distribution.items(),
            key=lambda item: item[1],
            reverse=True,
        )
        top_decades = [
            {
                "decade": decade,
                "building_count": count,
            }
            for decade, count in sorted_decades[:5]
        ]

    return {
        "city": city_id,
        "city_name": city,
        "summary": summary,
        "highlights": highlights,
        "interpretations": {
            "growth": growth_interpretation,
            "height": height_interpretation,
            "history": historical_interpretation,
        },
        "top_growth_decades": top_decades,
        "note": (
            "These insights are generated from GeoJSON building data using "
            "rule-based AI logic. This can later be upgraded with an LLM."
        ),
    }


def build_search_suggestions(city_id: str) -> list[str]:
    """
    Returns ready-to-use natural language queries for the frontend.
    """

    city_name = format_city_name(city_id)

    return [
        "Show tall buildings before 1930",
        "Show historical buildings",
        "Find modern buildings after 2000",
        "Show skyscrapers",
        "Show buildings between 1900 and 1950",
        "Find buildings higher than 100 meters",
        "Show old tall buildings",
        f"Explain the urban growth of {city_name}",
    ]
def build_city_timeline(stats: dict) -> dict:
    """
    Builds timeline-ready data from decade distribution.
    This is useful for frontend charts, timeline UI, and city growth visualization.
    """

    city_id = stats.get("city")
    decade_distribution = stats.get("decade_distribution", {})
    strongest_growth_decade = stats.get("fastest_growth_decade")

    timeline = []

    for decade, count in sorted(decade_distribution.items()):
        timeline.append(
            {
                "decade": decade,
                "building_count": count,
                "label": f"{decade}: {count} buildings",
            }
        )

    return {
        "city": city_id,
        "timeline": timeline,
        "strongest_growth_decade": strongest_growth_decade,
        "total_timeline_points": len(timeline),
        "note": "Timeline data is generated from construction year distribution.",
    }
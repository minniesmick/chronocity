def build_llm_context(
    city_id: str,
    question: str,
    stats: dict,
    insights: dict,
    timeline: dict,
) -> dict:
    """
    Builds an LLM-ready context package.

    This function does not call an external LLM.
    It prepares structured city data and a clean prompt that can later be sent
    to OpenAI, Gemini, OpenRouter, or another LLM provider.
    """

    city_name = insights.get("city_name") or format_city_name(city_id)

    compact_stats = {
        "total_buildings": stats.get("total_buildings"),
        "average_height": stats.get("average_height"),
        "min_height": stats.get("min_height"),
        "max_height": stats.get("max_height"),
        "oldest_year": stats.get("oldest_year"),
        "newest_year": stats.get("newest_year"),
        "buildings_before_1900": stats.get("buildings_before_1900"),
        "buildings_after_2000": stats.get("buildings_after_2000"),
        "tall_buildings_50m_plus": stats.get("tall_buildings_50m_plus"),
        "fastest_growth_decade": stats.get("fastest_growth_decade"),
    }

    top_growth_decades = insights.get("top_growth_decades", [])
    highlights = insights.get("highlights", [])
    interpretations = insights.get("interpretations", {})

    prompt = build_prompt(
        city_name=city_name,
        question=question,
        compact_stats=compact_stats,
        highlights=highlights,
        interpretations=interpretations,
        top_growth_decades=top_growth_decades,
    )

    return {
        "city": city_id,
        "city_name": city_name,
        "question": question,
        "llm_ready": True,
        "provider_ready_for": [
            "OpenAI",
            "Gemini",
            "OpenRouter",
            "Claude",
        ],
        "prompt": prompt,
        "context": {
            "stats": compact_stats,
            "summary": insights.get("summary"),
            "highlights": highlights,
            "interpretations": interpretations,
            "top_growth_decades": top_growth_decades,
            "timeline_points": timeline.get("timeline", [])[:10],
        },
        "note": (
            "This endpoint prepares clean structured context for an LLM. "
            "It does not call an external LLM yet."
        ),
    }


def build_prompt(
    city_name: str,
    question: str,
    compact_stats: dict,
    highlights: list,
    interpretations: dict,
    top_growth_decades: list,
) -> str:
    """
    Creates a clean LLM prompt from city analytics.
    """

    highlights_text = "\n".join([f"- {item}" for item in highlights[:8]])

    top_decades_text = "\n".join(
        [
            f"- {item.get('decade')}: {item.get('building_count')} buildings"
            for item in top_growth_decades[:5]
        ]
    )

    interpretations_text = "\n".join(
        [
            f"- {key}: {value}"
            for key, value in interpretations.items()
            if value
        ]
    )

    return f"""
You are an AI urban analytics assistant for the ChronoCity project.

Your task is to answer the user's question using only the city data provided below.
Do not invent facts that are not supported by the data.
If the data is limited, clearly mention that limitation.

City: {city_name}

User Question:
{question}

City Statistics:
- Total buildings: {compact_stats.get("total_buildings")}
- Average height: {compact_stats.get("average_height")} meters
- Minimum height: {compact_stats.get("min_height")} meters
- Maximum height: {compact_stats.get("max_height")} meters
- Oldest construction year: {compact_stats.get("oldest_year")}
- Newest construction year: {compact_stats.get("newest_year")}
- Buildings before 1900: {compact_stats.get("buildings_before_1900")}
- Buildings after 2000: {compact_stats.get("buildings_after_2000")}
- Buildings taller than 50 meters: {compact_stats.get("tall_buildings_50m_plus")}
- Strongest growth decade: {compact_stats.get("fastest_growth_decade")}

Important Highlights:
{highlights_text}

Urban Interpretations:
{interpretations_text}

Top Growth Decades:
{top_decades_text}

Answer requirements:
- Answer clearly and concisely.
- Use a helpful explanation style.
- Mention the strongest growth period if relevant.
- Mention data limitations if the available construction year data is weak.
""".strip()


def format_city_name(city_id: str | None) -> str:
    if not city_id:
        return "Unknown City"

    return city_id.replace("-", " ").title()
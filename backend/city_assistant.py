def detect_question_intent(question: str) -> str:
    """
    Detects the user's intent from a natural language question.
    This is rule-based for now and can later be replaced by an LLM classifier.
    """

    text = question.lower().strip()

    if any(word in text for word in ["growth", "develop", "development", "changed", "evolved", "evolution"]):
        return "growth_explanation"

    if any(word in text for word in ["tall", "height", "skyline", "vertical", "skyscraper"]):
        return "height_explanation"

    if any(word in text for word in ["old", "historic", "historical", "before", "heritage"]):
        return "historical_explanation"

    if any(word in text for word in ["modern", "new", "after 2000", "recent"]):
        return "modern_explanation"

    if any(word in text for word in ["summary", "summarize", "overview", "explain"]):
        return "general_summary"

    return "general_summary"


def calculate_intent_confidence(question: str, intent: str) -> dict:
    """
    Calculates a simple confidence score for detected intent.

    This is not a machine learning probability.
    It is a rule-based confidence score that explains how strongly
    the question matched known intent keywords.
    """

    text = question.lower().strip()

    intent_keywords = {
        "growth_explanation": [
            "growth",
            "develop",
            "development",
            "changed",
            "evolved",
            "evolution",
        ],
        "height_explanation": [
            "tall",
            "height",
            "skyline",
            "vertical",
            "skyscraper",
        ],
        "historical_explanation": [
            "old",
            "historic",
            "historical",
            "before",
            "heritage",
        ],
        "modern_explanation": [
            "modern",
            "new",
            "after 2000",
            "recent",
        ],
        "general_summary": [
            "summary",
            "summarize",
            "overview",
            "explain",
        ],
    }

    keywords = intent_keywords.get(intent, [])
    matched_keywords = [word for word in keywords if word in text]

    if len(matched_keywords) >= 2:
        confidence = 0.95
        label = "high"
    elif len(matched_keywords) == 1:
        confidence = 0.82
        label = "high"
    elif intent == "general_summary":
        confidence = 0.65
        label = "medium"
    else:
        confidence = 0.45
        label = "low"

    return {
        "score": confidence,
        "label": label,
        "matched_keywords": matched_keywords,
    }


def build_city_answer(question: str, stats: dict, insights: dict) -> dict:
    """
    Builds an assistant-style answer using city stats and insights.

    This is LLM-ready: the same stats/insights can later be passed to an LLM prompt.
    """

    intent = detect_question_intent(question)
    confidence = calculate_intent_confidence(question, intent)

    city_name = insights.get("city_name") or stats.get("city") or "This city"
    summary = insights.get("summary")
    interpretations = insights.get("interpretations", {})
    top_growth_decades = insights.get("top_growth_decades", [])

    total = stats.get("total_buildings")
    average_height = stats.get("average_height")
    oldest_year = stats.get("oldest_year")
    newest_year = stats.get("newest_year")
    fastest_decade = stats.get("fastest_growth_decade")
    tall = stats.get("tall_buildings_50m_plus")
    before_1900 = stats.get("buildings_before_1900")
    after_2000 = stats.get("buildings_after_2000")

    if intent == "growth_explanation":
        answer = (
            f"{city_name}'s urban growth is strongest in the {fastest_decade}. "
            f"The dataset includes construction years from {oldest_year} to {newest_year}. "
        )

        if top_growth_decades:
            top_list = ", ".join(
                [
                    f"{item['decade']} ({item['building_count']} buildings)"
                    for item in top_growth_decades[:3]
                ]
            )
            answer += f"The top growth decades are {top_list}. "

        if interpretations.get("growth"):
            answer += interpretations["growth"]

    elif intent == "height_explanation":
        answer = (
            f"{city_name}'s skyline has an average building height of {average_height} meters. "
            f"There are {tall} buildings taller than 50 meters in the dataset. "
        )

        if interpretations.get("height"):
            answer += interpretations["height"]

    elif intent == "historical_explanation":
        answer = (
            f"{city_name} has {before_1900} buildings built before 1900. "
            f"The oldest recorded construction year in the dataset is {oldest_year}. "
        )

        if interpretations.get("history"):
            answer += interpretations["history"]

    elif intent == "modern_explanation":
        answer = (
            f"{city_name} has {after_2000} buildings built after 2000. "
            f"The newest recorded construction year in the dataset is {newest_year}. "
            f"This helps describe the modern layer of the selected urban area."
        )

    else:
        answer = summary or (
            f"{city_name} has {total} buildings in the dataset, with an average height of "
            f"{average_height} meters and construction years ranging from {oldest_year} to {newest_year}."
        )

    return {
        "city": stats.get("city"),
        "city_name": city_name,
        "question": question,
        "intent": intent,
        "confidence": confidence["score"],
        "confidence_label": confidence["label"],
        "matched_keywords": confidence["matched_keywords"],
        "answer": answer,
        "source": "rule-based-ai",
        "llm_ready": True,
        "context_used": {
            "stats": {
                "total_buildings": total,
                "average_height": average_height,
                "oldest_year": oldest_year,
                "newest_year": newest_year,
                "fastest_growth_decade": fastest_decade,
                "tall_buildings_50m_plus": tall,
                "buildings_before_1900": before_1900,
                "buildings_after_2000": after_2000,
            },
            "top_growth_decades": top_growth_decades[:5],
        },
    }
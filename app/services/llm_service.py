import json
from typing import Any

from openai import OpenAI

from app.core.config import settings
from app.schemas.interview import InterviewQuestion


def generate_questions(document_text: str) -> tuple[list[InterviewQuestion], str]:
    if not settings.openai_api_key:
        return demo_questions(document_text), "demo"

    client_options: dict[str, Any] = {"api_key": settings.openai_api_key}
    if settings.openai_base_url:
        client_options["base_url"] = settings.openai_base_url
    client = OpenAI(**client_options)
    prompt = (
        "Create exactly 5 progressive interview questions from this candidate document. "
        "Return JSON with a questions array. Each item must have question, intent, and "
        "difficulty (warm-up, core, or deep-dive). Keep questions specific and grounded.\n\n"
        f"DOCUMENT:\n{document_text[:18000]}"
    )
    response = client.chat.completions.create(
        model=settings.openai_model,
        temperature=0.6,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You create rigorous, humane interview questions."},
            {"role": "user", "content": prompt},
        ],
    )
    parsed = json.loads(response.choices[0].message.content or "{}")
    questions = [InterviewQuestion.model_validate(item) for item in parsed.get("questions", [])[:5]]
    return (questions or demo_questions(document_text)), "live"


def demo_questions(document_text: str) -> list[InterviewQuestion]:
    first_line = next((line.strip() for line in document_text.splitlines() if line.strip()), "your recent work")
    return [
        InterviewQuestion(question=f"Could you give us the story behind {first_line[:90]}?", intent="Warm up and establish context.", difficulty="warm-up"),
        InterviewQuestion(question="Which project in your background best shows how you turn an ambiguous problem into a shipped result?", intent="Explore ownership and execution.", difficulty="core"),
        InterviewQuestion(question="Tell us about a technical trade-off you made in one of these projects. What did you optimize for, and what did you give up?", intent="Test technical judgment.", difficulty="core"),
        InterviewQuestion(question="If you rebuilt your most recent project today, what would you change first and why?", intent="Understand reflection and systems thinking.", difficulty="deep-dive"),
        InterviewQuestion(question="What kind of problem would you be excited to own in your next role?", intent="Close on motivation and fit.", difficulty="deep-dive"),
    ]

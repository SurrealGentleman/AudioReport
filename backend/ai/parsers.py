import re
from datetime import datetime


class AIReportParseError(ValueError):
    """The AI response does not match the expected report format."""


SECTION_PATTERN = re.compile(
    r"^\s*\*{0,2}"
    r"(Тема совещания|Ключевые вопросы|Содержание|Задачи)"
    r"\*{0,2}\s*:\s*",
    flags=re.IGNORECASE | re.MULTILINE,
)

TASK_PATTERN = re.compile(
    r"-\s*\*{0,2}Задача\*{0,2}\s*:\s*(.*?)"
    r"\s+\*{0,2}Срок\*{0,2}\s*:\s*([^\n]+)",
    flags=re.IGNORECASE | re.DOTALL,
)

EMPLOYEE_PATTERN = re.compile(
    r"^\s*\*{1,2}([^*\n]+)\*{1,2}\s*$",
    re.MULTILINE,
)


def _normalize_name(value: str) -> str:
    return " ".join(value.casefold().split())


def _split_sections(text: str) -> dict[str, str]:
    matches = list(SECTION_PATTERN.finditer(text))
    sections = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group(1).casefold()] = text[start:end].strip()
    return sections


def _participant_id_by_name(
    full_name: str,
    participants: list[dict],
) -> int | None:
    expected = _normalize_name(full_name)
    for participant in participants:
        names = (
            participant["last_name"],
            participant["first_name"],
            participant.get("patronymic") or "",
        )
        complete_name = _normalize_name(" ".join(names))
        short_name = _normalize_name(" ".join(names[:2]))
        if expected in {complete_name, short_name}:
            return participant["id"]
    return None


def _normalize_deadline(value: str) -> str:
    deadline = value.strip().rstrip(".;")
    for date_format in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(deadline, date_format).date()
            return parsed.strftime("%d.%m.%Y")
        except ValueError:
            continue
    raise AIReportParseError(f"Некорректный срок задачи: {deadline}")


def _parse_tasks(section: str, participants: list[dict]) -> list[dict]:
    employees = list(EMPLOYEE_PATTERN.finditer(section))
    tasks = []

    for index, match in enumerate(employees):
        employee_id = _participant_id_by_name(match.group(1), participants)
        if employee_id is None:
            raise AIReportParseError(
                "AI назначил задачу сотруднику, которого нет среди участников."
            )

        start = match.end()
        end = (
            employees[index + 1].start() if index + 1 < len(employees) else len(section)
        )
        employee_block = section[start:end]

        for task_match in TASK_PATTERN.finditer(employee_block):
            content = " ".join(task_match.group(1).split())
            if not content:
                raise AIReportParseError("AI вернул задачу без описания.")
            tasks.append(
                {
                    "employee_id": employee_id,
                    "content": content,
                    "deadline": _normalize_deadline(task_match.group(2)),
                }
            )
    return tasks


def parse_ai_report(text: str, participants: list[dict]) -> dict:
    if not isinstance(text, str) or not text.strip():
        raise AIReportParseError("AI вернул пустой текст отчёта.")

    sections = _split_sections(text)
    topic = sections.get("тема совещания", "").strip()
    summary = sections.get("содержание", "").strip()
    if not topic or not summary:
        raise AIReportParseError(
            "В ответе AI отсутствует тема или содержание совещания."
        )

    questions = [
        line.lstrip(" -*•\t").strip()
        for line in sections.get("ключевые вопросы", "").splitlines()
        if line.lstrip(" -*•\t").strip()
    ]
    tasks = _parse_tasks(sections.get("задачи", ""), participants)

    return {
        "topic": topic,
        "key_questions": questions,
        "summary": summary,
        "tasks": tasks,
    }

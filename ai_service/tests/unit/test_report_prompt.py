from app.services.report_prompt import build_report_prompt


def test_build_report_prompt_contains_input_data() -> None:
    prompt = build_report_prompt(
        transcript="Обсудили выпуск новой версии",
        participants="Иванов Иван, Петрова Ольга",
        meeting_date="2026-07-16",
    )

    assert "Транскрипция совещания: Обсудили выпуск новой версии" in prompt
    assert "Участники: Иванов Иван, Петрова Ольга" in prompt
    assert "Дата совещания: 2026-07-16" in prompt


def test_build_report_prompt_contains_required_report_structure() -> None:
    prompt = build_report_prompt(
        transcript="Текст встречи",
        participants="Иванов Иван",
        meeting_date="2026-07-16",
    )

    assert "**Тема совещания**" in prompt
    assert "**Ключевые вопросы**" in prompt
    assert "**Содержание**" in prompt
    assert "**Задачи**" in prompt
    assert "**Задача**" in prompt
    assert "**Срок**" in prompt


def test_build_report_prompt_preserves_unicode_and_special_characters() -> None:
    prompt = build_report_prompt(
        transcript='Решили: выпустить версию "2.0" — до пятницы.',
        participants="Анна Ёлкина",
        meeting_date="16.07.2026",
    )

    assert 'Решили: выпустить версию "2.0" — до пятницы.' in prompt
    assert "Анна Ёлкина" in prompt

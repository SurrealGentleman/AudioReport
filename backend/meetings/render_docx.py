from pathlib import Path

from docxtpl import DocxTemplate


def render_docx_template(
    template_path: Path,
    context: dict,
    output_path: Path,
) -> None:
    if not template_path.is_file():
        raise FileNotFoundError(f"Шаблон отчёта не найден: {template_path}")

    document = DocxTemplate(template_path)
    document.render(context)
    document.save(output_path)

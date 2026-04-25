import shutil
from openpyxl import load_workbook
from pathlib import Path
from datetime import datetime

TEMPLATE_PATH = Path(__file__).parent / "template.xlsx"
REPORTS_DIR = Path("reports")

# Data starts at row 4, template has 34 slots (rows 4..37)
DATA_START_ROW = 4
DATA_END_ROW = 37


def _next_empty_row(ws) -> int | None:
    for row_idx in range(DATA_START_ROW, DATA_END_ROW + 1):
        if ws.cell(row=row_idx, column=2).value is None:
            return row_idx
    return None


def get_or_create_report(report_path: Path) -> Path:
    if not report_path.exists():
        REPORTS_DIR.mkdir(exist_ok=True)
        shutil.copy(TEMPLATE_PATH, report_path)
    return report_path


def add_receipt(
    org_name: str,
    amount: float,
    vat: float,
    payment_date: datetime,
    report_path: Path | None = None,
) -> Path:
    path = report_path or REPORTS_DIR / f"report_{datetime.now():%Y-%m}.xlsx"
    get_or_create_report(path)

    wb = load_workbook(path)
    ws = wb.active

    row = _next_empty_row(ws)
    if row is None:
        raise RuntimeError("Шаблон заполнен — все 34 строки заняты")

    ws.cell(row=row, column=2).value = org_name
    ws.cell(row=row, column=3).value = amount
    ws.cell(row=row, column=4).value = vat
    ws.cell(row=row, column=5).value = payment_date

    wb.save(path)
    return path

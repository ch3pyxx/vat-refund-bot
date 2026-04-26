import shutil
from openpyxl import load_workbook
from pathlib import Path
from datetime import datetime

TEMPLATE_PATH = Path(__file__).parent / "template.xlsx"
REPORTS_DIR = Path("reports")

DATA_START_ROW = 4
DATA_END_ROW = 37
_IDS_SHEET = "_ids"


class DuplicateReceiptError(Exception):
    pass


def get_user_report_path(user_id: int) -> Path:
    """Путь к файлу-реестру конкретного пользователя за текущий месяц."""
    return REPORTS_DIR / f"{user_id}_{datetime.now():%Y-%m}.xlsx"


def _next_empty_row(ws) -> int | None:
    for row_idx in range(DATA_START_ROW, DATA_END_ROW + 1):
        if ws.cell(row=row_idx, column=2).value is None:
            return row_idx
    return None


def _get_seen_ids(wb) -> set[str]:
    if _IDS_SHEET not in wb.sheetnames:
        return set()
    return {str(row[0].value) for row in wb[_IDS_SHEET].iter_rows() if row[0].value}


def _record_id(wb, receipt_id: str) -> None:
    if _IDS_SHEET not in wb.sheetnames:
        ws = wb.create_sheet(_IDS_SHEET)
        ws.sheet_state = "hidden"
    else:
        ws = wb[_IDS_SHEET]
    ws.append([receipt_id])


def get_or_create_report(report_path: Path) -> Path:
    if not report_path.exists():
        REPORTS_DIR.mkdir(exist_ok=True)
        shutil.copy(TEMPLATE_PATH, report_path)
    return report_path


def add_receipt(
    user_id: int,
    org_name: str,
    amount: float,
    vat: float,
    payment_date: datetime,
    receipt_id: str,
) -> Path:
    path = get_user_report_path(user_id)
    get_or_create_report(path)

    wb = load_workbook(path)
    ws = wb.active

    if receipt_id in _get_seen_ids(wb):
        raise DuplicateReceiptError(receipt_id)

    row = _next_empty_row(ws)
    if row is None:
        raise RuntimeError("Шаблон заполнен — все 34 строки заняты")

    ws.cell(row=row, column=2).value = org_name
    ws.cell(row=row, column=3).value = amount
    ws.cell(row=row, column=4).value = vat
    ws.cell(row=row, column=5).value = payment_date

    _record_id(wb, receipt_id)
    wb.save(path)
    return path


def clear_user_reports(user_id: int) -> int:
    """Удаляет все файлы-реестры пользователя. Возвращает кол-во удалённых файлов."""
    if not REPORTS_DIR.exists():
        return 0
    deleted = 0
    for f in REPORTS_DIR.glob(f"{user_id}_*.xlsx"):
        f.unlink()
        deleted += 1
    return deleted

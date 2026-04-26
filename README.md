# 🧾 VAT Refund Bot

Telegram-бот для автоматического ведения реестра НДС по чекам с **soliq.uz**.

Пользователь отправляет фото QR-кода с чека → бот распознаёт код, скачивает данные с soliq.uz и добавляет строку в Excel-реестр НДС за текущий месяц.

---

## ✨ Возможности

- 📷 Распознавание QR-кодов с фото (с fallback-стратегией для плохих снимков)
- 🌐 Автоматический парсинг страницы чека на soliq.uz (организация, сумма, НДС, дата)
- 📊 Ведение Excel-реестра по готовому шаблону "Реестр НДС"
- 👥 Изолированные реестры для каждого пользователя
- 🗑️ Кнопка очистки реестра в один клик

---

## 🏗️ Архитектура

```
Фото QR  ─►  decode_qr  ─►  URL чека
                                │
                                ▼
                          parse_receipt  ─►  ReceiptData
                                                  │
                                                  ▼
                                            add_receipt  ─►  Excel
```

---

## 🚀 Установка и запуск

### 1. Клонирование

```bash
git clone https://github.com/ch3pyxx/vat-refund-bot.git
cd vat-refund-bot
```

### 2. Виртуальное окружение

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 3. Зависимости

```bash
pip install -r requirements.txt
```

> **Linux:** для `pyzbar` нужна системная библиотека:
> ```bash
> sudo apt install libzbar0
> ```

### 4. Токен бота

Создай файл `.env` в корне проекта:

```
TOKEN = 1234567890:AAH...your-token-here
```

Получить токен можно у [@BotFather](https://t.me/BotFather).

### 5. Запуск

```bash
cd src/bot
python main.py
```

---

## 📱 Команды бота

| Команда | Кнопка | Что делает |
|---|---|---|
| `/start` | — | Приветствие, показывает клавиатуру |
| `/help` | Помощь | Краткая инструкция |
| `/report` | Получить отчёт | Присылает Excel-реестр за текущий месяц |
| `/clear` | Очистить реестр | Удаляет все реестры пользователя |
| (фото) | Отправить чек | Запускает пайплайн обработки чека |

---

## 📁 Структура проекта

```
vat-refund-bot/
├── .env                        # Токен бота (не в git)
├── requirements.txt
├── README.md
└── src/
    ├── bot/                    # Telegram-интерфейс
    │   ├── main.py             # Точка входа
    │   ├── config.py           # Конфигурация (pydantic-settings)
    │   ├── handlers.py         # Хендлеры команд и фото
    │   └── keybord.py          # Клавиатура
    ├── recognition/            # Распознавание чека
    │   ├── decoder.py          # QR-код → URL
    │   └── parsep.py           # URL → ReceiptData
    └── reports/                # Excel-отчёты
        ├── template.xlsx       # Шаблон "Реестр НДС"
        └── excel_report.py     # Запись в реестр
```

---

## 🛠️ Стек технологий

| Категория | Технология |
|---|---|
| Telegram-бот | `aiogram 3.x` |
| Конфиг | `pydantic-settings` |
| Распознавание | `opencv-python`, `pyzbar`, `numpy` |
| Парсинг HTML | `requests`, `beautifulsoup4` |
| Excel | `openpyxl` |
| Тесты | `pytest`, `pytest-asyncio` |

---

## 🧪 Тестирование

В папке `fixturse/` лежат тестовые фото чеков. Прогон end-to-end:

```python
import asyncio, sys
sys.path.insert(0, "src")
from recognition.decoder import decode_qr
from recognition.parsep import parse_receipt
from reports.excel_report import add_receipt

async def test():
    image = open("fixturse/test.jpg", "rb").read()
    url = await decode_qr(image)
    receipt = await parse_receipt(url)
    add_receipt(
        user_id=999,
        org_name=receipt.org_name,
        amount=receipt.amount,
        vat=receipt.vat,
        payment_date=receipt.payment_date,
    )

asyncio.run(test())
```

---

## 📝 TODO

- [x] Поправить формулу в шаблоне: `=SUM(D4:D7)` → `=SUM(D4:D37)`
- [x] Защита от дублей чеков (по `receipt_id`)
- [ ] Логирование в файл (сейчас только в консоль)
- [ ] Обработка случая, когда 34 слота закончились
- [ ] Интеграционные тесты `pytest`
- [ ] Docker-контейнер для деплоя

---

## 👤 Автор

[ch3pyxx](https://github.com/ch3pyxx)

Первый стартап — учусь по ходу. Pull-реквесты и предложения приветствуются.

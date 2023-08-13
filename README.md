# Извлечение данных из API QuickResto

Этот скрипт на Python извлекает данные из API QuickResto за заданный период времени и создает отчеты в форматах JSON и
Excel.

## Подготовка

- Python 3.x
- Необходимые пакеты Python: `openpyxl`, `requests`

## Установка

1. Клонируйте этот репозиторий на ваше локальное устройство.
2. Установите необходимые пакеты, выполнив:

   ```bash
   pip install openpyxl requests

## Конфигурация

1. Создайте файл `config.json` в корневой директории проекта со следующим содержимым:

```json
{
  "cloud": "ВАШЕ_ОБЛАКО",
  "username": "ВАШ_ЛОГИН",
  "password": "ВАШ_ПАРОЛЬ"
}
```

Замените значения на свои данные облака QuickResto, имя пользователя и пароль.

## Использование

1. Запустите скрипт `main.py` для извлечения данных из API QuickResto и создания отчетов.

```
python main.py
```

2. Скрипт выполнит следующие действия:
    - Прочтет данные конфигурации из `config.json`.
    - Извлечет данные из API QuickResto для заданного периода времени.
    - Сохранит извлеченные данные в JSON-файле (`orders(начальная_дата_конечная_дата).json`).
    - Сгенерирует два отчета в формате Excel:
    - Общий отчет (`total_report_начальная_дата_конечная_дата.xlsx`): Содержит агрегированную статистику продаж.
    - Отчет о расходе продуктов (`product_expense_report_начальная_дата_конечная_дата.xlsx`): Содержит подробную
      информацию о расходах продуктов.
3. Сгенерированные отчеты будут сохранены в директории проекта.

## Функции для работы с API

### `api.py`

Содержит функции для взаимодействия с API QuickResto.

- `fetch_data(cloud, username, password, start_datetime_str, end_datetime_str)`: Извлекает данные о заказах за указанный
  период времени.
- `fetch_order_details(cloud, username, password, object_id)`: Извлекает подробную информацию о конкретном заказе.

## Лицензия

Этот проект лицензирован в соответствии с лицензией MIT - подробности в файле [LICENSE](LICENSE).

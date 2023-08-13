import os
import json
import openpyxl
from datetime import datetime
from openpyxl.styles import Border, Side, Alignment
from api import fetch_data, fetch_order_details

# Функция для создания Excel файла с заголовками и данными
def create_excel_file(filename, headers, data):
    """
    Создает Excel файл и заполняет его данными.

    :param filename: Имя файла для сохранения.
    :param headers: Заголовки столбцов.
    :param data: Данные для заполнения таблицы.
    """
    # Создание нового Excel-файла и активного листа
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Sheet'

    # Заполнение заголовков столбцов
    sheet.append(headers)

    # Заполнение таблицы данными
    for item in data:
        sheet.append(item)

    # Настройка границ ячеек и выравнивания текста
    thin_border = Border(left=Side(style='thin'),
                         right=Side(style='thin'),
                         top=Side(style='thin'),
                         bottom=Side(style='thin'))
    header_left_alignment = Alignment(horizontal='left', vertical='center')
    value_right_alignment = Alignment(horizontal='right', vertical='center')

    # Применение стилей к ячейкам
    for row in sheet.iter_rows(min_row=1, max_row=len(data) + 1, max_col=len(headers)):
        for cell in row:
            cell.border = thin_border
            if cell == row[0]:
                cell.alignment = header_left_alignment  # Выравнивание для заголовков
            else:
                cell.alignment = value_right_alignment  # Выравнивание для данных
            max_length = max(len(str(cell.value)) for cell in row)
            adjusted_width = (max_length + 2) * 1.2
            sheet.column_dimensions[cell.column_letter].width = adjusted_width

    # Сохранение файла
    workbook.save(filename)


# Чтение облака, логина и пароля из файла config.json
with open('config.json') as config_file:
    config_data = json.load(config_file)
    cloud = config_data['cloud']
    username = config_data['username']
    password = config_data['password']

# Установка периода для запроса данных
start_datetime_str = '2023-08-01'
end_datetime_str = '2023-08-05'

# Выполняем запрос к API для получения данных
data = fetch_data(cloud, username, password, start_datetime_str, end_datetime_str)

if data is not None:
    # Записываем данные в JSON файл
    json_filename = f'orders({start_datetime_str}_{end_datetime_str}).json'
    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)

    # Инициализация переменных для статистики и расходов продуктов
    first_sale_date = None
    last_sale_date = None
    total_discount = 0.0
    total_surcharge = 0.0
    total_canceled = 0
    total_profit = 0.0
    product_data = {}  # Словарь для хранения расходов продуктов

    # Проходим по всем чекам для вычисления статистики и получения подробной информации
    for entry in data:
        # Получаем objectId для запроса подробной информации о чеке
        object_id = entry.get('id')
        if object_id:
            order_details = fetch_order_details(cloud, username, password, object_id)
            if order_details is not None:
                # Сохраняем подробную информацию в JSON файл с уникальным именем
                order_details_filename = f'order_{object_id}.json'
                with open(order_details_filename, 'w', encoding='utf-8') as order_details_file:
                    json.dump(order_details, order_details_file, indent=4, ensure_ascii=False)
                print(f'Подробная информация о чеке {object_id} сохранена в файле: {order_details_filename}')

                # Обработка расходов продуктов
                products_outgoing = order_details.get('productOutgoing', [])
                for product in products_outgoing:
                    product_name = product['product']['name']
                    amount = product['amount']
                    measure_unit = product['product']['measureUnit']['name']
                    if product_name in product_data:
                        product_data[product_name]['amount'] += amount
                    else:
                        product_data[product_name] = {'amount': amount, 'measure_unit': measure_unit}
            else:
                print(f'Не удалось получить подробную информацию о чеке {object_id}')

        # Вычисляем статистику по всем чекам
        sale_date = entry.get('createDate')
        if sale_date:
            sale_date = datetime.strptime(sale_date, '%Y-%m-%dT%H:%M:%S.%fZ')
            if not first_sale_date or sale_date < first_sale_date:
                first_sale_date = sale_date
            if not last_sale_date or sale_date > last_sale_date:
                last_sale_date = sale_date

        front_sum = entry.get('frontSum', 0)
        front_total_price = entry.get('frontTotalPrice', 0)
        discount = front_sum - front_total_price
        if discount > 0:
            total_discount += discount
        else:
            total_surcharge += -discount

        if entry.get('returned'):
            total_canceled += 1

        total_profit += front_total_price

    # Создаем общий отчет
    report_data = [
        ('Дата первой продажи', first_sale_date.strftime('%Y-%m-%d %H:%M:%S') if first_sale_date else ''),
        ('Дата последней продажи', last_sale_date.strftime('%Y-%m-%d %H:%M:%S') if last_sale_date else ''),
        ('Сумма скидок', total_discount),
        ('Сумма надбавок', total_surcharge),
        ('Количество отмен', total_canceled),
        ('Общая прибыль', total_profit)
    ]
    create_excel_file(f'total_report_{start_datetime_str}_{end_datetime_str}.xlsx', ['Показатель', 'Значение'], report_data)

    # Создаем отчет о расходе продуктов
    product_report_data = []
    for product_name, data in product_data.items():
        product_report_data.append([product_name, data['amount'], data['measure_unit']])
    create_excel_file(f'product_expense_report_{start_datetime_str}_{end_datetime_str}.xlsx', ['Продукт', 'Общий расход', 'Единица измерения'], product_report_data)

    # Открываем файлы Excel
    try:
        os.system(f'start excel "total_report_{start_datetime_str}_{end_datetime_str}.xlsx"')
        os.system(f'start excel "product_expense_report_{start_datetime_str}_{end_datetime_str}.xlsx"')
        print(f'Общий отчет сохранен в файле: total_report_{start_datetime_str}_{end_datetime_str}.xlsx')
        print(f'Отчет о расходе продуктов сохранен в файле: product_expense_report_{start_datetime_str}_{end_datetime_str}.xlsx')
    except Exception as e:
        print(f'Произошла ошибка при открытии файла: {e}')
else:
    print('Не удалось получить данные из API')

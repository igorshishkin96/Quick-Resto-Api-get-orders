import os
import openpyxl
from datetime import datetime
from openpyxl.styles import Border, Side, Alignment


def generate_report(answer, start_date, end_date):
    # Инициализация переменных для расчета статистики
    first_sale_date = None
    last_sale_date = None
    total_discount = 0.0
    total_surcharge = 0.0
    total_canceled = 0
    total_profit = 0.0

    # Проходим по всем чекам для вычисления статистики
    for entry in answer:
        # Вычисляем первую и последнюю дату продаж
        sale_date = entry.get('createDate')
        if sale_date:
            sale_date = datetime.strptime(sale_date, '%Y-%m-%dT%H:%M:%S.%fZ')
            if not first_sale_date or sale_date < first_sale_date:
                first_sale_date = sale_date
            if not last_sale_date or sale_date > last_sale_date:
                last_sale_date = sale_date

        # Вычисляем сумму скидок и надбавок
        front_sum = entry.get('frontSum', 0)
        front_total_price = entry.get('frontTotalPrice', 0)
        discount = front_sum - front_total_price
        if discount > 0:
            total_discount += discount
        else:
            total_surcharge += -discount

        # Считаем количество отмен
        if entry.get('returned'):
            total_canceled += 1

        # Вычисляем общую прибыль
        total_profit += front_total_price

    # Создаем новый файл Excel
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Общий отчет'

    # Заполняем заголовки столбцов
    headers = ['Показатель', 'Значение']
    sheet.append(headers)

    # Заполняем таблицу данными
    report_data = [
        ('Дата первой продажи', first_sale_date.strftime('%Y-%m-%d %H:%M:%S') if first_sale_date else ''),
        ('Дата последней продажи', last_sale_date.strftime('%Y-%m-%d %H:%M:%S') if last_sale_date else ''),
        ('Сумма скидок', total_discount),
        ('Сумма надбавок', total_surcharge),
        ('Количество отмен', total_canceled),
        ('Общая прибыль', total_profit)
    ]

    for item in report_data:
        sheet.append(item)

    # Настройка границ ячеек и выравнивания текста
    thin_border = Border(left=Side(style='thin'),
                         right=Side(style='thin'),
                         top=Side(style='thin'),
                         bottom=Side(style='thin'))

    header_left_alignment = Alignment(horizontal='left', vertical='center')
    value_right_alignment = Alignment(horizontal='right', vertical='center')

    for row in sheet.iter_rows(min_row=1, max_row=len(report_data) + 1, max_col=2):
        header_cell, value_cell = row
        header_cell.border = thin_border
        value_cell.border = thin_border

        header_cell.alignment = header_left_alignment
        value_cell.alignment = value_right_alignment

    for column_cells in sheet.columns:
        max_length = max(len(str(cell.value)) for cell in column_cells)
        adjusted_width = (max_length + 2) * 1.2
        sheet.column_dimensions[column_cells[0].column_letter].width = adjusted_width

    # Сохраняем файл Excel с уникальным именем, включающим дату
    excel_filename = f'total_report_{start_date}_{end_date}.xlsx'
    workbook.save(excel_filename)

    # Проверяем наличие файла перед открытием
    try:
        os.system(f'start excel "{excel_filename}"')
        print(f'Общий отчет сохранен в файл: {excel_filename}')
    except Exception as e:
        print(f'Произошла ошибка при открытии файла: {e}')

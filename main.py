import requests
import json
from generate_total_report import generate_report

# Чтение облака, логина и пароля из файла config.json
with open('config.json') as config_file:
    config_data = json.load(config_file)
    cloud = config_data['cloud']
    username = config_data["username"]
    password = config_data["password"]

# Указываем URL для взаимодействия с API
url = f'https://{cloud}.quickresto.ru/platform/online/api/list'
start_datetime_str = '2023-07-01'
end_datetime_str = '2023-07-31'

# Заголовки для HTTP-запроса
headers = {
    'Content-Type': 'application/json',
    'Connection': 'keep-alive',
}

# Параметры для HTTP-запроса
data = {
    'filters': [{
        'field': 'serverRegisterTime',
        'operation': 'range',
        'value': {
            'since': start_datetime_str,
            'till': end_datetime_str
        }
    }]
}

params = {
    'moduleName': 'front.orders',
    'className': 'ru.edgex.quickresto.modules.front.orders.OrderInfo'
}

# Выполняем GET-запрос к API
response = requests.get(
    url=url,
    headers=headers,
    json=data,
    params=params,
    auth=(username, password)
)

# Проверяем статус ответа
if response.status_code == 200:
    # Преобразуем полученные данные в формат JSON
    answer = json.loads(response.text)

    # Сохраняем данные в файл JSON
    with open(f'orders({start_datetime_str}_{end_datetime_str}).json', 'w', encoding='utf-8') as file:
        json.dump(answer, file, indent=4)

    # Вызываем функцию для генерации отчета
    generate_report(answer, start_datetime_str, end_datetime_str)
else:
    print('Status code:', response.status_code)

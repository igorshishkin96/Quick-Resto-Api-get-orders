import requests
import json


def fetch_data(cloud, username, password, start_datetime_str, end_datetime_str):
    """
    Получает данные о чеках из API QuickResto за заданный период времени.

    :param cloud: Имя облака QuickResto.
    :param username: Имя пользователя.
    :param password: Пароль.
    :param start_datetime_str: Начальная дата и время в формате строки.
    :param end_datetime_str: Конечная дата и время в формате строки.
    :return: Json-объект со списком чеков или None в случае ошибки.
    """
    # Указываем URL для взаимодействия с API
    url = f'https://{cloud}.quickresto.ru/platform/online/api/list'
    params = {
        'moduleName': 'front.orders',
        'className': 'ru.edgex.quickresto.modules.front.orders.OrderInfo'
    }

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
        return json.loads(response.text)
    else:
        return None


def fetch_order_details(cloud, username, password, object_id):
    """
    Получает подробную информацию о чеке из API QuickResto.

    :param cloud: Имя облака QuickResto.
    :param username: Имя пользователя.
    :param password: Пароль.
    :param object_id: Идентификатор объекта чека.
    :return: Json-объект с подробной информацией о чеке или None в случае ошибки.
    """
    # Указываем URL для взаимодействия с API
    url = f'https://{cloud}.quickresto.ru/platform/online/api/read'
    params = {
        'moduleName': 'front.orders',
        'objectId': object_id
    }

    # Заголовки для HTTP-запроса
    headers = {
        'Content-Type': 'application/json',
        'Connection': 'keep-alive',
    }

    # Выполняем GET-запрос к API
    response = requests.get(
        url=url,
        headers=headers,
        params=params,
        auth=(username, password)
    )

    # Проверяем статус ответа
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print(f'Error fetching order details for objectId {object_id}. Status code:', response.status_code)
        return None

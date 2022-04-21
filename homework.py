import time
import telegram
import os
import requests
import logging
import sys
from dotenv import load_dotenv


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 60                 # пОМЕНЯТЬ НА 600!!!!!!!!!
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

UPDATE_STATUS = {}
HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправка сообщения в чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info(f'Бот отправил сообщение "{message}"')
    except Exception as error:
        logging.error('Сбой при отправке сообщения.', error)


def get_api_answer(current_timestamp):
    """Отправляем get запрос по API, приводим к типам данных Python."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code != 200:
        logging.error(
            f'Сбой в работе программы: Эндпоинт {ENDPOINT} недоступен.'
            f'Код ответа API: {response.status_code}')
        # Без SystemExit не проходил тесты
        raise SystemExit('Server response status code != 200')
    return response.json()


def check_response(response):
    """Проверяем ответ API на корректность, возвращая.
    список домашных работ.
    """
    # Если не поставить точку в первой строке docstring'a flake8
    # не пропускает D400, пришлось поставить (55,72 строка)
    homeworks = response['homeworks']
    if type(homeworks) != list:
        logging.error('Ответ от API пришел не в виде списка.')
        # Без SystemExit не проходил тесты
        raise SystemExit('Программа принудительно остановлена.')
    return homeworks


def parse_status(homework):
    """Логика проверки статуса: объявил глобальную переменную словарь.
    куда добавляется домашка: статус. Если домашки нету - добавляем.
    В ином случае проверяем по ключу - значение. Есть разница обновляем
    значение и отправляет вердикт.
    """
    # Ответ в виде: <github_nickname>__hw05_final.zip не очень, как по мне
    # я делал по ключу lesson_name и ответ был более красив:
    # Проект спринта: подписки на авторов. Но тесты не пускают :(
    homework_name = homework['homework_name']     # lesson_name
    homework_status = homework['status']
    if homework_name in UPDATE_STATUS:
        if UPDATE_STATUS[homework_name] == homework_status:
            logging.debug('Отсутствие в ответе новых статусов.')
            return 0
    else:
        UPDATE_STATUS[homework_name] = homework_status
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности переменных окружения."""
    env_dict = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    for name, env in env_dict.items():
        if not env:
            logging.critical(f'Нету обязательной переменной окружения {name}')
            return False
    return True


def main():
    """Основная логика работы бота."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )
    logging.StreamHandler(sys.stdout)
    if check_tokens() is False:
        raise SystemExit('Программа принудительно остановлена.')

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            for homework in homeworks:
                message = parse_status(homework)
                if message != 0:
                    send_message(bot, message)

            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            time.sleep(RETRY_TIME)
        else:
            logging.debug('Исключений не возникло, работаем.')


if __name__ == '__main__':
    main()

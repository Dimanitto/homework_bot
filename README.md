# Описание проекта homework_bot
Проект homework_bot предназначен для проверки статуса сданной домашней работы на сервере Яндекса. С периодичностью раз в 10 минут бот отправляет запрос к серверу Яндекса. В случае изменения статуса работы, бот пришлет сообщение в мессенджере Телеграм.
### Технологии
* Python 3.7
* python-telegram-bot 13.7
* Dotenv
* Logging
### Подготовка к запуску
- Установите и активируйте виртуальное окружение
```
python -m venv venv
source venv/scripts/activate
```
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
``` 
Создаем .env файл с токенами:

```
PRACTICUM_TOKEN=<PRACTICUM_TOKEN>
TELEGRAM_TOKEN=<TELEGRAM_TOKEN>
TELEGRAM_CHAT_ID =<CHAT_ID>
```
- Запустить проект
```
python homework.py
```

### Автор
Selivanov Dmitry

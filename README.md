# Чатбот интернет-магазин

Бот для совершения покупок через Telegram, который интегрируется с CMS, используя [ElasticPath API](https://documentation.elasticpath.com/commerce-cloud/docs/api/index.html)

## На данный момент в боте реализовано:

* Вывод списка товаров магазина
* Добавление товаров в корзину
* Удаление товаров из корзины
* Вывод содержимого корзины
* Навигация по меню
* Добавление заказа и клиента в базу

## Как уствновить

Python3 должен быть уже установлен. Затем используйте pip (или pip3, есть конфликт с Python2) для установки зависимостей.
```python 
pip install -r requirements.txt
```
Параметры TG_BOT_TOKEN, MOLTIN_CLIENT_SECRET, MOLTIN_CLIENT_ID, REDIS_PASSWORD, REDIS_HOST и REDIS_PORT должны находится в файле .env рядом со скриптом. 

## Пример использования

[![fish_store_bot.gif](https://s2.gifyu.com/images/fish_store_bot.gif)](https://gifyu.com/image/UJKe)

## Деплой на Heroku

Склонируйте репозиторий, войдите или зарегистрируйтесь на [Heroku](https://dashboard.heroku.com)

Создайте новое приложение Heroku, во вкладке Deploy подключите ваш github аккаунт.Выберите нужный репозиторий.

Во вкладке Settings установите переменные окружения как Config Vars.

Активируйте бота на вкладке Resourses.

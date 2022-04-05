1. Если длинна больше 4096 бот делить сообщение на части

2. Во время запроса данных по email ставиться блокировка на следующий запрос до завершения

3.Каждый 24 часа автоматически обновляются  количество суточных запросов, общая информация бота типа суточные подписки, сумма и тд.
так же статус подписки, если закончилась меняется на дефолтное 3 запроса в день.

4. В настройках работы бота можно отключить проверку на канал/группу для добавления суточные запросов. Бот должен быть добавлен в эту группу для проверки наличия юзера среди участников.

5. Каждый час делается backup основных данных типо юзера, подписки, проведенных платежей в папку backup в основном каталоге бота.

6. В админ меню, в функции "посмотреть меню" можно  поменять текст всех основных текстов и кнопок.
 Кнопки Профиль, Кнопка Описание, Кнопка Поддержка не менять первые символы, они используются для определения при нажатии

7. Запуск импорта
1. cd /home/user/user_database_tg/
2. poetry run python user_database_tg/db/utils/parsing_data.py --path=/var/lib/postgresql/TO_IMPORT
после успешной выгрузки данных в бд, удаляются файлы и каталог.
проверяйте корректность пути чтобы случайно не удалить важные файлы.
Процесс отображается в терминале или в папке logs/database.log в каталоге бота

8. Запуск бота
1. cd /home/user/user_database_tg/
2. poetry run python user_database_tg/main.py
Перед запуском проверьте не запущена ли другая копия бота, которая может привести к блокировке процесса.

9. Чтобы запустить бота в отдельном окне или проверить работу ввести screen -r после подключения в серверу. Запускать бота там же, чтобы процесс был запущен в фоне

10. Данные которые можно менять в бд
--таблица db_user.
language(russian, english)
is_search(Это блокировка во время поиска если true значит пользователь отправил запрос и ожидает ответа)

--таблица db_translation
можно менять все кроме столбцов title, language

- -таблица subscrition_info
хранить шаблоны для создания подписок,
столбец daily_limit ставить null для безлимита

--таблица payment. Информация о уже завершенных платежах с привязкой к таблице db_user

-таблица billing. Платежи ожидающие оплаты

-таблица Subscription. Лучше менять через админку.

11. Файл конфига с токеном и данными с бд .env в основном каталоге.

12.После каждого  изменения текста или описания в админ панели, автоматически переводиться на английский вариант и загружается в бд.

13. Резервная копия создается каждый час.
Выгрузка backup в базу командой:
1. cd /home/user/user_database_tg/
2. poetry run python user_database_tg/app/utils/backup.py
Скрипт проверяет наличие моделей и добавляет отсутствующие

*****
14.Для выгрузки на другую машину:
1.1| sudo apt update && sudo apt upgrade
1.2| sudo add-apt-repository ppa:deadsnakes/ppa && sudo apt update && sudo apt install python3.10 && sudo apt install python3.10-venv
1.3|
1.4|
1.5|
1.6| curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3.10 -

2.зайти в нужную папку c помощью: cd /home/
2.1 git clone https://github.com/taimaskhanov11/user_database_tg.git
2.2 cd user_database_tg
2.3 Заполнить данные в файле конфига .env
2.3 poetry install --no-dev
2.4 poetry update --no-dev
2.4.1 (если нужно перенести данные) poetry run python user_database_tg/app/utils/backup.py
2.5 poetry run python user_database_tg/main.py(При первом запуске может выскочить ошибка, просто заупстите еще раз)
______________________
14.
Для выгрузки с одной базы на другую
cd /home/user/user_database_tg/
poetry run python user_database_tg\db\utils\import_data.py --from_=old --username=postgres --password=Tel993917. --host=95.105.113.65 --port=5432 --db_name=users_database --to=new --username2=your_username --password2=your_password --host2=your_hosting --port2=your_port --db_name2=your_db_name
вместо  username2 password2 host2 port2 db_name2 поставить нужные данные
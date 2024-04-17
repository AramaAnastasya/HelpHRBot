**Введение:** Чат-бот предназначен для автоматизации задач HR. Он предоставляет сотрудникам удобный и эффективный способ подачи запросов, для HR фиксирование приходящих запросов сотрудников, вывод статистики выполнения, возможность дать обратную связь по выполненному запросу.

**Требования к базе данных**
Для работы чат-бота требуется база данных с шестью таблицами:
employee (сотрудники), Type_request (типы запросов), Applications (заявки), Question(вопросы), Division(подразделения), Position(должность)

Конфигурация таблицы "employee"
В таблице "employee" необходимо зарезервировать идентификатор (id) 1 для использования в заявках, в которых указывается кандидат. Это связано с тем, что чат-бот использует id 1 для фиксирования связи с таблицей employee, при добавлении кандидата в заявку.

Конфигурация таблицы "Type_request"
В таблице "Type_request" заявки должны располагаться в следующем порядке:
1. Заявка на перевод
2. Заявка на перевод на другой формат работы
3. Заявка на перевод на согласование заработной платы
4. Общая форма

**Использование чат-бота**
Для использования чат-бота выполните следующие действия:
1. Добавьте учетную запись HR и сотрудников в базу данных.
2. Авторизуйтесь под ролью HR.
3. Отправьте боту команду /start.
3. Следуйте инструкциям бота для создания и управления запросами.

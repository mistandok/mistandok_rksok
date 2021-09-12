<p style="text-align: center;"><strong>Реализация сервера хранения телефонной книги</strong><strong></strong></p>
<p style="text-align: left;">Сервер работает по собственному протоколу обмена данными, который напоминает протокол HTTP. Протокол состоит из нескольких команд:</p>
<p style="text-align: left;"><code>ОТДОВАЙ, УДОЛИ, ЗОПИШИ, АМОЖНА?</code></p>
<p style="text-align: left;">На которые можно получить несколько типов ответа:</p>
<p style="text-align: left;"><code>НОРМАЛДЫКС, НИНАШОЛ, НИЛЬЗЯ</code></p>
<p style="text-align: left;">Пример команды в текстовом формате:</p>
<p style="text-align: left;">*key* - ключевое значение, не длиннее 30 символов. (Витя, Коля Иванов, Николай Петров и т.п.)</p>
<p style="text-align: left;">*value_i* - значение телефона (формат не проверяется, в качестве телефона может быть любой набор символов)</p>
<p style="text-align: left;"><code><span>"ОТДОВАЙ *key* РКСОК/1.0\r\n\r\n"</span></code></p>
<p style="text-align: left;"><code><span>"ЗОПИШИ *key*&nbsp;РКСОК/1.0\r\n*value_1*\r\n*value_2*.\r\n...*value_n*\r\n\r\n"</span></code></p>
<p style="text-align: left;"><code><span>"УДОЛИ *key* РКСОК/1.0\r\n"</span></code></p>
<p style="text-align: left;"><span>Команды, помимо проверки на удовлетворение формату протокола, валидируются на сервере проверки, который должен быть указан в конфигурационном файле .env.</span></p>
<p style="text-align: left;"><span>Если запрос не удовлетворяет проверкам на соответствие формата протоколу, то клиенту возвращается ответ:</span></p>
<p style="text-align: left;"><code><span>"НИПОНЯЛ РКСОК/1.0\r\n\r\n"</span></code></p>
<p style="text-align: left;"><span>Валидирующий сервер проверки может как разрешить обрабатывать запрос, так и запретить. В первом случае он вернет ответ:</span></p>
<p style="text-align: left;"><code><span>"МОЖНА РКСОК/1.0\r\n\r\n"</span></code></p>
<p style="text-align: left;"><span>во втором случае:</span></p>
<p style="text-align: left;"><code><span>"НИЛЬЗЯ РКСОК/1.0\r\n*reason*\r\n\r\n"</span></code></p>
<p style="text-align: left;"><span>Если запрос не прошел проверку, то возвращается ответ от валидирующего сервера. Если запрос прошел проверку, то дальше идет работа с хранилищем данных и, в зависимости от операции, возвращается ответ:</span></p>
<p style="text-align: left;"><code><span>"НОРМАЛДЫКС РКСОК/1.0\r\n\r\n"</span></code></p>
<p style="text-align: left;"><code><span>"НИНАШОЛ РКСОК/1.0\r\n\r\n"</span></code></p>
<p style="text-align: left;"><span>Информация о пользователе и его телефоне хранится в БД PostgreSQL:</span></p>
<p style="text-align: left;"><span><code>phonebookdb</code></span></p>
<p style="text-align: left;"><span>В таблице:</span><span></span></p>
<p style="text-align: left;"><span><code>userphones</code></span></p>
<p style="text-align: center;"><span><strong>Запуск сервера</strong></span></p>
<p style="text-align: left;">Для того, чтобы сервер корректно работал, необходимо:</p>
<ol>
<li style="text-align: left;">Наличие установленной БД <span>PostgreSQL</span></li>
<li style="text-align: left;"><span>Наличие пользователя, от лица которого будет осуществляться соединение с БД.</span></li>
<li style="text-align: left;"><span>наличие созданной БД&nbsp;<code><strong>phonebookdb </strong></code>в которой находится таблица&nbsp;<code><strong>userphones</strong></code>. Скрипт с созданием БД и таблицы для этой БД находится в файле SQLscripts.txt</span></li>
</ol>
<p>После того, как база данных будет создана, необходимо в корневой папке проекта создать конфигурационный файл .env, со следующим содержанием (необходимо задать параметры пользователя, который будет подключаться к БД, самостоятельно):</p>
<p style="text-align: left;"><code><span>SERVER_HOST=127.0.0.1</span></code></p>
<p style="text-align: left;"><code><span><br />SERVER_PORT=8000</span></code></p>
<p style="text-align: left;"><code><span><br />VALIDATE_SERVER_HOST=vragi-vezde.to.digital</span></code></p>
<p style="text-align: left;"><code><span><br />VALIDATE_SERVER_PORT=51624</span></code></p>
<p style="text-align: left;"><code><span><br />STORAGE_TYPE=PostgreSQL</span></code></p>
<p style="text-align: left;"><code><span><br />DB_USER=dbusername</span></code></p>
<p style="text-align: left;"><code><span><br />DB_USER_PASSWORD=dbuserpassword</span></code></p>
<p style="text-align: left;"><code><span><br />DB_NAME=phonebookdb</span></code></p>
<p style="text-align: left;"><code><span><br />DB_HOST=127.0.0.1</span></code></p>
<p style="text-align: left;">Далее необходимо развернуть новое виртуальное окружение в корневой папке проекта:</p>
<p style="text-align: left;"><code>python3.9 -m venv env</code></p>
<p style="text-align: left;">активировать его находясь в корневой папке проекта (команда для Debian):</p>
<p style="text-align: left;"><code>source ./env/bin/activate</code></p>
<p style="text-align: left;">установить все требуемые пакеты из pip_requirements.txt</p>
<p style="text-align: left;"><code>pip install -r&nbsp;pip_requirements.txt</code></p>
<p style="text-align: left;">После этого можно запустить входной модуль <strong>server.py</strong></p>
<p style="text-align: left;"><code>python server.py</code></p>
<p style="text-align: left;">Сервер будет ожидать запросы. Для тестирования сервера можно использовать скрипт client.py</p>
<p style="text-align: left;">Запускать его нужно так:&nbsp;</p>
<p style="text-align: left;"><code>python client.py 127.0.0.1 8000&nbsp;</code></p>
<p style="text-align: left;"></p>

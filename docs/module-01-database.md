# Модуль 1 — База данных (RDBExpert + Firebird)

**Время:** 50 минут.

## Что сдать

1. БД в **3НФ** с PK/FK  
2. **ER-диаграмма** в PDF  
3. Данные из `*_import.xlsx` и `import\*.jpg`  
4. **SQL-скрипт** БД (экспорт метаданных)

## Путь к БД (рекомендуется)

```
C:\BookStore\database.fdb
```

- **Встроенный сервер** — включён  
- Кодировка: **UTF8**  
- Пользователь: `SYSDBA` / `masterkey`  
- Путь только **латиницей** (не кириллица в профиле Windows)

## Порядок работы

1. **Создать базу данных** → указать путь `C:\BookStore\database.fdb`  
2. **Создать подключение** → подключиться (зелёная точка)  
3. **Редактор ER-диаграмм** → 10 таблиц + связи → применить к БД  
4. Заполнить данные (импорт xlsx или SQL)  
5. **ER** → обратный инжиниринг → PDF  
6. **Экспорт метаданных в SQL** (иконка SQL со стрелкой) → `BookStore_script.sql`

## Таблицы

`ROLE`, `CATEGORY`, `MANUFACTURER`, `SUPPLIER`, `PICKUP_POINT`, `ORDER_STATUS`, `USERS`, `PRODUCT`, `ORDERS`, `ORDER_ITEM`

## Проверка

```sql
SELECT COUNT(*) FROM PRODUCT;   -- ~43
SELECT COUNT(*) FROM USERS;     -- 10
SELECT COUNT(*) FROM PICKUP_POINT; -- 35
```

## Роли (справочник ROLE)

| ROLE_ID | ROLE_NAME |
|---------|-----------|
| 1 | Администратор |
| 2 | Менеджер |
| 3 | Авторизированный клиент |

## Статусы заказов

| STATUS_ID | STATUS_NAME |
|-----------|-------------|
| 1 | Завершен |
| 2 | Новый |

Подробные SQL-скрипты генерируются скриптами `gen_fill_sql.py` / `gen_full_sql.py` в корне репозитория (локально).

код
CREATE TABLE ROLE (
  ROLE_ID INTEGER NOT NULL,
  ROLE_NAME VARCHAR(50) NOT NULL,
  CONSTRAINT PK_ROLE PRIMARY KEY (ROLE_ID),
  CONSTRAINT UQ_ROLE_NAME UNIQUE (ROLE_NAME)
);
 
CREATE TABLE CATEGORY (
  CATEGORY_ID INTEGER NOT NULL,
  CATEGORY_NAME VARCHAR(100) NOT NULL,
  CONSTRAINT PK_CATEGORY PRIMARY KEY (CATEGORY_ID),
  CONSTRAINT UQ_CATEGORY_NAME UNIQUE (CATEGORY_NAME)
);
 
CREATE TABLE MANUFACTURER (
  MANUFACTURER_ID INTEGER NOT NULL,
  MANUFACTURER_NAME VARCHAR(150) NOT NULL,
  CONSTRAINT PK_MANUFACTURER PRIMARY KEY (MANUFACTURER_ID),
  CONSTRAINT UQ_MANUFACTURER_NAME UNIQUE (MANUFACTURER_NAME)
);
 
CREATE TABLE SUPPLIER (
  SUPPLIER_ID INTEGER NOT NULL,
  SUPPLIER_NAME VARCHAR(150) NOT NULL,
  CONSTRAINT PK_SUPPLIER PRIMARY KEY (SUPPLIER_ID),
  CONSTRAINT UQ_SUPPLIER_NAME UNIQUE (SUPPLIER_NAME)
);
 
CREATE TABLE PICKUP_POINT (
  PICKUP_POINT_ID INTEGER NOT NULL,
  ADDRESS VARCHAR(300) NOT NULL,
  CONSTRAINT PK_PICKUP_POINT PRIMARY KEY (PICKUP_POINT_ID)
);
 
CREATE TABLE ORDER_STATUS (
  STATUS_ID INTEGER NOT NULL,
  STATUS_NAME VARCHAR(30) NOT NULL,
  CONSTRAINT PK_ORDER_STATUS PRIMARY KEY (STATUS_ID),
  CONSTRAINT UQ_ORDER_STATUS_NAME UNIQUE (STATUS_NAME)
);
 
CREATE TABLE USERS (
  USER_ID INTEGER NOT NULL,
  ROLE_ID INTEGER NOT NULL,
  FULL_NAME VARCHAR(200) NOT NULL,
  LOGIN VARCHAR(100) NOT NULL,
  PASSWORD VARCHAR(50) NOT NULL,
  CONSTRAINT PK_USERS PRIMARY KEY (USER_ID),
  CONSTRAINT UQ_USERS_LOGIN UNIQUE (LOGIN),
  CONSTRAINT FK_USERS_ROLE FOREIGN KEY (ROLE_ID) REFERENCES ROLE(ROLE_ID)
);
 
CREATE TABLE PRODUCT (
  PRODUCT_ID INTEGER NOT NULL,
  ARTICLE VARCHAR(20) NOT NULL,
  PRODUCT_NAME VARCHAR(300) NOT NULL,
  UNIT_MEASURE VARCHAR(10) NOT NULL,
  PRICE NUMERIC(10,2) NOT NULL,
  CATEGORY_ID INTEGER NOT NULL,
  MANUFACTURER_ID INTEGER NOT NULL,
  SUPPLIER_ID INTEGER NOT NULL,
  DISCOUNT NUMERIC(5,2) DEFAULT 0,
  QUANTITY_STOCK INTEGER NOT NULL,
  DESCRIPTION BLOB SUB_TYPE TEXT,
  PHOTO_PATH VARCHAR(255),
  CONSTRAINT PK_PRODUCT PRIMARY KEY (PRODUCT_ID),
  CONSTRAINT UQ_PRODUCT_ARTICLE UNIQUE (ARTICLE),
  CONSTRAINT FK_PRODUCT_CATEGORY FOREIGN KEY (CATEGORY_ID) REFERENCES CATEGORY(CATEGORY_ID),
  CONSTRAINT FK_PRODUCT_MANUFACTURER FOREIGN KEY (MANUFACTURER_ID) REFERENCES MANUFACTURER(MANUFACTURER_ID),
  CONSTRAINT FK_PRODUCT_SUPPLIER FOREIGN KEY (SUPPLIER_ID) REFERENCES SUPPLIER(SUPPLIER_ID)
);
 
CREATE TABLE ORDERS (
  ORDER_ID INTEGER NOT NULL,
  ORDER_DATE DATE NOT NULL,
  DELIVERY_DATE DATE,
  PICKUP_POINT_ID INTEGER NOT NULL,
  USER_ID INTEGER NOT NULL,
  PICKUP_CODE INTEGER NOT NULL,
  STATUS_ID INTEGER NOT NULL,
  CONSTRAINT PK_ORDERS PRIMARY KEY (ORDER_ID),
  CONSTRAINT FK_ORDERS_PICKUP_POINT FOREIGN KEY (PICKUP_POINT_ID) REFERENCES PICKUP_POINT(PICKUP_POINT_ID),
  CONSTRAINT FK_ORDERS_USER FOREIGN KEY (USER_ID) REFERENCES USERS(USER_ID),
  CONSTRAINT FK_ORDERS_STATUS FOREIGN KEY (STATUS_ID) REFERENCES ORDER_STATUS(STATUS_ID)
);
 
CREATE TABLE ORDER_ITEM (
  ORDER_ITEM_ID INTEGER NOT NULL,
  ORDER_ID INTEGER NOT NULL,
  PRODUCT_ID INTEGER NOT NULL,
  QUANTITY INTEGER NOT NULL,
  CONSTRAINT PK_ORDER_ITEM PRIMARY KEY (ORDER_ITEM_ID),
  CONSTRAINT FK_ORDER_ITEM_ORDERS FOREIGN KEY (ORDER_ID) REFERENCES ORDERS(ORDER_ID),
  CONSTRAINT FK_ORDER_ITEM_PRODUCT FOREIGN KEY (PRODUCT_ID) REFERENCES PRODUCT(PRODUCT_ID)
);
 
INSERT INTO ROLE VALUES (1, 'Администратор');
INSERT INTO ROLE VALUES (2, 'Менеджер');
INSERT INTO ROLE VALUES (3, 'Авторизированный клиент');
 
INSERT INTO ORDER_STATUS VALUES (1, 'Завершен');
INSERT INTO ORDER_STATUS VALUES (2, 'Новый');
 
INSERT INTO CATEGORY VALUES (1, 'Художественная литература');
INSERT INTO CATEGORY VALUES (2, 'Учебник для вузов');
INSERT INTO CATEGORY VALUES (3, 'Хрестоматия');
INSERT INTO CATEGORY VALUES (4, 'Учебное пособие');
 
INSERT INTO MANUFACTURER VALUES (1, 'Яуза');
INSERT INTO MANUFACTURER VALUES (2, 'Т8 Издательские технологии');
INSERT INTO MANUFACTURER VALUES (3, 'Прогресс книга');
INSERT INTO MANUFACTURER VALUES (4, 'Время');
INSERT INTO MANUFACTURER VALUES (5, 'Лениздат');
INSERT INTO MANUFACTURER VALUES (6, 'Неолит');
INSERT INTO MANUFACTURER VALUES (7, 'Амрита-Русь');
INSERT INTO MANUFACTURER VALUES (8, 'Златоуст');
INSERT INTO MANUFACTURER VALUES (9, 'Аспект Пресс');
INSERT INTO MANUFACTURER VALUES (10, 'ВКН');
 
INSERT INTO SUPPLIER VALUES (1, 'Виктор Астафьев');
INSERT INTO SUPPLIER VALUES (2, 'Гилберт Кит Честертон');
INSERT INTO SUPPLIER VALUES (3, 'Кирилл Каланджи');
INSERT INTO SUPPLIER VALUES (4, 'Людмила Улицкая');
INSERT INTO SUPPLIER VALUES (5, 'Аркадий Гайдар');
INSERT INTO SUPPLIER VALUES (6, 'Юрий Родичев');
INSERT INTO SUPPLIER VALUES (7, 'Дэниел Джей Барретт');
INSERT INTO SUPPLIER VALUES (8, 'Шон Кэрролл');
INSERT INTO SUPPLIER VALUES (9, 'Яков Гордин');
INSERT INTO SUPPLIER VALUES (10, 'Иосиф Бродский');
INSERT INTO SUPPLIER VALUES (11, 'Янь Чуннянь');
INSERT INTO SUPPLIER VALUES (12, 'Дмитрий Мережковский');
INSERT INTO SUPPLIER VALUES (13, 'Дмитрий Щербаков');
INSERT INTO SUPPLIER VALUES (14, 'Роджер Осборн');
INSERT INTO SUPPLIER VALUES (15, 'Любовь Беликова');
INSERT INTO SUPPLIER VALUES (16, 'Сергей Моргачев');
INSERT INTO SUPPLIER VALUES (17, 'Екатерина Габарта');
INSERT INTO SUPPLIER VALUES (18, 'Татьяна Лопаткина');
 
INSERT INTO PICKUP_POINT VALUES (1, '125061, г. Лесной, ул. Подгорная, 8');
INSERT INTO PICKUP_POINT VALUES (2, '630370, г. Лесной, ул. Шоссейная, 24');
INSERT INTO PICKUP_POINT VALUES (3, '400562, г. Лесной, ул. Зеленая, 32');
INSERT INTO PICKUP_POINT VALUES (4, '614510, г. Лесной, ул. Маяковского, 47');
INSERT INTO PICKUP_POINT VALUES (5, '410542, г. Лесной, ул. Светлая, 46');
INSERT INTO PICKUP_POINT VALUES (6, '620839, г. Лесной, ул. Цветочная, 8');
INSERT INTO PICKUP_POINT VALUES (7, '443890, г. Лесной, ул. Коммунистическая, 1');
INSERT INTO PICKUP_POINT VALUES (8, '603379, г. Лесной, ул. Спортивная, 46');
INSERT INTO PICKUP_POINT VALUES (9, '603721, г. Лесной, ул. Гоголя, 41');
INSERT INTO PICKUP_POINT VALUES (10, '410172, г. Лесной, ул. Северная, 13');
INSERT INTO PICKUP_POINT VALUES (11, '614611, г. Лесной, ул. Молодежная, 50');
INSERT INTO PICKUP_POINT VALUES (12, '454311, г. Лесной, ул. Новая, 19');
INSERT INTO PICKUP_POINT VALUES (13, '660007, г. Лесной, ул. Октябрьская, 19');
INSERT INTO PICKUP_POINT VALUES (14, '603036, г. Лесной, ул. Садовая, 4');
INSERT INTO PICKUP_POINT VALUES (15, '394060, г. Лесной, ул. Фрунзе, 43');
INSERT INTO PICKUP_POINT VALUES (16, '410661, г. Лесной, ул. Школьная, 50');
INSERT INTO PICKUP_POINT VALUES (17, '625590, г. Лесной, ул. Коммунистическая, 20');
INSERT INTO PICKUP_POINT VALUES (18, '625683, г. Лесной, ул. 8 Марта');
INSERT INTO PICKUP_POINT VALUES (19, '450983, г. Лесной, ул. Комсомольская, 26');
INSERT INTO PICKUP_POINT VALUES (20, '394782, г. Лесной, ул. Чехова, 3');
INSERT INTO PICKUP_POINT VALUES (21, '603002, г. Лесной, ул. Дзержинского, 28');
INSERT INTO PICKUP_POINT VALUES (22, '450558, г. Лесной, ул. Набережная, 30');
INSERT INTO PICKUP_POINT VALUES (23, '344288, г. Лесной, ул. Чехова, 1');
INSERT INTO PICKUP_POINT VALUES (24, '614164, г. Лесной, ул. Степная, 30');
INSERT INTO PICKUP_POINT VALUES (25, '394242, г. Лесной, ул. Коммунистическая, 43');
INSERT INTO PICKUP_POINT VALUES (26, '660540, г. Лесной, ул. Солнечная, 25');
INSERT INTO PICKUP_POINT VALUES (27, '125837, г. Лесной, ул. Шоссейная, 40');
INSERT INTO PICKUP_POINT VALUES (28, '125703, г. Лесной, ул. Партизанская, 49');
INSERT INTO PICKUP_POINT VALUES (29, '625283, г. Лесной, ул. Победы, 46');
INSERT INTO PICKUP_POINT VALUES (30, '614753, г. Лесной, ул. Полевая, 35');
INSERT INTO PICKUP_POINT VALUES (31, '426030, г. Лесной, ул. Маяковского, 44');
INSERT INTO PICKUP_POINT VALUES (32, '450375, г. Лесной, ул. Клубная, 44');
INSERT INTO PICKUP_POINT VALUES (33, '625560, г. Лесной, ул. Некрасова, 12');
INSERT INTO PICKUP_POINT VALUES (34, '630201, г. Лесной, ул. Комсомольская, 17');
INSERT INTO PICKUP_POINT VALUES (35, '190949, г. Лесной, ул. Мичурина, 26');
 
INSERT INTO USERS VALUES (1, 1, 'Никифорова Анна Семеновна', '94d5ous@gmail.com', 'uzWC67');
INSERT INTO USERS VALUES (2, 1, 'Стелина Евгения Петровна', 'uth4iz@mail.com', '2L6KZG');
INSERT INTO USERS VALUES (3, 1, 'Михайлюк Анна Вячеславовна', '5d4zbu@tutanota.com', 'rwVDh9');
INSERT INTO USERS VALUES (4, 2, 'Ситдикова Елена Анатольевна', 'ptec8ym@yahoo.com', 'LdNyos');
INSERT INTO USERS VALUES (5, 2, 'Ворсин Петр Евгеньевич', '1qz4kw@mail.com', 'gynQMT');
INSERT INTO USERS VALUES (6, 2, 'Старикова Елена Павловна', '4np6se@mail.com', 'AtnDjr');
INSERT INTO USERS VALUES (7, 3, 'Никифорова Весения Николаевна', 'yzls62@outlook.com', 'JlFRCZ');
INSERT INTO USERS VALUES (8, 3, 'Сазонов Руслан Германович', '1diph5e@tutanota.com', '8ntwUp');
INSERT INTO USERS VALUES (9, 3, 'Одинцов Серафим Артёмович', 'tjde7c@yahoo.com', 'YOyhfR');
INSERT INTO USERS VALUES (10, 3, 'Степанов Михаил Артёмович', 'wpmrc3do@tutanota.com', 'RSbvHv');
 
INSERT INTO PRODUCT VALUES (1, 'А112Т4', 'Прокляты и убиты', 'шт.', 585, 1, 1, 1, 25, 6, NULL, 'import\1.jpg');
INSERT INTO PRODUCT VALUES (2, 'G843H5', 'Тайны и загадки отца Брауна', 'шт.', 193, 1, 1, 2, 30, 9, NULL, 'import\2.jpg');
INSERT INTO PRODUCT VALUES (3, 'D325D4', 'Девайс', 'шт.', 1599, 1, 2, 3, 5, 12, NULL, 'import\3.jpg');
INSERT INTO PRODUCT VALUES (4, 'S432T5', 'Необыкновенное обыкновенное чудо', 'шт.', 549, 1, 2, 4, 15, 15, NULL, 'import\4.jpg');
INSERT INTO PRODUCT VALUES (5, 'F325D4', 'Чук и Гек', 'шт.', 209, 1, 2, 5, 18, 3, NULL, 'import\5.jpg');
INSERT INTO PRODUCT VALUES (6, 'G432G6', 'Информационная безопасность', 'шт.', 3899, 2, 3, 6, 22, 3, NULL, 'import\6.jpg');
INSERT INTO PRODUCT VALUES (7, 'H542F5', 'Linux. Командная строка', 'шт.', 1799, 2, 3, 7, 4, 5, NULL, 'import\7.jpg');
INSERT INTO PRODUCT VALUES (8, 'C346F5', 'Квантовые миры и пространство-время', 'шт.', 1349, 2, 3, 8, 5, 4, NULL, 'import\8.jpg');
INSERT INTO PRODUCT VALUES (9, 'F256G6', 'Вселенная', 'шт.', 1799, 2, 3, 8, 6, 2, NULL, NULL);
INSERT INTO PRODUCT VALUES (10, 'J532V5', 'Пушкин. Бродский. Империя и судьба', 'шт.', 529, 3, 4, 9, 8, 6, NULL, 'import\10.jpg');
INSERT INTO PRODUCT VALUES (11, 'G643F4', 'Избранные эссе', 'шт.', 4925, 3, 5, 10, 2, 24, NULL, 'import\11.jpg');
INSERT INTO PRODUCT VALUES (12, 'J326V5', 'Императорская керамика', 'шт.', 2599, 3, 5, 11, 5, 4, NULL, 'import\12.jpg');
INSERT INTO PRODUCT VALUES (13, 'J632F6', 'Вечные спутники', 'шт.', 1599, 3, 5, 12, 0, 6, NULL, 'import\13.jpg');
INSERT INTO PRODUCT VALUES (14, 'G632H6', 'Репутация Чернышевского', 'шт.', 1349, 3, 6, 13, 2, 8, NULL, 'import\14.jpg');
INSERT INTO PRODUCT VALUES (15, 'M642E5', 'Теория искусства', 'шт.', 879, 3, 6, 14, 3, 2, NULL, 'import\15.jpg');
INSERT INTO PRODUCT VALUES (16, 'G543F5', 'Религиозные верования', 'шт.', 879, 3, 7, 13, 4, 6, NULL, 'import\16.jpg');
INSERT INTO PRODUCT VALUES (17, 'B653G6', 'Русский язык: Первые шаги', 'шт.', 2699, 4, 8, 15, 8, 9, NULL, 'import\17.jpg');
INSERT INTO PRODUCT VALUES (18, 'J735J7', 'Синтетический образ', 'шт.', 1099, 3, 8, 16, 9, 4, NULL, 'import\18.jpg');
INSERT INTO PRODUCT VALUES (19, 'H436H7', 'Английский язык в спорте', 'шт.', 1999, 4, 9, 17, 2, 0, NULL, 'import\19.jpg');
INSERT INTO PRODUCT VALUES (20, 'H475R5', 'Лексика и грамматика китайского', 'шт.', 608, 4, 10, 18, 25, 12, NULL, 'import\20.jpg');
 
INSERT INTO PRODUCT VALUES (21, 'P021', 'Доп. товар 21', 'шт.', 350, 1, 1, 1, 5, 7, NULL, 'import\picture.png');
INSERT INTO PRODUCT VALUES (22, 'P022', 'Доп. товар 22', 'шт.', 420, 1, 2, 2, 8, 4, NULL, 'import\picture.png');
INSERT INTO PRODUCT VALUES (23, 'P023', 'Доп. товар 23', 'шт.', 510, 2, 3, 3, 0, 11, NULL, 'import\picture.png');
INSERT INTO PRODUCT VALUES (24, 'P024', 'Доп. товар 24', 'шт.', 760, 2, 4, 4, 12, 9, NULL, 'import\picture.png');
INSERT INTO PRODUCT VALUES (25, 'P025', 'Доп. товар 25', 'шт.', 980, 3, 5, 5, 3, 5, NULL, 'import\picture.png');
INSERT INTO PRODUCT VALUES (26, 'P026', 'Доп. товар 26', 'шт.', 1120, 3, 6, 6, 2, 6, NULL, 'import\picture.png');
INSERT INTO PRODUCT VALUES (27, 'P027', 'Доп. товар 27', 'шт.', 1340, 4, 7, 7, 7, 10, NULL, 'import\picture.png');
INSERT INTO PRODUCT VALUES (28, 'P028', 'Доп. товар 28', 'шт.', 1560, 4, 8, 8, 4, 3, NULL, 'import\picture.png');
INSERT INTO PRODUCT VALUES (29, 'P029', 'Доп. товар 29', 'шт.', 620, 1, 9, 9, 6, 8, NULL, 'import\picture.png');
INSERT INTO PRODUCT VALUES (30, 'P030', 'Доп. товар 30', 'шт.', 710, 2, 10, 10, 9, 2, NULL, 'import\picture.png');
INSERT INTO PRODUCT VALUES (31, 'P031', 'Доп. товар 31', 'шт.', 840, 3, 1, 11, 11, 14, NULL, 'import\picture.png');
INSERT INTO PRODUCT VALUES (32, 'P032', 'Доп. товар 32', 'шт.', 930, 4, 2, 12, 1, 6, NULL, 'import\picture.png');
INSERT INTO PRODUCT VALUES (33, 'P033', 'Доп. товар 33', 'шт.', 1040, 1, 3, 13, 5, 12, NULL, 'import\picture.png');
INSERT INTO PRODUCT VALUES (34, 'P034', 'Доп. товар 34', 'шт.', 1180, 2, 4, 14, 0, 7, NULL, 'import\picture.png');
INSERT INTO PRODUCT VALUES (35, 'P035', 'Доп. товар 35', 'шт.', 1270, 3, 5, 15, 13, 9, NULL, 'import\picture.png');
INSERT INTO PRODUCT VALUES (36, 'P036', 'Доп. товар 36', 'шт.', 1390, 4, 6, 16, 15, 1, NULL, 'import\picture.png');
INSERT INTO PRODUCT VALUES (37, 'P037', 'Доп. товар 37', 'шт.', 1480, 1, 7, 17, 10, 4, NULL, 'import\picture.png');
INSERT INTO PRODUCT VALUES (38, 'P038', 'Доп. товар 38', 'шт.', 1590, 2, 8, 18, 14, 5, NULL, 'import\picture.png');
INSERT INTO PRODUCT VALUES (39, 'P039', 'Доп. товар 39', 'шт.', 1660, 3, 9, 1, 6, 3, NULL, 'import\picture.png');
INSERT INTO PRODUCT VALUES (40, 'P040', 'Доп. товар 40', 'шт.', 1780, 4, 10, 2, 2, 8, NULL, 'import\picture.png');
INSERT INTO PRODUCT VALUES (41, 'P041', 'Доп. товар 41', 'шт.', 1890, 1, 1, 3, 18, 6, NULL, 'import\picture.png');
INSERT INTO PRODUCT VALUES (42, 'P042', 'Доп. товар 42', 'шт.', 1990, 2, 2, 4, 20, 2, NULL, 'import\picture.png');
INSERT INTO PRODUCT VALUES (43, 'P043', 'Доп. товар 43', 'шт.', 2150, 3, 3, 5, 25, 0, NULL, 'import\picture.png');
 
INSERT INTO ORDERS VALUES (1, DATE '2024-02-27', DATE '2024-04-20', 1, 10, 901, 1);
INSERT INTO ORDERS VALUES (2, DATE '2023-09-28', DATE '2024-04-21', 11, 7, 902, 1);
INSERT INTO ORDERS VALUES (3, DATE '2024-03-21', DATE '2024-04-22', 2, 8, 903, 1);
INSERT INTO ORDERS VALUES (4, DATE '2024-02-20', DATE '2024-04-23', 11, 9, 904, 1);
INSERT INTO ORDERS VALUES (5, DATE '2024-03-17', DATE '2024-04-24', 2, 10, 905, 1);
INSERT INTO ORDERS VALUES (6, DATE '2024-03-01', DATE '2024-04-25', 15, 7, 906, 1);
INSERT INTO ORDERS VALUES (7, DATE '2024-02-29', DATE '2024-04-26', 3, 8, 907, 1);
INSERT INTO ORDERS VALUES (8, DATE '2024-03-31', DATE '2024-04-27', 19, 9, 908, 2);
INSERT INTO ORDERS VALUES (9, DATE '2024-04-02', DATE '2024-04-28', 5, 10, 909, 2);
INSERT INTO ORDERS VALUES (10, DATE '2024-04-03', DATE '2024-04-29', 19, 10, 910, 2);
 
INSERT INTO ORDER_ITEM VALUES (1, 1, 1, 2);
INSERT INTO ORDER_ITEM VALUES (2, 1, 2, 2);
INSERT INTO ORDER_ITEM VALUES (3, 2, 2, 1);
INSERT INTO ORDER_ITEM VALUES (4, 2, 1, 1);
INSERT INTO ORDER_ITEM VALUES (5, 3, 3, 10);
INSERT INTO ORDER_ITEM VALUES (6, 3, 4, 10);
INSERT INTO ORDER_ITEM VALUES (7, 4, 5, 5);
INSERT INTO ORDER_ITEM VALUES (8, 4, 3, 4);
INSERT INTO ORDER_ITEM VALUES (9, 5, 6, 20);
INSERT INTO ORDER_ITEM VALUES (10, 5, 7, 20);
INSERT INTO ORDER_ITEM VALUES (11, 6, 1, 2);
INSERT INTO ORDER_ITEM VALUES (12, 6, 2, 2);
INSERT INTO ORDER_ITEM VALUES (13, 7, 8, 3);
INSERT INTO ORDER_ITEM VALUES (14, 7, 9, 3);
INSERT INTO ORDER_ITEM VALUES (15, 8, 5, 1);
INSERT INTO ORDER_ITEM VALUES (16, 8, 6, 1);
INSERT INTO ORDER_ITEM VALUES (17, 9, 10, 5);
INSERT INTO ORDER_ITEM VALUES (18, 9, 9, 1);
INSERT INTO ORDER_ITEM VALUES (19, 10, 9, 5);
INSERT INTO ORDER_ITEM VALUES (20, 10, 10, 5);
 
SELECT COUNT(*) AS ROLE_CNT FROM ROLE;
SELECT COUNT(*) AS PRODUCT_CNT FROM PRODUCT;
SELECT COUNT(*) AS ORDERS_CNT FROM ORDERS;
SELECT COUNT(*) AS ORDER_ITEM_CNT FROM ORDER_ITEM;

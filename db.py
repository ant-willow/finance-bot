import sqlite3
from entries import ExpenseList, GroupList, CategoryList


LAST_LIMIT = 5


def _db_exists():
    """Проверяет сущесвование БД"""
    cursor.execute(
        """SELECT name FROM sqlite_master
        WHERE type = 'table'
        AND name = 'purchase'""")
    return cursor.fetchall()


def _read_categories():
    with open("categories.txt", "r", encoding="utf8") as fp:
        return [[line.rstrip('\n')] for line in fp.readlines()]


def _init_db():
    """Создает и заполняет таблицы начальными данными"""
    cursor.execute(
        """CREATE TABLE category(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT);""")
    cursor.execute(
        """CREATE TABLE purchase(
            id INTEGER PRIMARY KEY,
            date TEXT,
            category_id INTEGER,
            user_id INTEGER,
            amount INTEGER NOT NULL);""")
    categories = _read_categories()
    print(categories)
    cursor.executemany(
        'INSERT INTO category VALUES(Null, ?);', categories)
    conn.commit()


def _get_category_id(category: str):
    """Возвращает id категории."""
    cursor.execute('SELECT id FROM category WHERE name = ?', (category,))
    found = cursor.fetchone()
    return found[0] if found else None


def select_today(user_id):
    """Возвращает группу по категориям за сегодня."""
    cursor.execute(
        """SELECT 'всего', SUM(amount) FROM purchase
        WHERE date = date('now')
        UNION
        SELECT category.name, SUM(amount)
        FROM purchase, category
        WHERE category.id = purchase.category_id
        AND date = date('now')
        AND user_id = ?
        GROUP BY category.name;""", (user_id,))
    return GroupList(cursor.fetchall())


def select_month(user_id):
    """Возвращает группу по категориям за месяц."""
    cursor.execute(
        """SELECT 'всего', SUM(amount) FROM purchase
        WHERE strftime('%m', date) = strftime('%m', 'now')
        UNION
        SELECT category.name, SUM(amount)
        FROM purchase, category
        WHERE category.id = purchase.category_id
        AND strftime('%m', date) = strftime('%m', 'now')
        AND user_id = ?
        GROUP BY category.name;""", (user_id,))
    return GroupList(cursor.fetchall())


def select_last(user_id):
    """Возвращает последние записи."""
    cursor.execute(
        """SELECT purchase.id, category.name, amount, strftime('%d.%m', date)
        FROM purchase, category
        WHERE category.id = purchase.category_id
        AND user_id = ?
        ORDER BY purchase.id DESC
        LIMIT ?""", (user_id, LAST_LIMIT))
    return ExpenseList(cursor.fetchall())


def select_categories():
    """Возвращает список категорий."""
    cursor.execute('SELECT name FROM category')
    return CategoryList(cursor.fetchall())


def insert_entry(user_id: int, amount: int, category: str):
    """Добавляет новую запись."""
    category_id = _get_category_id(category)
    cursor.execute(
        'INSERT INTO purchase VALUES(Null, (SELECT date("now")), ?, ?, ?);',
        (category_id, user_id, amount))
    conn.commit()


def delete_entry(id: int):
    """Удаляет запись."""
    cursor.execute('DELETE from purchase where id = ?;', (id,))
    conn.commit()


conn = sqlite3.connect('bot.db', check_same_thread=False)
cursor = conn.cursor()
if not _db_exists():
    _init_db()

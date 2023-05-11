import sqlite3


class DBEditor:
    def __init__(self, path):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)')
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS groups ('
            'id INTEGER PRIMARY KEY AUTOINCREMENT, '
            'type TEXT, '
            'url TEXT, '
            'last_post TEXT'
            ')'
        )
        self.conn.commit()

    def cancel_group(self, user_id, group_id):
        self.cursor.execute(f'DELETE FROM user{user_id} WHERE group_id = {group_id}')
        self.cursor.execute(f'DELETE FROM group{group_id} WHERE user_id = {user_id}')
        self.conn.commit()

    def add_user(self, user_id):
        self.cursor.execute(f'INSERT INTO users (id) VALUES ({user_id})')
        self.cursor.execute(f'CREATE TABLE IF NOT EXISTS user{user_id} (group_id INTEGER PRIMARY KEY, name TEXT)')
        self.conn.commit()

    def get_user_group(self, group_id, user_id):
        group = self.cursor.execute(f'SELECT name FROM user{user_id} WHERE group_id = {group_id}').fetchall()
        res = self.cursor.execute(f'SELECT type, url FROM groups WHERE id = {group_id}').fetchall()
        return group[0][0], res[0][0], res[0][1]

    def get_user_groups(self, user_id):
        groups = self.cursor.execute(f'SELECT group_id, name FROM user{user_id}').fetchall()
        res = []
        for group in groups:
            gr = self.cursor.execute(f'SELECT type, url FROM groups WHERE id = {group[0]}').fetchall()
            res.append((group[1], gr[0][0], gr[0][1], group[0]))
        return res

    def add_group(self, name, group_type, url, user_id):
        group = self.cursor.execute(
            f'SELECT id FROM groups WHERE url = "{url}"'
        ).fetchall()
        if len(group) == 0:
            self.cursor.execute(
                f'INSERT INTO groups ('
                f'type, url, last_post'
                f') VALUES ("{group_type}", "{url}", "-1")'
            )
            lastrowid = self.cursor.lastrowid
            self.cursor.execute(
                f'CREATE TABLE group{lastrowid} (user_id INTEGER PRIMARY KEY)'
            )
        else:
            lastrowid = group[0][0]
        self.cursor.execute(
            f'INSERT INTO user{user_id} (group_id, name) VALUES ({lastrowid}, "{name}")'
        )
        self.cursor.execute(
            f'INSERT INTO group{lastrowid} (user_id) VALUES ({user_id})'
        )
        self.conn.commit()

    def get_groups(self, group_type):
        groups = self.cursor.execute(f'SELECT id, url, last_post FROM groups WHERE type = "{group_type}"').fetchall()
        for i in range(len(groups)):
            recipients = self.cursor.execute(f'SELECT user_id FROM group{groups[i][0]}').fetchall()
            groups[i] = (groups[i][1], groups[i][2], [r[0] for r in recipients], groups[i][0])
        return groups

    def get_group_users(self, username):
        group = self.cursor.execute(f'SELECT id FROM groups WHERE url LIKE "%{username}%"').fetchall()
        if len(group) != 0:
            return self.cursor.execute(f'SELECT user_id FROM group{group[0][0]}').fetchall()


    def update_group_last_post(self, group_id, post_id):
        print(f'UPDATE groups SET last_post = "{post_id}" WHERE url = {group_id}')
        self.cursor.execute(f'UPDATE groups SET last_post = "{post_id}" WHERE id = {group_id}')
        self.conn.commit()
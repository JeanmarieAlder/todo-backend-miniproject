from uuid import uuid4

import aiosqlite

from app.models import DB_PATH, IP, PORT, create_uuid
from app.models.todo import Todo


class Tag:
    @classmethod
    async def get_all(cls):
        db = await aiosqlite.connect(DB_PATH)
        cursor = await db.execute('SELECT * FROM Tag')
        rows = await cursor.fetchall()
        col_names = [description[0] for description in cursor.description]  # Get column names
        await cursor.close()
        await db.close()

        result = []
        for row in rows:
            row_dict = {}
            for i, col_name in enumerate(col_names):
                row_dict[col_name] = row[i]
            result.append(row_dict)

        return result
    

    @classmethod
    async def get_one(cls, id):
        db = None
        cursor = None
        try:
            db = await aiosqlite.connect(DB_PATH)
            cursor = await db.execute(f'SELECT * FROM Tag WHERE id = "{id}"')
            tag = await cursor.fetchone()
            col_names = [description[0] for description in cursor.description]  # Get column names
            await cursor.close()
            await db.close()

            row_dict = {}
            for i, col_name in enumerate(col_names):
                row_dict[col_name] = tag[i]

            row_dict['todos'] = await cls.get_todos(id)
            return row_dict
        except Exception as e:
            # print(e.with_traceback())
            return {}
    

    @classmethod
    async def create(cls, data):
        new_id = create_uuid()
        data['url'] = f"http://{IP}:{PORT}/tags/{new_id}"

        db = await aiosqlite.connect(DB_PATH)
        cursor = await db.execute(f"""INSERT INTO Tag (id, title, url) 
                            VALUES ('{new_id}', '{data['title']}', '{data['url']}');""")
        await db.commit()
        await cursor.close()
        await db.close()
        return data['url']
    

    @classmethod
    async def update(cls, id, data):
        db = await aiosqlite.connect(DB_PATH)
        # Check if the specified tag exists in the database
        cursor = await db.execute(f'SELECT * FROM Tag WHERE id = "{id}"')
        existing_tag = await cursor.fetchone()

        if not existing_tag:
            await db.close()
            return {'error': 'Tag not found'}
        
        title = data['title'] if 'title' in data else existing_tag[1]

        await db.execute(f"""UPDATE Tag SET title = "{title}" 
                        WHERE id = '{id}'""")
        await db.commit()
        await db.close()

        return await cls.get_one(id)
    

    @classmethod
    async def delete_one(cls, id):
        db = await aiosqlite.connect(DB_PATH)
        await db.execute("PRAGMA foreign_keys = ON;") # Deals with cascade del
        cursor = await db.execute(f'DELETE FROM Tag WHERE id = "{id}";')
        await db.commit()
        await cursor.close()
        await db.close()
        return
    

    @classmethod
    async def delete_all(cls):
        db = await aiosqlite.connect(DB_PATH)
        await db.execute("PRAGMA foreign_keys = ON;") # Deals with cascade del
        cursor = await db.execute('DELETE FROM Tag;')
        await db.commit()
        await cursor.close()
        await db.close()
        return 
    

    @classmethod
    async def get_todos(cls, tag_id):
        db = await aiosqlite.connect(DB_PATH)
        cursor = await db.execute(f"""SELECT tt.todo_id as id, t.title as title, 
                                    t.completed as completed, t.url as url,
                                    "t.order" as "order"
                                    FROM Todo_Tag AS tt
                                    INNER JOIN Todo AS t ON tt.todo_id = t.id
                                    WHERE tt.tag_id = '{tag_id}'""")
        rows = await cursor.fetchall()
        col_names = [description[0] for description in cursor.description]  # Get column names
        await cursor.close()
        await db.close()

        result = []
        for row in rows:
            row_dict = {}
            for i, col_name in enumerate(col_names):
                row_dict[col_name] = row[i]
            result.append(row_dict)

        return result
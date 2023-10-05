
import aiosqlite

from app.models import DB_PATH, IP, PORT, create_uuid


class Todo:
    @classmethod
    async def get_all(cls):
        db = await aiosqlite.connect(DB_PATH)
        cursor = await db.execute('SELECT * FROM Todo')
        rows = await cursor.fetchall()
        col_names = [description[0] for description in cursor.description]  # Get column names
        await cursor.close()
        await db.close()

        result = []
        for row in rows:
            row_dict = {}
            for i, col_name in enumerate(col_names):
                row_dict[col_name] = row[i]
            
            row_dict['completed'] = bool(row_dict['completed'])
            result.append(row_dict)

        return result
    

    @classmethod
    async def get_one(cls, id):
        db = None
        cursor = None
        try:
            db = await aiosqlite.connect(DB_PATH)
            cursor = await db.execute(f'SELECT * FROM Todo WHERE id = "{id}"')
            todo = await cursor.fetchone()
            col_names = [description[0] for description in cursor.description]  # Get column names
            await cursor.close()
            await db.close()

            row_dict = {}
            for i, col_name in enumerate(col_names):
                row_dict[col_name] = todo[i]

            # Get tags of todos
            row_dict['tags'] = await cls.get_tags_of_todo(id)
            row_dict['completed'] = bool(row_dict['completed'])

            return row_dict
        except Exception as e:
            # print(e.with_traceback())
            return {}
    

    @classmethod
    async def get_tags_of_todo(cls, todo_id):
        db = await aiosqlite.connect(DB_PATH)
        cursor = await db.execute(f"""SELECT tt.tag_id as id, t.title as title, t.url as url
                                    FROM Todo_Tag AS tt
                                    INNER JOIN Tag AS t ON tt.tag_id = t.id
                                    WHERE tt.todo_id = '{todo_id}'""")
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
    async def create(cls, data):
        new_id = create_uuid()
        data['completed'] = bool(data.get('completed', False))
        data['order'] = int(data.get('order', 0))
        data['url'] = f"http://{IP}:{PORT}/todos/{new_id}"

        db = await aiosqlite.connect(DB_PATH)
        cursor = await db.execute(f"""INSERT INTO Todo (id, title, completed, "order", url) 
                            VALUES ('{new_id}', '{data['title']}', {data['completed']}, 
                                    {data['order']}, '{data['url']}');""")
        await db.commit()
        await cursor.close()
        await db.close()
        return data['url']
    

    @classmethod
    async def update(cls, id, data):
        db = await aiosqlite.connect(DB_PATH)
        # Check if the specified todo exists in the database
        cursor = await db.execute(f'SELECT * FROM Todo WHERE id = "{id}"')
        existing_todo = await cursor.fetchone()

        if not existing_todo:
            await db.close()
            return {'error': 'Todo not found'}
        
        title = data['title'] if 'title' in data else existing_todo[1]
        completed = data['completed'] if 'completed' in data else existing_todo[2]
        order = data['order'] if 'order' in data else existing_todo[4]

        await db.execute(f"""UPDATE Todo SET title = "{title}", 
                       completed = {completed}, "order" = {order} 
                       WHERE id = '{id}'""")
        await db.commit()
        await db.close()

        return await cls.get_one(id)


    @classmethod
    async def delete_all(cls):
        db = await aiosqlite.connect(DB_PATH)
        await db.execute("PRAGMA foreign_keys = ON;") # Deals with cascade del
        cursor = await db.execute('DELETE FROM Todo;')
        await db.commit()
        await cursor.close()
        await db.close()
        return 
    

    @classmethod
    async def delete_one(cls, id):
        db = await aiosqlite.connect(DB_PATH)
        await db.execute("PRAGMA foreign_keys = ON;") # Deals with cascade del
        cursor = await db.execute(f'DELETE FROM Todo WHERE id = "{id}";')
        await db.commit()
        await cursor.close()
        await db.close()
        return
        

    @classmethod
    async def add_tag(cls, id_todo, id_tag):
        db = None
        try:
            db = await aiosqlite.connect(DB_PATH)
            cursor = await db.execute(f'insert into Todo_Tag (todo_id, tag_id) VALUES ("{id_todo}", "{id_tag}")')
            await db.commit()
            await cursor.close()
            await db.close()
            return await cls.get_one(id_todo)
        except Exception as e:
            # print(e.with_traceback())
            await db.colose
            return {'error': 'Todo or Tag missing.'}
        

    @classmethod
    async def delete_tags(cls, id_todo):
        db = await aiosqlite.connect(DB_PATH)
        await db.execute("PRAGMA foreign_keys = ON;") # Deals with cascade del
        cursor = await db.execute(f'DELETE FROM Todo_Tag WHERE todo_id = "{id_todo}";')
        await db.commit()
        await cursor.close()
        await db.close()
        try:
            return await cls.get_one(id_todo)
        except Exception as e:
            # print(e.with_traceback())
            return {'error': 'Todo not found.'}
        

    @classmethod
    async def delete_one_tag(cls, id_todo, id_tag):
        try:
            db = await aiosqlite.connect(DB_PATH)
            await db.execute("PRAGMA foreign_keys = ON;") # Deals with cascade del
            cursor = await db.execute(f'DELETE FROM Todo_Tag WHERE todo_id = "{id_todo}" AND tag_id = "{id_tag}";')
            await db.commit()
            await cursor.close()
            await db.close()
        
            return await cls.get_one(id_todo)
        except Exception as e:
            # print(e.with_traceback())
            return {'error': 'Todo or Tag not found.'}
    
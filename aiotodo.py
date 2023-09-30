import logging
from aiohttp import web
import aiohttp_cors
import time

TODOS = {
    0: {'title': 'build an API', 'order': 1, 'completed': False},
    1: {'title': '?????', 'order': 2, 'completed': False},
    2: {'title': 'profit!', 'order': 3, 'completed': False}
}

TAGS = {
    0: {'title': 'Dev'},
    1: {'title': 'Design'},
    2: {'title': 'PM'}
}

TODOS_TAGS = {
    0: {'todo': 0, 'tag': 0},
    1: {'todo': 0, 'tag': 2},
    2: {'todo': 1, 'tag': 1},
    3: {'todo': 1, 'tag': 2}
}

def get_all_todos(request):
    return web.json_response([
        {'id': key, **todo} for key, todo in TODOS.items()
    ])

def remove_all_todos(request):
    TODOS.clear()
    TODOS_TAGS.clear() # No more relations as well
    return web.Response(status=204)

def get_one_todo(request):
    id = int(request.match_info['id'])

    if id not in TODOS:
        return web.json_response({'error': 'Todo not found'}, status=404)

    # Filter todo_tags ID with corresponding todo ID
    todo_tags_id = [todo_tag['tag'] for todo_tag in TODOS_TAGS.values() if todo_tag['todo'] == id]

    tags_result = [{'id': key, **tag} for key, tag in TAGS.items() if key in todo_tags_id]

    return web.json_response({'id': id, **TODOS[id], 'tags': tags_result})

async def create_todo(request):
    data = await request.json()

    if 'title' not in data:
        return web.json_response({'error': '"title" is a required field'})
    title = data['title']
    if not isinstance(title, str) or not len(title):
        return web.json_response({'error': '"title" must be a string with at least one character'})

    data['completed'] = bool(data.get('completed', False))
    data['order'] = int(data.get('order', 0))
    new_id = max(TODOS.keys(), default=0) + 1
    data['url'] = str(request.url.join(request.app.router['one_todo'].url_for(id=str(new_id))))

    TODOS[new_id] = data

    return web.Response(
        headers={'Location': data['url']},
        status=303
    )

async def update_todo(request):
    id = int(request.match_info['id'])

    if id not in TODOS:
        return web.json_response({'error': 'Todo not found'}, status=404)

    data = await request.json()
    TODOS[id].update(data)

    return web.json_response(TODOS[id])

def remove_todo(request):
    id = int(request.match_info['id'])

    if id not in TODOS:
        return web.json_response({'error': 'Todo not found'})
    
    # Filter todo_tags ID with corresponding todo ID
    todo_tags_id = [key for key, todo_tag in TODOS_TAGS.items() if todo_tag['todo'] == id]

    # Delete TODOS_TAGS with corresponding ids
    for todo_tag_id in todo_tags_id:
        TODOS_TAGS.pop(todo_tag_id)

    del TODOS[id]

    return web.Response(status=204)

def get_tags_of_todo(request):
    id = int(request.match_info['id'])

    if id not in TODOS:
        return web.json_response({'error': 'Todo not found'})
    
    # Filter todo_tags ID with corresponding todo ID
    todo_tags_id = [todo_tag['tag'] for todo_tag in TODOS_TAGS.values() if todo_tag['todo'] == id]

    tags_result = [{'id': key, **tag} for key, tag in TAGS.items() if key in todo_tags_id]
    return web.json_response(tags_result)

async def add_tag_to_todo(request):
    id_todo = int(request.match_info['id'])

    if id_todo not in TODOS:
        return web.json_response({'error': 'Todo not found'})
    
    data = await request.json()
    if 'id' not in data:
        return web.json_response({'error': '"id" of the tag is a required field'})
    
    id_tag = int(data['id'])
    if id_tag not in TAGS:
        return web.json_response({'error': 'Tag not found'})
    
    new_id = max(TODOS_TAGS.keys(), default=0) + 1
    TODOS_TAGS[new_id] = {'todo': id_todo, 'tag': id_tag}
    todo_url = TODOS[id_todo].get('url')

    return web.Response(
        headers={'Location': todo_url},
        status=303
    )

def delete_tags_of_todo(request):
    id_todo = int(request.match_info['id'])

    if id_todo not in TODOS:
        return web.json_response({'error': 'Todo not found'})
    
    # Filter todo_tags ID with corresponding todo ID
    todo_tags_id = [key for key, todo_tag in TODOS_TAGS.items() if todo_tag['todo'] == id_todo]

    # Delete TODOS_TAGS with corresponding ids
    for todo_tag_id in todo_tags_id:
        TODOS_TAGS.pop(todo_tag_id)

    todo_url = TODOS[id_todo].get('url', f'http://localhost:8080/todos/{id_todo}')

    return web.Response(
        headers={'Location': todo_url},
        status=303
    )

def delete_one_tag_of_todo(request):
    id_todo = int(request.match_info['id'])
    id_tag = int(request.match_info['tag_id'])

    if id_todo not in TODOS:
        return web.json_response({'error': 'Todo not found'})
    
    if id_tag not in TAGS:
        return web.json_response({'error': 'Tag not found'})
    
    id_todo_tag = []
    # find todo_tag id 
    for key, value in TODOS_TAGS.items():
        if value['todo'] == id_todo and value['tag'] == id_tag:
            id_todo_tag.append(key)
            print(key)

    print(TODOS_TAGS)
    if not id_todo_tag :
        return web.json_response({'error': 'Tag and Todo relation not found'})

    # Delete TODOS_TAG with corresponding id
    for curr_id in id_todo_tag:
        TODOS_TAGS.pop(curr_id)
    print(TODOS_TAGS)
    todo_url = TODOS[id_todo].get('url', f'http://localhost:8080/todos/{id_todo}')
    return web.Response(
        headers={'Location': todo_url},
        status=303
    )


# TAGS part

def get_all_tags(request):
    return web.json_response([
        {'id': key, **tag} for key, tag in TAGS.items()
    ])

async def create_tag(request):
    data = await request.json()

    if 'title' not in data:
        return web.json_response({'error': '"title" is a required field'})
    title = data['title']
    if not isinstance(title, str) or not len(title):
        return web.json_response({'error': '"title" must be a string with at least one character'})

    new_id = max(TAGS.keys(), default=0) + 1
    data['url'] = str(request.url.join(request.app.router['one_tag'].url_for(id=str(new_id))))

    TAGS[new_id] = data

    return web.Response(
        headers={'Location': data['url']},
        status=303
    )

def get_one_tag(request):
    id = int(request.match_info['id'])

    if id not in TAGS:
        return web.json_response({'error': 'Tag not found'}, status=404)
    
    # Filter todo_tags ID with corresponding to tag ID
    todo_tags_id = [todo_tag['todo'] for todo_tag in TODOS_TAGS.values() if todo_tag['tag'] == id]

    todos_result = [{'id': key, **todo} for key, todo in TODOS.items() if key in todo_tags_id]

    return web.json_response({'id': id, **TAGS[id], 'todos': todos_result})

def remove_tag(request):
    id = int(request.match_info['id'])

    if id not in TAGS:
        return web.json_response({'error': 'Tag not found'})

    del TAGS[id]

    return web.Response(status=204)

def remove_all_tags(request):
    TAGS.clear()
    return web.Response(status=204)

async def update_tag(request):
    id = int(request.match_info['id'])

    if id not in TAGS:
        return web.json_response({'error': 'Tag not found'}, status=404)

    data = await request.json()
    TAGS[id].update(data)

    return web.json_response(TAGS[id])


def get_todos_of_tags(request):
    id = int(request.match_info['id'])

    if id not in TAGS:
        return web.json_response({'error': 'Tag not found'})
    
    # Filter todo_tags ID with corresponding to tag ID
    todo_tags_id = [todo_tag['todo'] for todo_tag in TODOS_TAGS.values() if todo_tag['tag'] == id]

    todos_result = [{'id': key, **todo} for key, todo in TODOS.items() if key in todo_tags_id]
    return web.json_response(todos_result)


#APP setup part

app = web.Application()

# Configure default CORS settings.
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*",
        )
})

cors.add(app.router.add_get('/todos/', get_all_todos, name='all_todos'))
cors.add(app.router.add_delete('/todos/', remove_all_todos, name='remove_todos'))
cors.add(app.router.add_post('/todos/', create_todo, name='create_todo'))
cors.add(app.router.add_get('/todos/{id:\d+}', get_one_todo, name='one_todo'))
cors.add(app.router.add_patch('/todos/{id:\d+}', update_todo, name='update_todo'))
cors.add(app.router.add_delete('/todos/{id:\d+}', remove_todo, name='remove_todo'))

cors.add(app.router.add_get('/todos/{id:\d+}/tags/', get_tags_of_todo, name='tags_of_todo'))
cors.add(app.router.add_post('/todos/{id:\d+}/tags/', add_tag_to_todo, name='add_tag_to_todo'))
cors.add(app.router.add_delete('/todos/{id:\d+}/tags/', delete_tags_of_todo, name='delete_tags_of_todo'))
cors.add(app.router.add_delete('/todos/{id:\d+}/tags/{tag_id:\d+}', delete_one_tag_of_todo, name='delete_one_tag_of_todo'))

cors.add(app.router.add_get('/tags/', get_all_tags, name='all_tags'))
cors.add(app.router.add_post('/tags/', create_tag, name='create_tags'))
cors.add(app.router.add_get('/tags/{id:\d+}', get_one_tag, name='one_tag'))
cors.add(app.router.add_delete('/tags/{id:\d+}', remove_tag, name='remove_tag'))
cors.add(app.router.add_delete('/tags/', remove_all_tags, name='remove_tags'))
cors.add(app.router.add_patch('/tags/{id:\d+}', update_tag, name='update_tag'))
cors.add(app.router.add_get('/tags/{id:\d+}/todos/', get_todos_of_tags, name='get_todos_of_tags'))

logging.basicConfig(level=logging.DEBUG)
web.run_app(app, port=8080)


import logging
from os import getenv

import aiohttp_cors
from aiohttp import web
from aiohttp.web import Response

from app.models.tag import Tag
from app.models.todo import Todo

IP = getenv('TODO_IP', 'localhost')
PORT = getenv('TODO_PORT', '8080')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_app(loop):

    app = web.Application(loop=loop)

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
    cors.add(app.router.add_get('/todos/{id}', get_one_todo, name='one_todo'))
    cors.add(app.router.add_patch('/todos/{id}', update_todo, name='update_todo'))
    cors.add(app.router.add_delete('/todos/{id}', remove_todo, name='remove_todo'))

    cors.add(app.router.add_get('/todos/{id}/tags/', get_tags_of_todo, name='tags_of_todo'))
    cors.add(app.router.add_post('/todos/{id}/tags/', add_tag_to_todo, name='add_tag_to_todo'))
    cors.add(app.router.add_delete('/todos/{id}/tags/', delete_tags_of_todo, name='delete_tags_of_todo'))
    cors.add(app.router.add_delete('/todos/{id}/tags/{tag_id}', delete_one_tag_of_todo, name='delete_one_tag_of_todo'))

    cors.add(app.router.add_get('/tags/', get_all_tags, name='all_tags'))
    cors.add(app.router.add_post('/tags/', create_tag, name='create_tags'))
    cors.add(app.router.add_get('/tags/{id}', get_one_tag, name='one_tag'))
    cors.add(app.router.add_delete('/tags/{id}', remove_tag, name='remove_tag'))
    cors.add(app.router.add_delete('/tags/', remove_all_tags, name='remove_tags'))
    cors.add(app.router.add_patch('/tags/{id}', update_tag, name='update_tag'))
    cors.add(app.router.add_get('/tags/{id}/todos/', get_todos_of_tag, name='get_todos_of_tags'))

    logger.info("Starting server at %s:%s", IP, PORT)
    srv = await loop.create_server(app.make_handler(), IP, PORT)
    return srv

##################
# Todo part

async def get_all_todos(request):
    return web.json_response(await Todo.get_all())


async def remove_all_todos(request):
    await Todo.delete_all()
    return Response(status=200)


async def get_one_todo(request):
    id = str(request.match_info['id'])
    return web.json_response(await Todo.get_one(id))


async def create_todo(request):
    data = await request.json()

    if 'title' not in data:
        return web.json_response({'error': '"title" is a required field'})
    title = data['title']
    if not isinstance(title, str) or not len(title):
        return web.json_response({'error': '"title" must be a string with at least one character'})
    
    new_url = await Todo.create(data)

    return web.Response(
        headers={'Location': new_url},
        status=303
    )

async def update_todo(request):
    id = str(request.match_info['id'])
    data = await request.json()
    return web.json_response(await Todo.update(id, data))

async def remove_todo(request):
    id = str(request.match_info['id'])
    await Todo.delete_one(id)
    return web.Response(status=204)


async def get_tags_of_todo(request):
    id = str(request.match_info['id'])
    return web.json_response(await Todo.get_tags_of_todo(id))


async def add_tag_to_todo(request):
    id_todo = str(request.match_info['id']) #id of todo
    data = await request.json() # id of tag
    if 'id' not in data:
        return web.json_response({'error': 'No id supplied'})

    return web.json_response(await Todo.add_tag(id_todo, data['id']))


async def delete_tags_of_todo(request):
    id_todo = str(request.match_info['id'])
    return web.json_response(await Todo.delete_tags(id_todo))

async def delete_one_tag_of_todo(request):
    id_todo = str(request.match_info['id'])
    id_tag = str(request.match_info['tag_id'])
    return web.json_response(await Todo.delete_one_tag(id_todo, id_tag))


# TAGS part

async def get_all_tags(request):
    return web.json_response(await Tag.get_all())


async def create_tag(request):
    data = await request.json()

    if 'title' not in data:
        return web.json_response({'error': '"title" is a required field'})
    title = data['title']
    if not isinstance(title, str) or not len(title):
        return web.json_response({'error': '"title" must be a string with at least one character'})

    new_url = await Tag.create(data)

    return web.Response(
        headers={'Location': new_url},
        status=303
    )

async def get_one_tag(request):
    id = str(request.match_info['id'])
    return web.json_response(await Tag.get_one(id))

async def remove_tag(request):
    id = str(request.match_info['id'])
    await Tag.delete_one(id)
    return web.Response(status=204)

async def remove_all_tags(request):
    await Tag.delete_all()
    return Response(status=204)

async def update_tag(request):
    id = str(request.match_info['id'])
    data = await request.json()
    return web.json_response(await Tag.update(id, data))


async def get_todos_of_tag(request):
    id = str(request.match_info['id'])

    return web.json_response(await Tag.get_todos(id))


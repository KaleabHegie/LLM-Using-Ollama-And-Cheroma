import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user_id = None
        self.question= None
        self.response = None
    async def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.room_group_name = f'{self.user_id}'
        await (self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
    async def disconnect(self, close_code):
        pass
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def user(self, user_id):
         return await database_sync_to_async(User.objects.get)(id=user_id)
import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class PingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("POLACZONO")

    async def disconnect(self, close_code):
        print("KONIEC")

    async def receive(self, text_data=None, bytes_data=None):
        pass

from rest_framework.test import APITestCase
from channels.testing import HttpCommunicator, WebsocketCommunicator
from chat.consumers import ChatConsumer
from chat.models import ChatRoom



class MyTests(APITestCase):
    pass
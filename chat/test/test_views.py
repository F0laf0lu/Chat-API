from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from ..models import ChatRoom
# Create your tests here.

class ChatRoomViewSetTests(APITestCase):
    def setUp(self) -> None:
        self.admin = get_user_model().objects.create_superuser(username='adminuser', password='12345678')
        self.user1 = get_user_model().objects.create_user(username='testuser', password='testuser')
        self.user2 = get_user_model().objects.create_user(username='testuser2', password='testuser')
        self.chatroom = ChatRoom.objects.create(room_name='testroom', creator=self.user1)
        self.chatroom.members.add(self.user1)


    def test_correct_url(self):
        url = reverse('chatroom-list')
        self.assertEqual('/api/v1/chatroom/', url)

    def test_get_all_chat_rooms(self):
        '''Only authenticated users can access this endpoint'''
        url = reverse('chatroom-list')
        unauth_response = self.client.get(url)
        self.assertEqual(unauth_response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.user1)
        auth_response = self.client.get(url)
        self.assertEqual(auth_response.status_code, status.HTTP_200_OK)

    def test_retrieve_chat_room(self):
        url = reverse('chatroom-detail', kwargs={'room_id':self.chatroom.room_id})
        self.assertEqual(f'/api/v1/chatroom/{self.chatroom.room_id}/', url)
        self.client.force_authenticate(self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_chat_room(self):
        '''Only room creators can update room details'''
        url = reverse('chatroom-detail', kwargs={'room_id':self.chatroom.room_id})
        data = {
            'room_name': 'new room name'
        }
        self.client.force_authenticate(self.user2)
        no_perm_response = self.client.patch(url, data=data, format='json')
        self.assertEqual(no_perm_response.status_code, status.HTTP_403_FORBIDDEN)
        self.chatroom.refresh_from_db()
        self.assertEqual(self.chatroom.room_name, 'testroom')

        self.client.force_authenticate(self.user1)
        perm_response = self.client.patch(url, data=data, format='json')
        self.assertEqual(perm_response.status_code, status.HTTP_200_OK)
        self.chatroom.refresh_from_db()
        self.assertEqual(self.chatroom.room_name, 'new room name')

    def test_create_chatroom(self):
        url = reverse('chatroom-list')
        data = {
            'room_name':'new room',
            'description':'newly created room'
        }
        self.client.force_authenticate(self.user1)
        response = self.client.post(url, data, format='json')
        new_room = ChatRoom.objects.get(id=2)
        total_members =  new_room.members.count()
        self.assertEqual(new_room.room_name, 'new room')
        self.assertEqual(total_members, 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_users_to_chatroom(self):
        '''Only room creators can access his endpoint to add users'''
        url = reverse('chatroom-add-member', kwargs={'room_id':self.chatroom.room_id})
        self.assertEqual(url, f'/api/v1/chatroom/{self.chatroom.room_id}/add_member/')
        data1 = {
            'username':'testuser4'
        }

        # Adding a user that does not exist
        self.client.force_authenticate(self.user1)
        user_not_exist_response = self.client.post(url, data1, format='json')
        self.assertEqual(user_not_exist_response.status_code, status.HTTP_400_BAD_REQUEST)

        # Room creator making the request
        data2 = {
            'username':'testuser2'
        }
        self.client.force_authenticate(self.user1)
        perm_response = self.client.post(url, data2, format='json')
        self.assertEqual(perm_response.status_code, status.HTTP_201_CREATED)

        self.chatroom.refresh_from_db()
        self.assertEqual(self.chatroom.members.count(), 2)

    def test_list_all_members_in_chatroom(self):
        '''Admins and Chat room creators can access this view'''
        url = reverse('chatroom-get-members', kwargs={'room_id':self.chatroom.room_id})
        self.assertEqual(url, f'/api/v1/chatroom/{self.chatroom.room_id}/get_members/')
        self.client.force_authenticate(self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(self.user2)
        no_perm_response = self.client.get(url)
        self.assertEqual(no_perm_response.status_code, status.HTTP_403_FORBIDDEN)


    def test_get_chatroom_member(self):
        self.user3 = get_user_model().objects.create_user(username='testuser3', password='testuser')
        self.chatroom.members.add(self.user3)
        url = reverse('chatroom-member', 
                    kwargs={'room_id': str(self.chatroom.room_id), 
                            'user_id': self.user3.pk})
        expected_url = f'/api/v1/chatroom/{self.chatroom.room_id}/member/{self.user3.pk}/'
        self.assertEqual(url, expected_url)

        self.client.force_authenticate(self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_non_chatroom_member(self):
        url = reverse('chatroom-member', 
                    kwargs={'room_id': str(self.chatroom.room_id), 
                            'user_id': self.user2.pk})

        self.client.force_authenticate(self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_remove_chat_room_member(self):
        self.user3 = get_user_model().objects.create_user(username='testuser3', password='testuser')
        self.chatroom.members.add(self.user3)
        
        creator_url = reverse('chatroom-member', 
                    kwargs={'room_id': str(self.chatroom.room_id), 
                            'user_id': self.user1.pk})
        
        # Room creator can not be removed
        self.client.force_authenticate(self.user1)
        creator_response = self.client.delete(creator_url)
        self.assertEqual(creator_response.status_code, status.HTTP_400_BAD_REQUEST)

        url = reverse('chatroom-member', 
                    kwargs={'room_id': str(self.chatroom.room_id), 
                            'user_id': self.user3.pk})
        
        # Remove member from chat room
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.chatroom.refresh_from_db()
        self.assertEqual(self.chatroom.members.count(), 1)

    def test_members_can_chat(self):
        self.chatroom.members.add(self.user2)
        url = reverse('chatroom-chat', kwargs={'room_id': str(self.chatroom.room_id)})
        self.client.force_authenticate(self.user2)

        access_response = self.client.get(url)
        self.assertEqual(access_response.status_code, status.HTTP_200_OK)

        data = {
            'content':'Hello Room'
        }
        chat_response  = self.client.post(url, data, format='json')
        self.assertEqual(chat_response.status_code, status.HTTP_201_CREATED)

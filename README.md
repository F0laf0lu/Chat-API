# ChatApp API



The ChatApp API built with Django Rest Framework provides a set of RESTful endpoints to manage users, create rooms, join a room, send and receive messages. The API is designed to be simple to use and easy to integrate

## Getting Started
To run the API locally, follow these steps:

1.  Clone the repository: `git clonehttps://github.com/F0laf0lu/Chat-API.git`
2.  Create a virtual environment: `python -m venv venv`
3.  Activate the virtual environment: `source venv/bin/activate`
4.  Install dependencies: `pip install -r requirements.txt` 
5.  Set up the database: `python manage.py migrate`
6.  Start up a redis container in docker at port 6379
7.  Create a superuser account: `python manage.py createsuperuser`
8.  Start the development server: `python manage.py runserver`

Running Tests
---------------
Tests are organized into different files within the app's `tests` directory. Here's how to run them:

1. To run all the tests, use the following command:

    ```
    python manage.py test
    ```

2. To run a single test file, you can use the following command (replacing `<app_name>` and `<test_file>` with the appropriate values):

    ```
    python manage.py test <app_name>.tests.<test_file>
    ```

Functional Requirements Definition
--------------
- User Authentication
- Chat room creation
- Chat room joining
- Message Sending and receiving using websockets

Tech Stack
--------------

- Language: Python 3.9
- Framework: Django 4.0+
- Testing: Django Test Framework
- Test Coverage: 80%+
- Development Methodology: TDD (Test Driven Development)

Authentication
--------------

Authentication is required for most endpoints in the API. To authenticate, include an access token in the `Authorization` header of your request. The access token can be obtained by logging in to your account or registering a new account.

API Endpoints
-------------

The following endpoints are available in the API:

### Authentication Endpoints

-   `/api/v1/users/` (POST): to allow users to register for an account.
-   `/api/v1/auth/login/` (POST): to allow users to log in to their account.

### User Endpoints

-   `/api/v1/users/` (GET): to retrieve a list of all registered users. Available to admins only
-   `/api/v1/users/<user_id>/` (GET, PUT, PATCH, DELETE): to retrieve, update, partially update or delete a specific user's profile.
- `/api/v1/users/<user_id>/chatrooms` (GET) : to get all chatrooms a user belongs to 

### Chat room Endpoints
-   `/api/v1/chatroom/` (GET): to retrieve a list of all available chatrooms
-   `/api/v1/chatroom/` (POST): Create a new chatroom
-   `/api/v1/chatroom/<room_id>` (GET, PUT, PATCH, DELETE):  retrieve, update, partially update or delete a chatroom.
-   `/api/v1/chatroom/<room_id>/add_member` (POST): Add a new memeber to the chatroom. Only room creator can access this
- `/api/v1/chatroom/<room_id>/get_members` (GET): Get all chatroom members
- `/api/v1/chatroom/<room_id>/member/<user_id>/` (GET): retrieve a chat room member
- `/api/v1/chatroom/<room_id>/member/<user_id>/` (DELETE): remove a member from the chatroom
- `/api/v1/chatroom/<room_id>/chat/` (POST): Send chat messages to the room


Contributing
------------

Contributions to this project are welcome!
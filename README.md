# BlogCore

A modern, asynchronous blog platform built with FastAPI, featuring a responsive web interface and REST API.

## Features

- **RESTful API** with FastAPI
- **Modern UI** with responsive design
- **Asynchronous operations** for better performance
- **CRUD Operations** for users and posts
- **Data Validation** with Pydantic
- **In-memory Storage** with JSON file persistence
- **Auto-generated API Documentation** - Swagger UI
- **HTML Templates** for web interface

## Project Structure

```
BlogCore/
├── app.py                 # Main FastAPI application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── post.html
│   ├── create_post.html
│   ├── edit_post.html
│   └── error.html
└── data.json             # Data storage file
```

## Quick Start

### Prerequisites
- Python 3.8+
- FastAPI
- Uvicorn

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd BlogCore

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app:app --reload --port 8000
```

### Access Points
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## API Endpoints

### Users
- `POST /api/users/` - Create new user
- `GET /api/users/` - List all users
- `GET /api/users/{id}` - Get user by ID
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

### Posts
- `POST /api/posts/` - Create new post
- `GET /api/posts/` - List all posts
- `GET /api/posts/{id}` - Get post by ID
- `PUT /api/posts/{id}` - Update post
- `DELETE /api/posts/{id}` - Delete post
- `GET /api/users/{id}/posts` - Get user's posts

### Web Pages
- `GET /` - Homepage with all posts
- `GET /posts/{id}` - View specific post
- `GET /create` - Create new post page
- `GET /edit/{id}` - Edit post page

## Data Models

### User
```python
class User:
    id: int
    email: str
    login: str
    password: str
    createdAt: datetime
    updatedAt: datetime
```

### Post
```python
class Post:
    authorId: int
    title: str
    content: str
    createdAt: datetime
    updatedAt: datetime
```

## Technologies Used

- **Backend**: FastAPI, Python
- **Frontend**: HTML5, CSS3, Jinja2 Templates
- **Data Validation**: Pydantic
- **Server**: Uvicorn (ASGI)
- **Storage**: In-memory with JSON file persistence

## Development Features

This project implements all core requirements for the 11th grade assignment:

- ✅ REST API with CRUD operations for Users and Posts
- ✅ Asynchronous request handlers
- ✅ Input data validation
- ✅ Package structure with requirements.txt
- ✅ GitHub repository ready
- ✅ Web interface with HTML templates
- ✅ File-based JSON storage
- ✅ Comprehensive error handling

## Screenshots

### Web Interface
![Homepage](https://github.com/user-attachments/assets/a363f162-6bb8-4839-adf7-9dc2e9332e12)

### API Documentation
![API Docs](https://github.com/user-attachments/assets/78782852-a39b-4ba8-8d61-033f5781a8c3)

### Post Management
![Post Creation](https://github.com/user-attachments/assets/e3cb1ff4-2c3c-40da-b08c-96a7d465c3e9)

![Post Editing](https://github.com/user-attachments/assets/7a4e345e-c043-4549-828f-c7723c2fa1de)

### User Interface
![User Posts](https://github.com/user-attachments/assets/15b5c445-0f5a-4d0a-a6ac-04826bae5f16)

---



"""Blogcore Blog Platform - Main Application Module."""

import json
import os
from datetime import datetime
from typing import Any, Optional

import uvicorn
from fastapi import FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, field_validator


class UserModel:
    """User data model."""

    def __init__(self, user_id: int, email: str, username: str, password: str) -> None:
        self.id = user_id
        self.email = email
        self.username = username
        self.password = password
        self.created_at = datetime.now()
        self.updated_at = datetime.now()


class PostModel:
    """Post data model."""

    def __init__(self, post_id: int, user_id: int, title: str, content: str) -> None:
        self.id = post_id
        self.user_id = user_id
        self.title = title
        self.content = content
        self.created_at = datetime.now()
        self.updated_at = datetime.now()


class UserCreateSchema(BaseModel):
    """Schema for user creation."""

    email: str
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def check_username(cls, v: str) -> str:
        """Validate username constraints."""
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if " " in v:
            raise ValueError("Username cannot contain spaces")
        return v

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        """Validate password constraints."""
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        """Validate email format."""
        if "@" not in v:
            raise ValueError("Invalid email address")
        return v


class PostCreateSchema(BaseModel):
    """Schema for post creation."""

    title: str
    content: str

    @field_validator("title")
    @classmethod
    def check_title(cls, v: str) -> str:
        """Validate title is not empty."""
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @field_validator("content")
    @classmethod
    def check_content(cls, v: str) -> str:
        """Validate content length."""
        if len(v) < 10:
            raise ValueError("Post content must be at least 10 characters long")
        return v


class DataManager:
    """Manager for handling data persistence."""

    def __init__(self) -> None:
        self.users_data_file = "users_data.json"
        self.posts_data_file = "posts_data.json"
        self.users_table: dict[int, UserModel] = {}
        self.posts_table: dict[int, PostModel] = {}
        self.next_user_id = 1
        self.next_post_id = 1
        self.load_all_data()

    def save_users(self) -> None:
        """Save users data to JSON file."""
        data = {
            "users": [
                {
                    "id": u.id,
                    "email": u.email,
                    "username": u.username,
                    "password": u.password,
                    "created_at": u.created_at.isoformat(),
                    "updated_at": u.updated_at.isoformat(),
                }
                for u in self.users_table.values()
            ],
            "next_id": self.next_user_id,
        }
        with open(self.users_data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save_posts(self) -> None:
        """Save posts data to JSON file."""
        data = {
            "posts": [
                {
                    "id": p.id,
                    "user_id": p.user_id,
                    "title": p.title,
                    "content": p.content,
                    "created_at": p.created_at.isoformat(),
                    "updated_at": p.updated_at.isoformat(),
                }
                for p in self.posts_table.values()
            ],
            "next_id": self.next_post_id,
        }
        with open(self.posts_data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_all_data(self) -> None:
        """Load all data from JSON files."""
        if os.path.exists(self.users_data_file):
            try:
                with open(self.users_data_file, encoding="utf-8") as f:
                    content = f.read().strip()
                    if not content:
                        return

                    data = json.loads(content)
                    for user_data in data["users"]:
                        user = UserModel(
                            user_data["id"],
                            user_data["email"],
                            user_data["username"],
                            user_data["password"],
                        )
                        user.created_at = datetime.fromisoformat(user_data["created_at"])
                        user.updated_at = datetime.fromisoformat(user_data["updated_at"])
                        self.users_table[user.id] = user
                    self.next_user_id = data.get("next_id", 1)
            except json.JSONDecodeError as e:
                print(f"JSON error in users file: {e}")
            except (KeyError, OSError) as e:
                print(f"Error loading users: {e}")

        if os.path.exists(self.posts_data_file):
            try:
                with open(self.posts_data_file, encoding="utf-8") as f:
                    content = f.read().strip()
                    if not content:
                        return

                    data = json.loads(content)
                    for post_data in data["posts"]:
                        post = PostModel(
                            post_data["id"],
                            post_data["user_id"],
                            post_data["title"],
                            post_data["content"],
                        )
                        post.created_at = datetime.fromisoformat(post_data["created_at"])
                        post.updated_at = datetime.fromisoformat(post_data["updated_at"])
                        self.posts_table[post.id] = post
                    self.next_post_id = data.get("next_id", 1)
            except json.JSONDecodeError as e:
                print(f"JSON error in posts file: {e}")
            except (KeyError, OSError) as e:
                print(f"Error loading posts: {e}")

    def create_user(self, email: str, username: str, password: str) -> UserModel:
        """Create a new user."""
        for user in self.users_table.values():
            if user.email == email:
                raise ValueError("User with this email already exists")
            if user.username == username:
                raise ValueError("User with this username already exists")

        user = UserModel(self.next_user_id, email, username, password)
        self.users_table[user.id] = user
        self.next_user_id += 1
        self.save_users()
        return user

    def get_user(self, user_id: int) -> Optional[UserModel]:
        """Get user by ID."""
        return self.users_table.get(user_id)

    def get_all_users(self) -> list[UserModel]:
        """Get all users."""
        return list(self.users_table.values())

    def update_user(self, user_id: int, **kwargs: Any) -> Optional[UserModel]:
        """Update user data."""
        user = self.users_table.get(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key) and key not in ["id", "created_at"]:
                    setattr(user, key, value)
            user.updated_at = datetime.now()
            self.save_users()
        return user

    def delete_user(self, user_id: int) -> bool:
        """Delete user and their posts."""
        if user_id in self.users_table:
            user_posts = [pid for pid, p in self.posts_table.items() if p.user_id == user_id]
            for post_id in user_posts:
                del self.posts_table[post_id]

            del self.users_table[user_id]
            self.save_users()
            self.save_posts()
            return True
        return False

    def create_post(self, user_id: int, title: str, content: str) -> Optional[PostModel]:
        """Create a new post."""
        if user_id not in self.users_table:
            return None

        post = PostModel(self.next_post_id, user_id, title, content)
        self.posts_table[post.id] = post
        self.next_post_id += 1
        self.save_posts()
        return post

    def get_post(self, post_id: int) -> Optional[PostModel]:
        """Get post by ID."""
        return self.posts_table.get(post_id)

    def get_all_posts(self) -> list[PostModel]:
        """Get all posts."""
        return list(self.posts_table.values())

    def get_user_posts(self, user_id: int) -> list[PostModel]:
        """Get user's posts."""
        return [p for p in self.posts_table.values() if p.user_id == user_id]

    def update_post(self, post_id: int, **kwargs: Any) -> Optional[PostModel]:
        """Update post."""
        post = self.posts_table.get(post_id)
        if post:
            for key, value in kwargs.items():
                if hasattr(post, key) and key not in ["id", "user_id", "created_at"]:
                    setattr(post, key, value)
            post.updated_at = datetime.now()
            self.save_posts()
        return post

    def delete_post(self, post_id: int) -> bool:
        """Delete post."""
        if post_id in self.posts_table:
            del self.posts_table[post_id]
            self.save_posts()
            return True
        return False


# Application setup
app = FastAPI(title="Blogcore Blog Platform", docs_url="/api")

# Create folders if they don't exist
os.makedirs("templates", exist_ok=True)
os.makedirs("assets/css", exist_ok=True)

# Setup static files and templates
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
templates = Jinja2Templates(directory="templates")

# Initialize data manager
data_manager = DataManager()


@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request) -> Any:
    """Home page with posts list."""
    posts = data_manager.get_all_posts()
    users = {u.id: u for u in data_manager.get_all_users()}
    return templates.TemplateResponse("main.html", {"request": request, "posts": posts, "users": users})


@app.get("/post/{post_id}", response_class=HTMLResponse)
async def view_post(request: Request, post_id: int) -> Any:
    """Post viewing page."""
    post = data_manager.get_post(post_id)
    if not post:
        return templates.TemplateResponse("error.html", {"request": request, "error": "Post not found"})

    author = data_manager.get_user(post.user_id)
    return templates.TemplateResponse("post.html", {"request": request, "post": post, "author": author})


@app.get("/create", response_class=HTMLResponse)
async def create_post_form(request: Request) -> Any:
    """Post creation form."""
    return templates.TemplateResponse("create.html", {"request": request})


@app.post("/create")
async def create_post_handler(
    request: Request,
    author_id: int = Form(...),
    title: str = Form(...),
    content: str = Form(...),
) -> Any:
    """Post creation handler."""
    try:
        post = data_manager.create_post(author_id, title, content)
        if not post:
            return templates.TemplateResponse(
                "create.html",
                {
                    "request": request,
                    "error": "User not found",
                    "author_id": author_id,
                    "title": title,
                    "content": content,
                },
            )
        return RedirectResponse(url="/?msg=Post+created+successfully", status_code=303)
    except Exception as e:
        return templates.TemplateResponse(
            "create.html",
            {
                "request": request,
                "error": str(e),
                "author_id": author_id,
                "title": title,
                "content": content,
            },
        )


@app.get("/edit/{post_id}", response_class=HTMLResponse)
async def edit_post_form(request: Request, post_id: int) -> Any:
    """Post editing form."""
    post = data_manager.get_post(post_id)
    return templates.TemplateResponse("edit.html", {"request": request, "post": post})


@app.post("/edit/{post_id}")
async def edit_post_handler(
    request: Request,
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
) -> Any:
    """Edit post handler."""
    try:
        post = data_manager.update_post(post_id, title=title, content=content)
        if not post:
            return templates.TemplateResponse(
                "edit.html",
                {"request": request, "post": None, "error": "Post not found"},
            )
        return RedirectResponse(url=f"/post/{post_id}?msg=Changes+saved+successfully", status_code=303)
    except Exception as e:
        post = data_manager.get_post(post_id)
        return templates.TemplateResponse(
            "edit.html",
            {"request": request, "post": post, "error": str(e)},
        )


@app.post("/delete/{post_id}")
async def delete_post_handler(post_id: int) -> RedirectResponse:
    """Post deletion handler."""
    data_manager.delete_post(post_id)
    return RedirectResponse(url="/?msg=Post+deleted+successfully", status_code=303)


# API Endpoints - Users
@app.post("/api/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreateSchema) -> dict[str, Any]:
    """Create user."""
    try:
        user = data_manager.create_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
        )
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "created_at": user.created_at,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/api/users/")
async def get_users_list() -> list[dict[str, Any]]:
    """Get users list."""
    users = data_manager.get_all_users()
    return [
        {
            "id": u.id,
            "email": u.email,
            "username": u.username,
            "created_at": u.created_at,
        }
        for u in users
    ]


@app.get("/api/users/{user_id}")
async def get_user_detail(user_id: int) -> dict[str, Any]:
    """Get user."""
    user = data_manager.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


@app.put("/api/users/{user_id}")
async def update_user_data(user_id: int, user_data: UserCreateSchema) -> dict[str, Any]:
    """Update user."""
    user = data_manager.update_user(
        user_id,
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "updated_at": user.updated_at,
    }


@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int) -> dict[str, str]:
    """Delete user."""
    if not data_manager.delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


# API Endpoints - Posts
@app.post("/api/posts/")
async def create_post(post_data: PostCreateSchema, user_id: int) -> dict[str, Any]:
    """Create post."""
    post = data_manager.create_post(user_id, post_data.title, post_data.content)
    if not post:
        raise HTTPException(status_code=404, detail="Author not found")
    return {
        "id": post.id,
        "user_id": post.user_id,
        "title": post.title,
        "content": post.content,
        "created_at": post.created_at,
    }


@app.get("/api/posts/")
async def get_posts_list() -> list[dict[str, Any]]:
    """Get posts list."""
    posts = data_manager.get_all_posts()
    return [
        {
            "id": p.id,
            "user_id": p.user_id,
            "title": p.title,
            "content": p.content,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
        }
        for p in posts
    ]


@app.get("/api/posts/{post_id}")
async def get_post_detail(post_id: int) -> dict[str, Any]:
    """Get post."""
    post = data_manager.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {
        "id": post.id,
        "user_id": post.user_id,
        "title": post.title,
        "content": post.content,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
    }


@app.put("/api/posts/{post_id}")
async def update_post_data(post_id: int, post_data: PostCreateSchema) -> dict[str, Any]:
    """Update post."""
    post = data_manager.update_post(
        post_id,
        title=post_data.title,
        content=post_data.content,
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {
        "id": post.id,
        "user_id": post.user_id,
        "title": post.title,
        "content": post.content,
        "updated_at": post.updated_at,
    }


@app.delete("/api/posts/{post_id}")
async def delete_post(post_id: int) -> dict[str, str]:
    """Delete post."""
    if not data_manager.delete_post(post_id):
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted successfully"}


@app.get("/api/users/{user_id}/posts")
async def get_user_posts_list(user_id: int) -> list[dict[str, Any]]:
    """Get user's posts."""
    if not data_manager.get_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    posts = data_manager.get_user_posts(user_id)
    return [
        {
            "id": p.id,
            "title": p.title,
            "content": p.content,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
        }
        for p in posts
    ]


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "BlogCore API",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
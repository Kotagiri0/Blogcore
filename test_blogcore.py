import pytest
import json
import os
from fastapi.testclient import TestClient
from app import app, data_manager

client = TestClient(app)


class TestBlogCoreAPI:
    """Тесты для BlogCore API"""

    def setup_method(self):
        """Очистка данных перед каждым тестом"""
        # Очищаем данные в менеджере
        data_manager.users_table.clear()
        data_manager.posts_table.clear()
        data_manager.next_user_id = 1
        data_manager.next_post_id = 1

        # Очищаем файлы данных
        if os.path.exists('users_data.json'):
            os.remove('users_data.json')
        if os.path.exists('posts_data.json'):
            os.remove('posts_data.json')

    # Тесты для пользователей
    def test_create_user_success(self):
        """Успешное создание пользователя"""
        response = client.post(
            "/api/users/",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "password123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert "id" in data
        assert "created_at" in data

    def test_create_user_short_password(self):
        """Создание пользователя с коротким паролем"""
        response = client.post(
            "/api/users/",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "123"
            }
        )
        assert response.status_code == 422
        data = response.json()
        assert "Password must be at least 6 characters long" in str(data)

    def test_create_user_invalid_email(self):
        """Создание пользователя с невалидным email"""
        response = client.post(
            "/api/users/",
            json={
                "email": "invalid-email",
                "username": "testuser",
                "password": "password123"
            }
        )
        assert response.status_code == 422
        data = response.json()
        assert "Invalid email address" in str(data)

    def test_create_user_short_username(self):
        """Создание пользователя с коротким именем"""
        response = client.post(
            "/api/users/",
            json={
                "email": "test@example.com",
                "username": "ab",
                "password": "password123"
            }
        )
        assert response.status_code == 422
        data = response.json()
        assert "Username must be at least 3 characters long" in str(data)

    def test_create_user_duplicate_email(self):
        """Создание пользователя с существующим email"""
        # Первый пользователь
        client.post(
            "/api/users/",
            json={
                "email": "test@example.com",
                "username": "user1",
                "password": "password123"
            }
        )

        # Второй пользователь с тем же email
        response = client.post(
            "/api/users/",
            json={
                "email": "test@example.com",
                "username": "user2",
                "password": "password123"
            }
        )
        assert response.status_code == 400
        assert "User with this email already exists" in response.json()["detail"]

    def test_get_users_list(self):
        """Получение списка пользователей"""
        # Создаем двух пользователей
        client.post("/api/users/", json={
            "email": "user1@example.com",
            "username": "user1",
            "password": "password123"
        })
        client.post("/api/users/", json={
            "email": "user2@example.com",
            "username": "user2",
            "password": "password123"
        })

        response = client.get("/api/users/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["username"] == "user1"
        assert data[1]["username"] == "user2"

    def test_get_user_detail(self):
        """Получение информации о пользователе"""
        create_response = client.post("/api/users/", json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        })
        user_id = create_response.json()["id"]

        response = client.get(f"/api/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["username"] == "testuser"

    def test_get_nonexistent_user(self):
        """Получение несуществующего пользователя"""
        response = client.get("/api/users/999")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_update_user(self):
        """Обновление пользователя"""
        create_response = client.post("/api/users/", json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        })
        user_id = create_response.json()["id"]

        response = client.put(f"/api/users/{user_id}", json={
            "email": "updated@example.com",
            "username": "updateduser",
            "password": "newpassword123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "updateduser"
        assert data["email"] == "updated@example.com"

    def test_delete_user(self):
        """Удаление пользователя"""
        create_response = client.post("/api/users/", json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        })
        user_id = create_response.json()["id"]

        response = client.delete(f"/api/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "User deleted successfully"

        # Проверяем, что пользователь действительно удален
        get_response = client.get(f"/api/users/{user_id}")
        assert get_response.status_code == 404

    # Тесты для постов
    def test_create_post_success(self):
        """Успешное создание поста"""
        # Сначала создаем пользователя
        user_response = client.post("/api/users/", json={
            "email": "author@example.com",
            "username": "author",
            "password": "password123"
        })
        user_id = user_response.json()["id"]

        response = client.post(
            f"/api/posts/?user_id={user_id}",
            json={
                "title": "Test Post",
                "content": "This is a test post content with enough length"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Post"
        assert data["user_id"] == user_id
        assert "id" in data
        assert "created_at" in data

    def test_create_post_nonexistent_user(self):
        """Создание поста для несуществующего пользователя"""
        response = client.post(
            "/api/posts/?user_id=99999",
            json={
                "title": "Test Post",
                "content": "This is a test post content with enough length"
            }
        )
        assert response.status_code == 404
        assert "Author not found" in response.json()["detail"]

    def test_create_post_short_content(self):
        """Создание поста с коротким содержанием"""
        user_response = client.post("/api/users/", json={
            "email": "author@example.com",
            "username": "author",
            "password": "password123"
        })
        user_id = user_response.json()["id"]

        response = client.post(
            f"/api/posts/?user_id={user_id}",
            json={
                "title": "Test Post",
                "content": "Short"
            }
        )
        assert response.status_code == 422
        data = response.json()
        assert "Post content must be at least 10 characters long" in str(data)

    def test_create_post_empty_title(self):
        """Создание поста с пустым заголовком"""
        user_response = client.post("/api/users/", json={
            "email": "author@example.com",
            "username": "author",
            "password": "password123"
        })
        user_id = user_response.json()["id"]

        response = client.post(
            f"/api/posts/?user_id={user_id}",
            json={
                "title": "   ",
                "content": "This is a test post content with enough length"
            }
        )
        assert response.status_code == 422
        data = response.json()
        assert "Title cannot be empty" in str(data)

    def test_get_posts_list(self):
        """Получение списка постов"""
        user_response = client.post("/api/users/", json={
            "email": "author@example.com",
            "username": "author",
            "password": "password123"
        })
        user_id = user_response.json()["id"]

        # Создаем несколько постов
        client.post(f"/api/posts/?user_id={user_id}", json={
            "title": "Post 1",
            "content": "Content of post 1 with enough length"
        })
        client.post(f"/api/posts/?user_id={user_id}", json={
            "title": "Post 2",
            "content": "Content of post 2 with enough length"
        })

        response = client.get("/api/posts/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Post 1"
        assert data[1]["title"] == "Post 2"

    def test_get_user_posts(self):
        """Получение постов пользователя"""
        user_response = client.post("/api/users/", json={
            "email": "author@example.com",
            "username": "author",
            "password": "password123"
        })
        user_id = user_response.json()["id"]

        # Создаем посты для пользователя
        client.post(f"/api/posts/?user_id={user_id}", json={
            "title": "User Post 1",
            "content": "Content of user post 1 with enough length"
        })
        client.post(f"/api/posts/?user_id={user_id}", json={
            "title": "User Post 2",
            "content": "Content of user post 2 with enough length"
        })

        response = client.get(f"/api/users/{user_id}/posts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(post["title"].startswith("User Post") for post in data)

    def test_update_post(self):
        """Обновление поста"""
        user_response = client.post("/api/users/", json={
            "email": "author@example.com",
            "username": "author",
            "password": "password123"
        })
        user_id = user_response.json()["id"]

        post_response = client.post(f"/api/posts/?user_id={user_id}", json={
            "title": "Original Title",
            "content": "Original content with enough length"
        })
        post_id = post_response.json()["id"]

        response = client.put(f"/api/posts/{post_id}", json={
            "title": "Updated Title",
            "content": "Updated content with enough length"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["content"] == "Updated content with enough length"

    def test_delete_post(self):
        """Удаление поста"""
        user_response = client.post("/api/users/", json={
            "email": "author@example.com",
            "username": "author",
            "password": "password123"
        })
        user_id = user_response.json()["id"]

        post_response = client.post(f"/api/posts/?user_id={user_id}", json={
            "title": "Post to delete",
            "content": "Content to delete with enough length"
        })
        post_id = post_response.json()["id"]

        response = client.delete(f"/api/posts/{post_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Post deleted successfully"

        # Проверяем, что пост действительно удален
        get_response = client.get(f"/api/posts/{post_id}")
        assert get_response.status_code == 404

    # Тесты веб-интерфейса
    def test_main_page(self):
        """Тест главной страницы"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_health_check(self):
        """Тест health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "BlogCore" in data["service"]

    def test_api_documentation(self):
        """Тест доступности документации API"""
        response = client.get("/api")
        assert response.status_code == 200

    def test_post_pages(self):
        """Тест страниц постов"""
        # Создаем пользователя и пост для тестирования
        user_response = client.post("/api/users/", json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        })
        user_id = user_response.json()["id"]

        post_response = client.post(f"/api/posts/?user_id={user_id}", json={
            "title": "Test Post",
            "content": "Test content with enough length"
        })
        post_id = post_response.json()["id"]

        # Тестируем страницу поста
        response = client.get(f"/post/{post_id}")
        assert response.status_code == 200

        # Тестируем страницу создания поста
        response = client.get("/create")
        assert response.status_code == 200

        # Тестируем страницу редактирования поста
        response = client.get(f"/edit/{post_id}")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
# Content Hub API

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.15-red.svg)](https://www.django-rest-framework.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

Production-ready RESTful API для управления контентом, демонстрирующий практики enterprise-разработки.

## Технологический стек

**Backend**
- Django 5.0 + Django REST Framework 3.15
- PostgreSQL 15 (оптимизированные индексы, connection pooling)
- Redis 7 (кэширование с автоматической инвалидацией)
- Gunicorn + Nginx (production-ready конфигурация)

**Архитектура**
- Модульная структура приложений (apps/content, apps/users, core)
- Split settings (base/development/production)
- ViewSets с продвинутой фильтрацией и пагинацией
- JWT-аутентификация (SimpleJWT)
- Soft deletes, custom managers, query optimization

**DevOps**
- Docker multi-stage builds (оптимизация размера образов)
- Docker Compose (4 сервиса: db, redis, web, nginx)
- Makefile (40+ команд автоматизации)
- CI/CD ready (GitHub Actions)
- Health checks, logging, monitoring

**Качество кода**
- Black, Flake8, isort, Pylint, mypy
- Type hints, docstrings
- Pre-commit hooks ready

## Быстрый старт

```bash
git clone <repository-url>
cd blog_api_project
make setup
```

**Одна команда** выполняет:
- Создание `.env` из `.env.example`
- Сборку Docker-контейнеров
- Запуск всех сервисов
- Миграции БД
- Создание суперпользователя
- Сбор статических файлов

**Доступ к API:**
- API: http://localhost/api/v1/
- Swagger: http://localhost/api/docs/
- Admin: http://localhost/admin/
- Health: http://localhost/health/

## Ключевые возможности

**API Endpoints**
- `/api/v1/content/articles/` - Управление статьями (CRUD, поиск, фильтрация, статистика)
- `/api/v1/content/comments/` - Вложенные комментарии с threading
- `/api/v1/users/` - Регистрация, профили, JWT-токены
- `/api/v1/auth/token/` - Получение access/refresh токенов

**Технические особенности**
- Redis-кэширование с автоматической инвалидацией через signals
- Оптимизация запросов (`select_related`, `prefetch_related`)
- Полнотекстовый поиск по статьям
- Rate limiting (защита от abuse)
- Soft deletes (неразрушающее удаление)
- Auto-generated Swagger/ReDoc документация

## Команды разработки

```bash
# Docker
make build          # Сборка контейнеров
make up             # Запуск сервисов
make down           # Остановка сервисов
make logs           # Просмотр логов

# База данных
make migrate        # Применить миграции
make makemigrations # Создать миграции
make dbshell        # PostgreSQL консоль

# Разработка
make shell          # Django shell
make bash           # Bash в контейнере

# Качество кода
make lint           # Flake8 + Pylint
make format         # Black + isort
make type-check     # MyPy

# Утилиты
make clear-cache    # Очистить Redis
make backup-db      # Бэкап БД
make health         # Проверка health check
```

## Структура проекта

```
blog_api_project/
├── apps/
│   ├── content/          # Статьи и комментарии
│   │   ├── models.py     # Article, Comment (soft deletes, custom managers)
│   │   ├── serializers.py # List/Detail/Create serializers
│   │   ├── views.py      # ViewSets с custom actions
│   │   ├── filters.py    # DRF filters
│   │   └── signals.py    # Cache invalidation
│   └── users/            # Пользователи и аутентификация
├── config/
│   └── settings/         # Разделённые настройки
│       ├── base.py
│       ├── development.py
│       └── production.py
├── core/                 # Shared utilities
│   ├── models.py         # Abstract base models
│   ├── pagination.py     # Custom pagination
│   └── middleware.py     # Request logging
├── docker/
│   ├── nginx/            # Nginx конфигурация
│   └── entrypoint.sh     # Startup скрипт
├── Dockerfile            # Multi-stage build
├── docker-compose.yml    # Оркестрация сервисов
├── Makefile              # Команды автоматизации
└── requirements.txt      # Python зависимости
```

## Production deployment

```bash
# Настройка переменных окружения
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<your-secret-key>
ALLOWED_HOSTS=yourdomain.com

# Деплой
make prod-build
make prod-up
```

**Production features:**
- Gunicorn с 4 workers
- Nginx reverse proxy (gzip, static/media serving)
- PostgreSQL connection pooling
- Redis persistence (AOF)
- Secure headers, CORS настройка
- Environment-based configuration

## Технические детали

**Оптимизация производительности:**
- Redis кэширование (TTL 300s, 70%+ hit rate)
- Database indexes на часто запрашиваемых полях
- Query optimization (избегание N+1 проблем)
- Gzip compression статики

**Безопасность:**
- JWT токены (60 мин access, 24ч refresh)
- Rate limiting (100 req/hour по умолчанию)
- PBKDF2 хеширование паролей
- CORS whitelist
- SQL injection защита (Django ORM)
- XSS/CSRF protection

**API Design:**
- RESTful архитектура
- Версионирование (v1)
- Консистентные response форматы
- Pagination на всех list endpoints
- Filtering, searching, ordering
- Auto-generated OpenAPI schema

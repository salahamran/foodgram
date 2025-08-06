# Foodgram

Foodgram is a web application that allows users to publish, browse, favorite, and manage recipes. Users can subscribe to other authors, generate shopping lists, and more.

## Features

- User registration and authentication
- Recipe creation and editing
- Filtering recipes by tags
- Adding recipes to favorites
- Subscribing to authors
- Downloadable shopping list with combined ingredients
- Avatar upload and user profile management

## Tech Stack

- **Backend**: Django, Django REST Framework, PostgreSQL
- **Frontend**: React
- **Deployment**: Docker, Nginx, Gunicorn, GitHub Actions

## Installation

### Requirements

- Docker
- Docker Compose

## Clone the Repository

```bash
git clone https://github.com/<your-username>/foodgram.git
cd foodgram
```

## Create a .env file
Use the .env.example as a reference and create your own .env file in the root directory:

- Fill in environment variables such as:

```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your_db
POSTGRES_USER=yoyr_user
POSTGRES_PASSWORD=your_password
DB_HOST=your_host
DB_PORT=5432
SECRET_KEY=your_secret_key
DEBUG=True  
```

## Build and run containers
```bash
docker compose up --build
```

### Access the app

- Frontend: http://localhost/

- API: http://localhost/api/

- Admin panel: http://localhost/admin/


### Project Structure
```bash
├── backend/           # Django backend
├── frontend/          # Static frontend files
├── data/              # Static and media volumes
├── docs/              # API documentation
├── docker-compose.yml
├── .env
└── README.md
```

### Domain And credentials for testing 
```bash
- Domain https://canvastudio.ru/
- testing email: user@test.com
- password: usertest
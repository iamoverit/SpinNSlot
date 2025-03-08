# SpinNSlot

A seamless platform for booking time slots quickly and easily. Includes web backend, frontend, and tg bot.

## Description

SpinNSlot is a comprehensive platform that allows users to efficiently manage and book time slots. The system provides:

- Web-based interface for slot management
- Telegram bot integration for notifications
- Customer and tournament management capabilities
- Automated scheduling and notifications

## Key Features

- Time slot booking and management
- Tournament organization and participation
- Integration with third-party services (Telegram)
- User authentication and authorization
- Data validation and error handling
- Reporting and analytics

## Roadmap
 Please read our [src/README.md](src/README.md) for roadmap details.

## Technologies

- **Python** - Backend development
- **Django** - Web framework
- **sqlite** - Database
- **Nginx** - Reverse proxy server
- **Gunicorn** - WSGI HTTP server
- **Docker** - Containerization
- **Poetry** - Dependency management

## Installation & Setup

### Prerequisites

- Docker installed on your system
- Python 3.8+
- sqlite database

### Steps

1. Clone the repository:

```sh
git clone https://github.com/iamoverit/SpinNSlot.git
cd SpinNSlot
```

 2. Install dependencies using Poetry:

```sh
poetry install
```

 3. Configure your environment variables by copying `.env.example` and adding your values.

 4. Build Docker containers:

```sh
docker-compose build
```

 5. Start the application stack:

```sh
docker-compose up -d
```

 ## Configuration

 ### Environment Variables

 Create a `.env` file in the project root using the example provided by `.env.example`. Update it with your actual
 values.



 Example `.env` configuration:

```
DEBUG = 1
DJANGO_SECRET_KEY = 'your-secret-key'
TELEGRAM_BOT_NAME = 'botname'
TELEGRAM_BOT_TOKEN = 'secret'
TELEGRAM_LOGIN_REDIRECT_URL = 'http://127.0.0.1'
BASE_HOST = 'http://127.0.0.1'
VIRTUAL_HOST = 'http://127.0.0.1'
LETSENCRYPT_HOST = 'http://127.0.0.1'
```

 ## Using the System
 ### Web Interface
 Access the web interface at: http://localhost:8000
 ### Telegram Bot
 The system includes a Telegram bot for notifications. Configure it by setting up the environment variables as shown
 in `.env.example`.
 ## License
 MIT License
 ## Contributing
 We welcome contributions! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.
 ## Contact
 For questions or support, please contact:
 - **Email**: ilya.filisteev@gmail.com


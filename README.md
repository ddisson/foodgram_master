# Foodgram Project

![Foodgram workflow](https://github.com/ddisson/foodgram_master/actions/workflows/foodgram_workflow.yml/badge.svg?branch=main)(https://github.com/ddisson/foodgram_master/actions/workflows/foodgram_workflow.yml)

Embark on a culinary journey with Foodgram, crafted by Dmitry Disson—a sailor by day and a coder by night. When the seas are still and the stars alight, Dmitry weaves this platform for food enthusiasts to share, savor, and subscribe to a universe of recipes.

Set sail to culinary discovery at: [http://158.160.26.37/](http://158.160.26.37/)

## 🚢 About the Author
Dmitry Disson, the sailor who charts the seas by day, takes to coding by night, blending the discipline of navigation with the finesse of software development. In the calm of nocturnal waves, he architects Foodgram, steering through the realms of React, Django, Docker, and GitHub Actions to dock a community where epicurean explorations abound.

## 🍔 Features
- **Create & Share Recipes**: Bring your culinary art to the Foodgram table.
- **Follow Favorites**: Keep tabs on top recipes and their creators.
- **Curate Favorites**: Amass your go-to recipes for culinary inspiration.
- **Shopping List Generator**: Convert recipes into a convenient shopping list with ease.

## 🛠 Tech Stack
- **Frontend**: React
- **Backend**: Django
- **Containerization**: Docker
- **CI/CD**: GitHub Actions

## 🚀 Getting Started

Ensure you have the following prerequisites installed on your machine:
- Python (>= 3.6)
- Docker
- Git



To get Foodgram up and sailing on your local development environment or on an external server, follow these nautical steps:

1. **Clone the repository:**

    Navigate to your desired directory and run the following command to clone the Foodgram repository:

    ```bash
    git clone https://github.com/ddisson/foodgram_master.git
    cd foodgram
    ```

2. **Set up the environment:**

    Prepare your virtual environment using Python 3.6 or higher, and activate it:

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies:**

    Within the active virtual environment, upgrade `pip` and install the required dependencies:

    ```bash
    pip install --upgrade pip
    cd backend
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**

    Craft a `.env` file in the root directory and populate it with your secret keys and database information:

    ```plaintext
    # .env file content
    SECRET_KEY='django-insecure-tty(dm80q($gnsb@z0d)j@a2#5$t=+2wp@z-0y@+jj%n)#ay0!'

    DB_ENGINE=django.db.backends.postgresql
    POSTGRES_DB=postgres
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    DB_HOST=db
    DB_PORT=5432

    ALLOWED_HOSTS=127.0.0.1,localhost,your_local_ip

    LANGUAGE_CODE=ru-ru 

    DEBUG = False
    ```

5. **Launch with Docker Compose:**

    Build and run the Docker containers using the following commands from the `infra` directory:

    ```bash
    cd infra
    docker-compose build
    docker-compose up
    ```

    After successful completion, the Foodgram application should be accessible at [http://localhost:8000](http://localhost:8000).

6. **Database migrations and static files setup:**

    Once the containers are running, perform the database migrations and collect the static files:

    ```bash
    # Apply database migrations
    docker-compose exec backend python manage.py migrate
    
    # Collect static files
    docker-compose exec backend python manage.py collectstatic --no-input
    ```

7. **Create a superuser:**

    For full access to the admin site, create a superuser with the following command:

    ```bash
    docker-compose exec backend python manage.py createsuperuser
    ```

    Follow the prompts to complete the creation of a superuser. Once done, you can access the Django admin panel by navigating to [http://localhost:8000/admin](http://localhost:8000/admin) and logging in with your superuser credentials.

### Launch on an External Server

Execute the following commands to deploy Foodgram on an external server:

```bash

# Enter virtual environment and create a folder for the project
mkdr foodgram
cd foodgram

# Create .env and copy your local .env info in it
sudo nano .env

# Create nginx.conf copy your local .env info in it
sudo nano nginx.conf

# Launch the containers from dockerhub images
docker compose -f docker-compose.yml up

# Run database migrations
docker-compose -f docker-compose.yml exec backend python manage.py migrate

# Collect static files
docker-compose -f docker-compose.yml exec backend python manage.py collectstatic --no-input

# Copy collected static files to the static directory
docker-compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/

# Create a superuser for the Django admin
docker-compose -f docker-compose.yml exec backend python manage.py createsuperuser

# Import ingredients data from CSV
docker-compose -f docker-compose.yml exec backend python manage.py import_ingredients /data/ingredients.csv

## 🚀 Steps to Get Up and Running

## 📜 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

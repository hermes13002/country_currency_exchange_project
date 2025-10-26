# Country Currency & Exchange API

This is a Django REST Framework API I built for the HNG Backend Track Stage 1 assessment. It fetches country and currency data from external sources, calculates an estimated GDP for each country, and caches all data in a MySQL database. It uses Celery and Redis to perform all data fetching and processing as a non-blocking background task.

------------------------------------------------------------------------

## 🧩 Features

-   **Asynchronous Data Refresh**: The main data-fetching operation
    (`/countries/refresh`) is handled by a Celery worker, providing
    an immediate API response (202 Accepted).
-   **External Data Caching**: Fetches and combines data from
    restcountries.com (for country info) and open.er-api.com (for
    currency rates).
-   **GDP Estimation**: Computes an `estimated_gdp` for each country
    based on its population and USD exchange rate.
-   **Dynamic Image Generation**: Creates and serves a dynamic summary
    image (`/countries/image`) showing the top 5 countries by GDP
    and the last refresh time.
-   **Filtering & Sorting**: The main `/countries` endpoint supports
    filtering by region and currency, as well as sorting by GDP.
-   **Deployment Ready**: Configured for production deployment with
    Gunicorn, Celery, Redis, and MySQL (e.g., on Railway or similar
    platforms).

------------------------------------------------------------------------

## ⚙️ Technical Stack

-   **Backend**: Django, Django REST Framework\
-   **Database**: MySQL\
-   **Task Queue**: Celery\
-   **Message Broker**: Redis\
-   **Libraries**: requests, pillow, django-filter, gunicorn,
    dj-database-url

------------------------------------------------------------------------

## 🚀 Setup and Installation (Local Development)

### Prerequisites

-   Python 3.10+
-   MySQL Server
-   Redis Server

### 1. Clone the Repository

``` bash
git clone https://github.com/hermest3002/country_currency_exchange_project.git
cd country_currency_exchange_project
```

### 2. Set Up Virtual Environment

``` bash
python -m venv venv
# Activate it
# macOS/Linux
source venv/bin/activate
# Windows
.env\Scriptsctivate
```

### 3. Install Dependencies

``` bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root and fill in your local details.

**.env.example**

``` ini
# --- Django Settings ---
SECRET_KEY="your-django-secret-key-here"
DEBUG=True

# --- Database (MySQL) ---
DB_NAME="countries_db"
DB_USER="root"
DB_PASSWORD="your-mysql-password"
DB_HOST="127.0.0.1"
DB_PORT="3306"

# --- Broker (Redis) ---
REDIS_URL="redis://127.0.0.1:6379/0"
```

### 5. Set Up Database

Make sure your MySQL server is running, then create the database
manually:

``` sql
CREATE DATABASE countries_db;
```

Run Django migrations:

``` bash
python manage.py migrate
```

### 6. Run the Application (3 Terminals)

#### Terminal 1: Start Redis

``` bash
redis-server
```

#### Terminal 2: Start the Celery Worker

``` bash
celery -A country_currency_exchange_project worker --loglevel=info
```

#### Terminal 3: Start the Django Server

``` bash
python manage.py runserver
```

Your API will be live at: <http://127.0.0.1:8000>

The project is also live at: https://web-production-aa90b.up.railway.app

------------------------------------------------------------------------

## ☁️ Deployment (Railway)

This project includes a **Procfile** with:

-   **Web service** →
    `gunicorn country_currency_exchange_project.wsgi --log-file -`
-   **Worker service** →
    `celery -A country_currency_exchange_project worker -l info`

Provision the following: - Redis (for task queue) - MySQL (Aiven or
Railway) - Add environment variables: `DATABASE_URL`, `REDIS_URL`,
`SECRET_KEY`, `DEBUG=False`

------------------------------------------------------------------------

## 📡 API Endpoints

**Base URL:** `https://<your-domain>/api`

  ------------------------------------------------------------------------------------------------------------------------
  Method       Endpoint               Description          Example Response
  ------------ ---------------------- -------------------- ---------------------------------------------------------------
  **POST**     `/countries/refresh`   Queues a background  `202 Accepted {"message": "Refresh task has been queued..."}`
                                      task to fetch and    
                                      update data          

  **GET**      `/status`              Shows total cached   `{"total_countries": 250, "last_refreshed_at": "..."}`
                                      countries & last     
                                      refresh timestamp    

  **GET**      `/countries`           Lists countries      `[{"name": "Nigeria", ...}]`
                                      (supports            
                                      filtering/sorting)   

  **GET**      `/countries/:name`     Gets details of one  `{"id": 1, "name": "Nigeria", ...}`
                                      country              

  **DELETE**   `/countries/:name`     Deletes a country    `204 No Content`
                                      record               

  **GET**      `/countries/image`     Returns summary      *(image/png)*
                                      image                
  ------------------------------------------------------------------------------------------------------------------------

------------------------------------------------------------------------

**Author:** [Hermes13002](https://github.com/hermes13002)

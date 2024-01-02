
# PolyVisor

This is a web application built with Django and uses MongoDB as the database. It's designed to manage students' study plans and keep track of their course progress for their bachelor's degree.

## Getting Started

These instructions will help you set up the project on your local machine for development and testing purposes.

### Prerequisites

Before you begin, ensure you have the following requirements installed:

- Python 3.6 or higher
- pip (Python package installer)
- Virtual environment
- Visual Studio Code
- MongoDB Compass

### Installation

Follow these steps to set up your development environment:

1. Clone the repository to your local machine.

2. Set up a virtual environment:
   
   - Open Visual Studio Code in the project folder.
   - Create a virtual environment by running the following command in the integrated terminal:
   
     ```
     python -m venv venv
     ```

   - Activate the virtual environment:

     - On Windows:

       ```
       .\venv\Scripts\Activate
       ```

     - On Unix or MacOS:

       ```bash
       source venv/bin/activate
       ```

3. Install required Python packages by running the following commands:

   ```bash
   pip install django==4.0.3
   pip install djongo==1.3.6
   pip install pymongo==3.12.3
   pip install pytz==2022.1
   pip install django-jazzmin
   pip install django-widget-tweaks
   ```

### Setting Up MongoDB

1. **Install MongoDB Compass:**

   - Download and install MongoDB Compass from the official MongoDB website: [MongoDB Compass](https://www.mongodb.com/try/download/compass)

2. **Run MongoDB:**

   - Start MongoDB Compass and ensure that it's running as a service in the background. Make sure it's running after installation.

### Configure Project

1. **Database Setup:**

   - Replace the default database configuration with Djongo to use MongoDB as the database. Update the ENGINE, NAME, and other relevant settings. Here's an example configuration for Djongo with MongoDB:

     ```python
     DATABASES = {
         'default': {
             'ENGINE': 'djongo',
             'NAME': 'testdb',
             'CLIENT': {
                 'host': 'mongodb://localhost:27017',
             },
         },
     }
     ```

   - Ensure MongoDB is running and execute the following command to apply database migrations:

     ```bash
     python manage.py migrate
     ```

3. **Run the Development Server:**

   - Start the Django development server by running the following command in the integrated terminal:

     ```bash
     python manage.py runserver
     ```

   - Open a web browser and navigate to `http://127.0.0.1:8000/` to view the application.

### Additional Notes

- **Admin Interface:**

  - To create an admin user, use the following command:

    ```bash
    python manage.py createsuperuser
    ```

  - Follow the prompts to create your user and then access the admin panel by navigating to `http://127.0.0.1:8000/admin`.

- **Dependencies:**

  - This project uses the following key dependencies:
    - Django: The web framework for perfectionists with deadlines.
    - Djongo: To use MongoDB as a backend for Django ORM.

### Contact

Amira Alawadhi - 201900500@student.polytechnic.bh


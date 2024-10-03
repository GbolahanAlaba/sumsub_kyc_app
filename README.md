
# **Library API**

## **Overview**

This project demonstrates a simple application that interacts with the SUMSUB API, a compliance platform that helps businesses verify customers and comply with regulations. The application is designed to showcase how to integrate the SUMSUB API into a Django Rest Framework (DRF) project, enabling seamless customer verification and regulatory compliance.

## **Prerequisites**

- `Python 3.11.3`
- `Django 5.1.1`
- `Django Rest Framework (DRF) 3.15.2`
- `SQLite or any other preferred database`


## **Installation**
Clone the Repository


git clone https://github.com/GbolahanAlaba/sumsub_kyc_app

cd sumsub_kyc_app


## **Create Virtual Environment**

It's recommended to use a virtual environment to manage dependencies:


`python -m venv venv`

## **Activate Virtual Environment**

MAC `source venv/bin/activate`

Windows `venv/Scripts/activate`

## **Install Dependencies**

Install the required dependencies using pip:

`pip install -r requirements.txt`


## **Run Migrations**

Apply the migrations to set up your database schema:

`python manage.py makemigrations`

`python manage.py migrate`


## **Run the Development Server**
Start the development server to verify everything is set up correctly:

`python manage.py runserver`
You should now be able to access the application at http://127.0.0.1:8000/.

## **API Endpoints**

- `POST /create-applicant`: Create a new applicant.
- `POST /add-id-document/{applicant_id}`: Upload applicant ID document.
- `GET /applicant-statusk/{applicant_id}/`: Get applicant verification status.


## **API Implementation**


#### POST /enroll-user/

- **Request Body**:

  ```json
  {
    "first_name": "Gbolahan",
    "last_name": "Alaba",
    "email": "gbolahan@gmail.com",
  }

- **Response**:

  ```json


  {
    "status": "success",
    "message": "User enrolled",
    "data": {
        "user_id": "7903ed92-9037-4bcc-b863-f60b7f807e25",
        "first_name": "Gbolahan",
        "last_name": "Alaba",
        "email": "gb0lahan@gmainl.com",
        "created_at": "2024-09-12T13:03:55.089390Z"
    }
  }

`201 Created` on success.

`400 Bad Request` on validation error.


#### GET /borrowed-books-and-user/

- **Response**:

  ```json
  [
    {
        "first_name": "Gbolahan",
        "last_name": "Alaba",
        "email": "gb0lahan@gmainl.com",
        "borrowed_books": [
            {
                "borrow_id": "def65e2f-e74b-46bd-a577-538082e82062",
                "user": "Gbolahan",
                "book": "Forge",
                "borrow_date": "2024-09-14",
                "return_date": "2024-09-24"
            }
        ]
    },
    {
        "first_name": "Dorcas",
        "last_name": "Alaba",
        "email": "dorcas@gmainl.com",
        "borrowed_books": [
            {
                "borrow_id": "8a416d1e-8571-496c-b667-0b7152dbf7fd",
                "user": "Dorcas",
                "book": "Forge",
                "borrow_date": "2024-09-14",
                "return_date": "2024-09-24"
            }
        ]
    }
  ]

`200 OK` with books data on success.

`400 Bad Request` on validation error.


## **Testing**
Run a tests to ensure the API endpoints work as expected.

`py manage.py test`
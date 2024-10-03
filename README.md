
# **Sumsub KYC App**

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
You should now be able to access the application at http://127.0.0.1:8000/api/.

## **API Endpoints**

- `POST /create-applicant/`: Create a new applicant.
- `POST /add-id-document/{applicant_id}`: Upload applicant ID document.
- `GET /applicant-status/{applicant_id}/`: Get applicant verification status.


## **API Implementation**


#### POST /create-applicant/

- **Request Body**:

  ```json
  {  
    "levelName": "Cam",
    "externalUserId": "55544",
    "type": "individual",
    "info": { "companyInfo": {
            "address": {
                "street": "Sola Makidne",
                "postCode": "100275"
            },
            "companyName": "Expedier",
            "registrationNumber": "BC123456",
            "country": "Nigeria",
            "legalAddress": "3, Ajilekege Street, Idimu"
        } }
  }

- **Response**:

  ```json


  {
    "status": "failed",
    "message": {
        "id": "66fe86edf6ef587111670580",
        "createdAt": "2024-10-03 11:58:37",
        "createdBy": "service-sbx-APBRRXWFWAVYKL-app-gb",
        "key": "APBRRXWFWAVYKL",
        "clientId": "entacrest.com",
        "inspectionId": "66fe86edf6ef587111670580",
        "externalUserId": "554544",
        "info": {
            "companyInfo": {
                "companyName": "Expedier",
                "registrationNumber": "BC123456",
                "country": "Nigeria",
                "legalAddress": "3, Ajilekege Street, Idimu",
                "address": {
                    "street": "Sola Makidne",
                    "postCode": "100275"
                }
            }
        },
        "applicantPlatform": "API",
        "requiredIdDocs": {
            "docSets": [
                {
                    "idDocSetType": "IDENTITY",
                    "types": [
                        "DRIVERS",
                        "ID_CARD",
                        "RESIDENCE_PERMIT",
                        "PASSPORT"
                    ],
                    "videoRequired": "disabled"
                },
                {
                    "idDocSetType": "SELFIE",
                    "types": [
                        "SELFIE"
                    ],
                    "videoRequired": "photoRequired"
                }
            ]
        },
        "review": {
            "reviewId": "JokQk",
            "attemptId": "BLObF",
            "attemptCnt": 0,
            "levelName": "Cam",
            "levelAutoCheckMode": null,
            "createDate": "2024-10-03 11:58:37+0000",
            "reviewStatus": "init",
            "priority": 0
        },
        "type": "individual"
    }
  }

`201 Created` on success.

`409 Conflict` on conflict error.

`509 Internal Server Error` on server error.



#### POST /add-id-document/{applicant_id}/

- **Request Body**:

  ```json
  {
    "img_url": "https://www.ryrob.com/wp-content/uploads/2020/04/What-is-a-URL-Website-URLs-Explained-and-Best-Practices-for-Creating-URLs.jpg",
    "idDocType": "PASSPORT",
    "country": "USA"
  }

- **Response**:

  ```json
  {
    "status": "success",
    "message": "Document added successfully",
    "data": {
        "idDocType": "PASSPORT",
        "country": "USA"
    }
  }

`201 Created` on success.

`409 Conflict` on conflict error.

`509 Internal Server Error` on server error.



#### GET /applicant-status/{applicant_id}/

- **Response**:

  ```json
  {
    "status": "success",
    "message": "Verification status for: 66fe7d5e43297b0628f2054d",
    "data": {
        "IDENTITY": null,
        "SELFIE": null
    }
  }

`200 OK` with applicant successful verification status.

`400 Bad Request` on validation error.

`509 Internal Server Error` on server error.


## **Testing**
Run a tests to ensure the API endpoints work as expected.

`py manage.py test`
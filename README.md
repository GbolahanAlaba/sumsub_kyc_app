
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
You should now be able to access the application at http://127.0.0.1:8000/api

## **API Endpoints**
Base URL - `http://127.0.0.1:8000/api`

- `POST /create-applicant/`: Create a new applicant.
- `POST /add-id-document/{applicant_id}/`: Upload applicant ID document.
- `GET /fetch-verification-status/{applicant_id}/`: Fetch applicant verification status.
- `GET /all-saved-verification-status/`: Get all saved applicant verification status data.
- `GET /get-saved-verification-status/{applicant_id}/`: Get saved applicant verification status data.


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
    "status": "success",
    "message": "applicant created successfully",
    "data": {
        "id": "66fea5d8f7da9104ccf04036",
        "createdAt": "2024-10-03 14:10:32",
        "createdBy": "service-sbx-APBRRXWFWAVYKL-app-gb",
        "key": "APBRRXWFWAVYKL",
        "clientId": "globalme.com",
        "inspectionId": "66fea5d8f7da9104ccf04036",
        "externalUserId": "5990vv544",
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
            "reviewId": "PRkXY",
            "attemptId": "lVPhL",
            "attemptCnt": 0,
            "levelName": "Cam",
            "levelAutoCheckMode": null,
            "createDate": "2024-10-03 14:10:32+0000",
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

`200 OK` on success.

`400 Bad Request` on validation error.

`509 Internal Server Error` on server error.



#### GET /fetch-verification-status/{applicant_id}/

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


#### GET /all-saved-verification-status/

- **Response**:

  ```json
  {
    "status": "success",
    "message": "All saved Verification data",
    "data": [
        {
            "applicant_id": "66fe86b143297b0628f286ac",
            "country": "USA",
            "id_doc_type": "PASSPORT",
            "image_ids": [
                1306190006
            ],
            "image_review_results": {
                "1306190006": {}
            },
            "forbidden": false,
            "partial_completion": null,
            "step_statuses": null,
            "image_statuses": [],
            "selfie": null
        },
        {
            "applicant_id": "66fe7d5e43297b0628f2054d",
            "country": "USA",
            "id_doc_type": "PASSPORT",
            "image_ids": [
                62458182
            ],
            "image_review_results": {
                "62458182": {}
            },
            "forbidden": false,
            "partial_completion": null,
            "step_statuses": null,
            "image_statuses": [],
            "selfie": null
        },
        {
            "applicant_id": "66ff9996af3a7e2194c8ba19",
            "country": "Unknown",
            "id_doc_type": "Unknown",
            "image_ids": [],
            "image_review_results": {},
            "forbidden": false,
            "partial_completion": null,
            "step_statuses": null,
            "image_statuses": [],
            "selfie": null
        }
    ]
  }

`200 OK` with all applicant successful verification status data.

`509 Internal Server Error` on server error.


#### GET /get-saved-verification-status/{applicant_id}/

- **Response**:

  ```json
  {
    "status": "success",
    "message": "Verification data for applicant 66fe7d5e43297b0628f2054d",
    "data": {
        "applicant_id": "66fe7d5e43297b0628f2054d",
        "country": "USA",
        "id_doc_type": "PASSPORT",
        "image_ids": "[62458182]",
        "image_review_results": "{\"62458182\": {}}",
        "forbidden": false,
        "partial_completion": null,
        "step_statuses": "[]",
        "image_statuses": "[]",
        "selfie": null
    }
  }

`200 OK` with an applicant successful verification status.

`400 Bad Request` on validation error.

`509 Internal Server Error` on server error.


## **Testing**
Run a tests to ensure the API endpoints work as expected.

`py manage.py test`
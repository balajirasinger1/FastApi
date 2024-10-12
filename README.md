
# FastAPI CRUD Application  


This FastAPI application provides CRUD (Create, Read, Update, Delete) functionality for managing two entities: Items and User ClockIn Records. The application uses MongoDB as the database, and FastAPI's integrated Swagger UI for API documentation.



## Table of Contents 

1. [Project Overview](#project-overview)
2. [Getting Started](#getting-started)
3. [Project Setup](#project-setup)
4. [Running the Project](#running-the-project)
5. [API Endpoints](#api-endpoints)
6. [Swagger Documentation](#swagger-documentation)
7. [License](#license)


## Project Overview


The application consists of two main parts:
- **Items API**: Handles item-related data with features like creating, updating, deleting, filtering, and aggregation.
- **ClockIn Records API**: Manages user clock-in data with similar CRUD operations and filtering capabilities.



## Getting Started


### Prerequisites

- Python 3.8+ installed on your system
- MongoDB instance, either local or MongoDB Atlas
- `pip` for Python package management



### Installation

1. **Clone the Repository**:
   ```bash
   git clone <your_repository_url>
   cd <your_repository_name>
   ```
2. **Install Dependencies**: Run the following command in your project directory to install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set Up Environment Variables**:
   - Create a `.env` file in the project directory.
   - Add the following line to the `.env` file, replacing `<your_mongodb_uri>` with your actual MongoDB connection string:
     ```plaintext
     MONGO_URI=<your_mongodb_uri>
     ```



## Project Setup



### Creating the MongoDB URI

To get the MongoDB URI:

1. Go to MongoDB Atlas and create a cluster if you don’t have one already.
2. Under **Database Access**, create a user with appropriate permissions.
3. Under **Network Access**, allow IPs that will access the database.
4. Connect to your cluster and copy the MongoDB URI, replacing `<password>` with your password.


### Structure

The main application code is in `main.py`, which contains:

- MongoDB connection setup
- FastAPI initialization
- Pydantic models for input validation
- CRUD endpoints



## Running the Project


### Run the FastAPI Application

Use the following command to start the server locally:
   ```bash
   uvicorn main:app --reload
   ```
By default, this will start the application at http://127.0.0.1:8000.



### Access the Swagger UI


Once the server is running, you can view and test the APIs in your browser at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).


## API Endpoints



### Items APIs



- **POST /items** - Create a new item  
  **Request Body**:
  ```json
  {
    "name": "John Doe",
    "email": "john@example.com",
    "item_name": "Milk",
    "quantity": 5,
    "expiry_date": "20241231"
  }
  ```
  **Response**:
  ```json
  {
    "message": "Item created",
    "item_id": "60e67f1e3f8b2a7d2e634ddd"
  }
  ```

- **GET /items/{id}** - Retrieve an item by ID  
  **Path Parameter**: `id` (ObjectId of the item)  
  **Response**:
  ```json
  {
    "_id": "60e67f1e3f8b2a7d2e634ddd",
    "name": "John Doe",
    "email": "john@example.com",
    "item_name": "Milk",
    "quantity": 5,
    "expiry_date": "20241231",
    "insert_date": "20230810T14:00:00Z"
  }
  ```

- **GET /items/filter** - Filter items by various fields  
  **Query Parameters**:
    - `email`: Exact match on email
    - `expiry_date`: Filter items expiring on or after this date
    - `insert_date`: Filter items inserted after this date
    - `quantity`: Filter items with quantity greater than or equal to this value  
  **Response**: A list of items matching the filter criteria.

- **GET /items/aggregate** - Aggregate items by email  
  **Response**:
  ```json
  [
    { "_id": "john@example.com", "total_items": 10 },
    { "_id": "jane@example.com", "total_items": 5 }
  ]
  ```

- **DELETE /items/{id}** - Delete an item by ID  
  **Path Parameter**: `id` (ObjectId of the item)  
  **Response**:
  ```json
  { "message": "Item deleted successfully" }
  ```


### ClockIn Records APIs



- **POST /clockin** - Create a new clockin record  
  **Request Body**:
  ```json
  {
    "email": "john@example.com",
    "location": "Office"
  }
  ```
  **Response**:
  ```json
  {
    "message": "Clockin record created",
    "record_id": "60e68e3f2b4b1b3a2e745efe"
  }
  ```

- **GET /clockin/{id}** - Retrieve a clockin record by ID  
  **Path Parameter**: `id` (ObjectId of the clockin record)  
  **Response**:
  ```json
  {
    "_id": "60e68e3f2b4b1b3a2e745efe",
    "email": "john@example.com",
    "location": "Office",
    "insert_datetime": "20230810T14:00:00Z"
  }
  ```

- **GET /clockin/filter** - Filter clockin records  
  **Query Parameters**:
    - `email`: Exact match on email
    - `location`: Exact match on location
    - `insert_datetime`: Filter records created after this date  
  **Response**: A list of records matching the filter criteria.

- **DELETE /clockin/{id}** - Delete a clockin record by ID  
  **Path Parameter**: `id` (ObjectId of the clockin record)  
  **Response**:
  ```json
  { "message": "Clockin record deleted successfully" }
  ```



## Swagger Documentation


You can view all the API endpoints and test them interactively using FastAPI's integrated Swagger UI at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

 
 

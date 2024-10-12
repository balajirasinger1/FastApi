from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field, constr, validator
from datetime import datetime, date
from typing import Optional
from dotenv import load_dotenv
import os
from bson import ObjectId, errors as bson_errors

# Load environment variables
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")

# Initialize MongoDB client
client = MongoClient(mongo_uri)

# FastAPI app
app = FastAPI() 

# Database and collections
db = client["fastapi_database"]
items_collection = db["items"]
clock_in_collection = db["clock_in_records"]

# Pydantic models for input validation
class Item(BaseModel):
    name: constr(max_length=100) = Field(..., example="John Doe")
    email: EmailStr = Field(..., example="john@example.com")
    item_name: constr(max_length=100) = Field(..., example="Milk")
    quantity: int = Field(..., gt=0, example=5)
    expiry_date: date = Field(..., example="2024-12-31")
    
    @validator('expiry_date')
    def check_expiry_date(cls, v):
        if v < date.today():
            raise ValueError('Expiry date must be in the future')
        return v

class ClockInRecord(BaseModel):
    email: EmailStr = Field(..., example="john@example.com")
    location: constr(max_length=100) = Field(..., example="Office")

from typing import Optional

class ItemUpdate(BaseModel):
    name: Optional[constr(max_length=100)] = Field(None, example="John Doe")
    email: Optional[EmailStr] = Field(None, example="john@example.com")
    item_name: Optional[constr(max_length=100)] = Field(None, example="Milk")
    quantity: Optional[int] = Field(None, gt=0, example=5)
    expiry_date: Optional[date] = Field(None, example="2024-12-31")

# API for creating a new item
@app.post("/items")
def create_item(item: Item):
    item_dict = item.dict()
    item_dict["insert_date"] = datetime.utcnow()  # Automatically set insert date
    # Convert expiry_date to string in "yyyy-mm-dd" format
    item_dict["expiry_date"] = item_dict["expiry_date"].strftime("%Y-%m-%d")
    result = items_collection.insert_one(item_dict)
    return {"message": "Item created", "item_id": str(result.inserted_id)}

# # API to GET /clock-in/filter (Filter clock-in records by email, location, and insert date)
@app.get("/items/filter")
def filter_items(
    email: Optional[str] = None,
    expiry_date: Optional[str] = None,
    insert_date: Optional[str] = None,
    quantity: Optional[int] = None
): 
    query = {}
    
    if email:
        query["email"] = email  # Exact match for email
    
    if expiry_date:
        try:
            # Convert expiry_date string to a date object
            expiry_date_obj = datetime.fromisoformat(expiry_date).date()
            query["expiry_date"] = {"$gt": expiry_date_obj}  # Items expiring after the provided date
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format for expiry_date. Use yyyy-mm-dd format.")

    if insert_date:
        try:
            # Convert insert_date string to a datetime object
            insert_date_obj = datetime.fromisoformat(insert_date)
            query["insert_date"] = {"$gte": insert_date_obj}  # Items inserted after the provided date
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format for insert_date. Use yyyy-mm-dd format.")

    if quantity is not None:
        query["quantity"] = {"$gte": quantity}  # Items with quantity greater than or equal to the provided number

    items = list(items_collection.find(query))
    for item in items:
        item["_id"] = str(item["_id"])  # Convert ObjectId to string for readability
    return items
  
# API to aggregate items to count grouped by email
@app.get("/items/aggregate")
def aggregate_items_by_email():
    aggregation = items_collection.aggregate([
        {"$group": {"_id": "$email", "total_items": {"$sum": 1}}}
    ])
    return list(aggregation) 
      
# API to retrieve an item by ID
@app.get("/items/{id}") 
def get_item(id: str):
    try:
        item = items_collection.find_one({"_id": ObjectId(id)})
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        item["_id"] = str(item["_id"])  # Convert ObjectId to string for readability
        return item   
    except bson_errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid item ID")

# API to GET /items/filter (Filter items based on email, expiry date, insert date, and quantity)
@app.get("/items/filter")
def filter_items(
    email: Optional[str] = None,
    expiry_date: Optional[str] = None,
    insert_date: Optional[str] = None,
    quantity: Optional[int] = None
):
    query = {}
    if email:
        query["email"] = email
    if expiry_date:
        query["expiry_date"] = {"$gt": expiry_date}  # Filter for items expiring after the given date
    if insert_date:
        try:
            insert_date_obj = datetime.fromisoformat(insert_date)
            query["insert_date"] = {"$gte": insert_date_obj}
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid insert_date format. Use yyyy-mm-dd.")
    if quantity is not None:
        query["quantity"] = {"$gte": quantity}

    items = list(items_collection.find(query))
    for item in items:
        item["_id"] = str(item["_id"])  # Convert ObjectId to string for readability
    return items

# API to GET /items/aggregate (Aggregate items to count grouped by email)
@app.get("/items/aggregate")
def aggregate_items_by_email():
    aggregation = items_collection.aggregate([
        {"$group": {"_id": "$email", "total_items": {"$sum": 1}}}
    ])
    return list(aggregation)

# API to DELETE /items/{id} (Delete an item by ID)
@app.delete("/items/{id}")
def delete_item(id: str):
    try:
        result = items_collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message": "Item deleted successfully"}
    except bson_errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid item ID")

# # API to PUT /items/{id} (Update an item by ID)
@app.put("/items/{id}")
def update_item(id: str, item: ItemUpdate):
    try:
        update_data = item.dict(exclude_unset=True)

        # Convert expiry_date to datetime if it is provided
        if "expiry_date" in update_data and update_data["expiry_date"] is not None:
            # Convert date to datetime, setting time to midnight
            update_data["expiry_date"] = datetime.combine(update_data["expiry_date"], datetime.min.time())
        
        result = items_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return {"message": "Item updated successfully"}
    except bson_errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid item ID")
 

# API to POST /clock-in (Create a new clock-in record)
@app.post("/clock-in")
def clock_in(record: ClockInRecord):
    record_dict = record.dict()
    record_dict["insert_datetime"] = datetime.utcnow()  # Automatically set insert date and time
    result = clock_in_collection.insert_one(record_dict)
    return {"message": "Clock-in record created", "record_id": str(result.inserted_id)}

# API to GET /clock-in/{id} (Retrieve a clock-in record by ID)
@app.get("/clock-in/{id}")
def get_clock_in_record(id: str):
    try:
        record = clock_in_collection.find_one({"_id": ObjectId(id)})
        if record is None:
            raise HTTPException(status_code=404, detail="Clock-in record not found")
        record["_id"] = str(record["_id"])  # Convert ObjectId to string for readability
        return record
    except bson_errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid record ID")


# API to PUT /clock-in/{id} (Update a clock-in record by ID)
@app.put("/clock-in/{id}")
def update_clock_in_record(id: str, record: ClockInRecord):
    try:
        update_data = record.dict(exclude_unset=True)
        result = clock_in_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Clock-in record not found")
        
        return {"message": "Clock-in record updated successfully"}
    except bson_errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid record ID")

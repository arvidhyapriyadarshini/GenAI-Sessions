from fastapi import FastAPI, UploadFile, File, APIRouter
import pandas as pd
from io import StringIO
from datetime import datetime

app = FastAPI()

# Creating API routers
router_gross_margin = APIRouter()
router_most_profitable_vendor = APIRouter()
router_most_profitable_day = APIRouter()
router_least_profitable_customer = APIRouter()

# Temporary storage for the uploaded file
uploaded_file_df = None

@app.post("/upload_csv/")
async def upload_csv(file: UploadFile = File(...)):
    global uploaded_file_df
    contents = await file.read()
    csv_string_io = StringIO(contents.decode())
    uploaded_file_df = pd.read_csv(csv_string_io)
    return {"filename": file.filename, "detail": "File uploaded successfully."}

@router_gross_margin.get("/gross_margin/")
async def get_gross_margin():
    global uploaded_file_df
    total_revenue = (uploaded_file_df['Selling price'] * uploaded_file_df['Quantity sold']).sum()
    total_cost = (uploaded_file_df['Buying price'] * uploaded_file_df['Quantity sold']).sum()
    gross_margin = (total_revenue - total_cost) / total_revenue
    return {"gross_margin": gross_margin}

@router_most_profitable_vendor.get("/most_profitable_vendor/")
async def get_most_profitable_vendor():
    global uploaded_file_df
    uploaded_file_df['Profit'] = (uploaded_file_df['Selling price'] - uploaded_file_df['Buying price']) * uploaded_file_df['Quantity sold']
    profit_by_vendor = uploaded_file_df.groupby('Firm bought from')['Profit'].sum()
    most_profitable_vendor = profit_by_vendor.idxmax()
    return {"most_profitable_vendor": most_profitable_vendor}

@router_most_profitable_day.get("/most_profitable_day/")
async def get_most_profitable_day():
    global uploaded_file_df
    uploaded_file_df['Date'] = pd.to_datetime(uploaded_file_df['Date'], format='%d/%m/%y')
    uploaded_file_df['DayOfWeek'] = uploaded_file_df['Date'].dt.dayofweek
    days = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
    uploaded_file_df['DayOfWeek'] = uploaded_file_df['DayOfWeek'].map(days)
    profit_by_day = uploaded_file_df.groupby('DayOfWeek')['Profit'].sum()
    most_profitable_day = profit_by_day.idxmax()
    return {"most_profitable_day": most_profitable_day}

@router_least_profitable_customer.get("/least_profitable_customer/")
async def get_least_profitable_customer():
    global uploaded_file_df
    profit_by_customer = uploaded_file_df.groupby('Customer')['Profit'].sum()
    least_profitable_customer = profit_by_customer.idxmin()
    return {"least_profitable_customer": least_profitable_customer}

# Include routers in the application
app.include_router(router_gross_margin, prefix="/analyze")
app.include_router(router_most_profitable_vendor, prefix="/analyze")
app.include_router(router_most_profitable_day, prefix="/analyze")
app.include_router(router_least_profitable_customer, prefix="/analyze")
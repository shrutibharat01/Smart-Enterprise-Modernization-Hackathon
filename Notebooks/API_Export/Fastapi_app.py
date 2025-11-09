from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.get("/sales_summary")
def sales_summary():
    try:
        df = spark.table("enterprise_modernization.gold.customer_vehicle_fleet")
        total_sales = df.selectExpr("sum(sales) as total_sales").collect()[0]["total_sales"]
        return {"total_sales": total_sales}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/total_sales_by_month")
def total_sales_by_month():
    df = spark.table("enterprise_modernization.gold.customer_vehicle_fleet")
    sales_by_month = df.groupBy("month").sum("sales").orderBy("month").collect()
    result = [{"month": row["month"], "total_sales": row["sum(sales)"]} for row in sales_by_month]
    return {"sales_by_month": result}

# @app.post("/predict_sales")
# def predict_sales(request: QueryRequest):
#     # Use your trained model to predict based on request.query
#     prediction = your_model_predict_function(request.query)
#     return {"prediction": prediction}

# @app.post("/chatbot_query")
# def chatbot_query(request: QueryRequest):
#     answer = chatbot_response(request.query)
#     return {"answer": answer}


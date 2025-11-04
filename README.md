# 🚗 Smart Modernization Hub

**Smart Modernization Hub** is a cloud-native data modernization framework designed to transform traditional automotive enterprise systems (SAP, CRM, IoT/FleetEdge) into **API-first, AI-driven, real-time pipelines** using **FastAPI**, **Databricks LakeFlow**, and **Delta Lake**.

This project is part of **i.mobilothon 5.0 (Hack2Skill x Volkswagen)** — focused on *Smart Enterprise Modernization*.

---

## 🧠 Key Features

✅ **Multi-Source Ingestion Layer**
- Connects to SAP, CRM, and IoT/FleetEdge systems via REST APIs or data dumps.  
- Simulated connectors for demo using public datasets and APIs.

✅ **Real-Time Streaming Simulation**
- Fleet telemetry data simulated via a Python service (sends vehicle JSON data in real time).

✅ **Unified Orchestration**
- API layer (FastAPI) to trigger and monitor ETL pipelines.
- Databricks LakeFlow for end-to-end workflow execution.

✅ **Delta Lake Storage**
- ACID transactions, schema evolution, and time travel on AWS S3 or local path.

✅ **AI Layer (Coming Next)**
- Predictive demand forecasting  
- Cost optimization & job scheduling recommendations  
- Churn prediction & customer insights

✅ **Zero-Downtime Modernization**
- Incremental migration of legacy systems into reusable, scalable microservices.

---

## 🏗️ Architecture Overview

+-----------------------+
| Source Systems        |
| SAP | CRM | IoT Edge  |
+-----------------------+
         ↓
+-------------------+
| FastAPI Ingestion |
| Layer (Layer 0)   |
+-------------------+
         ↓
+-------------------+
| Delta Lake (S3)   |
| Bronze → Silver   |
| → Gold Layers     |
+-------------------+
         ↓
+-------------------+
| Databricks        |
| LakeFlow / Jobs   |
+-------------------+
         ↓
+--------------------------+
| Databricks SQL/Dashboard |
| AI Insights              |
+--------------------------+


---

## 🧱 Project Structure

Smart-Modernization-Hub/
│
├── README.md
├── requirements.txt
├── Dockerfile
├── .env.example
│
├── src/
│ ├── main.py
│ ├── connectors.py
│ ├── storage.py
│ ├── simulate_fleet.py
│ ├── config.py
│ └── init.py
│
├── data/
│ ├── bronze/
│ ├── ingestion_log.jsonl
│ └── samples/
│
├── notebooks/
│ ├── bronze_to_silver.py
│ ├── silver_to_gold.py
│ └── ai_forecast_demo.py
│
└── docs/
├── ARCHITECTURE.md
├── DEPLOYMENT.md
└── API_REFERENCE.md


---

## ⚙️ Tech Stack

| Category | Technology |
|-----------|-------------|
| API Layer | FastAPI, Python |
| ETL & Orchestration | Databricks LakeFlow, PySpark |
| Storage | Delta Lake on AWS S3 / local |
| Visualization | Databricks SQL, Power BI |
| Containerization | Docker |
| AI Layer | PySpark MLlib / scikit-learn / LangChain |
| Deployment | Render / AWS ECS / Databricks Repos |

---

## 🧩 Getting Started

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/Smart-Modernization-Hub.git
cd Smart-Modernization-Hub
```

### 2️⃣ Setup Environment
```bash
python -m venv venv
source venv/bin/activate       # For Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3️⃣ Run Locally
```bash
export SIMULATE_FLEET=true
uvicorn src.main:app --reload
```
API Docs: http://localhost:8000/docs


### 🚀 Using the API
✅ Trigger Ingestion
Endpoint: POST /ingest

Example Request:
```json
{
  "source": "crm",
  "params": { "region": "india" }
}
```

Example Response:
```json
{
  "status": "ok",
  "path": "./data/bronze/crm/crm_1730590062.parquet",
  "rows": 1289
}
```

### ✅ Stream Fleet Telemetry

Real-time telemetry data (simulated by a background thread):
Endpoint: POST /fleet_ingest
```json
{
  "vehicle_id": "VEH-3245",
  "timestamp": 1730590062,
  "lat": 12.912,
  "lon": 77.54,
  "speed": 85,
  "rpm": 3100,
  "fault_code": null
}
```

## 🧠 How Data Flows
Step	Description	Layer
1	Fetch SAP, CRM, FleetEdge data via APIs	Ingestion (L0)
2	Store raw data (as-is) in Delta/S3	Bronze (L1)
3	Transform & standardize	Silver (L2)
4	Aggregate business KPIs	Gold (L3)
5	Power dashboards & AI models	Serving (L4)


## 🧰 Deployment
🐳 Docker
```bash
docker build -t smart-modernization-hub:latest .
docker run -p 8000:8000 smart-modernization-hub
```

### 🌐 Render Cloud (Free)

1. Connect GitHub → “New Web Service”
2. Runtime: Python 3.10
3. Start Command:
   uvicorn src.main:app --host 0.0.0.0 --port 8000
4. Add environment variables from .env.example


## ☁️ Databricks Integration

1. Use Databricks REST API to trigger LakeFlow pipelines from FastAPI.
2. Use Auto Loader to ingest raw JSON/Parquet from S3 → Delta.
3. Notebooks handle Bronze → Silver → Gold transformations.

## 🧮 Business Impact
| AI Module                     | Value Proposition              | Business Impact                    |
| ----------------------------- | ------------------------------ | ---------------------------------- |
| Predictive Demand Forecasting | Align production with market   | ↑ Sales by 12%, ↓ Inventory by 20% |
| Cost Optimization             | Recommend optimal cluster size | ↓ Infra cost by 25%                |
| Customer Retention Model      | Predict churn risk             | ↑ Retention by 10%                 |
| AI Agent for Automation       | Natural-language orchestration | Faster insights, less manual work  |


## 🧠 Future Enhancements
1. Integrate Databricks MLflow for model tracking
2. AI agent using LangChain + OpenAI for conversational data orchestration
3. Live Databricks SQL dashboard for revenue analytics
4. Enterprise-grade monitoring (Prometheus + Grafana)

## 📊 Example Datasets (for Demo)
| Source    | Dataset                                                           | Use Case                      |
| --------- | ----------------------------------------------------------------- | ----------------------------- |
| CRM       | [Kaggle - Automotive Sales Data](https://www.kaggle.com/datasets) | Customer segmentation & sales |
| SAP       | Vehicle manufacturing / parts CSVs                                | Production KPIs               |
| FleetEdge | Telemetry stream (simulated)                                      | Predictive maintenance        |

Place CSV/JSON data inside /data/samples/.


## 📜 Environment Variables
| Variable                | Description                              |
| ----------------------- | ---------------------------------------- |
| `DATA_DIR`              | Local or S3 storage path for Bronze data |
| `SAP_API_URL`           | SAP source endpoint                      |
| `CRM_API_URL`           | CRM source endpoint                      |
| `SIMULATE_FLEET`        | Enable simulated fleet ingestion         |
| `AWS_ACCESS_KEY_ID`     | For S3 access (optional)                 |
| `AWS_SECRET_ACCESS_KEY` | For S3 access (optional)                 |
| `FLEET_INGEST_URL`      | Local or deployed API URL                |

Use .env.example as reference.


## 🧑‍💻 Contributing
We welcome contributions!
Fork the repo, create a new branch, commit your changes, and open a Pull Request.


## 🏁 License
MIT License © 2025 Smart Modernization Hub Team


## 💬 Acknowledgements
Hack2Skill & Volkswagen Group Technology Solutions India for organizing i.mobilothon 5.0
Databricks for LakeFlow orchestration
OpenAI / Kaggle for public data and model APIs

### Smart Modernization Hub —
#### Modernize. Automate. Monetize.

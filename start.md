Back-end
uvicorn api_farmacia:app --reload --port 8002

AI
uvicorn api_ai_farmacia:app --reload --port 8003

Front-end
streamlit run app_farmacia.py 
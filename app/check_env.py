from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())   # מאתר את .env מהשורש וטוען
print("DB_CONN =", os.getenv("DB_CONN"))

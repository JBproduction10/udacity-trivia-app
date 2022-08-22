from dotenv import load_dotenv
import os
load_dotenv()

database_host = os.environ.get("database_host")
database_user = os.environ.get("database_user")
database_name = os.environ.get("database_name")
database_password = os.environ.get("database_password")
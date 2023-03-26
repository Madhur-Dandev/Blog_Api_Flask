from dotenv import load_dotenv
from os import getenv
from sqlalchemy import create_engine

load_dotenv()

# print(f'''mysql+pymysql://{getenv("DATABASE_USERNAME")}:{getenv("DATABASE_PASSWORD")}@{getenv("DATABASE_HOST")}/{getenv("DATABASE")}?charset=utf8mb4''')

# connection engine object
# making connection with cloud database. Doesn't required ssl if database is in your local machine.
db = create_engine(
    f'''mysql+pymysql://{getenv("DATABASE_USERNAME")}:{getenv("DATABASE_PASSWORD")}@{getenv("DATABASE_HOST")}/{getenv("DATABASE")}?charset=utf8mb4''',
    connect_args={
        "ssl": {
            "ssl_ca": getenv("DATABASE_SSL")
        }
    }    
)

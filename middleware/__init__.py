from functools import wraps
from database import db
from sqlalchemy import text, exc
from jwt import decode, encode, ExpiredSignatureError, InvalidSignatureError
from dotenv import load_dotenv
from os import getenv
from flask import request as req, make_response as res, jsonify
from datetime import datetime, timedelta

load_dotenv()

# wrapper for checking if the user is logged in or not
def check_token(func):
    @wraps(func)
    def wrapper(token, *args, **kwargs):
        resp = {}
        try:
            with db.connect() as conn:
                result = conn.execute(text(f'''SELECT COUNT(1) FROM blog_users WHERE token = "{token}"''')).first()
                print(req.cookies.get("refresh_token"))
                if result[0]:
                    data = decode(token, getenv("SECRET_KEY"), algorithms=["HS256"])
                    resp["loggedin"] = True
                    resp["id"] = data.get("id")
                    resp["token"] = token
                else:
                    resp["loggedin"] = False

        except Exception as e:
            if isinstance(e, ExpiredSignatureError):
                refresh_token = req.cookies.get("refresh_token")
                id = decode(refresh_token, getenv("SECRET_KEY"), algorithms=["HS256"]).get('id')
                if id:
                    access_token = encode({"id": id, "exp": datetime.utcnow() + timedelta(minutes=30)}, getenv("SECRET_KEY"))
                    decodeResp = decode(access_token, getenv("SECRET_KEY"), algorithms=["HS256"])
                    if decodeResp:
                        try:
                            with db.connect() as conn:
                                updateRes = conn.execute(text(f'''UPDATE blog_users SET token = "{access_token}" WHERE id = "{id}"''')).rowcount
                                if updateRes:
                                    resp["loggedin"] = True
                                    resp["id"] = id
                                    resp["token"] = access_token

                                    
                        except exc.SQLAlchemyError as e:
                            print(e)
                            return res(jsonify({"message": "Server Error"}), 500)
                        resp["loggedin"] = True
                        resp["id"] = decodeResp.get("id")
                    
                    else:
                        resp["message"] = "Server Error!"
                else:
                    resp["message"] = "Please Log in first."
            else:
                print(e)
                resp["message"] = "Server Error!"
        return func(token, resp, *args, **kwargs)
    return wrapper

    
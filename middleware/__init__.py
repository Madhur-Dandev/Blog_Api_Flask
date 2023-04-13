from functools import wraps
from database import db
from sqlalchemy import text, exc
from jwt import decode, encode, ExpiredSignatureError, InvalidTokenError
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
                # print(req.cookies.get("refresh_token"))
                if result[0] == 1:
                    data = decode(token, getenv("SECRET_KEY"), algorithms=["HS256"])
                    resp["loggedin"] = True
                    resp["id"] = data.get("id")
                    resp["token"] = token
                else:
                    resp["loggedin"] = False

        except (Exception, ExpiredSignatureError, InvalidTokenError) as e:
            if isinstance(e, ExpiredSignatureError):
                # print("new token generating...")
                refresh_token = req.cookies.get("refresh_token")
                id = decode(refresh_token, getenv("SECRET_KEY"), algorithms=["HS256"]).get('id')
                # print(id)
                if id:

                    # Below methods only works on some operating system where decode it done manually
                    # access_token = encode({"id": id, "exp": datetime.utcnow() + timedelta(minutes=30)}, getenv("SECRET_KEY")).decode("utf-8")
                    
                    access_token = encode({"id": id, "exp": datetime.utcnow() + timedelta(minutes=30)}, getenv("SECRET_KEY"), algorithm="HS256")
                    # print(access_token)
                    # decodeResp = decode(access_token, getenv("SECRET_KEY"), algorithms=["HS256"])
                    # if decodeResp:
                        # print("new token generated...")
                    try:
                        with db.connect() as conn:
                            conn.execute(text(f'''UPDATE blog_users SET token = "{access_token}" WHERE id = "{id}"'''))
                            # print("new token updated in database...")
                            resp["loggedin"] = True
                            resp["id"] = id
                            resp["token"] = access_token

                                
                    except exc.SQLAlchemyError as e:
                        print(e)
                        return res(jsonify({"message": "Server Error"}), 500)
                    # resp["loggedin"] = True
                    # resp["id"] = decodeResp.get("id")
                    
                    # else:
                    #     # resp["message"] = "Server Error!"
                    #     return res(jsonify({"message": "Server Error"}), 500)
                else:
                    resp["message"] = "Please Log in first."
            elif isinstance(e, InvalidTokenError):
                resp["message"] = "Invalid Token"
            else:
                print(e)
                # resp["message"] = "Server Error!"
                return res(jsonify({"message": "Server Error"}), 500)
        # print(resp)   
        return func(token, resp, *args, **kwargs)
    return wrapper

    
from database import db
from flask import make_response as res, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from jwt import encode
from datetime import datetime, timedelta
from dotenv import load_dotenv
from os import getenv
from exception import UserDefined
from sqlalchemy import text

load_dotenv()


class GetUser:
    def __init__(self, userData: str, userPassword: str):
        self.__userData = userData
        self.__userPassword = userPassword

    @property
    def userData(self):
        return self.__userData
    
    def getUserDetail(self, exist_user):
        try:
            if exist_user:
                if check_password_hash(exist_user.get("user_password"), self.__userPassword):
                    access_token = encode({"id": exist_user.get("id"), "exp": datetime.utcnow() + timedelta(minutes=30)}, getenv("SECRET_KEY"))
                    refresh_token = encode({"id": exist_user.get("id"), "exp": datetime.utcnow() + timedelta(days=30)}, getenv("SECRET_KEY"))
                    resp = res({
                        "login": True,
                        "username": exist_user.get("username"),
                        "token": access_token
                    })
                    resp.set_cookie("refresh_token", refresh_token, secure=True, httponly=True, max_age=(3600 * 24 * 30))
                    return resp
                else:
                    raise UserDefined({"message": "Password is incorrect!"})
            else:
                raise UserDefined({"message": "Email or Username is incorrect!"})
        except (UserDefined, Exception) as e:
            if isinstance(e, UserDefined):
                print(e)
                return res(jsonify(e.args[0]), 400)
            
            print(e)
            return res(jsonify({"message": "Server Error"}), 500)


           

class GetUserByEmail(GetUser):
    def __init__(self, userData: str, userPassword: str):
        super().__init__(userData, userPassword)
        
    def getUserDetail(self):
        try:
            with db.connect() as conn:
                exist_user = conn.execute(text(f'''select id, user_name, user_password from blog_users where user_email ="{self.userData}"''')).mappings().first()
                return super().getUserDetail(exist_user)
        except (UserDefined, Exception) as e:
            if isinstance(e, UserDefined):
                return res(jsonify(e.args[0]), 400)
            print(e)
            return res(jsonify({"message": "Server Error"}), 500)

class GetUserByUser(GetUser):
    def __init__(self, userData: str, userPassword: str):
        super().__init__(userData, userPassword)
        
    def getUserDetail(self):
        try:
            with db.connect() as conn:
                exist_user = conn.execute(text(f'''select id, user_name, user_password from blog_users where user_name ="{self.userData}"''')).mappings().first()
                return super().getUserDetail(exist_user)
        except (UserDefined, Exception) as e:
            if isinstance(e, UserDefined):
                return res(jsonify(e.args[0]), 400)
            print(e)
            return res(jsonify({"message": "Server Error"}), 500)

            
        
            
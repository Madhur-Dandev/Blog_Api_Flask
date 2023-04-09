from database import db
from flask import make_response as res, jsonify, request as req
from werkzeug.security import check_password_hash
from jwt import encode
from datetime import datetime, timedelta
from dotenv import load_dotenv
from os import getenv
from exception import UserDefined
from sqlalchemy import text, exc

load_dotenv()


class GetUser:
    def __init__(self, userData: str, userPassword: str):
        self.__userData = userData
        self.__userPassword = userPassword

    @property
    def userData(self):
        return self.__userData
    
    def getUserDetail(self, type=""):
        try:
            query = "SELECT id, user_name, user_password, token FROM blog_users WHERE"
            if type == "email":
                query += f''' user_email = "{self.__userData}"'''
            else:
                query += f''' user_name = "{self.__userData}"'''

            with db.connect() as conn:
                exist_user = conn.execute(text(query)).mappings().first()
                if exist_user:
                    if check_password_hash(exist_user.get("user_password"), self.__userPassword):
                        # refresh_token = encode({"id": exist_user.get("id"), "exp": datetime.utcnow() + timedelta(days=30)}, getenv("SECRET_KEY")).decode("utf-8")
                        # access_token = exist_user.get("token") if exist_user.get("token") else encode({"id": exist_user.get("id"), "exp": datetime.utcnow() + timedelta(minutes=30)}, getenv("SECRET_KEY")).decode("utf-8")
                        refresh_token = encode({"id": exist_user.get("id"), "exp": datetime.utcnow() + timedelta(days=30)}, getenv("SECRET_KEY"), algorithm="HS256")
                        access_token = exist_user.get("token") if exist_user.get("token") else encode({"id": exist_user.get("id"), "exp": datetime.utcnow() + timedelta(minutes=30)}, getenv("SECRET_KEY"), algorithm="HS256")

                        if exist_user.get("id"):
                            conn.execute(text(f'''UPDATE blog_users SET token = "{access_token}" WHERE id = {exist_user.get("id")}'''))

                        resp = res({
                                "message": "Login Successfully!",
                                "userName": exist_user.get("user_name"),
                                "token": access_token
                            })
                        resp.set_cookie("refresh_token", value=refresh_token, secure=True, httponly=True, samesite=None, max_age=(3600 * 24 * 30))
                        return resp
                    else:
                        raise UserDefined({"message": "Password is incorrect!", "incorrect": "password"})
                else:
                    raise UserDefined({"message": "Email or Username is incorrect!", "incorrect": "useremail"})
                
        except (Exception) as e:
            if isinstance(e, UserDefined):
                print(e)
                return res(jsonify(e.args[0]), 400)
            
            print(e)
            return res(jsonify({"message": "Server Error"}), 500)

class GetUserByEmail(GetUser):
    def __init__(self, userData: str, userPassword: str):
        super().__init__(userData, userPassword)
        
    def getUserDetail(self):
        return super().getUserDetail(type="email")

class GetUserByUser(GetUser):
    def __init__(self, userData: str, userPassword: str):
        super().__init__(userData, userPassword)
        
    def getUserDetail(self):
        return super().getUserDetail(type="name")
        

class Comment:

    def __init__(self, resp, comment_id=None, blog_id=None, reply_id=None) -> None:
        self.__resp = resp
        self.__comment_id = comment_id
        self.__blog_id = blog_id
        self.__reply_id = reply_id

    @property
    def resp(self):
        return self.__resp
        
    @property
    def comment_id(self):
        return self.__comment_id

    @property
    def blog_id(self):
        return self.__blog_id

    @property
    def blog_id(self):
        return self.__reply_id

    def exists_action(self, what="", action=""):
        try:
            with db.connect() as conn:
                if what == "blog":
                    exists = conn.execute(text(f'''SELECT * FROM new_blogs WHERE id = {self.__blog_id}''')).mappings().first()
                
                if what == "comment" or what == "check_comment":
                    exists = conn.execute(text(f'''SELECT * FROM blog_comments WHERE id = {self.__comment_id}''')).mappings().first()

                if what == "reply":
                    exists = conn.execute(text(f'''SELECT * FROM blog_comment_replies WHERE id = {self.__reply_id}''')).mappings().first()
                
                if exists:
                    if exists.get("user_id") == self.__resp.get("id"):
                        if action == "delete":
                            if what == "comment":
                                conn.execute(text(f'''DELETE FROM blog_comments WHERE id = {self.__comment_id}'''))
                                return res(jsonify({"message": "Comment Deleted!"}), 200)

                            if what == "reply":
                                conn.execute(text(f'''DELETE FROM blog_comment_replies WHERE id = {self.__reply_id}'''))
                                return res(jsonify({"message": "Reply Deleted!"}), 200)
                        
                        else:
                            if req.is_json:
                                body = req.json.get("body")
                                if body != "":

                                    if what == "comment" or what == "blog":
                                        if action == "insert":
                                            conn.execute(text(f'''INSERT INTO blog_comments (blog_id, user_id, comment_body) VALUES ({self.__blog_id}, {self.__resp.get("id")}, "{body}")'''))
                                            
                                            return res(jsonify({"message": "Comment Added"}), 201)

                                        if action == "update":
                                            conn.execute(text(f'''UPDATE blog_comments SET comment_body = "{body}" WHERE id = {self.__comment_id}'''))
                                    
                                            return res(jsonify({"message": "Comment Updated!"}), 200)
                                    
                                    if what == "reply" or what == "check_comment":
                                        if action == "insert":
                                            conn.execute(text(f'''INSERT INTO blog_comment_replies (blog_id, user_id, comment_id, reply_body) VALUES ({self.__blog_id}, {self.__resp.get("id")}, {self.__comment_id}, "{body}")'''))
                                            
                                            return res(jsonify({"message": "Reply Added"}), 201)

                                        if action == "update":
                                            conn.execute(text(f'''UPDATE blog_comment_replies SET reply_body = "{body}" WHERE id = {self.__reply_id}'''))
                                    
                                            return res(jsonify({"message": "Reply Updated!"}), 200)

                            raise UserDefined({"message": "Data is required and comment body must not be empty!"})
                    else:
                        return res(jsonify({"message": "Not Authorized!"}), 401)
                else:
                    if what == "blog":
                        raise UserDefined({"message": "Blog not exists!"})
                    
                    if what == "comment" or what == "check_comment":
                        raise UserDefined({"message": "Comment not exists!"})
                    
                    if what == "reply":
                        raise UserDefined({"message": "Reply not exists!"})

        except (exc.SQLAlchemyError, Exception) as e:
            if isinstance(e, UserDefined):
                print(e.args[0])
                return res(jsonify(e.args[0]), 400)
            
            print(e)
            return res(jsonify({"message": "Server Error"}), 500)         
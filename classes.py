from database import db
from flask import make_response as res, jsonify, request as req
from werkzeug.security import check_password_hash, generate_password_hash
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
    
    def getUserDetail(self, exist_user):
        try:
            if exist_user:
                if check_password_hash(exist_user.get("user_password"), self.__userPassword):
                    access_token = encode({"id": exist_user.get("id"), "exp": datetime.utcnow() + timedelta(minutes=30)}, getenv("SECRET_KEY")).decode("utf-8")
                    refresh_token = encode({"id": exist_user.get("id"), "exp": datetime.utcnow() + timedelta(days=30)}, getenv("SECRET_KEY")).decode("utf-8")
                    with db.connect() as conn:
                        token_update_result = conn.execute(text(f'''UPDATE blog_users SET token = "{access_token}" WHERE id = {exist_user.get("id")}''')).rowcount
                        if token_update_result:
                            resp = res({
                                "login": True,
                                "username": exist_user.get("username"),
                                "token": access_token
                            })
                            resp.set_cookie("refresh_token", refresh_token, secure=True, httponly=True, max_age=(3600 * 24 * 30))
                            return resp
                        else:
                            raise Exception("Can't update user token in database.")
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
        
            
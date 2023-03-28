from flask import Blueprint, jsonify, request as req, make_response as res, render_template as render
from database import db
from sqlalchemy import text
from exception import UserDefined
from os import getenv
from dotenv import load_dotenv
from middleware import check_token
from string import ascii_lowercase, ascii_uppercase, digits
from random import choice
from os import path, mkdir, rmdir

blogs = Blueprint("blogs", __name__, url_prefix="/blogs")

def genFolderName():
    return "".join([choice(f"{ascii_lowercase}{ascii_uppercase}{dir}") for i in range(8)])    

@blogs.get("/")
@blogs.get("/<sort>")
def index():
    return "Index of all blogs in Flask_Blog_Api"


@blogs.post("/create/<string:token>")
@check_token
def create(token, resp):
    try:
        print(resp)
        if resp.get('loggedin'):
            title = req.form.get("title")
            description = req.form.get("description")       
            blog_img_str = ""             
            
            for name, value in req.files.items():
                if name == "img":
                    if "img" in value.mimetype:
                        folderName = genFolderName()
                        if not path.exists(path.join(getenv("UPLOAD_FOLDER"), folderName)):
                            mkdir(path.join(getenv("UPLOAD_FOLDER"), folderName))
                        value.save(path.join(getenv("UPLOAD_FOLDER"), folderName, f"blog_img.{value.filename.rsplit('.', 1)[-1]}"))
                        blog_img_str = f'''http://localhost:5000/api/blogs/img/{folderName}/blog_img.{value.filename.rsplit('.', 1)[-1]}'''
                    else:
                        raise UserDefined({"message": "The blog image must be in a valid image format."})
            
            if len(title) <= 500:
                if len(description) <= 2000:
                    with db.connect() as conn:
                        result = conn.execute(text(f'''INSERT INTO blogs (blog_title, blog_description, blog_image, user_id) VALUES ("{title}", "{description}", "{blog_img_str}", {resp.get("id")})''')).rowcount

                        if result:
                            return jsonify({"message": "Blog created successfully!"})
                        else:
                            raise UserDefined({"message": "Can't process your request now. Try again later."})
                else:
                    raise UserDefined({"message": "Length of description must be 2000 or less."})
            else:
                    raise UserDefined({"message": "Length of title must be 500 or less."})    
            
        else:
            raise UserDefined({"message": "Please log in first."})
    except (Exception, IOError) as e:
        if isinstance(e, IOError):
            print(e)
            return res(jsonify({"message": e}), 500)
        
        if isinstance(e, UserDefined):
            # return jsonify({"Message": e.args[0]})
            print(e.args[0])
            print(e.__traceback__)
            return jsonify(e.args[0]), 400
        print(e)
        return res(jsonify({"message": "Server Error"}), 500)


@blogs.put('/blog_activity/<string:token>/<blog_id>')
@check_token
def blog_activity(token, resp, blog_id):
    print(token, resp, blog_id)
    # if resp.get("loggedin"):
    #     activity = req.args.get("activity")
    #     try:
    #         with db.connect() as conn:
    #             if activity == "like":
    #                 # current_stat = conn.execute(text(f'''SELECT * FROM use_blog_stat WHERE user_id = {resp.get("id")} AND blog_id = {blog_id}''')).mappings().first()
    #                 current_stat = conn.execute(text(f'''
    #                 BEGIN;
    #                 SELECT * FROM user_blog_stats WHERE blog_id = {blog_id} AND user_id = {resp.get("id")};
    #                 INSERT INTO user_blog_stats (user_id, blog_id, {activity}) VALUES ({resp.get("id")}, {blog_id}, TRUE);
    #                 COMMIT;''')).mappings().first()


    #                 if current_stat:
    #                     # if current_stat.get("like_stat") == 
    #                     pass
    #                 else:
    #                     insert_result = conn.execute()
    #             # blog_act = conn.execute(text(f'''UPDATE blogs SET {activity}s  = {activity}s + 1 WHERE id = {blog_id}'''))
    #             # update_user_stat = conn.execute(text(f'''
    #             # BEGIN;
    #             # UPDATE user_blog_stats SET {activity}_stat = 
    #             # '''))
    #     except (Exception) as e:
    #         pass
    return "hi"


@blogs.put("/delete/<string:id>")
def delete():
    return "Delete an existing blog"
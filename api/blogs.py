from flask import Blueprint, jsonify, request as req, make_response as res, send_from_directory
from .comments import comments
from database import db
from sqlalchemy import text, exc
from exception import UserDefined
from os import getenv
from dotenv import load_dotenv
from middleware import check_token
from string import ascii_lowercase, ascii_uppercase, digits
from random import choice
from os import path, mkdir
from shutil import rmtree, move

load_dotenv()

blogs = Blueprint("blogs", __name__, url_prefix="/blogs")
blogs.register_blueprint(comments)

def genFolderName():
    return "".join([choice(f"{ascii_lowercase}{ascii_uppercase}{digits}") for i in range(8)])    

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
                if name == "blog_img":
                    if "image" in value.mimetype:
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
                        result = conn.execute(text(f'''INSERT INTO new_blogs (blog_title, blog_description, blog_image, user_id) VALUES ("{title}", "{description}", "{blog_img_str}", {resp.get("id")})''')).rowcount

                        if result:
                            return jsonify({"message": "Blog created successfully!"})
                        else:
                            raise UserDefined({"message": "Can't process your request now. Try again later."})
                else:
                    raise UserDefined({"message": "Length of description must be 2000 or less."})
            else:
                    raise UserDefined({"message": "Length of title must be 500 or less."})    
            
        else:
            return res(jsonify({"message": "Please log in first."}), 401)
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
    if resp.get("loggedin"):
        activity = req.args.get("activity")
        try:
            with db.connect() as conn:
                blog_exists = conn.execute(text(f'''SELECT * FROM new_blogs WHERE id = {blog_id}''')).mappings().first()
                if blog_exists:
                    current_stat = conn.execute(text(f'''SELECT * FROM user_blog_stats WHERE user_id = {resp.get("id")} AND blog_id = {blog_id}''')).mappings().first()
                    if activity == "like":                    
                        if current_stat:
                            print(current_stat)
                            if current_stat.get("like_stat"):
                                update_user_stat = conn.execute(text(f'''UPDATE user_blog_stats SET like_stat = FALSE AND dislike_stat = FALSE WHERE id = {current_stat.get("id")}''')).rowcount

                                conn.execute(text(f'''UPDATE new_blogs SET likes = likes - 1 WHERE id = {current_stat.get("blog_id")}''')).rowcount

                                if update_user_stat:
                                    return res(jsonify({"message": '''Removed from "Like Blogs"'''}))
                                else:
                                    raise UserDefined({"message": "Can't process your request now. Please try again later."})
                            else:

                                conn.execute(text(f'''UPDATE new_blogs SET dislikes = CASE WHEN EXISTS(SELECT 1 FROM user_blog_stats WHERE blog_id = {blog_id} AND user_id = {resp.get('id')} and dislike_stat = 1) THEN dislikes - 1 ELSE dislikes END, likes = likes + 1 WHERE id = {blog_id}''' )).rowcount

                                update_user_stat = conn.execute(text(f'''UPDATE user_blog_stats SET like_stat = TRUE, dislike_stat = FALSE WHERE user_id = {resp.get("id")} and blog_id = {blog_id}'''))

                                if not update_user_stat:
                                    raise UserDefined({"message": "Can't process your request now. Please try again later."})

                        else:
                            conn.execute(text(f'''INSERT INTO user_blog_stats (user_id, blog_id, {activity}_stat) VALUES ({resp.get("id")}, {blog_id}, TRUE)''')).rowcount
                            conn.execute(text(f'''UPDATE new_blogs SET {activity}s = {activity}s + 1 WHERE id = {blog_id}'''))

                        return res(jsonify({"message": '''Added to "Like Blogs"'''}))
                    
                    if activity == "dislike":                    
                        if current_stat:
                            print(current_stat)
                            if current_stat.get("dislike_stat"):
                                update_user_stat = conn.execute(text(f'''UPDATE user_blog_stats SET dislike_stat = FALSE AND dislike_stat = FALSE WHERE id = {current_stat.get("id")}''')).rowcount

                                conn.execute(text(f'''UPDATE new_blogs SET dislikes = dislikes - 1 WHERE id = {current_stat.get("blog_id")}''')).rowcount

                                if update_user_stat:
                                    return res(jsonify({"message": '''Dislike Removed.'''}))
                                else:
                                    raise UserDefined({"message": "Can't process your request now. Please try again later."})
                            else:

                                conn.execute(text(f'''UPDATE new_blogs SET likes = CASE WHEN EXISTS(SELECT 1 FROM user_blog_stats WHERE blog_id = {blog_id} AND user_id = {resp.get('id')} and like_stat = 1) THEN likes - 1 ELSE likes END, dislikes = dislikes + 1 WHERE id = {blog_id}''' )).rowcount

                                update_user_stat = conn.execute(text(f'''UPDATE user_blog_stats SET dislike_stat = TRUE, like_stat = FALSE WHERE user_id = {resp.get("id")} and blog_id = {blog_id}'''))

                                if not update_user_stat:
                                    raise UserDefined({"message": "Can't process your request now. Please try again later."})

                        else:
                            conn.execute(text(f'''INSERT INTO user_blog_stats (user_id, blog_id, {activity}_stat) VALUES ({resp.get("id")}, {blog_id}, TRUE)''')).rowcount
                            conn.execute(text(f'''UPDATE new_blogs SET {activity}s = {activity}s + 1 WHERE id = {blog_id}'''))

                        return res(jsonify({"message": '''You have disliked the blog.'''}))

                else:
                    raise UserDefined({"message": "Sorry Blog doesn't exists."})
                        
        except (Exception) as e:
            if isinstance(e, UserDefined):
                print(e)
                return res(jsonify(e.args[0]), 400)
            
            print(e)
            return res(jsonify({"message": "Servor Error"}), 500)
    
    else:
        return res(jsonify({"message": "Please Login First"}), 401)
        



@blogs.delete("/delete/<string:token>/<int:id>")
@check_token
def delete(token, resp, id):
    print(resp)
    if resp.get("loggedin"):
        try:
            with db.connect() as conn:

                blog_exists = conn.execute(text(f'''SELECT * FROM new_blogs WHERE id = {id}''')).mappings().first()
                print(blog_exists)

                if blog_exists:
                    if blog_exists.get("blog_image"):
                        folderName = blog_exists.get("blog_image").rsplit("/", 2)[-2]
                        try:
                            if path.exists(path=path.join(getenv("UPLOAD_FOLDER"), folderName)):
                                rmtree(path=path.join(getenv("UPLOAD_FOLDER"), folderName))
                                if path.exists(path=path.join(getenv("UPLOAD_FOLDER"), folderName)):
                                    return res(jsonify({"message": "Server Error. Please try again."}), 500)
                        except OSError as e:
                            print(e)
                            return res(jsonify({"message": "Server Error. Please try again."}), 500)

                    delete_res = conn.execute(text(f'''DELETE new_blogs, user_blog_stats, blog_comments, blog_comment_replies FROM new_blogs LEFT JOIN user_blog_stats ON new_blogs.id = user_blog_stats.blog_id LEFT JOIN blog_comments ON new_blogs.id = blog_comments.blog_id LEFT JOIN blog_comment_replies ON new_blogs.id = blog_comment_replies.blog_id WHERE new_blogs.id = {id} AND new_blogs.user_id = {resp.get("id")}''')).rowcount

                    if delete_res:
                        return res(jsonify({"message": "Blog Deleted!"}), 200)
                    else:
                        raise UserDefined({"message": "Unable to Delete"})
                else:
                    raise UserDefined({"message": "Sorry Blog doesn't exists."})
        except (Exception, exc.SQLAlchemyError) as e:
            if isinstance(e, UserDefined):
                print(e.args[0])
                return res(jsonify(e.args[0]), 400)
            
            print(e)
            return res(jsonify({"message": "Server Error"}), 500)
    else:
        return res(jsonify({"message": "Please Login First"}), 401)
    

@blogs.put("/update/<string:token>/<int:blog_id>")
@check_token
def upadateBlog(token, resp, blog_id):
    if resp.get("loggedin"):
        if req.form:
            try:
                with db.connect() as conn:
                    blog_exists = conn.execute(text(f'''SELECT * FROM new_blogs WHERE id = {blog_id}''')).mappings().first()
                    if blog_exists:
                        if blog_exists.get("user_id") == resp.get("id"):
                            title = req.form.get("title")
                            description = req.form.get("description")
                            blog_img = req.files.get("blog_img")

                            # if title or description or blog_img:
                            query_str = ""
                            blog_img_str = ""
                            if blog_img:
                                if "image" in blog_img.mimetype:
                                    folderName = blog_exists.get("blog_image").rsplit("/", 2)[-2] if blog_exists.get("blog_image") else genFolderName()
                                    if not path.exists(path.join(getenv("UPLOAD_FOLDER"), folderName)):
                                        mkdir(path.join(getenv("UPLOAD_FOLDER"), folderName))

                                    try:
                                        blog_img.save(path.join(getenv("UPLOAD_FOLDER"), folderName, f"blog_img.{blog_img.filename.rsplit('.', 1)[-1]}"))
                                        blog_img_str = f'''http://localhost:5000/api/blogs/img/{folderName}/blog_img.{blog_img.filename.rsplit('.', 1)[-1]}'''
                                    except (IOError, OSError) as e:
                                        print(e)
                                        print(e.args[0])
                                        return res(jsonify({"message": "Server Error"}), 500)                                    
                                    
                                    query_str = f'''UPDATE new_blogs SET blog_title = {blog_exists.get("blog_title") if blog_exists.get("blog_title") else title}, blog_description =  {blog_exists.get("blog_description") if blog_exists.get("blog_description") else description}, blog_image = {blog_img_str},'''
                                else:
                                    raise UserDefined({"message": "Uploaded file must be image."})
                            query_str = f'''UPDATE new_blogs SET blog_title = "{blog_exists.get("blog_title") if blog_exists.get("blog_title") == title else title}", blog_description =  "{blog_exists.get("blog_description") if blog_exists.get("blog_description") == description else description}", blog_image = "{blog_exists.get("blog_image") if blog_img_str == "" else blog_img_str}" WHERE id = {blog_id} AND user_id = {resp.get("id")}'''

                            update_resp = conn.execute(text(query_str)).rowcount

                            if not update_resp:
                                return res(jsonify({"message": "Something went wrong. Try again later!"}), 500)

                            return res(jsonify({"message": "Blog Updated!"}), 200)
                            # else:
                            #     return res(jsonify({"message": "Nothing to change!"}), 200)
                        else:
                            return res(jsonify({"message": "Not allowed!"}), 401)
                    else:
                        raise UserDefined({"message": "Blog does not exists!"})
            except (Exception, exc.SQLAlchemyError) as e:
                if isinstance(e, UserDefined):
                    print(e.args[0])
                    return res(jsonify(e.args[0]), 400)

                print(e)
                return res(jsonify({"message": "Server Error"}), 500)
        else:
            return res(jsonify({"message": "Data is required."}), 400)
    else:
        return res(jsonify({"message": "Please Log In First"}), 401)
    
@blogs.get("/img/<string:folderName>/<string:fileName>")
def blog_img(folderName, fileName):
    try:
        return send_from_directory(path.join(getenv("UPLOAD_FOLDER"), folderName), fileName, as_attachment=False)
    except (FileNotFoundError, FileExistsError, OSError) as e:
        print(e)
        return res(jsonify({"message": "File Does not Exist!"}))
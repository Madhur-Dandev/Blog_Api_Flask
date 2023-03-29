from flask import Blueprint, jsonify, request as req, make_response as res
from middleware import check_token
from classes import Comment

comments = Blueprint("comments", __name__, url_prefix="/comment")    

@comments.post('/create/<string:token>/<int:blog_id>/')
@check_token
def create(token, resp, blog_id):
    if resp.get('loggedin'):
        resp = Comment(resp, blog_id=blog_id)
        return resp.exists_action(what="blog", action="insert")
    else:
        return res(jsonify({"message": "Please log in first."}), 401)
    
@comments.put("/update/<string:token>/<int:comment_id>")
@check_token
def update(token, resp, comment_id):
    if resp.get("loggedin"):
        resp = Comment(resp, comment_id=comment_id)
        return resp.exists_action(what="comment", action="update")
    else:
        return res(jsonify({"message": "Please log in first."}), 401)
    
@comments.delete("/delete/<string:token>/<int:comment_id>")
@check_token
def delete(token, resp, comment_id):
    if resp.get("loggedin"):
        resp = Comment(resp, comment_id=comment_id)
        return resp.exists_action(what="comment", action="delete")
    else:
        return res(jsonify({"message": "Please log in first."}), 401)

@comments.post('/reply/create/<string:token>/<int:comment_id>/<string:blog_id>')
@check_token
def reply_create(token, resp, comment_id, blog_id):
    if resp.get('loggedin'):
        resp = Comment(resp, comment_id=comment_id, blog_id=blog_id)
        return resp.exists_action(what="check_comment", action="insert")
    else:
        return res(jsonify({"message": "Please log in first."}), 401)
    
@comments.put("/reply/update/<string:token>/<int:reply_id>/")
@check_token
def reply_update(token, resp, reply_id):
    if resp.get("loggedin"):
        resp = Comment(resp, reply_id=reply_id)
        return resp.exists_action(what="reply", action="update")
    else:
        return res(jsonify({"message": "Please log in first."}), 401)
    
@comments.delete("/reply/delete/<string:token>/<int:reply_id>")
@check_token
def reply_delete(token, resp, reply_id):
    if resp.get("loggedin"):
        resp = Comment(resp, reply_id=reply_id)
        return resp.exists_action(what="reply", action="delete")
    else:
        return res(jsonify({"message": "Please log in first."}), 401)
from flask import Blueprint, jsonify, request as req, make_response as res
from database import db
from sqlalchemy import text, exc
from exception import UserDefined
from middleware import check_token

profile = Blueprint("profile", __name__, url_prefix="/profile")

def getProfileData(id):
    try:
        with db.connect() as conn:
            result = conn.execute(text(f'''SELECT user_name FROM blog_users WHERE id = {id}''')).mappings().first()
            return dict(result)
    except (Exception, exc.SQLAlchemyError) as e:
        print(e)
        return {"message": "Server Error"}

@profile.get("/<string:token>")
@check_token
def get_owner_profile(token, resp):
    if resp.get("loggedin"):
        data_receive = getProfileData(resp.get("id"))
        if not data_receive.get("message"):
            return res(jsonify({"access_token": resp.get("token"), "owner": True, "data": data_receive}), 200)
        else:
            return res(jsonify({"access_token": resp.get("token"), "owner": True, "data": data_receive}), 500)
    elif resp.get("message"):
        return res(jsonify(resp), 401)
    else:
        return res(jsonify({"message": "Please Login First"}), 401)

@profile.get("/<int:id>")
def get_profile(id):
    data_receive = getProfileData(id)
    if not data_receive.get("message"):
        return res(jsonify({"owner": False, "data": data_receive}), 200)
    else:
        return res(jsonify({"owner": False, "data": data_receive}), 500)

    
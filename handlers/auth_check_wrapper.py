from flask import request, jsonify, session
from flask_jwt_extended import jwt_required, verify_jwt_in_request, get_jwt_identity
from functools import wraps
from extensions.mongo import mongo
from pymongo.errors import DuplicateKeyError, OperationFailure, PyMongoError
from logg.log import log

def auth_check_wrapper():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            if "oauth_user" in session:
                try:
                    oauth_user = mongo.db.users.find_one({"id": session["oauth_user"], "password": "Github User"})
                except OperationFailure as e:
                    log("AUTH", "critical", f"failed to find an oauth user: {e}")
                    return {"message": "auth check error at oauth check"}, 500
                except PyMongoError as e:
                    log("AUTH", "critical", f"failed to find an oauth user: {e}, pymongo error")
                    return {"message": "auth check error at oauth check"}, 500
                except Exception as e:
                    log("AUTH", "critical", f"something went wrong at oauth check: {e}")
                    return {"message": "something went wrong"}, 500
                
                if not oauth_user:
                    log("AUTH", "warning", f"oauth user was not found, oauth session: {session['oauth_user']}")
                    return {"message": "oauth user was not found, redirect to login"}, 401
                
                request.auth_identity = oauth_user["id"]

                return fn(*args, **kwargs)
            
            verify_jwt_in_request(optional=True)
            auth_user = get_jwt_identity()

            if auth_user is None:
                log("AUTH", "warning", "user not included or invalid token at jwt verification")
                return {"message": "missing or invalid token"}, 500
            
            request.auth_identity = auth_user

            return fn(*args, **kwargs)
        return decorator
    return wrapper

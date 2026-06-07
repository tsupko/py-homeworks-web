from functools import wraps

from flask import Flask, request, jsonify
from flask.views import MethodView

from db import Session, Ad, verify_password
from errors import HttpError

app = Flask('app')


def auth_required(func):
    """Decorator to require authentication"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth:
            raise HttpError(401, "Authentication required")

        if not verify_password(auth.username, auth.password):
            raise HttpError(401, "Invalid credentials")

        # Store user email in request context
        request.user_email = auth.username
        return func(*args, **kwargs)

    return wrapper


@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    response = jsonify({"error": error.message})
    response.status_code = error.status_code
    return response


class AdView(MethodView):
    decorators = [auth_required]

    def post(self):
        body = request.json
        if not body:
            raise HttpError(400, "Request body is required")

        title = body.get("title")
        description = body.get("description")

        if not title:
            raise HttpError(400, "Title is required")

        with Session() as session:
            ad = Ad(
                title=title,
                description=description or "",
                owner=request.user_email
            )
            session.add(ad)
            session.commit()

            return jsonify(ad.dict), 201

    def get(self, id: int):
        with Session() as session:
            ad = session.get(Ad, id)
            if ad is None:
                raise HttpError(404, "Ad not found")
            return jsonify(ad.dict)

    def patch(self, id: int):
        body = request.json
        if not body:
            raise HttpError(400, "Request body is required")

        with Session() as session:
            ad = session.get(Ad, id)
            if ad is None:
                raise HttpError(404, "Ad not found")

            if ad.owner != request.user_email:
                raise HttpError(403, "You can only edit your own ads")

            if "title" in body:
                ad.title = body["title"]
            if "description" in body:
                ad.description = body["description"]

            session.commit()
            return jsonify(ad.dict)

    def delete(self, id: int):
        with Session() as session:
            ad = session.get(Ad, id)
            if ad is None:
                raise HttpError(404, "Ad not found")

            if ad.owner != request.user_email:
                raise HttpError(403, "You can only delete your own ads")

            session.delete(ad)
            session.commit()

            return jsonify({"deleted": id})


ad_view = AdView.as_view('ad_view')

app.add_url_rule('/ad', view_func=ad_view, methods=['POST'])
app.add_url_rule('/ad/<int:id>', view_func=ad_view, methods=['GET', 'PATCH', 'DELETE'])


@app.route('/login', methods=['POST'])
def login():
    """Simple login endpoint for test users"""
    body = request.json
    if not body:
        raise HttpError(400, "Request body is required")

    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        raise HttpError(400, "Email and password are required")

    if not verify_password(email, password):
        raise HttpError(401, "Invalid credentials")

    return jsonify({
        "message": "Login successful",
        "user": {"email": email}
    })


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)

import flask
from flask import jsonify, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from db import Session, User
from errors import HttpError

app = flask.Flask("app")


@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    http_response = jsonify({"error": error.message})
    http_response.status_code = error.status_code
    return http_response


@app.before_request
def before_request():
    session = Session()
    request.session = session


class UserView(MethodView):
    def get(self, user_id: int):
        with Session() as session:
            user = session.get(User, user_id)
            if user is None:
                raise HttpError(404, "User not found")

        return jsonify(user.dict)

    def post(self):
        json_data = request.json
        if "name" not in json_data or "password" not in json_data:
            http_response = jsonify({"error": "Bad request"})
            http_response.status_code = 400
            return http_response

        with Session() as session:
            user = User(name=json_data["name"], password=json_data["password"])
            session.add(user)
            try:
                session.commit()
            except IntegrityError:
                raise HttpError(409, "User already exists")
            return jsonify(user.id_dict)

    def patch(self, user_id: int):
        json_data = request.json
        with Session() as session:
            user = session.get(User, user_id)
            if user is None:
                http_response = jsonify({"error": "Not found"})
                http_response.status_code = 404
                return http_response
            if "name" in json_data:
                user.name = json_data["name"]
            if "password" in json_data:
                user.password = json_data["password"]
            try:
                session.add(user)
                session.commit()
            except IntegrityError:
                http_response = jsonify({"error": "User already exists"})
                http_response.status_code = 409
                return http_response
            return jsonify(user.id_dict)

    def delete(self, user_id: int):
        with Session() as session:
            user = session.get(User, user_id)
            if user is None:
                http_response = jsonify({"error": "Not found"})
                http_response.status_code = 404
                return http_response
            session.delete(user)
            session.commit()
            return jsonify({"status": "deleted"})


def hello_world(some_id: int):
    json_data = request.json
    headers = request.headers
    qs = request.args
    print(f"{some_id=}")
    print(f"{json_data=}")
    print(f"{headers=}")
    print(f"{qs=}")

    http_response = flask.jsonify({"hello": "world"})
    http_response.status_code = 201
    return http_response


user_view = UserView.as_view("as_view")
app.add_url_rule("/hello/world/<int:some_id>", view_func=hello_world, methods=["POST"])
app.add_url_rule("/users", view_func=user_view, methods=["POST"])
app.add_url_rule(
    "/users/<int:user_id>", view_func=user_view, methods=["GET", "PATCH", "DELETE"]
)

app.run()

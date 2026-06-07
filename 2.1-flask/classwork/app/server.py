from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from db import Session, User

app = Flask("app")


def hello_world(some_id):
    json_data = request.json
    headers = request.headers
    qs = request.args
    print(f"{some_id=}")
    print(f"{json_data=}")
    print(f"{headers=}")
    print(f"{qs=}")
    response = jsonify({"hello": "world"})
    return response


class UserView(MethodView):

    def get(self, user_id: int):
        with Session() as session:
            user = session.get(User, user_id)
            if user is None:
                response = jsonify({"error": "User not found"})
                response.status_code = 404
                return response
            return jsonify(user.dict)

    def post(self):
        json_data = request.json
        with Session() as session:
            user = User(name=json_data["name"], password=json_data["password"])
            session.add(user)
            try:
                session.commit()
            except IntegrityError:
                response = jsonify({"error": "User already exists"})
                response.status_code = 409
                return response
            return jsonify(user.id_dict)

    def patch(self, user_id: int):
        json_data = request.json
        with Session() as session:
            user = session.get(User, user_id)
            if user is None:
                response = jsonify({"error": "User not found"})
                response.status_code = 404
                return response
            if "name" in json_data:
                user.name = json_data["name"]
            if "password" in json_data:
                user.password = json_data["password"]
            session.add(user)
            try:
                session.commit()
            except IntegrityError:
                response = jsonify({"error": "User already exists"})
                response.status_code = 409
                return response
            return jsonify(user.id_dict)

    def delete(self, user_id: int):
        with Session() as session:
            user = session.get(User, user_id)
            if user is None:
                response = jsonify({"error": "User not found"})
                response.status_code = 404
                return response
            session.delete(user)
            session.commit()
            return jsonify({"status": "deleted"})


user_view = UserView.as_view("user_view")

app.add_url_rule("/users", view_func=user_view, methods=["POST"])
app.add_url_rule(
    "/users/<int:user_id>", view_func=user_view, methods=["GET", "PATCH", "DELETE"]
)
app.add_url_rule("/hello/world/<int:some_id>", view_func=hello_world, methods=["POST"])

if __name__ == "__main__":
    app.run()

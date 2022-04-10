# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
movies_ns = api.namespace("movies")
directors_ns = api.namespace("directors")
genres_ns = api.namespace("genres")


class Movie(db.Model):
    __tablename__ = 'movie'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))

    genre = db.relationship("Genre")
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


# оригинал на Шаг 2 для получения всего списка фильмов без фильтрации
# @movies_ns.route("/")
# class MoviesView(Resource):
#     def get(self):
#         all_movies = Movie.query.all()
#
#         if not all_movies:
#             return "", 404
#
#         return movies_schema.dump(all_movies), 200


# Movies
# получаем вьюшку с отображением фильмов с учетом возможной фильтрации по режиссеру и/или жанру.
@movies_ns.route("/")
class MoviesView(Resource):
    def get(self):
        all_movies_query = db.session.query(Movie)

        director_id = request.args.get("director_id")
        if director_id:
            all_movies_query = all_movies_query.filter(Movie.director_id == director_id)

        genre_id = request.args.get("genre_id")
        if genre_id:
            all_movies_query = all_movies_query.filter(Movie.genre_id == genre_id)

        final_query = all_movies_query.all()

        return movies_schema.dump(final_query), 200

    def post(self):
        new_data = request.json

        movie_ = movie_schema.load(new_data)
        new_movie = Movie(**movie_)
        with db.session.begin():
            db.session.add(new_movie)

        return "", 201
# ставим при проверке закрывающий слэш в Postman


movie_new = {
        "trailer": "https://youtu.be/VISiqVeKTq8",
        "year": 2022,
        "title": "Гарри Поттер в Средиземье",
        "rating": 7.1,
        "genre_id": 3,
        "description": "История попадания в Средиземье того самого Гарри Поттера - спаситель должен примерить на себя роль Лучшего Друга ГГ саги, Сэма, и взглянуть на собственные приключения с новой стороны.",
        "director_id": 4
    }


# представление отображает детальную информацию по фильму (выбранному по id).
# если выбранного id не существует, возвращаем ошибку.
@movies_ns.route("/<int:mid>")
class MovieView(Resource):
    def get(self, mid):
        movie = Movie.query.get(mid)

        if not movie:
            return "", 404

        return movie_schema.dump(movie), 200

    def put(self, mid):
        movie_selected = db.session.query(Movie).filter(Movie.id == mid)
        movie_first = movie_selected.first()

        if movie_first is None:
            return "", 404

        new_data = request.json
        movie_selected.update(new_data)
        db.session.commit()

        return "", 204

    def delete(self, mid):
        movie_selected = db.session.query(Movie).filter(Movie.id == mid)
        movie_first = movie_selected.first()

        if movie_first is None:
            return "", 404

        rows_deleted = movie_selected.delete()

        # если произошло удаление более 1 строки, то указываем на наличие проблемы.
        if rows_deleted != 1:
            return "", 400

        db.session.commit()
        return "", 204



# Directors
# получаем вьюшку с отображением режиссеров.
@directors_ns.route("/")
class DirectorsView(Resource):
    def get(self):
        query_all = db.session.query(Director)
        final_query = query_all.all()

        return directors_schema.dump(final_query), 200

    def post(self):
        new_data = request.json

        director_ = director_schema.load(new_data)
        new_director = Director(**director_)
        with db.session.begin():
            db.session.add(new_director)

        return "", 201
# ставим при проверке закрывающий слэш в Postman


new_director = {"name": "Шеридан Шеридан"}


# представление отображает детальную информацию по режиссеру (выбранному по id).
# если выбранного id не существует, возвращаем ошибку.
@directors_ns.route("/<int:did>")
class DirectorView(Resource):
    def get(self, did):
        query_one = Director.query.get(did)

        if not query_one:
            return "", 404

        return director_schema.dump(query_one), 200

    def put(self, did):
        director_selected = db.session.query(Director).filter(Director.id == did)
        director_first = director_selected.first()

        if director_first is None:
            return "", 404

        new_data = request.json
        director_selected.update(new_data)
        db.session.commit()

        return "", 204

    def delete(self, did):
        director_selected = db.session.query(Director).filter(Director.id == did)
        director_first = director_selected.first()

        if director_first is None:
            return "", 404

        rows_deleted = director_selected.delete()

        # если произошло удаление более 1 строки, то указываем на наличие проблемы.
        if rows_deleted != 1:
            return "", 400

        db.session.commit()
        return "", 204




# Genres
# получаем вьюшку с отображением жанров.
@genres_ns.route("/")
class GenresView(Resource):
    def get(self):
        query_all = db.session.query(Genre)
        final_query = query_all.all()

        return genres_schema.dump(final_query), 200

    def post(self):
        new_data = request.json

        genre_ = genre_schema.load(new_data)
        new_genre = Genre(**genre_)
        with db.session.begin():
            db.session.add(new_genre)

        return "", 201


new_genre = {"name": "Гоблинский перевод"}
# ставим при проверке закрывающий слэш в Postman


# представление отображает детальную информацию по жанру (выбранному по id).
# если выбранного id не существует, возвращаем ошибку.
@genres_ns.route("/<int:gid>")
class GenreView(Resource):
    def get(self, gid):
        query_one = Genre.query.get(gid)

        if not query_one:
            return "", 404

        return genre_schema.dump(query_one), 200

    def put(self, gid):
        genre_selected = db.session.query(Genre).filter(Genre.id == gid)
        genre_first = genre_selected.first()

        if genre_first is None:
            return "", 404

        new_data = request.json
        genre_selected.update(new_data)
        db.session.commit()

        return "", 204

    def delete(self, gid):
        genre_selected = db.session.query(Genre).filter(Genre.id == gid)
        genre_first = genre_selected.first()

        if genre_first is None:
            return "", 404

        rows_deleted = genre_selected.delete()

        # если произошло удаление более 1 строки, то указываем на наличие проблемы.
        if rows_deleted != 1:
            return "", 400

        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(debug=True)

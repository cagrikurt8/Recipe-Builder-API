from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask import Flask
import sys
from flask import Response
from flask import request
import json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
db = SQLAlchemy(app)
engine = create_engine('sqlite:///recipes.db')


def execute_query(query):
    return engine.execute(query).fetchall()


class Recipe:
    def __init__(self, recipe_json):
        if recipe_json is None:
            return

        if isinstance(recipe_json, dict):
            self.recipe = recipe_json

        if isinstance(recipe_json, str):
            self.recipe = json.loads(recipe_json)

        self.title = self.recipe['title']
        self.directions = self.recipe['directions']
        self.ingredients = self.recipe['ingredients']


class RecipeID:
    def append_recipe(self, recipe_json):
        if recipe_json is None:
            return

        if isinstance(recipe_json, dict):
            new_recipe = json.dumps(recipe_json)
            db.session.add(User(recipe=new_recipe))

        if isinstance(recipe_json, str):
            db.session.add(User(recipe=recipe_json))

        db.session.commit()
        query = f"SELECT id FROM user"
        rs = execute_query(query)
        return Response(json.dumps({"id": rs[-1][0]}), 200)

    def return_recipe_with_id(self, recipe_id):
        query = "SELECT recipe FROM user"
        rs = execute_query(query)

        if len(rs) == 0:
            return Response(json.dumps({"error": "No recipe here yet"}), 200)

        try:
            query = f"SELECT recipe FROM user WHERE id = {recipe_id};"
            rs = execute_query(query)
            rs[0][0]
        except:
            return Response(status=404)
        else:
            return Response(rs[0][0], 200)

    def check_ingredients_argument(self, ingredients, max_directions=None):
        returning_recipes = list()
        query = "SELECT recipe FROM user"
        rs = execute_query(query)

        for recipe_json in rs:
            recipe_dict = json.loads(recipe_json[0])
            recipe_ingredients = recipe_dict['ingredients']
            final_recipe_ingredients = list()

            for ingredient in recipe_ingredients:
                final_recipe_ingredients.append(ingredient['title'])

            if ingredients == final_recipe_ingredients or set(final_recipe_ingredients).issubset(set(ingredients)):
                returning_recipes.append(recipe_dict)

        if len(returning_recipes) == 0:
            return Response(json.dumps(list()), 200)
        else:
            final_recipes = list()
            for idx, recipe in enumerate(returning_recipes):
                recipe_json = json.dumps(recipe)
                recipe_json = recipe_json.replace("'", "''") # to pass the test script's quote mark error in the directions
                query = f"SELECT id FROM user WHERE recipe = '{recipe_json}';"
                rs = execute_query(query)
                id = rs[0][0]
                new_recipe_json = {"id": id}
                new_recipe_json.update(recipe)

                if max_directions is not None:
                    if len(new_recipe_json['directions']) <= max_directions:
                        final_recipes.append(new_recipe_json)
                else:
                    final_recipes.append(new_recipe_json)
            final_recipes = self.sort_recipes(final_recipes)
            return Response(json.dumps(final_recipes), 200)

    def sort_recipes(self, recipe_list):
        for idx in range(len(recipe_list)):
            recipe_list[idx] = json.dumps(recipe_list[idx])
        recipe_list.sort(reverse=True)

        for idx in range(len(recipe_list)):
            recipe_list[idx] = json.loads(recipe_list[idx])
        return recipe_list

    def delete_recipe(self, recipe_id):
        query = f"DELETE FROM user WHERE id = {recipe_id}"
        engine.connect().execute(query)
        return Response(status=204)

    def update_recipe(self, recipe_id, json_body):
        if isinstance(json_body, str):
            new_recipe = json_body

        if isinstance(json_body, dict):
            new_recipe = json.dumps(json_body)

        new_recipe = new_recipe.replace("'", "''")
        query = f"UPDATE user SET recipe = '{new_recipe}' WHERE id = {recipe_id}"
        engine.connect().execute(query)
        return Response(status=204)


class User(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, nullable=False, autoincrement=True)
    recipe = db.Column(db.String, nullable=False)


db.create_all()

recipe_obj = None
recipe_obj_id = RecipeID()


@app.route("/api/recipe/new", methods=['POST'])
def new_recipe_post():
    if request.json != "{}" or request.json is not None:
        return recipe_obj_id.append_recipe(request.json)
    else:
        return Response(status=400)


@app.route("/api/recipe/<recipe_id>", methods=['GET', 'DELETE', 'PUT'])
def get_recipe_with_id(recipe_id):
    if request.method == 'GET':
        try:
            recipe_id = int(recipe_id)
        except ValueError:
            return Response(status=404)
        else:
            return recipe_obj_id.return_recipe_with_id(recipe_id)

    elif request.method == 'DELETE':
        query = f"SELECT id FROM user WHERE id = {recipe_id}"
        rs = execute_query(query)

        if len(rs) == 0:
            return Response(status=404)
        else:
            return recipe_obj_id.delete_recipe(recipe_id)

    elif request.method == 'PUT':
        rs = execute_query(f"SELECT recipe FROM user WHERE id = {recipe_id}")

        if len(rs) == 0:
            return Response(status=404)
        else:
            return recipe_obj_id.update_recipe(recipe_id, request.json)


@app.route("/api/recipe", methods=['GET'])
def get_recipe_with_ingredients():
    query = "SELECT recipe FROM user"
    rs = execute_query(query)
    if len(rs) == 0:
        return Response(json.dumps({"error": "No recipe here yet"}), 200)

    elif 'ingredients' not in request.args:
        return Response(json.dumps({"error": "No recipe for these ingredients"}), 200)
    else:
        ingredients = request.args['ingredients'].split('|')
        if 'max_directions' in request.args:
            return recipe_obj_id.check_ingredients_argument(ingredients, int(request.args['max_directions']))
        else:
            return recipe_obj_id.check_ingredients_argument(ingredients)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()

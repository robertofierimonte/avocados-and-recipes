import os

from loguru import logger
from flask import Flask, render_template, request, jsonify

from src.base.utils import hash_string
from src.api.database import db, ma
from src.api.models import (
    Recipe,
    RecipeSchema,
    Ingredient,
    IngredientSchema,
    RecipeIngredients,
)


# Read the environment variables
mysql_host = os.environ.get("MYSQL_HOST", "localhost")
mysql_port = os.environ.get("MYSQL_PORT", 3306)
mysql_user = os.environ.get("MYSQL_USER", "root")
mysql_pwd = os.environ.get("MYSQL_PASSWORD")
mysql_db = "recipes"

# Create the app
app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"mysql+pymysql://{mysql_user}:{mysql_pwd}@{mysql_host}:{mysql_port}/{mysql_db}"
app.config["SQLALCHEMY_ECHO"] = True
logger.info(app.config["SQLALCHEMY_DATABASE_URI"])

# Create the extension and initialise the app with the extension
db.init_app(app)
ma.init_app(app)

# Initialise the schema objects
recipe_schema = RecipeSchema()
recipes_schema = RecipeSchema(many=True)
ingredient_schema = IngredientSchema()
ingredients_schema = IngredientSchema(many=True)


@app.route("/")
def hello():
    """Root page method."""
    return render_template("index.html")


@app.route("/recipes", methods=["GET"])
def get_recipes():
    """Get all the recipes."""
    all_recipes = Recipe.query.all()
    result = recipes_schema.dump(all_recipes)
    return jsonify(result)


@app.route("/recipes/<recipe_name>", methods=["GET", "PUT", "POST", "DELETE"])
def recipe(recipe_name: str):
    """Create, get, update, or delete a recipe by its name.

    Args:
        recipe_name (str): Name of the recipe
    """
    # Get the name of the recipe and the corresponding ID
    logger.debug(f"Recipe Name: {recipe_name} .")
    recipe_id = hash_string(recipe_name, 18)
    logger.debug(f"Recipe ID: {recipe_id} .")

    # If POST, create a new recipe
    if request.method == "POST":
        # If the recipe does not already exist, create the recipe, then check
        # all the ingredients. If any of the ingredients does not exist, create
        # it and set the ref_unit_of_measure to the UOM specified in the
        # recipe. Finally, add the recipe and the ingredients to the mapping
        # table
        if Recipe.query.get(recipe_id) is None:
            try:
                ingredients = request.json.pop("ingredients")
            # TODO: If the ingredients are not in the request, return an error
            except KeyError:
                pass
            recipe = Recipe(id=recipe_id, **request.json)
            db.session.add(recipe)
            for ing in ingredients:
                ing_name = ing["name"]
                ing_id = hash_string(ing_name, 18)
                ing_uom = ing["unit_of_measure"]
                ing_qty = ing["quantity"]
                ingredient = Ingredient(
                    id=ing_id, name=ing_name, ref_unit_of_measure=ing_uom
                )
                if Ingredient.query.get(ing_id) is None:
                    db.session.add(ingredient)
                # TODO: Add the recipe and the ingredients to the mapping table
                recipe_ingredient = RecipeIngredients(
                    unit_of_measure=ing_uom, quantity=ing_qty
                )
                recipe_ingredient.ingredient = ingredient
                recipe.ingredients.append(ingredient)
            db.session.commit()
            return recipe_schema.jsonify(recipe)
        # TODO: If the recipe exists already, return an error
        else:
            pass

    # If GET, get the recipe or return 404 Not Found
    elif request.method == "GET":
        return recipe_schema.jsonify(Recipe.query.get_or_404(recipe_id))

    # If PUT, update the recipe
    elif request.method == "PUT":
        recipe = Recipe.query.get_or_404(recipe_id)

    # If DELETE, delete the recipe
    else:
        pass


@app.route("/ingredients", methods=["GET"])
def ingredients():
    """Get all the ingredients."""
    all_ingredients = Ingredient.query.all()
    result = recipes_schema.dump(all_ingredients)
    return jsonify(result)


@app.route("/ingredients/<ingredient_name>/recipes", methods=["GET"])
def recipes_by_ingredient(ingredient_id: str):
    """Get all the recipes given an ingredient.

    Args:
        ingredient_id (str): Name of the ingredient
    """
    pass


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)

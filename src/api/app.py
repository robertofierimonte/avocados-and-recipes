import os

from loguru import logger
from flask import Flask, render_template, request, jsonify

from src.base.utils import hash_string, clean_string
from src.api.database import db, ma
from src.api.models import (
    Recipe,
    RecipeSchema,
    Ingredient,
    IngredientSchema,
    RecipeIngredients,
)


# Read the environment variables
mysql_user = os.environ.get("MYSQL_USER")
mysql_pwd = os.environ.get("MYSQL_PASSWORD")
mysql_host = os.environ.get("MYSQL_HOST", "localhost")
mysql_port = os.environ.get("MYSQL_PORT", 3306)
mysql_db = os.environ.get("MYSQL_DATABASE", "recipes")

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
    return jsonify(result), 200


@app.route("/recipes/<recipe_name>", methods=["GET", "PUT", "POST", "DELETE"])
def recipe(recipe_name: str):
    """Create, get, update, or delete a recipe by its name.

    Args:
        recipe_name (str): Name of the recipe
    """
    # Get the name of the recipe and the corresponding ID
    logger.debug(f"Recipe Name: {recipe_name} .")
    recipe_id = hash_string(clean_string(recipe_name), 18)
    logger.debug(f"Recipe ID: {recipe_id} .")

    # If POST, create a new recipe
    if request.method == "POST":
        # If the recipe does not already exist, create the recipe, then check
        # all the ingredients.
        if Recipe.query.get(recipe_id) is None:
            try:
                ingredients = request.json.pop("ingredients")
                recipe = Recipe(id=recipe_id, **request.json)
                db.session.add(recipe)
                # If any of the ingredients does not exist, create it and set
                # the ref_unit_of_measure to the UOM specified in the recipe.
                # Finally, add the recipe and the ingredients to the mapping
                # table
                for ing in ingredients:
                    ing_name = ing["name"]
                    ing_id = hash_string(clean_string(ing_name), 18)
                    ing_uom = ing["unit_of_measure"]
                    ing_qty = ing["quantity"]
                    ingredient = Ingredient(
                        id=ing_id, name=ing_name, ref_unit_of_measure=ing_uom
                    )
                    if Ingredient.query.get(ing_id) is None:
                        db.session.add(ingredient)
                    # Add the recipe and the ingredient to the mapping table
                    recipe_ingredient = RecipeIngredients(
                        recipe_id=recipe_id,
                        ingredient_id=ing_id,
                        unit_of_measure=ing_uom,
                        quantity=ing_qty,
                    )
                    db.session.add(recipe_ingredient)
                # Commit all the changes to the database
                db.session.commit()
                return recipe_schema.jsonify(recipe)
            # If the ingredients are not in the request, return an error (400)
            except KeyError as e:
                jsonify(
                    {"error:": f"Attribute {e} does not exist in the payload."}
                ), 400
        # If the recipe exists already, return an error (409)
        else:
            return jsonify({"error": "This recipe already exists."}), 409

    # If GET, get the recipe or return 404 Not Found
    elif request.method == "GET":
        recipe = db.get_or_404(Recipe, recipe_id)
        return recipe_schema.jsonify(recipe)

    # If PUT, update the recipe
    elif request.method == "PUT":
        # Get the recipe or return 404 Not Found
        recipe = db.get_or_404(Recipe, recipe_id)
        # If the list of ingredients has changed, update the ingredients. The
        # ingredients can be added, modified, or removed (using a special
        # keyword)
        ingredients = request.json.pop("ingredients", None)
        if ingredients is not None:
            try:
                for ing in ingredients:
                    ing_name = ing.pop("name")
                    ing_id = hash_string(clean_string(ing_name), 18)
                    # If the ingredient is not part of the recipe anymore,
                    # delete it from the mapping table
                    if "delete" in ing and ing["delete"] == "true":
                        recipe_ingredient = RecipeIngredients.query.get_or_404(
                            (recipe_id, ing_id)
                        )
                        db.session.delete(recipe_ingredient)
                    # Otherwise...
                    else:
                        # If the ingredient is completely new, add it to the list
                        # of ingredients
                        if Ingredient.query.get(ing_id) is None:
                            ingredient = Ingredient(
                                id=ing_id,
                                name=ing_name,
                                ref_unit_of_measure=ing["unit_of_measure"],
                            )
                            db.session.add(ingredient)
                        # If the ingredient is new to the recipe, add it to the
                        # mapping table
                        if RecipeIngredients.query.get((recipe_id, ing_id)) is None:
                            recipe_ingredient = RecipeIngredients(
                                recipe_id=recipe_id,
                                ingredient_id=ing_id,
                                unit_of_measure=ing["unit_of_measure"],
                                quantity=ing["quantity"],
                            )
                            db.session.add(recipe_ingredient)
                        # If not, just update the mapping table
                        else:
                            recipe_ingredient = RecipeIngredients.query.get(
                                (recipe_id, ing_id)
                            )
                            for k, v in ing.items():
                                setattr(recipe_ingredient, k, v)
            # If the ingredients do not contain enough information, return an error (400)
            except KeyError as e:
                jsonify(
                    {"error:": f"Attribute {e} does not exist in the payload."}
                ), 400
        # Update all the other attributes of the recipe
        for k, v in request.json.items():
            setattr(recipe, k, v)
        # Commit all the changes to the database
        db.session.merge(recipe)
        db.session.commit()
        return recipe_schema.jsonify(recipe)

    # If DELETE, delete the recipe
    elif request.method == "DELETE":
        # Get the recipe or return 404 Not Found
        recipe = db.get_or_404(Recipe, recipe_id)
        # Get all the ingredients associated with the recipe in the mapping table
        n_rows = RecipeIngredients.query.filter(
            RecipeIngredients.recipe_id == recipe_id
        ).delete()
        logger.debug(f"{n_rows} will be deleted from the `recipe_ingredients` table.")
        # Delete the recipe
        db.session.delete(recipe)
        # Apply the changes
        db.session.commit()
        # Return confirmation of deletion
        return f"Recipe {recipe_name} was successfully deleted."


@app.route("/ingredients", methods=["GET"])
def ingredients():
    """Get all the ingredients."""
    all_ingredients = Ingredient.query.all()
    result = ingredients_schema.dump(all_ingredients)
    return jsonify(result), 200


@app.route("/ingredients/<ingredient_name>/recipes", methods=["GET"])
def recipes_by_ingredient(ingredient_name: str):
    """Get all the recipes given an ingredient.

    Args:
        ingredient_name (str): Name of the ingredient
    """
    # Get the ingredient ID
    ing_id = hash_string(clean_string(ingredient_name), 18)
    # Get all the recipe ID from the mapping table that are associate with the ingredient ID
    recipe_ids = db.select(RecipeIngredients.recipe_id).where(
        RecipeIngredients.ingredient_id == ing_id
    )
    # Return the recipes
    recipes = Recipe.query.filter(Recipe.id.in_(recipe_ids)).all()
    result = recipes_schema.dump(recipes)
    return jsonify(result), 200


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)

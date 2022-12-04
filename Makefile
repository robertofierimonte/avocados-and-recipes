#!make
-include .env
export

help: ## Display this help screen
	@grep -h -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

pre-commit: ## Run the pre-commit over the entire repo
	@poetry run pre-commit run --all-files

download-data: ## Download the dataset inside the `data` folder
	@curl -o data/avocados.zip -L "https://drive.google.com/uc?export=download&id=1rhRzA2s44I8ASm_bMHnCpmAz_mNJQ7M3" && \
	unzip -d data data/avocados.zip && \
	rm -f data/avocados.zip

mysql-create-user: ## Create a non-root MySQL user. Must have defined the environment variables in the .env file
	@ mysql -h ${MYSQL_HOST} -u ${MYSQL_ROOT_USER} -p${MYSQL_ROOT_PASSWORD} -e "CREATE USER '${MYSQL_USER}'@'localhost' IDENTIFIED BY '${MYSQL_PASSWORD}';"

mysql-create-schema: ## Create a `recipes` schema to use for the project and grant object access to the newly created user
	@ mysql -h ${MYSQL_HOST} -u ${MYSQL_ROOT_USER} -p${MYSQL_ROOT_PASSWORD} \
	-e "CREATE SCHEMA IF NOT EXISTS recipes; GRANT SELECT, INSERT, UPDATE, DELETE on recipes.* TO ${MYSQL_USER}@${MYSQL_HOST};"

mysql-drop-schema: ## Drop the `recipes` schema in case it needs to be recreated
	@ mysql -h ${MYSQL_HOST} -u ${MYSQL_ROOT_USER} -p${MYSQL_ROOT_PASSWORD} -e "DROP SCHEMA IF EXISTS recipes;"

mysql-create-tables: ## Create all the relevant tables and triggers in the `recipe` schema
	@ mysql -h ${MYSQL_HOST} -iu ${MYSQL_ROOT_USER} -p${MYSQL_ROOT_PASSWORD} recipes < src/queries/q_create_tables.sql

mysql-setup-schema: ## Drop the `recipe` schema if present and re-create it as well as the tables and the triggers
	$(MAKE) mysql-drop-schema && $(MAKE) mysql-create-schema && $(MAKE) mysql-create-tables

run-server-local: ## Run the REST API server locally
	@ poetry run python -m flask --app src/api/app.py run --debugger

get-all-recipes: ## Make an API request to get all the recipes
	@ curl -X GET -H "Content-Type: application/json" http://localhost:5000/recipes

get-all-ingredients: ## Make an API request to get all the ingredients
	@ curl -X GET -H "Content-Type: application/json" http://localhost:5000/ingredients

get-recipe-by-name: ## Make an API request to get a recipe by its name. Must specify recipe=<recipe-name>
	@ curl -X GET -H "Content-Type: application/json" \
	http://localhost:5000/recipes/$(shell sed -r 's/[^A-Za-z[:space:]]//g' <<< '$(recipe)' | sed -r -E 's/[[:space:]]+/_/g' | tr '[:upper:]' '[:lower:]')

post-recipe-by-name: ## Make an API request to post a recipe by its name. Must specify recipe=<recipe-name>
	@ curl -X POST -H "Content-Type: application/json" \
	-d "@$(shell sed -r 's/[^A-Za-z[:space:]]//g' <<< '$(recipe)' | sed -r -E 's/[[:space:]]+/_/g' | tr '[:upper:]' '[:lower:]').json" \
	http://localhost:5000/recipes/$(shell sed -r 's/[^A-Za-z[:space:]]//g' <<< '$(recipe)' | sed -r -E 's/[[:space:]]+/_/g' | tr '[:upper:]' '[:lower:]')

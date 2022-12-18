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
	@ mysql -h ${MYSQL_HOST} -u root -p${MYSQL_ROOT_PASSWORD} -e "CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'${MYSQL_HOST}' IDENTIFIED BY '${MYSQL_PASSWORD}';"

mysql-create-schema: ## Create a `recipes` schema to use for the project and grant object access to the newly created user
	@ mysql -h ${MYSQL_HOST} -u root -p${MYSQL_ROOT_PASSWORD} \
	-e "CREATE SCHEMA IF NOT EXISTS ${MYSQL_DATABASE}; GRANT SELECT, INSERT, UPDATE, DELETE on ${MYSQL_DATABASE}.* TO ${MYSQL_USER}@${MYSQL_HOST};"

mysql-drop-schema: ## Drop the `recipes` schema in case it needs to be recreated
	@ mysql -h ${MYSQL_HOST} -u root -p${MYSQL_ROOT_PASSWORD} -e "DROP SCHEMA IF EXISTS ${MYSQL_DATABASE};"

mysql-create-tables: ## Create all the relevant tables and triggers in the `recipe` schema
	@ mysql -h ${MYSQL_HOST} -iu root -p${MYSQL_ROOT_PASSWORD} ${MYSQL_DATABASE} < scripts/db/init.sql

mysql-setup-local: ## Drop the `recipe` schema if present and re-create it as well as the tables and the triggers
	$(MAKE) mysql-create-user && $(MAKE) mysql-drop-schema && $(MAKE) mysql-create-schema && $(MAKE) mysql-create-tables

run-server-local: ## Run the REST API server locally
	@ poetry run python -m flask --app src/api/app.py run --debugger

get-all-recipes: ## Make an API request to get all the recipes
	@ curl -X GET http://localhost:5000/recipes

get-all-ingredients: ## Make an API request to get all the ingredients
	@ curl -X GET http://localhost:5000/ingredients

get-recipe-by-name: ## Make an API request to get a recipe by its name. Must specify recipe=<recipe-name>
	@ curl -X GET \
	http://localhost:5000/recipes/$(shell export PYTHONPATH=${PWD} && poetry run python scripts/clean_string.py "$(recipe)")

get-recipes-by-ingredient: ## Make an API request to get all recipes given an ingredient. Must specify ingredient=<ingredient-name>
	@ curl -X GET http://localhost:5000/ingredients/$(shell export PYTHONPATH=${PWD} && poetry run python scripts/clean_string.py "$(ingredient)")/recipes

post-recipe-by-name: ## Make an API request to post a recipe by its name. Must specify recipe=<recipe-name>
	@ curl -X POST -H "Content-Type: application/json" \
	-d "@api_examples/post_$(shell export PYTHONPATH=${PWD} && poetry run python scripts/clean_string.py "$(recipe)").json" \
	http://localhost:5000/recipes/$(shell export PYTHONPATH=${PWD} && poetry run python scripts/clean_string.py "$(recipe)")

put-recipe-by-name: ## Make an API request to put (update) a recipe by its name. Must specify recipe=<recipe-name>
	@ curl -X PUT -H "Content-Type: application/json" \
	-d "@api_examples/put_$(shell export PYTHONPATH=${PWD} && poetry run python scripts/clean_string.py "$(recipe)").json" \
	http://localhost:5000/recipes/$(shell export PYTHONPATH=${PWD} && poetry run python scripts/clean_string.py "$(recipe)")

delete-recipe-by-name: ## Make an API request to delete a recipe by its name. Must sprcify recipe=<recipe-name>
	@ curl -X DELETE \
	http://localhost:5000/recipes/$(shell export PYTHONPATH=${PWD} && poetry run python scripts/clean_string.py "$(recipe)")

create-volume: ## Create a Docker volume where to persist the database tables when the DB container is shut down
	@ docker volume create db-data

build-compose: ## Build the Docker compose for the DB and the Flask App
	@ $(MAKE) create-volume && \
	docker compose --env-file .env build

run-compose: ## Run the Docker compose for the DB and the Flask APP
	@ $(MAKE) build-compose && 	docker compose --env-file .env up -d

mysql-setup-docker:
	@ docker exec -i mysqldb /bin/bash -c "mysql -iu root -p${MYSQL_ROOT_PASSWORD} ${MYSQL_DATABASE} < scripts/db/init.sql"

#!make
-include .env
export

help: ## Display this help screen
	@grep -h -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

pre-commit: ## Run the pre-commit over the entire repo
	@poetry run pre-commit run --all-files

download-data: ## Downloads the dataset inside the `data` folder
	@curl -o data/avocados.zip -L "https://drive.google.com/uc?export=download&id=1rhRzA2s44I8ASm_bMHnCpmAz_mNJQ7M3" && \
	unzip -d data data/avocados.zip && \
	rm -f data/avocados.zip

mysql-create-user: ## Create a MySQL user
	@ mysql -h localhost -u root -p${MYSQL_ROOT_PASSWORD} -e "CREATE USER '${MYSQL_USER}'@'localhost' IDENTIFIED BY '${MYSQL_PASSWORD}';"

mysql-create-schema:
	@ mysql -h localhost -u ${MYSQL_USER} -p${MYSQL_PASSWORD} -e "CREATE SCHEMA IF NOT EXISTS recipes;"

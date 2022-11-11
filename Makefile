#!make

help: ## Display this help screen
	@grep -h -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

pre-commit: ## Run the pre-commit over the entire repo
	@poetry run pre-commit run --all-files

download-data: ## Downloads the dataset inside the `data` folder
	@curl -o data/avocados.zip -L "https://drive.google.com/uc?export=download&id=1rhRzA2s44I8ASm_bMHnCpmAz_mNJQ7M3" && \
	unzip -d data data/avocados.zip && \
	rm -f data/avocados.zip

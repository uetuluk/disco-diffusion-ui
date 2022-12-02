help: ## display this help message
	@echo "Please use \`make <target>' where <target> is one of"
	@grep '^[a-zA-Z]' $(MAKEFILE_LIST) | sort | awk -F ':.*?## ' 'NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

client: ## access client
	SERVER_LOCATION=$(SERVER_LOCATION) python client.py

gui: ## Run Streamlit
	SERVER_LOCATION=$(SERVER_LOCATION) streamlit run gui.py

gui-custom-models: ## Run Streamlit with Custom Models
	SERVER_LOCATION=$(SERVER_LOCATION) CUSTOM_MODELS='true' streamlit run gui.py

install: ## Install Requirement
	pip install -r requirements.txt

install-dev: ## Install Requirement for Development
	pip install -r requirements.dev.txt

update-models: ## Get the latest model list
	wget https://raw.githubusercontent.com/jina-ai/discoart/main/discoart/resources/models.yml
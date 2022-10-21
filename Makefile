help: ## display this help message
	@echo "Please use \`make <target>' where <target> is one of"
	@grep '^[a-zA-Z]' $(MAKEFILE_LIST) | sort | awk -F ':.*?## ' 'NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

client: ## access client
	SERVER_LOCATION="https://disco-diffusion2.ritsdev.top" python client.py

gui: ## Run Streamlit
	SERVER_LOCATION="https://disco-diffusion2.ritsdev.top" streamlit run gui.py
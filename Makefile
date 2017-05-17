VE = run
VE_DIR = .tox/$(VE)

POSTGRES_URI := postgresql:///basic-auth


.PHONY: help
help:  ## Print help about available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


.PHONY: deps
deps:  ## Install dependencies
	sudo apt install -y tox postgresql-9.5


.PHONY: setup
setup: setup-db config.yaml  ## Setup config and database


.PHONY: setup-db
setup-db: $(VE_DIR) alembic.ini  ## Setup database
	./dev/setup-postgres
	$(MAKE) upgrade-db-schema


.PHONY: upgrade-db-schema
upgrade-db-schema: $(VE_DIR)  ## Upgrade database schema
	$(VE_DIR)/bin/alembic upgrade head


.PHONY: check-patches
check-patches: DUPLICATED_PATCH_NUMBERS := $(shell ls alembic/versions/*.py | \
	sed 's,.*/\([0-9]\+\)_.*,\1,' | sort -n | uniq -d)

check-patches:  ## Check for duplicated patches
	@if [ "$(DUPLICATED_PATCH_NUMBERS)" ]; then \
		echo "Duplicated patch number(s): $(DUPLICATED_PATCH_NUMBERS)"; \
		exit 1; \
	fi


.PHONY: db-revision
db-revision: $(VE_DIR)  ## Autogenerate database patch
	$(VE_DIR)/bin/alembic revision --autogenerate


alembic.ini: templates/alembic.ini
	@sed 's,{{ sqlalchemy_url }},$(POSTGRES_URI),' $< > $@


config.yaml: templates/config.yaml
	@sed -e 's,{{ db_dsn }},$(POSTGRES_URI),' $< > $@


$(VE_DIR):
	tox -e $(VE)

WITH_ENV = env `cat .env 2>/dev/null | xargs`

COMMANDS = help clean compile-deps pip lint test docs
.PHONY: $(COMMANDS)

help:
	@echo "commands: $(COMMANDS)"

clean:
	@find . -name '*.pyc' -type f -delete
	@find . -name '__pycache__' -type d -delete
	@find . -type d -empty -delete
	@rm -rf build dist htmlcov
	@rm -rf .cache

compile-deps:
	@pip-compile --output-file requirements/base.txt requirements/base.in
	@pip-compile --output-file requirements/dev.txt requirements/dev.in
	@pip-compile --output-file requirements/testing.txt requirements/testing.in

pip:
	@[ -n "$(VIRTUAL_ENV)" ] || (echo 'out of virtualenv'; exit 1)
	@pip install -U pip setuptools
	@pip install -r requirements/base.txt
	@pip install -r requirements/dev.txt
	@pip install -r requirements/testing.txt

lint:
	@echo "[\033[94mlint\033[0m] basic"
	@$(WITH_ENV) flake8
	@echo "[\033[94mlint\033[0m] complexity (warning only)"
	@$(WITH_ENV) flake8 --max-complexity=12 gelyung || true

test:
	@$(WITH_ENV) py.test tests

docs:
	@$(WITH_ENV) $(MAKE) -C docs html

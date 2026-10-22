HUGO ?= hugo
THEME_REPLACEMENT ?= github.com/pgsty/oink -> $(abspath ../oink)
RELEASE_ENV = env -u HUGO_MODULE_REPLACEMENTS GOWORK=off HUGO_MODULE_WORKSPACE=off HUGO_ENVIRONMENT=production HUGO_ENV=production

.PHONY: dev build build-local check check-local clean

dev:
	GOWORK=off HUGO_MODULE_WORKSPACE=off HUGO_MODULE_REPLACEMENTS='$(THEME_REPLACEMENT)' $(HUGO) server --renderToMemory

build:
	$(RELEASE_ENV) $(HUGO) build --minify --cleanDestinationDir

build-local:
	GOWORK=off HUGO_MODULE_WORKSPACE=off HUGO_MODULE_REPLACEMENTS='$(THEME_REPLACEMENT)' $(HUGO) build --minify --cleanDestinationDir

check:
	GOWORK=off go mod verify
	$(RELEASE_ENV) $(HUGO) build --minify --cleanDestinationDir --printPathWarnings --printI18nWarnings
	python3 bin/check_internal_links.py public

check-local:
	GOWORK=off HUGO_MODULE_WORKSPACE=off HUGO_MODULE_REPLACEMENTS='$(THEME_REPLACEMENT)' $(HUGO) build --minify --cleanDestinationDir --printPathWarnings --printI18nWarnings
	python3 bin/check_internal_links.py public

clean:
	$(HUGO) mod clean

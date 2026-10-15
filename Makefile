HUGO ?= hugo
THEME_REPLACEMENT ?= github.com/pgsty/oink -> $(abspath ../oink)

.PHONY: dev build build-local check check-local clean

dev:
	GOWORK=off HUGO_MODULE_WORKSPACE=off HUGO_MODULE_REPLACEMENTS='$(THEME_REPLACEMENT)' $(HUGO) server --renderToMemory

build:
	$(HUGO) build --minify --cleanDestinationDir

build-local:
	GOWORK=off HUGO_MODULE_WORKSPACE=off HUGO_MODULE_REPLACEMENTS='$(THEME_REPLACEMENT)' $(HUGO) build --minify --cleanDestinationDir

check:
	go mod verify
	$(HUGO) build --minify --cleanDestinationDir --printPathWarnings --printI18nWarnings --panicOnWarning
	python3 bin/check_internal_links.py public

check-local:
	GOWORK=off HUGO_MODULE_WORKSPACE=off HUGO_MODULE_REPLACEMENTS='$(THEME_REPLACEMENT)' $(HUGO) build --minify --cleanDestinationDir --printPathWarnings --printI18nWarnings --panicOnWarning
	python3 bin/check_internal_links.py public

clean:
	$(HUGO) mod clean

BINARY := ai-harness
PKG := ./cmd/ai-harness

.DEFAULT_GOAL := help

.PHONY: help build test vet fmt install

help: ## List available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

build: ## Compile the ai-harness binary into the current directory
	go build -o $(BINARY) $(PKG)

test: ## Run the full test suite
	go test ./...

vet: ## Run go vet across all packages
	go vet ./...

fmt: ## Format all Go sources in place
	gofmt -w .

install: ## Install the ai-harness binary onto PATH (bootstrap; then run `ai-harness install`)
	go install $(PKG)

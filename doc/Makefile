NPM_BIN = node_modules/.bin
OUTPUT = output

doc:
	$(NPM_BIN)/bootprint openapi swagger.yaml $(OUTPUT)
	$(NPM_BIN)/html-inline -i $(OUTPUT)/index.html -o api.html
	rm -rf $(OUTPUT)

setup:
	sudo apt install -y nodejs nodejs-legacy npm
	npm install bootprint bootprint-openapi html-inline

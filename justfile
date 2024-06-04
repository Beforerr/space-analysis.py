import "files/quarto.just"

default:
  just --list

ensure_env:
  pre-commit install

update:
  git add .
  -git commit -am "update"
  git push

publish: pypi-publish quarto-publish

pypi-publish: export
  pdm publish
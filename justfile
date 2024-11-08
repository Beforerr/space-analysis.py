import "files/quarto.just"

default:
    just --list

ensure-env:
    pixi install
    pre-commit install

update:
    git add .
    -git commit -am "update"
    git push

publish: quarto-publish pypi-publish

pypi-publish: export
    pdm publish

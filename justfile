export:
  nbdev_export
  
preview: export
  nbdev_preview

publish: export
  nbdev_proc_nbs && cd _proc && quarto publish gh-pages --no-prompt

env-create:
  micromamba env create -f environment.yml

env-update: export
  micromamba install --file environment.yml
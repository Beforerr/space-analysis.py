publish: export
  
preview: export
  nbdev_preview

export:
  nbdev_export

env-create:
  micromamba env create -f environment.yml

env-update:
  micromamba install --file environment.yml
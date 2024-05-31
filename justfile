update: export
  git add .
  -git commit -am "update"
  git push

export:
  nbdev_export
  
preview: export
  nbdev_preview

publish: export
  nbdev_readme
  nbdev_proc_nbs && cd _proc && quarto publish gh-pages --no-prompt
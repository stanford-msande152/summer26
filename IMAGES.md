# IMAGES

Posting image links in md files so that they render properly in the gihub.io static pages face a few compatibility issues.  The standard wisdom to use html embedings with \<img> tags does not work on the webpage display.  

The options are to use 

- Obsidian style \!\[[   ]] embeddings, 
- Standard markdown \!\[  ](  ) embeddings
- <img=> embeddings.

Then the question is how they display in the different editors, Obsidian, VS Code preview, in Github web preview and on the webpage. 

_The best choice is to create standard markdown embeddings by dragging files into an Obsidian document._ Obsidian will create the correct relative path for image files. This works for both svg and png format images, but it will not render svg files properly in github file preview. Obsidian may "html convert" file names with embedded spaces.  These will not render on github.io

__This choice does work for github.io static pages. Therefore it is recommended___

Excalidraw will sometimes (?) create an equivalent markdown file for drawings.  These need to be converted to png for display. 

Some of these choices may depend on the extensions included in VS Code or Obsidian. 


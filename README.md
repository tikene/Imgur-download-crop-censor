When you specify an Imgur link, it will be downloaded and cropped according to the dimensions you specify (height/width).

![imgcrop1](https://user-images.githubusercontent.com/92279236/137273810-5c9a823e-4dea-4394-bc76-3f394b65a041.png)

This is useful because it allows users to post these images in social media platforms where only some specific dimensions are accepted, such as Instagram or Twitter.

![imagecrop1](https://user-images.githubusercontent.com/92279236/137273616-62f2637d-574f-4a04-aad0-972f384e4d8b.png)

It can also detect any slurs using ProfanityFilter module and censor them using a random image from the "Censor Images" folder.

![imgcrop2](https://user-images.githubusercontent.com/92279236/137273917-c7eda3d5-2f10-4154-a91e-1f3f2db1a8b8.png)

You can press enter at any time to use the default settings, which can be changed by editing the code

Imgur links use the following format: https://imgur.com/gallery/xxxxxxx


Installation:
- Install the required modules: "pip install python-slugify"... 
- Download language file for profanity detecton "python -m spacy download en"
- Download Imagemagick (make sure it's in the system path) https://docs.wand-py.org/en/0.4.1/guide/install.html

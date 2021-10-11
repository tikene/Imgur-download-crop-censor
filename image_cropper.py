from colorama import init, Fore, Style, Back
from PIL import Image
from time import sleep
from math import ceil
from slugify import slugify
import pytesseract
from pytesseract import Output
import json
import time
import zipfile
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from fake_headers import Headers
from random import randint, choices
from profanity_filter import ProfanityFilter
import requests
import string
import cv2
import os
import re

pf = ProfanityFilter()
init(convert=True)
init(autoreset=True)

bright = Style.BRIGHT
dim = Style.DIM
red = Fore.RED + dim
green = Fore.GREEN + dim
cyan = Fore.CYAN + dim
yellow = Fore.LIGHTYELLOW_EX + dim
blue = Fore.BLUE + dim
white = Fore.WHITE + dim
magenta = Fore.MAGENTA + dim

DEFAULT_LINK = "https://imgur.com/gallery/kr0Ip7x"
CENSOR_IMG_FOLDER = "Censor Images"
defaultMaxHeight = 700
defaultWidthPercentage = 100

def findBadWord(imagesFolder):

    found_bad_words = False
    print(cyan + "\n\nLooking for meanie words to censor\n")

    for imgName in os.listdir(imagesFolder):

        cock = time.time()
        imgPath = os.path.join(imagesFolder, imgName)
        img = Image.open(imgPath)
        d = pytesseract.image_to_data(img, output_type=Output.DICT)

        longitud = len(d["text"])
        censor_count = 0

        for word in range(0, longitud):
            confidence_level = d["conf"][word]
            found_text = d["text"][word]

            if int(confidence_level) <= 30:
                # Si no está nada seguro de que sea una palabra
                continue
            elif not found_text.isalpha() and not "'" in found_text:
                # Si contiene numeros o simbolos no va a detectar tacos, excepto si es '
                continue
            elif len(found_text) < 3:
                # No creo que existan muchos tacos de 1-2 letras
                continue
            elif pf.is_clean(found_text):
                # Palabra meanie detectada
                continue
            # Invertí demasiado tiempo libre en optimizar esto. Ahora tarda un 30% menos tho - 2 segundos

            print("  - " + found_text)

            # solo seleccionar letras de posicion
            # https://nanonets.com/blog/ocr-with-tesseract/#detectonlydigits

            initial_censor_width = int(d['width'][word])
            initial_censor_height = int(d['height'][word])
            new_censor_width = int(initial_censor_width * 0.75)
            new_censor_height = int(initial_censor_height * 0.75)

            x_axis = d['left'][word]
            y_axis = d['top'][word]

            new_x_axis = int(x_axis + (new_censor_width / 2))
            new_y_axis = int(y_axis + (new_censor_height / 2))
            newsize = (new_censor_width, new_censor_height)

            allCensorImg = os.listdir(CENSOR_IMG_FOLDER)
            randomNum = randint(0, len(allCensorImg) - 1)
            randomImgPath = os.path.join(CENSOR_IMG_FOLDER, allCensorImg[randomNum])
            randomImg = Image.open(randomImgPath)

            emoji = randomImg.resize(newsize)
            img.paste(emoji, (new_x_axis, new_y_axis))

            censor_count += 1
            # Añadir censura de imagenes, que busque colores distintos por la pantalla pa detectar imagen

        if censor_count > 0:
            img.save(imgPath)
            finaltime = time.time() - cock
            print(yellow + " > Censored " + str(censor_count) + " words from " + imgName + " [" + str(round(finaltime, 2)) + "s]\n")


def cropImages(folderPath, widthPercentage, maxHeight, censorImages):

    count = 0
    initialDimensions = {}

    print(yellow + "\nSplitting images - Max height: " + blue + str(maxHeight))

    for subFile in os.listdir(folderPath):

        imgPath = os.path.join(folderPath, subFile)

        if os.path.isdir(imgPath):
            continue

        image = Image.open(imgPath)
        width, height = image.size
        image.close()

        initialDimensions[subFile] = {"width": width, "height": height}

        if height <= 700:
            toPercentage = 100
        else:
            imgParts = ceil(height / maxHeight)
            newHeight = height / imgParts
            toPercentage = 100 / imgParts
            #print(yellow + "The image will be divided in " + white + str(imgParts) + yellow + " parts")

        newWidth = widthPercentage

        #print(yellow + "Cropping height '" + white + subFile + yellow + "' - " + white + str(width) + "x" + str(height) + " -> " + str())

        file_name = os.path.splitext(subFile)[0]
        new_folder = os.path.join(folderPath, file_name)

        if not os.path.exists(new_folder):
            os.mkdir(new_folder)

        new_path = os.path.join(new_folder, subFile)

        os.system("convert -background none -crop 100%x" + str(toPercentage) + "% +repage " + imgPath + " " + new_path)

        for img_file in os.listdir(new_folder):
            # Delete small images
            img_loc = os.path.join(new_folder, img_file)
            image = Image.open(img_loc)
            width, height = image.size
            image.close()

            if width <= 20 or height <= 20:
                os.remove(img_loc)

        count += 1

    print(green + " > Done")

    # cutre pero pereza, ahora resize width
    if widthPercentage != 100:

        print(yellow + "\nReducing width by " + blue + str(100 - widthPercentage) + "%")
        count = 0

        for subFile in os.listdir(folderPath):

            subSubFolder = os.path.join(folderPath, subFile)

            if not os.path.isdir(subSubFolder):
                continue

            for file in os.listdir(subSubFolder):
                processedFile = os.path.join(subSubFolder, file)

                image = Image.open(processedFile)
                width, height = image.size
                image.close()

                if width <= 30 or height <= 30:
                    #print("Skipping " + file)
                    os.remove(processedFile)
                    continue

                os.system("convert -background none -extent " + str(widthPercentage) + "%x100%+0+0 \"" + processedFile + "\" " + processedFile)
                count += 1

        print(green + " > Done")

    # venga mas loops di q si no se como hacer que imagemagick returnee las imagenes creadas
    for subFile in os.listdir(folderPath):

        subSubFolder = os.path.join(folderPath, subFile)

        if not os.path.isdir(subSubFolder):
                continue

        list_dir = os.listdir(subSubFolder)
        file = list_dir[0]
        processedFile = os.path.join(subSubFolder, file)
        filename, ext = os.path.splitext(file)
        remove_ending = filename[:filename.rfind('-')] + ext

        try:
            initial_width = initialDimensions[remove_ending]["width"]
            initial_height = initialDimensions[remove_ending]["height"]
        except:
            # si la imagen no fue cropeada en partes
            initial_width = initialDimensions[filename]["width"]
            initial_height = initialDimensions[filename]["height"]
            remove_ending = file

        image = Image.open(processedFile)
        new_width, new_height = image.size
        image.close()

        print("\n" + magenta + bright + remove_ending + white + " was split into " + magenta + bright + str(len(list_dir)) + white + " parts")
        print(white + " New dimensions: " + blue + bright + str(initial_width) + "x" + str(initial_height) + white + " -> " + cyan + bright + str(new_width) + "x" + str(new_height))

        if censorImages:
            found = findBadWord(subSubFolder)

    print(yellow + "\n\nDone processing - press enter to return to the menu\n")
    input()
    main()

def downloadAlbum(albumUrl, widthPercentage, maxHeight, censorImages):


    headers = Headers(os="win", headers=True).generate()
    r = requests.get(albumUrl, headers=headers)

    print(yellow + "\n\nDownloading album from Imgur [" + str(r.status_code) + "]...\n")

    soup = BeautifulSoup(r.text, 'lxml')

    for element in soup.find_all('script'):

        found = re.search(r'<script>window.postDataJSON="(.*?)"</script>', str(element))

        if not found:
            continue

        parsedJson = found.group(1).replace("\\", "")
        parsedJson = json.loads(parsedJson)

        album_name = slugify(parsedJson["title"])

        if not os.path.exists(album_name):
            os.mkdir(album_name)
        else:
            for file in os.listdir(album_name):
                cur_file = os.path.join(album_name, file)

                if not os.path.isdir(cur_file):
                    os.remove(cur_file)

        count = 0
        for x in parsedJson["media"]:

            url = x["url"]
            id = x["id"]

            resp = requests.get(url, stream=True)

            filename, file_extension = os.path.splitext(url)
            new_file = slugify(album_name) + file_extension
            new_file_path = os.path.join(album_name, new_file)

            if os.path.exists(new_file_path):   # Para imagenes con mismo titulo
                new_file = slugify(album_name + "-" + id) + file_extension
                new_file_path = os.path.join(album_name, new_file)

            with open(new_file_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=1024):
                    f.write(chunk)

            print(green + "Downloaded " + white + bright + album_name)

        cropImages(album_name, widthPercentage, maxHeight, censorImages)


def main():

    os.system("cls")
    os.system("title Automatic image downloader and cropper")

    print(Back.MAGENTA + bright + "\n\nAutomatic image downloader & cropper\n\n")

    link = input("> Imgur album link: ")

    if link == "":
        link = DEFAULT_LINK

    widthPercentage = input("> Width percentage: ")
    if widthPercentage == "":
        widthPercentage = defaultWidthPercentage
    widthPercentage = int(widthPercentage)

    maxHeight = input("> Max height: ")
    if maxHeight == "":
        maxHeight = defaultMaxHeight
    maxHeight = int(maxHeight)

    censorImages = input("> Censor images? (y/n): ")
    if censorImages == "y" or censorImages == "yes":
        censorImages = True
    else:
        censorImages = False

    downloadAlbum(link, widthPercentage, maxHeight, censorImages)

main()

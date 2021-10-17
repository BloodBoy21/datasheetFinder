
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

server = "https://www.electronicsdatasheets.com"
fullPath = ""
requestError = False


def get_soup(url):
    """
    Function to get data from a web page

    Args:
        url (String): URl to scrapping data

    Returns:
        BeautifulSoup: Object with web page data
    """
    global requestError
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.text,  features="html.parser")
    except Exception:
        requestError = True
    return soup


def get_elements():
    """[summary]

    Returns:
        [type]: [description]
    """
    userInput = input("Search:")
    url = f"{server}/search/?query={userInput}&source=header"
    try:
        soup = get_soup(url)
        itemsTable = soup.find("div", {"class": "col-md-8 col-sm-pull-right"}
                               ).find_all("div", {"class": "row"}, recursive=False)
        itemsFrame = []
        for item in itemsTable:
            itemsDivs = item.find_all(
                "div", {"class": "col-xs-12 col-sm-6 col-md-12"}, recursive=False)
            for itemDiv in itemsDivs:
                itemRows = itemDiv.find("div", {"class": "white-background result-box"}).find_all(
                    "div", {"class": "row"}, recursive=False)
                itemData = itemRows[0].find(
                    "div", {"class": "col-md-7 col-sm-12"})
                if itemData is None:
                    itemData = itemRows[0].find(
                        "div", {"class": "col-md-10 col-sm-12"})
                partName = itemData.find("span").text
                brand = itemData.find("a", recursive=False).text
                link = itemRows[1].find("a")["href"]
                itemsFrame.append([brand, partName, link])
    except Exception:
        pass
    return itemsFrame


def save_file(path, data):
    global fullPath
    if path == "":
        path = r"D:/datasheetFinder/"
    if not os.path.exists(path):
        os.makedirs(path)
    fullPath = os.path.join(path, data["filename"])
    open(fullPath, "wb").write(data["data"])


def download_pdf(pdfName, url):
    soup = get_soup(url)
    itemData = soup.find("div", {
                         "class", "section-float-right top-download-box mobile-central tablet-central"}).find("div", {"class": "white-background info-box"}).find("div", {"class": "row"}).find("div", {"class": "col-xs-6"})
    link = itemData.find("a")["href"]
    if link.startswith("/download"):
        link = server+link
    elif link.endswith("#datasheet"):
        link = soup.find(
            "a", {"class": "button button-dark-blue button-full-width"})["href"]
    try:
        pdf = requests.get(link)
        if pdf.ok:
            data = {"filename": f"{pdfName}.pdf", "data": pdf.content}
            path = input("Default path:~/datahsheets/\nEnter path to save:")
            save_file(path, data)
            print("Datasheet download finished")
        else:
            print("Datasheet download failed")
    except Exception as e:
        print(e)
        print("Datasheet not found")


if __name__ == "__main__":
    itemsFrame = get_elements()
    if not requestError:
        df = pd.DataFrame(itemsFrame, columns=["Brand", "Part", "Link"])
        print(df)
        itemToDownload = int(input("Item to download:"))
        url = itemsFrame[itemToDownload][2]
        pdfName = itemsFrame[itemToDownload][1]
        download_pdf(pdfName, url)
        openFile = input("Open file(y/n)?(defaul n):")
        if openFile.lower() == "y":
            os.system(fullPath)

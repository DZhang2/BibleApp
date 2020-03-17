from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from bs4 import BeautifulSoup
import requests
import re
import sys
from PyQt5.QtWidgets import *

# export GOOGLE_APPLICATION_CREDENTIALS="/Users/davidzhang/Desktop/Python/Bible/MyFirstProject.json"  
class ScrapedBible(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scraped Bible")
        self.layout = QVBoxLayout()
        formlayout = QFormLayout()
        self.book = QLineEdit()
        self.chapter = QLineEdit()
        self.verse = QLineEdit()
        formlayout.addRow("Book", self.book)
        formlayout.addRow("Chapter", self.chapter)
        formlayout.addRow("Verse", self.verse)
        verseButton1 = QPushButton("Get Verse (ESV)")
        verseButton1.clicked.connect(lambda: print(self.getVerseESV(self.book.text(), self.chapter.text(), int(self.verse.text()))))
        verseButton2 = QPushButton("Get Verse (KJV)")
        verseButton2.clicked.connect(lambda: print(self.getVerseKJV(self.book.text(), self.chapter.text(), int(self.verse.text()))))
        sentimentButton1 = QPushButton("Get Sentiment (ESV)")
        sentimentButton1.clicked.connect(lambda: self.getSentimentESV(self.book.text(), self.chapter.text(), int(self.verse.text())))
        sentimentButton2 = QPushButton("Get Sentiment (KJV)")
        sentimentButton2.clicked.connect(lambda: self.getSentimentKJV(self.book.text(), self.chapter.text(), int(self.verse.text())))

        self.layout.addLayout(formlayout)
        self.layout.addWidget(verseButton1)
        self.layout.addWidget(verseButton2)
        self.layout.addWidget(sentimentButton1)
        self.layout.addWidget(sentimentButton2)
        self.setLayout(self.layout)

    def getChapterESV(self, book, chapter):
        page = requests.get('https://www.biblestudytools.com/esv/' + book + '/' + chapter + '.html')
        soup = BeautifulSoup(page.content, 'html.parser')
        n = 20      #number of verses to parse through **cannot go over**
        verses = []
        for i in range(n):     #first 20 verses
            verses.append(soup.find(class_ = ('verse-' + str(i+1))).getText())
            verses[i] = re.sub(r'\s+', ' ', verses[i])      #removing extra whitespace/newline chars
            verses[i] = verses[i].replace('["\']', '')      #removing single and double quotes
            verses[i] = re.sub('[0-9]', '', verses[i])      #removing digits
        return verses

    def getChapterKJV(self, book, chapter):
        page = requests.get('https://www.biblestudytools.com/kjv/' + book + '/' + chapter + '.html')
        soup = BeautifulSoup(page.content, 'html.parser')
        n = 20 
        verses = []
        for i in range(n):
            verses.append(soup.find(class_ = ('verse-' + str(i+1))).getText())
            verses[i] = re.sub(r'\s+', ' ', verses[i])
            verses[i] = verses[i].replace('["\']', '') 
            verses[i] = re.sub('[0-9]', '', verses[i])
        return verses

    def getVerseESV(self, book, chapter, verse):
        page = requests.get('https://www.biblestudytools.com/esv/' + book + '/' + chapter + '.html')
        soup = BeautifulSoup(page.content, 'html.parser')   
        result = soup.find(class_ = ('verse-' + str(verse))).getText()
        result = re.sub(r'\s+', ' ', result)
        result = re.sub('["\'0-9]', '', result) 
        return result

    def getVerseKJV(self, book, chapter, verse):
        page = requests.get('https://www.biblestudytools.com/kjv/' + book + '/' + chapter + '.html')
        soup = BeautifulSoup(page.content, 'html.parser')   
        result = soup.find(class_ = ('verse-' + str(verse))).getText()
        result = re.sub(r'\s+', ' ', result)
        result = re.sub('["\'0-9]', '', result) 
        return result

    def getSentimentESV(self, book, chapter, verse):
        client = language.LanguageServiceClient()
        text = self.getVerseESV(book, chapter, verse)
        document = types.Document(
            content=text,
            type=enums.Document.Type.PLAIN_TEXT)

        sentiment = client.analyze_sentiment(document=document).document_sentiment

        score = round(sentiment.score, 4)
        mag = round(sentiment.magnitude, 4)
        label = QLabel('Sentiment for {} {}:{} (ESV) => {}, {}'.format(book, chapter, verse, score, mag))
        self.layout.addWidget(label)

    def getSentimentKJV(self, book, chapter, verse):
        client = language.LanguageServiceClient()
        text = self.getVerseKJV(book, chapter, verse)
        document = types.Document(
            content=text,
            type=enums.Document.Type.PLAIN_TEXT)

        sentiment = client.analyze_sentiment(document=document).document_sentiment

        score = round(sentiment.score, 4)
        mag = round(sentiment.magnitude, 4)
        label = QLabel('Sentiment for {} {}:{} (KJV) => {}, {}'.format(book, chapter, verse, score, mag))
        self.layout.addWidget(label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    Bible = ScrapedBible()
    Bible.show()
    sys.exit(app.exec())
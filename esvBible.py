from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from PyQt5.QtWidgets import *
import requests
import sys
import pyttsx3
import re

# export GOOGLE_APPLICATION_CREDENTIALS="/Users/davidzhang/Desktop/Python/Bible/MyFirstProject.json"
API_KEY = 'b0d192dbd47d526d64782227b6a18bdf51169cb8'
API_URL = 'https://api.esv.org/v3/passage/text/'
class EsvBible(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ESV Bible')
        self.layout = QVBoxLayout()
        formlayout = QFormLayout()
        self.book = QLineEdit()
        self.chapter = QLineEdit()
        self.verse = QLineEdit()
        formlayout.addRow("Book", self.book)
        formlayout.addRow("Chapter/s", self.chapter)
        formlayout.addRow("Verse/s", self.verse)
        verseButton = QPushButton("Get Passage")
        verseButton.clicked.connect(lambda: print(self.get_esv_text_nums(self.book.text() + self.chapter.text() + ":" + self.verse.text()) + "\n"))
        sentimentButton = QPushButton("Get Sentiment")
        sentimentButton.clicked.connect(lambda: self.getSentiment(self.book.text() + self.chapter.text() + ":" + self.verse.text()))
        maxSent = QPushButton("Max Sentiment")
        maxSent.clicked.connect(lambda: self.maxSentiment(self.book.text(), self.chapter.text()))
        audioButton = QPushButton("Play Audio")
        audioButton.clicked.connect(lambda: self.get_audio(self.book.text() + self.chapter.text() + ":" + self.verse.text()))

        self.sentiment_verses = []
        self.num = -1
        self.sentiment_storage = []

        self.layout.addLayout(formlayout)
        self.layout.addWidget(verseButton)
        self.layout.addWidget(sentimentButton)
        self.layout.addWidget(maxSent)
        self.layout.addWidget(audioButton)
        self.setLayout(self.layout)

    def get_esv_text(self, passage):      #verse
        params = {
            'q': passage,
            'include-headings': False,
            'include-footnotes': False,
            'include-verse-numbers': False,
            'include-short-copyright': False,
            'include-passage-references': False
        }
        headers = {
            'Authorization': 'Token %s' % API_KEY
        }
        response = requests.get(API_URL, params=params, headers=headers)
        passages = response.json()['passages']
        return passages[0].strip() if passages else 'Error: Passage not found'

    def get_esv_text_nums(self, passage):      #verse with verse numbers
        params = {
            'q': passage,
            'include-headings': False,
            'include-footnotes': False,
            'include-verse-numbers': True,
            'include-short-copyright': False,
            'include-passage-references': False
        }
        headers = {
            'Authorization': 'Token %s' % API_KEY
        }
        response = requests.get(API_URL, params=params, headers=headers)
        passages = response.json()['passages']
        return passages[0].strip() if passages else 'Error: Passage not found'

    def get_audio(self, passage):
        text = self.get_esv_text(passage)
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[7].id)       #names: Alex, Daniel, Fred, (0, 7, 11)
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate-200)     #default 200 rate
        engine.say(text)
        engine.runAndWait()

    #args to specify verse text outside of using verse.text from gui when calculating maxSentiment
    def getSentiment(self, passage, *args):      
        client = language.LanguageServiceClient()
        text = self.get_esv_text(passage)
        document = types.Document(
            content=text,
            type=enums.Document.Type.PLAIN_TEXT)

        sentiment = client.analyze_sentiment(document=document).document_sentiment

        score = round(sentiment.score, 4)
        mag = round(sentiment.magnitude, 4)
        verse_text = self.verse.text()
        if len(args) != 0:
            verse_text = args[0]
        label = QLabel('Sentiment for {} {}:{} => {}, {}'.format(self.book.text(), self.chapter.text(), verse_text, score, mag))
        self.layout.addWidget(label)
        return score

    def getSentiment_phrase(self, passage, arr, *args):
        client = language.LanguageServiceClient()
        text = passage
        document = types.Document(
            content=text,
            type=enums.Document.Type.PLAIN_TEXT)

        sentiment = client.analyze_sentiment(document=document).document_sentiment

        score = round(sentiment.score, 4)
        mag = round(sentiment.magnitude, 4)
        verse_text = self.verse.text()
        if len(args) != 0:
            verse_text = args[0]
        arr.append('Sentiment for {} {}:{} => {}, {}'.format(self.book.text(), self.chapter.text(), verse_text, score, mag))
        return score

    def maxSentiment(self, book, chapter):
        verses = self.get_esv_text_nums(book+chapter)
        verses = re.sub('\[\d+\] ', 'zzz', verses.strip())
        verses = verses.split('zzz')    #empty "" at index 0
        self.sentiment_verses.append(verses)
        arr = []
        total_score = 0
        score = self.getSentiment_phrase(verses[1], arr, '1')
        total_score += score
        max_verse, min_verse = ['1'], ['1']
        max_score, min_score = score, score
        for i in range(2, len(verses)):
            score = self.getSentiment_phrase(verses[i], arr, str(i))
            total_score += score
            if score > max_score:
                max_score = score
                max_verse.clear()
                max_verse.append(str(i))
            elif score < min_score:
                min_score = score
                min_verse.clear()
                min_verse.append(str(i))
            elif score == max_score:
                max_verse.append(str(i))
            elif score == min_score:
                min_verse.append(str(i))
        max_verse_string = ",".join(max_verse)
        min_verse_string = ",".join(min_verse)
        print(f"Max Sentiment is {book} {chapter}:{max_verse_string} => {max_score}\n")
        for maxverse in max_verse:
            verse = verses[int(maxverse)]
            print(f'[{maxverse}] {verse.strip()}\n')
        print(f"Min Sentiment is {book} {chapter}:{min_verse_string} => {min_score}\n")
        for minverse in min_verse:
            verse = verses[int(minverse)]
            print(f'[{minverse}] {verse.strip()}\n')
        print(f"Avg Sentiment per verse is {round((total_score/(len(verses)-1)),2)}")
        self.sentimentBox = QComboBox()
        self.sentimentBox.addItems(arr)
        self.sentiment_storage.append(self.sentimentBox)
        self.num += 1
        outdex = self.num
        sent_index = len(self.sentiment_storage) - 1
        self.sentimentBox.currentIndexChanged.connect(lambda: self.verseClicked(outdex, sent_index))
        self.layout.addWidget(self.sentimentBox)

    def verseClicked(self, outdex, sent_index):
        index = self.sentiment_storage[sent_index].currentIndex() + 1
        print(f'[{index}] {self.sentiment_verses[outdex][index]}')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    Bible = esvBible()
    Bible.show()
    sys.exit(app.exec())
import discord
from googlesearch import search
from bs4 import BeautifulSoup
import requests
import nltk
import string
import math
from heapq import nlargest
nltk.download('stopwords')
nltk.download('punkt')


def Summary(text):
    if text.count(". ") > 20:
        length = int(round(text.count(". ")/10, 0))
    else:
        length = 1

    nopuch =[char for char in text if char not in string.punctuation]
    nopuch = "".join(nopuch)

    processed_text = [word for word in nopuch.split() if word.lower() not in nltk.corpus.stopwords.words('english')]

    word_freq = {}
    for word in processed_text:
        if word not in word_freq:
            word_freq[word] = 1
        else:
            word_freq[word] = word_freq[word] + 1

    max_freq = max(word_freq.values())
    for word in word_freq.keys():
        word_freq[word] = (word_freq[word]/max_freq)

    sent_list = nltk.sent_tokenize(text)
    sent_score = {}
    for sent in sent_list:
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_freq.keys():
                if sent not in sent_score.keys():
                    sent_score[sent] = word_freq[word]
                else:
                    sent_score[sent] = sent_score[sent] + word_freq[word]

    summary_sents = nlargest(length, sent_score, key=sent_score.get)
    summary = " ".join(summary_sents)
    return summary


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        if message.author == self.user:
            return
        UserMessage = message.content.split()
        if len(UserMessage) > 2:
            if UserMessage[0].lower() == 'scrape':
                args = " ".join(UserMessage[2:])
                try:
                    SearchNumber = int(UserMessage[1])
                except ValueError:
                    await message.channel.send("Please Enter a Valid Search Number")
                    return
                SearchResults = []
                InformationResults = []
                for j in search(args, tld="co.in", num=SearchNumber, stop=SearchNumber, pause=1):
                    if "jpg" not in j:
                        r = requests.get(j).text
                        soup = BeautifulSoup(r, "html.parser")
                        if soup.title is not None:
                            SearchResults.append(f'{soup.title.text} <{j}>')
                        for para in soup.find_all("p"):
                            a = para.get_text()
                            if len(a) > 20 and a is not None:
                                InformationResults.append([Summary(a), soup.title.text])
                print(InformationResults)
                EmbedArray = []
                Information = ""
                counter = 0
                embedVar = discord.Embed(title=InformationResults[0][1], color=0x00ff00)
                for i in range(len(InformationResults)):
                    if i == 0:
                        Source = InformationResults[i][1]
                    else:
                        Source = InformationResults[i-1][1]
                    if counter == 5 or InformationResults[i][1] != Source:
                        counter = 0
                        await message.channel.send(embed=embedVar)
                        embedVar = discord.Embed(title=InformationResults[i][1], color=0x00ff00)
                    if len(Information + "\n\n- " + InformationResults[i][0]) > 1024:
                        embedVar.add_field(name="\u200b", value=Information, inline=False)
                        Information = ""
                        counter += 1
                    else:
                        Information += "\n\n- " + InformationResults[i][0]



                if len(UserMessage) > 2:
                    #[await message.channel.send(embed=i) for i in EmbedArray]
                    await message.channel.send("\n".join(SearchResults))
                else:
                    await message.channel.send("Please enter valid arguments")


client = MyClient()
client.run('OTI1ODc0NzU3NTI0NjY4NDg2.YczeEA.wBtWQjGd7SwFrfokwh3BjT1psEs')

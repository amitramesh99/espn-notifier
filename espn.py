from bs4 import BeautifulSoup
import os
import requests
import time
from pprint import pprint


def notify(title, subtitle, message):
    t = '-title {!r}'.format(title)
    s = '-subtitle {!r}'.format(subtitle)
    m = '-message {!r}'.format(message)
    os.system('terminal-notifier {}'.format(' '.join([m, t, s])))

class Play(object):

    def __init__(self, time, score, details):
        self.time = time
        self.score = score
        self.details = details

    def __str__(self):
        outString = "%s: (%s) %s" % (self.time, self.score, self.details)

    def notify(self):
        notify(game.title, "%s (%s)" % (self.time, self.score), self.details)

class Game(object):

    def __init__(self, url):
        self.url = url
        self.gameId = (url.split("gameId="))[1]
        self.data = self.getGamedata()
        # self.soup init
        self.teams = self.soup.select('.team-name .short-name')
        self.title = "%s vs. %s" % (self.teams[0], self.teams[1])
        self.status = self.soup.select('.game-status .game-time')[0].text
        # fix
        self.isOver = True if self.status == "Final" else False

    def getGamedata(self):
        print "loading game %s" % self.gameId
        self.soup = BeautifulSoup(requests.get(gameURL, headers={'User-Agent': 'Mozilla/5.0'}).text, 'html.parser')
        print "game loaded"
        self.status = self.soup.select('.game-status .game-time')[0].text
        # fix
        self.isOver = True if self.status == "Final" else False

        playTable = self.soup.find('div', {'id':'gamepackage-qtrs-wrap'})
        quarters = playTable.select('.accordion-item')
        gameData = []
        for index, quarter in enumerate(reversed(quarters)):
            gameData.append([])
            plays = quarter.select('table tr')
            for play in reversed(plays[1:]):
                gameData[index].append(
                    Play(
                        str(play.select('.time-stamp')[0].text),
                        str(play.select('.combined-score')[0].text),
                        str(play.select('.game-details')[0].text)
                    )
                )

        return gameData

    def loadNewData(self):
        newGameData = self.getGamedata()
        newPlays = []
        Data_lastQuarterPos = len(self.data)-1

        for i in xrange(len(newGameData[Data_lastQuarterPos])-len(self.data[-1])):
            newPlays.append(newGameData[Data_lastQuarterPos][len(self.data[-1])+i])

        for i in xrange(len(newGameData)-len(self.data)):
            for play in newGameData[len(self.data)+i]:
                newPlays.append(play)

        if len(newPlays) > 0:
            print newPlays[-1]
            newPlays.notify()
        self.data = newGameData


# test game
gameURL = "http://espn.go.com/nba/playbyplay?gameId=400828867"
game = Game(gameURL)
game.data[-1][-1].notify()
while not game.isOver:
    time.sleep(60)
    game.loadNewData()
notify(game.title,game.data[-1][-1].score,"The Game has ended")

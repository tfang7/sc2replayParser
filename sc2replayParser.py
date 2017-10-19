#from sc2reader.factories import SC2Factory
import sc2reader
from sc2reader.factories import SC2Factory
from playerData import Player
from sc2reader.engine.plugins import APMTracker
import os
from os import listdir
import argparse
from shutil import copyfile

#Player object contained in player dictionary
class Player(object):
	name = ""
	wins = 0
	losses = 0
	winPerc = 0.0
	matchups = []
	race = ""
	avgTime = 0
	hasPlayed = {}
	def __init__(self):
		name = "unnamed"
		self.hasPlayed = {}
		self.avgTime = [0,0]
		self.wins = 0
	def addPlayed(self, other):
		if other in self.hasPlayed:
			self.hasPlayed[other] += 1
		else:
			self.hasPlayed[other] = 1
	def addTime(self, time):
		parsedTime = str(time).split(".")
		#Avg time [Minutes, Seconds], adds time from all games, averages them later
		self.avgTime[0] += int(parsedTime[0])
		if (self.avgTime[1] + int(parsedTime[1]) >= 60):
			self.avgTime[0] += 1
			self.avgTime[1] = (self.avgTime[1] + int(parsedTime[1])) - 60
		else:
			self.avgTime[1] += int(parsedTime[1])
		#print(self.avgTime)

	def addWin(self, num):
		if (num == -1):
			self.losses += 1
		if (num == 1):
			self.wins += 1
	def winPercent():
		w = self.wins
		l = self.losses
		if (l + w != 0):
			perc = float(w) / float(l + w)
			self.winPerc = perc * 100.0
		else:
			self.winPerc = 0.0
		return self.winPerc
		#print(self.wins + "," + self.losses + str(float(self.wins)))	}

def formatReplay(replay):
    return """
{filename}
--------------------------------------------
SC2 Version {release_string}
{category} Game, {start_time}
{type} on {map_name}
Length: {game_length}

{formattedTeams}
""".format(formattedTeams=formatTeams(replay), **replay.__dict__)
def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def formatTeams(replay):
    teams = list()
    print(replay.map_name)
   # print(replay.details)
    for team in replay.teams:
        players = list()
        for player in team:
            players.append("({0}) {1}".format(player.pick_race[0], player.name))
        for p in players:
        	fName = p.split()[1]
        formattedPlayers = '\n         '.join(players)
        teams.append("Team {0}:  {1}".format(team.number, formattedPlayers))
    return '\n\n'.join(teams)
#I originally created this for a networking assignment to extract nodes and edges out of sc2 replays.
#I had some trouble reading a folder of replays initially with sc2reader, so if anyone
#comes across this file, it will be useful if you are trying to parse multiple sc2replay files.
class replayParser:
	def __init__(self, args):
		self.args = args.parse_args()
		self.matchDict = {}
	def run(self):
		path = './' + self.args.replayPath + '/'#./replays/lotv/replays'
		#Dictionary for holding player information
		# Example: players["Byun"] = Player Object() of Byun
		players = {}
		files = os.listdir(path)
		filesToCount = 1000#len(files)
		sc2 = SC2Factory(
			directory='~/' + path
		)
		outfiles = []
		fileDict = {}
		#Enable APM tracker if you need this information.
		#sc2reader.engine.register_plugin(APMTracker())
		replayCount = 0
		done = False
		print("#-----------Running replay analysis-----------#")
		for i in range(0,filesToCount):
			#print("filename " + files[i])
			replayCount += 1
			#percentDone = (replayCount/filesToCount)
			#if (percentDone % 0.25 == 0): print( str(percentDone * 100) + "%")
			try:
				replay = (sc2.load_replay(path + files[i], load_level = 3))
				#get rid of ai players
				if (self.isValidName(replay.players) == False):
					continue
				if (len(replay.players) == 2):
					races = ""
					#print(replay.players)
					for p in replay.players:
						races += (p.play_race[0])
					c = self.checkMatch(races, 'z','p','t')
					if (c == True):
						outfiles.append(i)
				for count in self.matchDict:
					if (count >= 50):
				 		done = True
				if (done or i >= filesCount):
					break
				print("Looping")
			except:
				pass
		sc2.configure(depth=1)
		print(self.matchDict)
		self.copyReplays(path, "out/", files, outfiles)
		return (outfiles)
	def copyReplays(self, src, target, files, indices):
		for i in indices:
			fp = src + files[i]
			targ = target + files[i]
			copyfile(fp, targ)

	def isValidName(self, players):
		invalid = "."
		for p in players:
			for char in invalid:
				if char in p.name:
					return False
		return True

	def checkMatchCounts(self, r1, r2, count):
		if self.matchDict[r1+r2] >= count:
			print("checking counts" + self.matchDict)
			return True
		return False
	def checkMatch(self, races, r1, r2, r3):
		check = False
		races = races.lower()
		if r1 in races:
			if races == r1*2 and r1 != None:
				if r1+r1 not in self.matchDict:
					self.matchDict[r1+r1] = 1
					check = True
				else:
					if (self.checkMatchCounts(r1, r1, 50) == False):
						self.matchDict[r1+r1] += 1
						check = True
			elif races == r1 + r2 or  races[::-1] == (r1+ r2) and r2 != None:
				if r1+r2 not in self.matchDict:
					self.matchDict[r1+r2] = 1
					check = True
				else:
					if (self.checkMatchCounts(r1, r2, 50) == False):
						self.matchDict[r1+r2] += 1	
						check = True
			elif races == r1 + r3 or races[::-1] == (r1 + r3) and r3 != None:
				if r1+r3 not in self.matchDict:
					self.matchDict[r1+r3] = 1
					check = True
				else:
					if (self.checkMatchCounts(r1, r3, 50) == False):
						self.matchDict[r1+r3] += 1	
						check = True
		return check
	def	countRaces(self, raceList, race):
		matchup = ""
		for i in raceList:
			if i == "Terran":
				matchup += "t"
			elif i == "Zerg":
				matchup += "z"
			elif i == "Protoss":
				matchup += "p"
		return matchup
#		, matchupCounts
#		if "z" in matchup:
#			if ("zz" == matchup):
#				matchupCounts["zz"] += 1
#			if ("zp" == matchup or "zp" == matchup.reverse()):
#				matchupCounts["zp"] += 1
#			if ("zt" == matchup or "zt" == matchup.reverse()):
#				matchupCounts["zt"] += 1
			
	def addPlayer(self, player, players):
		name = player.strip(" ")
		if (name not in players):
			#print(name + " not in players")
			players[name] = Player()
		return players[name]
			#print(name + " found in players")

	#Checks the winner of each replay and updates it in the players dictionary.
	def checkWinner(replay, players):
		winner = (replay.winner.players[0].name)
		loser = None
		for player in replay.players:
			playerName = player.name
			if playerName != winner:
				loser = playerName
			players[playerName].addTime(replay.game_length)
		p1 = winner
		p2 = loser
		if p1 in players and p2 in players:
			players[p2].losses += 1
			players[p1].wins += 1
			players[p1].addPlayed(p2)
			players[p2].addPlayed(p1)
	
def writeData(players):
	#getNodes(players)
	getEdges(players)
def getNodes(players):
	toWrite = ""
	for i in players:
		toWrite += i + "\n"
	file = open("players.nodes", "w")
	file.write(toWrite)
	file.close()

#Input: player dictionary
#Output: csv file containing Source,Target edges using player dictionary.
def getEdges(players):
	toWrite = ""
	for i in players:
		player = players[i]
		for j in player.hasPlayed:
			toWrite += i + "," + j + "\n"
	file = open("players.csv", "w")
	file.write(toWrite)
	file.close()

	#for i in players:
		#p = players[i];
		#p.winPercent()
		#print(p.hasPlayed)
	return 1
	
def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("replayPath", type=str,
						help="path to replay folder")
	replayManager = replayParser(parser)
	outfiles = replayManager.run()
	print("Obtained " + str(len(outfiles)) + " replays within specified parameters")
	print(outfiles)
	

if __name__ == "__main__":
    main()

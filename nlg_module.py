import json
import aiml
import random
import re
eun = lambda x: "" if len(x) == 0 else ("은" if hasJongsung(x[-1]) else "는")
eul = lambda x: "" if len(x) == 0 else ("을" if hasJongsung(x[-1]) else "를")
ee = lambda x: "" if len(x) == 0 else ("이" if hasJongsung(x[-1]) else "가")
gwa = lambda x: "" if len(x) == 0 else ("과" if hasJongsung(x[-1]) else "와")
eomi_ee = lambda x: "" if len(x) == 0 or not hasJongsung(x[-1]) else "이"
redirection = {"은": eun, "을": eul, "이": ee, "과": gwa, "어미_이": eomi_ee}
def hasJongsung(character):
	x = ord(character)
	if(x < 0xAC00 and x > 0xD7A3): return False
	return (x - 0xAC00) % 28 != 0

class NLG:
	def __init__(self, entityFileName="KoreanMusicalArtists.txt"):
		self.loadAIML()
		# self.loadDict()
		self.loadArtistEntries(entityFileName)


	# main function. generate utterance from input json
	def nlg(self, artistName=None, keyword_only=True):
		result = {}
		artist = self.pickArtist() if artistName is None else artistName
		for item in ["RECOMMEND", "DEBUT", "SIMILAR", "TV", "RECORD", "MISC"]:
			result[item] = self.postprocess(self.aimlCoreKernel.respond(item), artist)
		return result

	def nlg_keyword(self, artistName, max_keyword_num):
		result = {}
		for item in ["RECOMMEND", "DEBUT", "SIMILAR", "TV", "RECORD", "MISC"]:
			keywords = self.selectKeywords(self.aimlKeywordKernel.respond(item).split("/"), max_keyword_num)
			result[item] = list(map(lambda x: " ".join((artistName, *x)), keywords))
		return result

	def all_question_iter(self):
		for artist in self.artists:
			yield self.nlg(artist)
		

	# load AIML file and train kernel
	def loadAIML(self):
		self.aimlCoreKernel = aiml.Kernel()
		self.aimlCoreKernel.learn("nlgAIML.xml")
		self.aimlKeywordKernel = aiml.Kernel()
		self.aimlKeywordKernel.learn("nlgKeywordAIML.xml")
	# load tag dictionary
	# def loadDict(self, dictFileName="dict"):

	# 	self.tagDict = {}
	# 	f = open("nlgdict", encoding="UTF8")
	# 	for line in f.readlines():
	# 		sp = line.strip().split(",")
	# 		self.tagDict[sp[0]] = sp[1]
	# 	f.close()
	
	def loadArtistEntries(self, entryFileName="KoreanMusicalArtists.txt"):
		self.artists = []
		with open(entryFileName, encoding="UTF8") as f:
			for line in f.readlines():
				if(len(line.strip())) == 0: continue
				name = line.strip().split("/")[-1].split("_(")[0].replace("_", " ") # to remove () and change _ into blank

				if ord(name[0]) >= 0xAC00 and ord(name[0]) < 0xD7A3: # only korean names allowed
					self.artists.append(name)

				


	# convert English tags/colon tags into Korean tags
	# def convertTagToText(self, tagCandidate):
	
	# 	tags = tagCandidate.split(":")
	# 	tag = tags[-1].lower()
	# 	if tag in self.tagDict:
	# 		return self.tagDict[tag]
	# 	return tags[-1]

	# randomly pick musical artist name
	def pickArtist(self):
		return random.choice(self.artists)

	def selectKeywords(self, keywords, maxkeyword=3):
		def gen(keywords, num):
			if num == 0: return []
			if num <= 1:
				return list(map(lambda x: [x], keywords))
			result = []
			for i in range(len(keywords)):
				startElem = keywords[i]
				for item in gen(keywords[i+1:], num-1):
					result.append([startElem, *item])
			return result
		result = []
		for i in range(1, maxkeyword+1):
			for item in gen(keywords, i):
				result.append(item)
		return result


	# process raw json to aiml-understandable string
	# python-aiml module recognizes no punctuation and order-sensitive, so we need to convert json into fixed form
	# PROPERTY1 VALUE1 E | PROPERTY2 VALUE2 ...
	# if value is list, 
	# properties must be in alphabet-order

	# NOT USED FOR QUESTION GENERATOR

	# def preprocess(self, inputJson):
	# 	# print(inputJson)
	# 	ignoreKey = ["dialog"]
	# 	# print(inputJson["dialog"])
	# 	items = []
	# 	result = []
	# 	# sort key in alphabetical order
	# 	for k, v in inputJson.items():
	# 		items.append((k, v))
	# 	items.sort(key=lambda x: x[0])
	# 	result.append("DIV") # always start with * in AIML
	# 	for item in items:
	# 		k, v = item[0], item[1]
	# 		if k in ignoreKey:
	# 			continue
	# 		result.append(k)
	# 		if type(v) == list:
	# 			result.append("LISTBEGIN") # list start notation
	# 			for i in v:
	# 				result.append(i)
	# 			result.append("LISTEND") # list end notation
	# 		else: 
	# 			if type(v) is not str:
	# 				result.append(str(v))
	# 				continue
	# 			for tagFragment in v.split(":"):
	# 				result.append(tagFragment.replace("-", ""))
	# 		result.append("DIV") # always put * between tags
	# 	return " ".join(result)

	# from aiml response, put proper tag value into slots, noted as [tag]
	# also make response more natural like putting right josa like [을]
	# area that needs postprocessing will be enclosed by []
	def postprocess(self, utterance, artist=None):
		
		last = ""
		flag = False
		temp = []
		sysval = ""
		x = utterance.split("/ ")
		for utter in x:
			result = []
			for c in utter:
				if c == '[':
					flag = True
					continue
				if c == ']':
					flag = False
					if sysval in redirection:
						result.append(redirection[sysval](last))
					else:
						if sysval == "가수":
							result.append(self.pickArtist() if artist is None else artist)
						# try:
						# 	result.append(self.convertTagToText(inputJson[sysval]))
						# except KeyError:
						# 	print("Keyerror: %s is not in json" % sysval)
						# 	result.append(sysval)
					sysval = ""
					last = result[-1]
					continue
				if flag:
					sysval += c
					continue
				last = c
				result.append(c)
			temp.append("".join(result))
		return temp



	# def test(self):
	# 	f = open("nlgtest", encoding="UTF8")
	# 	for line in f.readlines():
	# 		print(line.strip())
	# 		print(json.dumps(self.nlg(json.loads(line.strip())), ensure_ascii=False))

	# def aimltest(self, teststr):
	# 	print(self.aimlCoreKernel.respond(teststr))

if __name__ == '__main__':
	nlg = NLG("MusicalArtistEntities.txt")
	# nlg.aimltest("hello hello w,")
	print(nlg.nlg_keyword("싸이", 3))
	x = 0
	# for item in nlg.all_question_iter():
	# 	print(item)
	# 	x += 1
	# 	if x == 10:
	# 		break

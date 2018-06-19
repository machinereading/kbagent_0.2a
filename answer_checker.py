import konlpy


class AnswerChecker():
	def __init__(self):
		self.keywords = []
		with open("keywordDictionary", encoding="UTF8") as f:
			for line in f.readlines():
				self.keywords.append(line.strip())

		words = {}
		self.proper_response = set([])

		self.artists = []
		with open("KoreanMusicalArtists.txt", encoding="UTF8") as f:
			for line in f.readlines():
				if(len(line.strip())) == 0: continue
				name = line.strip().split("/")[-1].split("_(")[0].replace("_", " ") # to remove () and change _ into blank

				if ord(name[0]) >= 0xAC00 and ord(name[0]) < 0xD7A3 and len(name) > 1: # only korean names allowed
					self.artists.append(name)

		self.tagger = konlpy.tag.Twitter()

	def check(self, answer):
		answer = answer.strip().replace("\r", " ")
		if answer in self.proper_response:
			return True
		morph = list(map(lambda x: x[0], self.tagger.pos(answer, norm=True)))
		for keyword in self.keywords:
			if keyword in morph:
				self.proper_response.add(answer)
				return True
		for artist in self.artists:
			if artist in morph:
				self.proper_response.add(answer)
				return True
		return False

	def naive_check(self, answer):
		answer = answer.strip().replace("\r", " ")
		if answer in self.proper_response:
			return True
		for artist in self.artists:
			if artist in answer:
				return True
		for keyword in self.keywords:
			if keyword in answer:
				return True
		return False
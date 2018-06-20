from gensim.models.word2vec import Word2Vec
from gensim.models.fasttext import FastText
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn import metrics
from konlpy.tag import Twitter
from functools import reduce
import pickle
import random
class AnswerChecker():
	def __init__(self, vectorizer="word2vec", classifier="logistic"):
		self.logistic = self.mlp = None
		self.vectorizer = None
		self.vectorizer_name = vectorizer
		self.classifier = None
		self.classifier_name = classifier
		self.tokenizer = Twitter()
		self._load_vector_data()
		self._load_classifier_data()
		self.unseen_words = set([])

	def _train_vectorizer(self, data):
		flag = self.vectorizer is not None
		if not flag:
			self.vectorizer = Word2Vec(window=5, size=100) if self.vectorizer_name == "word2vec" else FastText(window=5, size=100)
		
		# if self.vectorizer_name == "word2vec":
		# 	train_data = []
		# 	c = 0
		# 	for item in data:
		# 		train_data.append(LabeledSentence(words=item, tags=["SENTENCE%d" %c]))
		# 		c += 1
		# else:
		train_data = data
		self.vectorizer.build_vocab(train_data, update=flag)
		self.vectorizer.train(train_data, total_examples=self.vectorizer.corpus_count, epochs=10)
		
		self.vectorizer.save("train/%s.bin" % self.vectorizer_name)

	def _train_classifier(self, data, labels, save=True):
		if len(data) != len(labels):
			raise Exception("Length mismatch")
		if self.classifier is None:
			self.classifier = LogisticRegression(solver='liblinear',dual=True, penalty="l2", multi_class='ovr') if self.classifier_name == "logistic" else MLPClassifier()
		trainX = list(map(self._vectorize, data))
		self.classifier.fit(trainX, labels)
		if save:
			with open("train/%s/%s" % (self.vectorizer_name, self.classifier_name), "wb") as f:
				pickle.dump(self.classifier, f)

	def _vectorize(self, list_of_word):
		for word in list_of_word:
			if word not in self.vectorizer:
				self.unseen_words.add(word)
		return reduce(lambda x, y: x + y, [self.vectorizer[w] if w in self.vectorizer else 0 for w in list_of_word]) / len(list_of_word)

	def _load_vector_data(self):
		try:
			self.vectorizer = Word2Vec.load("train/word2vec.bin") if self.vectorizer_name == "word2vec" else FastText.load("train/fasttext.bin")
		except FileNotFoundError:
			print("Vectorizer train data not found")
			self.vectorizer = None

	def _load_classifier_data(self):
		try:
			self.classifier = pickle.load(open("train/%s/%s" % (self.vectorizer_name, self.classifier_name), "rb"))
		except FileNotFoundError:
			print("Classifier train data not found")
			self.classifier = None

	def train(self, pc, nc, train_mode=None):
		if train_mode is None:
			train_mode = [self.vectorizer is None, self.classifier is None]
		if not any(train_mode):
			return
		data = []
		label = []
		for line in pc.readlines():
			data.append(self.tokenizer.morphs(line.strip()))
			label.append(1)

		for line in nc.readlines():
			data.append(self.tokenizer.morphs(line.strip()))
			label.append(0)
		train_len = int(0.9*len(data))

		d = list(zip(data, label))
		random.shuffle(d)
		train_data = list(map(lambda x: x[0], d[:train_len]))
		train_label = list(map(lambda x: x[1], d[:train_len]))
		dev_data = list(map(lambda x: x[0], d[train_len:]))
		dev_label = list(map(lambda x: x[1], d[train_len:]))
		
		if train_mode[0]:
			self._train_vectorizer(data)
		if train_mode[1]:
			self._train_classifier(train_data, train_label)
			p = self.classifier.predict(list(map(self._vectorize, dev_data)))
			print(metrics.accuracy_score(dev_label, p))

		
	def check(self, *sentence):
		try:
			morphs = list(map(lambda x: self._vectorize(self.tokenizer.morphs(x.strip())), sentence))
			return self.classifier.predict_proba(morphs).tolist()
		except ValueError:
			# print(sentence)
			return [[1, 0]]
		


if __name__ == '__main__': 
	vec = ["word2vec", "fasttext"]
	cla = ["logistic", "mlp"]
	for v in vec:
		for c in cla:
			a = AnswerChecker(vectorizer=v, classifier=c)
			# flag = [a.vectorizer is None, a.classifier is None]
			with open("train/abstracts.txt", encoding="UTF8") as pc, open("train/abstracts_nonartists.txt", encoding="UTF8") as nc:
				a.train(pc, nc, [False, True])
			with open("statistics/all_response", encoding="UTF8") as rf:
				for s in rf.readlines():
					if len(s) == 0: continue
					val = a.check(s)
				# wf.write(str(len(a.unseen_words))+"\n")
				# for item in a.unseen_words:
				# 	wf.write(item+"\n")
				# break
			# with open("statistics/all_response", encoding="UTF8") as rf, open("statistics/gensim/%s_%s" % (v, c), "w", encoding="UTF8") as wf:
			# 	for sentence in rf.readlines():
			# 		s = sentence.strip()
			# 		if len(s) == 0: continue
			# 		val = a.check(s)
			# 		wf.write("%s\t%d\t%.2f\t%.2f\n" % (s, val[0].index(max(val[0])), val[0][0], val[0][1]))
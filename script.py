import os
x = "statistics/gensim/"

for item in os.listdir(x):
	with open(x+item, encoding="UTF8") as rf, open(x+item+"_proper_response", "w", encoding="UTF8") as wf:
		val = 0
		for line in rf.readlines():
			s = line.split("\t")
			val += int(s[1])
			if int(s[1]) == 1:
				wf.write(s[0]+"\n")
		print(item, val)
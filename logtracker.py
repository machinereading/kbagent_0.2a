import json
from answer_checker import AnswerChecker
import os

logs = []
for dirpath, dirnames, filenames in os.walk("logs"):
	for filename in [f for f in filenames]:
		name = os.path.join(dirpath, filename)
		if os.path.isfile(name):
			logs.append(name)

# print(logs)
ac = AnswerChecker()
proper_response = set([])
naive_proper_response = set([])
all_response = set([])
length = len(logs)
count = 0

for logfile in logs:
	# print(logfile)
	with open(logfile, encoding="UTF8") as f:
		j = json.load(f)
	for category in ["RECOMMEND", "DEBUT", "SIMILAR", "TV", "RECORD", "MISC"]:
		if category not in j:
			continue
		for k, v in j[category].items():
			for response in v:
				response = response.strip().replace("\r", " ")
				all_response.add(response)
				if ac.check(response):
					proper_response.add(response)
				# if ac.naive_check(response):
				# 	naive_proper_response.add(response)

	
	count += 1
	print("\r%d/%d" %(count, length), end="", flush=True)
	# if count == 100: break

# with open("statistics/keyword_checker/proper_response", "w", encoding="UTF8") as f:
# 		for response in proper_response:
# 			f.write("%s\n" % (response))

# with open("statistics/keyword_checker/naive_proper_response", "w", encoding="UTF8") as f:
# 	for response in naive_proper_response:
# 		f.write("%s\n" % (response))

# with open("statistics/all_response", "w", encoding="UTF8") as f:
# 	for response in all_response:
# 		f.write("%s\n" % (response))

with open("statistics/words/word_statistics.json", "w", encoding="UTF8") as f:
	json.dump(ac.words, f, ensure_ascii=False, indent=4)

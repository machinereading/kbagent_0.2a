import json
from answer_checker import AnswerChecker
logfile = "logs/180619_125720_695"
with open(logfile, encoding="UTF8") as f:
	j = json.load(f)

ac = AnswerChecker()
proper_response = set([])
naive_proper_response = set([])
for category in ["RECOMMEND", "DEBUT", "SIMILAR", "TV", "RECORD", "MISC"]:
	print(len(j[category]))
	for k, v in j[category].items():
		for response in v:
			response = response.strip().replace("\r", " ")
			if ac.check(response):
				proper_response.add(response)
			if ac.naive_check(response):
				naive_proper_response.add(response)

with open("proper_response", "w", encoding="UTF8") as f:
	for response in proper_response:
		f.write("%s\n" % (response))

with open("naive_proper_response", "w", encoding="UTF8") as f:
	for response in naive_proper_response:
		f.write("%s\n" % (response))

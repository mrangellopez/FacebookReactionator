import json
import codecs
import re

with open('data.json') as data_file:
	data = json.load(data_file)
	
with codecs.open('untitled.json', 'r', encoding = 'utf-8') as inp:
	inps = json.load(inp)

def getOutput(jsonDict):
	output = 0
	for k,v in jsonDict.items():
		if k == "message":
			output += len(v)
		elif k == "instagram_eligibility":
			output += 10
		else:
			output += 1
	output *= 100
	return output

outputs = []
for d in inps:
	outputs.append(getOutput(d))
print (outputs)



# emoji_pattern = re.compile("["
# 	u"\U0001F600-\U0001F64F"  # emoticons
# 	u"\U0001F300-\U0001F5FF"  # symbols & pictographs
# 	u"\U0001F680-\U0001F6FF"  # transport & map symbols
# 	u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
# 	                   "]+", flags=re.UNICODE)
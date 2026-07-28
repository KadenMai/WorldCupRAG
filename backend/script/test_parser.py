from app.ingest.parser import WorldCupParser
import json

parser = WorldCupParser("../data/worldcup.json/2022")

data = parser.load()

wc = data.name

print(data.name)
print(data.year)

print(f"Number of matches: {len(data.matches)}")

print(f"Number of groups: {len(data.groups)}")

print(f"Number of stadiums: {len(data.stadiums)}")
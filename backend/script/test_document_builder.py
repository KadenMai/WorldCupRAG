from app.ingest.parser import WorldCupParser
from app.ingest.document_builder import DocumentBuilder

parser = WorldCupParser("../data/raw/2022")
tournament = parser.load()

documents = DocumentBuilder().build(tournament)

print(f"Tournament: {tournament.name}")
print(f"Year: {tournament.year}")
print(f"Documents built: {len(documents)}")
print()

sample = documents[0]
print("=== Sample document ===")
print(f"ID: {sample.id}")
print(f"Title: {sample.title}")
print(f"Metadata: {sample.metadata}")
print()
print(sample.content)
print()

final = next(doc for doc in documents if doc.metadata.get("round") == "Final")
print("=== Final ===")
print(f"ID: {final.id}")
print(f"Title: {final.title}")
print()
print(final.content)

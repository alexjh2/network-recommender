import json
import spacy
from neo4j import GraphDatabase

def extract_orgs(text, nlp):
    doc = nlp(text)
    return list(set(ent.text for ent in doc.ents if ent.label_ == "ORG"))

def build_graph(parsed_bios_path="../data/parsed_bios.jsonl", uri="neo4j+s://02c99ce4.databases.neo4j.io", user="neo4j", password="Sbs8raev43vRNFjPOdJqPQgmqV7TiCp7GOQkdSZfOGk"):
    with open(parsed_bios_path, "r") as f:
        bios = [json.loads(line) for line in f]

    nlp = spacy.load("en_core_web_sm")

    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session() as session:
        for bio in bios:
            user_id = bio["user_id"]
            user_name = bio["user_name"]
            orgs = extract_orgs(bio["bio"], nlp)

            for org in orgs:
                session.run(
                    """
                    MERGE (p:Person {id: $user_id})
                    SET p.name = $user_name
                    MERGE (o:Org {name: $org})
                    MERGE (p)-[:ATTENDED]->(o)
                    """,
                    user_id=user_id,
                    org=org,
                    user_name=user_name
                )
            print(f"Added {len(orgs)} orgs for user {user_id}")

    driver.close()
    print("Finished building graph.")

if __name__ == "__main__":
    build_graph()

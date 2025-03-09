from src.knowledge_graph import KnowledgeGraph
import time
import json
# from flask import Flask, request, jsonify

kg = KnowledgeGraph()

def init_knowledge_graph():
    kg.clear_knowledge_graph()

    with open('src/field.txt', 'r') as field_fin:
        for line in field_fin:
            row = line.strip().split('\t')
            if len(row) < 11:
                continue
            if not kg.check_node_exists(row[7]):
                kg.insert("domain", 'd', {
                    "name": row[7],
                    "id": row[6]})

            if not kg.check_node_exists(row[5]):
                kg.insert("field", 'f', {
                    "name": row[5],
                    "id": row[4]})
                kg.insert_connection(row[7], row[5]) 

            if not kg.check_node_exists(row[3]):
                kg.insert("subfield", 's', {
                    "name": row[3],
                    "id": row[2]})
                kg.insert_connection(row[5], row[3])

            if not kg.check_node_exists(row[1]):
                kg.insert("topic", 't', {
                    "name": row[1],
                    "id": row[0],
                    "summary": row[9],
                    "link": row[10]})
                kg.insert_connection(row[3], row[1])

    with open('src/article.txt', 'r') as fin:
        content = json.loads(fin.read())
        for i in content:
            try:
                if not kg.check_node_exists(i['title']):
                    kg.insert("paper", 'p', {
                        "name": i['title'],
                        "openalex_id": i['openalex_id'],
                        "author_id": i['author_id'],
                        "doi": i['doi'],
                        "date": i['publication_date']})
                    for j in i['topics']:
                        kg.insert_connection(i['title'], j['display_name'])
            except Exception as e:
                print(e)
                continue
        
def main():
    # wait for the neo4j to start
    time.sleep(8)

    init_knowledge_graph()


if __name__ == "__main__":
    main()
    ds= input("Press enter to exit:")
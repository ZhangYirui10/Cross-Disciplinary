from src.knowledge_graph import KnowledgeGraph
from src.callgpt import CallGPT
import time
import json
# from flask import Flask, request, jsonify

kg = KnowledgeGraph()

def init_knowledge_graph():
    kg.clear_knowledge_graph()
    with open('data/faculty.json', 'r') as a:
                        fc = json.loads(a.read())["faculty"]
                        for x in fc:
                            kg.insert("faculty", 'x', {
                                    "name": x['id'],
                                    "affiliation": x['affiliation'],
                                    "nametext": x['name']})

    with open('data/field.txt', 'r') as field_fin:
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

    with open('data/article.txt', 'r') as fin:
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
                        kg.insert_connection(j['display_name'], i['title'])
                    for x in fc:
                            if i['author_id'] == x['id']:
                                kg.insert_connection(x['id'], i['title'])

                    try:
                        with open(f"src/gptoutput_json/{i['openalex_id']}.json", 'r') as g:
                            data = json.loads(g.read())
                            if "Keywords" in data:
                                for kw in data["Keywords"]:
                                    kg.insert("keyword", 'k', {
                                        "name": kw})
                                    kg.insert_connection(i['title'], kw)
                            if "Problem" in data:
                                kg.insert("problem", 'q', {
                                    "name": "Problem"+i['openalex_id'],
                                    "description": data["Problem"]})
                                kg.insert_connection(i['title'], "Problem"+i['openalex_id'])
                                try:
                                    with open(f"src/key_json_file/{i['openalex_id']}.json", 'r') as g:
                                        gdata = json.loads(g.read())["Entities"]
                                        if "Problem" in gdata:
                                            for entity in gdata["Problem"]:
                                                kg.insert("problemkeyword", 'a', {
                                                    "name": entity})
                                                kg.insert_connection("Problem"+i['openalex_id'], entity)
                                except Exception as e:
                                    print(e)
                            if "Method" in data:
                                kg.insert("method", 'm', {
                                    "name":"Method"+i['openalex_id'],
                                    "description": data["Method"]})
                                kg.insert_connection(i['title'], "Method"+i['openalex_id'])
                                try:
                                    with open(f"src/key_json_file/{i['openalex_id']}.json", 'r') as g:
                                        gdata = json.loads(g.read())["Entities"]
                                        if "Method" in gdata:
                                            for entity in gdata["Method"]:
                                                kg.insert("methodkeyword", 'c', {
                                                    "name": entity})
                                                kg.insert_connection("Method"+i['openalex_id'], entity)
                                except Exception as e:
                                    print(e)
                            if "Model" in data and data["Model"] != "NO":
                                kg.insert("model", 'n', {
                                    "name": data["Model"],
                                    })
                                kg.insert_connection(i['title'], data["Model"])
                            if "Task" in data:
                                try:
                                    with open(f"src/key_json_file/{i['openalex_id']}.json", 'r') as g:
                                        gdata = json.loads(g.read())["Entities"]
                                        if "Task" in gdata:

                                            kg.insert("task", 'j', {
                                                "name": gdata['Task'],
                                                "description": data["Task"]})
                                            kg.insert_connection(i['title'], gdata['Task'])
                                except Exception as e:
                                    print(e)
                            if "Results" in data:
                                kg.insert("result", 'b', {
                                    "name": "Result"+i['openalex_id'],
                                    "description": str(data["Results"])})
                                kg.insert_connection(i['title'], "Result"+i['openalex_id'])
                                try:
                                    with open(f"src/key_json_file/{i['openalex_id']}.json", 'r') as g:
                                        gdata = json.loads(g.read())["Entities"]
                                        if "Results" in gdata:
                                            for entity in gdata["Results"]:
                                                if gdata["Results"][entity]:
                                                    kg.insert("resultkeyword", 'e', {
                                                        "name": entity+i['openalex_id'],
                                                        "description": ','.join(gdata["Results"][entity])})
                                                    kg.insert_connection("Result"+i['openalex_id'], entity+i['openalex_id'])
                                except Exception as e:
                                    print(e)

                            
                    except Exception as e:
                        print(e)
                        pass

            except Exception as e:
                print(e)
                continue
        
def main():
    # wait for the neo4j to start
    # dfstpkqamcnjb
    time.sleep(8)
    
    init_knowledge_graph()
    # print(CallGPT("What is the impact of COVID-19 on the economy?"))
    


if __name__ == "__main__":
    main()
    input("Press enter to exit:")
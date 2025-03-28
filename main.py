from src.knowledge_graph import KnowledgeGraph
from src.callgpt import extract_from_abstract
from src.paper_loader import get_article_info_by_author_id
from src.chroma import ChromaClient
import time
import json
import re
import os
from flask import Flask, request, jsonify, render_template
# refst

kg = KnowledgeGraph()
interest_cm = ChromaClient("vector_database_name_interest")
topic_cm = ChromaClient("vector_database_name_topic")
paper_cm = ChromaClient("vector_database_name_paper")

# input: <a href=\"\" ng-click=\"setFaculty('11','Algorithms & Theory');\"><span id='divlink' class='11'>Algorithms & Theory</span></a>
def get_span_name(input):
    pattern = re.compile(r"setFaculty\('\d+','(.*?)'\)")
    faculties = pattern.findall(input)
    return ','.join(faculties)

def init_knowledge_graph():
    kg.clear_knowledge_graph()
    # with open('data/faculty.json', 'r') as a:
    #                     fc = json.loads(a.read())["faculty"]
    #                     for x in fc:
    #                         kg.insert("faculty", 'x', {
    #                                 "name": x['id'],
    #                                 "affiliation": x['affiliation'],
    #                                 "nametext": x['name']})

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

    with open('data/nus_faculty_with_openalex_id.json', 'r') as a:
        fc = json.loads(a.read())
        for faculty in fc:
            try:
                for i in faculty['interests']:
                    interest_cm.add_document(i+"*,*" + faculty['Bio'] +"*,*" +faculty['name'], {"content": i})
                kg.insert("faculty", 'x', {
                    "name": faculty['name'],
                    "title": faculty['title'],
                    "email": faculty['email'],
                    "office": faculty['office'],
                    "tel": faculty['tel'],
                    "pic": faculty['pic'],
                    "socid": faculty['socid'],
                    "Dept": faculty['Dept'],
                    "Area": faculty['Area'],
                    "Bio": faculty['Bio'],
                    "ApptAdm": faculty['ApptAdm'],
                    "researcharea": get_span_name(faculty['researcharea']),
                    "biolinkstat": faculty['biolinkstat'],
                    "photoSrc": faculty['photoSrc'],
                    "interests": ",".join(faculty['interests']),
                    "openalex_id": faculty['openalex_id']})
                papers = get_article_info_by_author_id(faculty['openalex_id'])
                for p in papers:
                    if not kg.check_node_exists(p['title']):
                        kg.insert("paper", 'p', {
                            "name": p['title'],
                            "openalex_id": p['openalex_id'],
                            "author_id": p['author_id'],
                            "doi": p['doi'],
                            "abstract": p['abstract'],
                            "date": p['publication_date']})
                        # extract_abstract = extract_from_abstract(p['abstract'])
                        extract_abstract = p['abstract']
                        paper_cm.add_document(extract_abstract+"*,*" + p['title'] +"*,*" +faculty['name'], {"content": extract_abstract})

                        for j in p['topics']:
                            topic_cm.add_document(j['display_name']+"*,*" + p['title'] +"*,*" +faculty['name'], {"content": j['display_name']})
                            kg.insert_connection( p['title'],j['display_name'])
                        kg.insert_connection(faculty['name'],p['title'])

                
            except Exception as e:
                print(e)
                continue
 
def get_from_chroma(query):
    return {
        "interest": interest_cm.query(query, 5),
        "topic": topic_cm.query(query, 5),
        "paper": paper_cm.query(query, 5)
    }
def main():
    # wait for the neo4j to start
    # dfstpkqamcnjb
    time.sleep(12)
    
    # init_knowledge_graph()
    # print(CallGPT("What is the impact of COVID-19 on the economy?"))
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    app = Flask(__name__,template_folder='templates')
    @app.route('/searchdb', methods=['GET'])
    def searchdb():
        query = request.args.get('query')
        return jsonify(get_from_chroma(query))

    # return a beautiful http interface, it provides a search bar for user to search the database
    @app.route('/home', methods=['GET'])
    def home():
        return '''
        <!doctype html>
        <title>Search Database</title>
        <h1>Search Database</h1>
        <form>
            <label>Query:</label>
            <input name="query">
            <button>Search</button>
        </form>
        '''
        
    # template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    # app = Flask(__name__, template_folder=template_dir)
    # app.debug = True  # 开启调试模式
    
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/analyze', methods=['GET'])
    def analyze():
        query = request.args.get('query', '').strip()
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
            
        print("Received query:", query)
        # 调用 GPT 分析功能并返回 JSON 格式的结果
        capabilities = capability_analyze(query)
        cleaned_list = [s.strip("*") for s in capabilities]
        print("Capabilities:", cleaned_list)
        
        # 对每个能力进行向量搜索
        results = []
        for capability in cleaned_list:
            print(f"Searching for capability: {capability}")
            chroma_results = get_from_chroma(capability)
            print(f"Search results for {capability}:", chroma_results)
            results.append({
                "capability": capability,
                "vector_results": chroma_results
            })
        
        return jsonify({
            "capabilities": cleaned_list,
            "search_results": results
        })

    @app.route('/subgraph', methods=['GET'])
    def get_subgraph():
        return "subgraph"

    # app.run(debug=False, host='0.0.0.0', port=8009)

    # @app.route('/searchdb', methods=['GET'])
    # def searchdb():
    #     query = request.args.get('query')
    #     print(query)
    #     return jsonify(cm.query(query, 5))

    app.run(debug=False, host='0.0.0.0', port=8008)

    
    

    


if __name__ == "__main__":
    main()
    input("Press enter to exit:")
from src.knowledge_graph import KnowledgeGraph
from src.callgpt import extract_from_abstract
from src.paper_loader import get_article_info_by_author_id
from src.chroma import ChromaClient
import time
import json
import re
import os
from flask import Flask, request, jsonify, render_template, send_from_directory
import logging
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
                print("--------------------------------")
                print(f"Processing faculty: {faculty['name']}")
                print(f"Total papers found: {len(papers)}")
                print("--------------------------------")
                
                paper_count = 0
                for p in papers:
                    if paper_count >= 50:
                        print(f"Reached limit of 50 papers for faculty {faculty['name']}")
                        break
                        
                    try:
                        # 检查所有必要字段是否都存在且不为空
                        required_fields = ['title', 'openalex_id', 'author_id', 'doi', 'abstract', 'publication_date']
                        missing_fields = [field for field in required_fields if not p.get(field)]
                        
                        if missing_fields:
                            print(f"Skipping paper '{p.get('title', 'No title')}' due to missing fields: {', '.join(missing_fields)}")
                            continue
                            
                        print(f"Processing paper: {p['title']}")
                        
                        if not kg.check_node_exists(p['title']):
                            # 插入论文节点
                            kg.insert("paper", 'p', {
                                "name": p['title'],
                                "openalex_id": p['openalex_id'],
                                "author_id": p['author_id'],
                                "doi": p['doi'],
                                "abstract": p['abstract'],
                                "date": p['publication_date']
                            })
                            
                            # 处理摘要
                            paper_cm.add_document(p['abstract']+"*,*" + p['title'] +"*,*" +faculty['name'], {"content": p['abstract']})

                            # 处理主题
                            if p.get('topics'):
                                for j in p['topics']:
                                    if j.get('display_name'):
                                        topic_cm.add_document(j['display_name']+"*,*" + p['title'] +"*,*" +faculty['name'], {"content": j['display_name']})
                                        kg.insert_connection(p['title'], j['display_name'])
                            
                            # 连接论文和教师
                            kg.insert_connection(faculty['name'], p['title'])
                            print(f"Successfully added paper: {p['title']}")
                        else:
                            print(f"Paper already exists: {p['title']}")
                            
                        paper_count += 1
                            
                    except Exception as e:
                        print(f"Error processing paper '{p.get('title', 'No title')}': {str(e)}")
                        continue  # 跳过当前文章，继续处理下一篇
                
            except Exception as e:
                print(f"Error processing faculty {faculty.get('name', 'Unknown')}: {str(e)}")
                continue  # 处理下一个faculty
 
def get_from_chroma(query):
    return {
        "interest": interest_cm.query(query, 5),
        "topic": topic_cm.query(query, 5),
        "paper": paper_cm.query(query, 5)
    }
def main():
    # wait for the neo4j to start
    time.sleep(12)
    
    # init_knowledge_graph()
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    app = Flask(__name__, template_folder='templates')
    
    # Configure logging
    app.logger.setLevel('DEBUG')
    handler = logging.StreamHandler()
    handler.setLevel('DEBUG')
    app.logger.addHandler(handler)

    # 添加静态文件路由
    @app.route('/images/<path:filename>')
    def serve_professor_image(filename):
        print(f"\n=== DEBUG INFO ===")
        print(f"Requested image: {filename}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Directory contents: {os.listdir('/app/professor_images')}")
        print(f"File exists: {os.path.exists(os.path.join('/app/professor_images', filename))}")
        print(f"File path: {os.path.join('/app/professor_images', filename)}")
        print("================\n")
        image_dir = os.path.join(os.getcwd(), 'professor_images')
    
        print(f"\n=== DEBUG INFO ===")
        print(f"Requested image: {filename}")
        print(f"Resolved dir: {image_dir}")
        print(f"Directory contents: {os.listdir(image_dir)}")
        print(f"File exists: {os.path.exists(os.path.join(image_dir, filename))}")
        print(f"File path: {os.path.join(image_dir, filename)}")
        print("================\n")
        
        try:
            return send_from_directory(image_dir, filename)
        except Exception as e:
            print(f"\n=== ERROR ===")
            print(f"Error type: {type(e)}")
            print(f"Error message: {str(e)}")
            print("=============\n")
            return "Image not found", 404

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
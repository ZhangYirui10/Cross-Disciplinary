import os
import re
from flask import Flask, request, jsonify, render_template, send_from_directory, make_response
from src.chroma import ChromaClient
from src.gpt import capability_analyze, get_final_answer, get_professor_analysis
from src.knowledge_graph import KnowledgeGraph
from src.paper_loader import get_article_info_by_author_id
import time
import json
# from main import get_from_chroma, init_knowledge_graph

time.sleep(5)
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
    # 获取当前文件的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取项目根目录
    project_root = current_dir
    # 设置模板目录的绝对路径
    template_dir = os.path.join(project_root, 'templates')
    
    app = Flask(__name__, template_folder=template_dir)
    app.debug = True  # 开启调试模式
    
    kg = KnowledgeGraph()
    
    # # 初始化数据
    # print("Initializing data...")
    # try:
    #     time.sleep(10)
    #     init_knowledge_graph()
    #     print("Data initialization completed successfully.")
    # except Exception as e:
    #     print(f"Error during data initialization: {str(e)}")
    #     raise  # 重新抛出异常以便看到完整的错误信息
    
    @app.route('/')
    def index():
        return render_template('index.html')
    @app.route('/images/<path:filename>')
    def serve_professor_image(filename):
        image_dir = os.path.join(os.getcwd(), 'professor_images')
        try:
            response = make_response(send_from_directory(image_dir, filename))
            response.headers["Cache-Control"] = "no-store"
            return response
        except Exception as e:
            return "Image not found", 404

    @app.route('/analyze', methods=['GET'])
    def analyze():
        query = request.args.get('query', '').strip()
        k = int(request.args.get('k', '3'))  # Number of professors to recommend, default to 3
        
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
            
        print("Received query:", query)
        # 调用 GPT 分析功能并返回 JSON 格式的结果
        capabilities, response = capability_analyze(query)
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
        
        # 计算每位教授的总分数
        professor_scores = {}
        
        # 遍历所有能力的搜索结果
        for capability_index, capability_result in enumerate(results):
            for search_type, search_results in capability_result["vector_results"].items():
                for item in search_results:
                    # Parse the item based on the format from ChromaClient.query
                    # The format is a list [document, distance] where document is a string and distance is a float
                    if isinstance(item, list) and len(item) >= 2:
                        document = item[0]  # Document content
                        distance = item[1]  # Distance value (lower is better)
                        
                        # Convert distance to similarity score (1 - distance)
                        # The closer the distance is to 0, the higher the score should be
                        score = 1.0 - distance
                        
                        # Parse the document to extract professor name
                        parts = document.split("*,*")
                        if len(parts) >= 3:
                            professor_name = parts[2].strip()
                            
                            # 累加分数
                            if professor_name not in professor_scores:
                                professor_scores[professor_name] = 0
                            professor_scores[professor_name] += score
        
        # 根据总分排序教授
        ranked_professors = sorted(professor_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 选择前k个教授
        top_professors = ranked_professors[:k]
        
        # 查询教授的详细信息
        prof_details = []
        for prof_name, score in top_professors:
            prof_info = kg.queryProf(prof_name.strip())
            prof_info["score"] = score
            prof_details.append(prof_info)
        
        # 根据这些教授找到相关的论文
        paper_details = []
        for prof_name, _ in top_professors:
            # 获取教授的论文
            papers = kg.queryProfPapers(prof_name.strip())
            for paper in papers:
                paper_info = kg.queryPaper(paper.strip())
                if paper_info:
                    paper_details.append(paper_info)
        
        # 提取参数用于分析
        capability_list = cleaned_list
        capability_reasoning = response
        professor_analysis_input = {
            "project_description": query,
            "capabilities": capability_list,
            "capability_reasoning": capability_reasoning,
            "professors": prof_details,
            "papers": paper_details
        }
        
        try:
            # 调用分析函数，而非让LLM做推荐决策
            analysis_result = get_professor_analysis(professor_analysis_input)
            
            # 返回排序的教授、相关论文和分析结果
            return jsonify({
                "professors": prof_details,
                "papers": paper_details,
                "analysis": analysis_result,
                "capabilities": capability_list,
                "capability_reasoning": response
            })
            
        except Exception as e:
            print("Error in analysis:", str(e))
            return jsonify({
                "error": "Error generating analysis",
                "details": str(e)
            }), 500

    @app.route('/subgraph', methods=['GET'])
    def get_subgraph():
        return "subgraph"
        query = request.args.get('query', '').strip()
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
            
        # 获取与查询相关的子图数据
        subgraph_data = kg.get_subgraph(query)
        return jsonify(subgraph_data)

    app.run(debug=False, host='0.0.0.0', port=8008)

if __name__ == "__main__":
    main()
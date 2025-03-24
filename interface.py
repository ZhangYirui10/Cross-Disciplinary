import os
from flask import Flask, request, jsonify, render_template
from src.chroma import ChromaClient
from src.gpt import capability_analyze, get_final_answer
from main import get_from_chroma, init_knowledge_graph

def main():
    # 获取当前文件的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取项目根目录
    project_root = current_dir
    # 设置模板目录的绝对路径
    template_dir = os.path.join(project_root, 'templates')
    
    app = Flask(__name__, template_folder=template_dir)
    app.debug = True  # 开启调试模式
    
    # 初始化数据
    # print("Initializing data...")
    # init_knowledge_graph()
    # print("Data initialization completed.")
    
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
        
        # 提取参数
        project_description = query  # 添加项目描述
        capability_list = cleaned_list
        capability_reasoning = response
        capability_1_name = cleaned_list[0] if len(cleaned_list) > 0 else ""
        capability_1_results = results[0]["vector_results"] if len(results) > 0 else {}
        capability_2_name = cleaned_list[1] if len(cleaned_list) > 1 else ""
        capability_2_results = results[1]["vector_results"] if len(results) > 1 else {}
        capability_3_name = cleaned_list[2] if len(cleaned_list) > 2 else ""
        capability_3_results = results[2]["vector_results"] if len(results) > 2 else {}
        
        try:
            # 调用 get_final_answer
            final_answer = get_final_answer(
                project_description=project_description,
                capability_list=capability_list,
                capability_reasoning=capability_reasoning,
                capability_1_name=capability_1_name,
                capability_1_results=capability_1_results,
                capability_2_name=capability_2_name,
                capability_2_results=capability_2_results,
                capability_3_name=capability_3_name,
                capability_3_results=capability_3_results
            )
            print("Final answer:", final_answer)
            
            # 返回最终答案
            return jsonify({
                "final_answer": str(final_answer)
            })
            
        except Exception as e:
            print("Error in get_final_answer:", str(e))
            return jsonify({
                "error": "Error generating final answer",
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

    app.run(debug=False, host='0.0.0.0', port=8009)

if __name__ == "__main__":
    main()
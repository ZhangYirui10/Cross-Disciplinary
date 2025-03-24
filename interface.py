import os
from flask import Flask, request, jsonify, render_template
from src.chroma import ChromaClient
from src.gpt import capability_analyze
from src.knowledge_graph import KnowledgeGraph

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
    
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/analyze', methods=['GET'])
    def analyze():
        query = request.args.get('query')
        print(query)
        # 调用 GPT 分析功能并返回 JSON 格式的结果
        capabilities = capability_analyze(query)
        print(capabilities)
        return jsonify({
            "capabilities": capabilities
        })

    @app.route('/subgraph', methods=['GET'])
    def get_subgraph():
        query = request.args.get('query')
        # 获取与查询相关的子图数据
        subgraph_data = kg.get_subgraph(query)
        return jsonify(subgraph_data)

    app.run(debug=False, host='0.0.0.0', port=8008)

if __name__ == "__main__":
    main()
    input("Press enter to exit:")
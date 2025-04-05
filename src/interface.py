import os
from flask import Flask, request, jsonify, render_template
from chroma import ChromaClient
from knowledge_graph import KnowledgeGraph

def main():
    # 获取当前文件的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取项目根目录（src的父目录）
    project_root = os.path.dirname(current_dir)
    # 设置模板目录的绝对路径
    template_dir = os.path.join(project_root, 'templates')
    
    app = Flask(__name__, template_folder=template_dir)
    app.debug = True  # 开启调试模式
    
    cm = ChromaClient("vector_database_name_3")
    
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/searchdb', methods=['GET'])
    def searchdb():
        query = request.args.get('query')
        print(query)
        return jsonify(cm.query(query, 5))

    app.run(debug=False, host='0.0.0.0', port=8008)

if __name__ == "__main__":
    main()
    
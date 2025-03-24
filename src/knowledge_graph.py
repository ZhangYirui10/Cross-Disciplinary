from neo4j import GraphDatabase
from main import get_from_chroma

class KnowledgeGraph:
    insertkey = []
    def __init__(self):
        self.driver = GraphDatabase.driver(
            # "bolt://neo4j_cross:7687",
            "bolt://localhost:7687",
            auth=("neo4j", "password")
        )
    
    def querytwoprof(self, keyword1, keyword2):
        with self.driver.session() as session:
            result = session.run("MATCH path = (a:Prof {name: '"+keyword1.replace("'", "\"")+"'})-[*]->()<-[*]-(b:Prof {name:'"+keyword2.replace("'", "\"")+"'}) UNWIND nodes(path) AS node WITH DISTINCT node RETURN node")
            return result.data()
    
    def queryConcept(self, keyword):
        with self.driver.session() as session:
            result = session.run("MATCH path = (a:Prof {name: '"+keyword.replace("'", "\"")+"'})-[*]->(c:Concept) WITH DISTINCT c return c")
            return result.data()
        
    def __replace_comma__(self, s):
        if s == None:
            return ""
        return s.replace("'", "\"")

    
    def insert(self, label, name, properties):
        # label = "Professor"
        # name = "Yao Lu"
        # properties = {"name":"Yao Lu", "birthday": "1983"}
        for i in properties:
            properties[i] = self.__replace_comma__(properties[i])
        

        if 'name' not in properties or self.check_node_exists(properties['name']):
            return
        propertiesList = []
        for i in properties:
            propertiesList.append(f"{i}: '{properties[i]}'")
        propertiesStr = ", ".join(propertiesList)

        with self.driver.session() as session:
            try:
                session.run(f"CREATE ({name}:{label} {{{propertiesStr}}})")
            except Exception as e:
                print(e)
                pass

    def check_node_exists(self, name):
        with self.driver.session() as session:
            try:
                name = self.__replace_comma__(name)
                query = "OPTIONAL MATCH (n {name: '"+name+"'}) RETURN n"
                result = session.run(query).data()
                if len(result)>1 or 'None' not in str(result):
                    return 1
                return 0
            except Exception as e:
                print(e)
                return 0
            
    def clear_knowledge_graph(self):
        with self.driver.session() as session:
            try:
                query = "MATCH (n) DETACH DELETE (n)"
                session.run(query)
            except Exception as e:
                print(e)
    
    def insert_connection(self, name1, name2, relation="HAVE"):
        with self.driver.session() as session:
            try:
                name1 = self.__replace_comma__(name1)
                name2 = self.__replace_comma__(name2)
                session.run("MATCH (a {name: '"+ name1+"'}), (b {name: '"+name2+"'}) CREATE (a)-[r:"+relation+"]->(b)")
            except Exception as e:
                print(e)
                pass

    def get_subgraph(self, query):
        with self.driver.session() as session:
            # 使用模糊匹配查找相关节点
            query = self.__replace_comma__(query)
            result = session.run("""
                MATCH (n)
                WHERE n.name CONTAINS $query
                MATCH path = (n)-[*1..3]-(related)
                UNWIND nodes(path) as node
                WITH DISTINCT node
                MATCH (node)-[r]-(connected)
                RETURN collect(DISTINCT {
                    id: node.name,
                    name: node.name,
                    type: labels(node)[0],
                    properties: properties(node)
                }) as nodes,
                collect(DISTINCT {
                    source: startNode(r).name,
                    target: endNode(r).name,
                    type: type(r)
                }) as links
            """, query=query)
            data = result.single()
            return {
                "nodes": data["nodes"] if data["nodes"] else [],
                "links": data["links"] if data["links"] else []
            }

if __name__ == "__main__":
    # kg = KnowledgeGraph()
    get_from_chroma("observability product")
    # print(kg.__replace_comma__("Yao's Lu"))
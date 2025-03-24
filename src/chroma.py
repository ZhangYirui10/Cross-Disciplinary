import chromadb
import time
from chromadb.utils import embedding_functions

# Default the embedding function diamension
# all-MiniLM-L6-v2 : 384
# sentence-t5-xl : 1024
# sentence-transformers/paraphrase-MiniLM-L6-v2 : 384


# diamension of the embedding can be padding
def embedding(text):
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    return ef(text)

class ChromaClient:
    def __init__(self, vector_name="vector_database_name_1"):
        self.vector_name = vector_name
        self.id = 100
        # self.chroma_client = chromadb.HttpClient(host="chroma", port=8000)
        self.chroma_client = chromadb.HttpClient(host="localhost", port=8000)
        # print(self.chroma_client.list_collections())
        # if self.vector_name in self.chroma_client.list_collections():
        #     self.chroma_client.delete_collection(name=self.vector_name)
        self.collection = self.chroma_client.get_or_create_collection(name=vector_name, embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2"))

    def add_document(self, content, metadata):
        self.collection.add(documents=[content], metadatas=[metadata], ids=[str(self.id)])
        self.id += 1

    def delete_document(self):
        self.chroma_client.delete_collection(name=self.vector_name)
        # print(type(self.collection.get()))  
        # print(self.collection.get())  
        # all_ids = [doc["id"] for doc in self.collection.get()["ids"]]

        # if len(all_ids) > 0:
        #     self.collection.delete(ids=all_ids)


    def query(self, query_text, top_k=3):
        retrieved_docs = self.collection.query(query_texts=[query_text], n_results=top_k)
        result = []
        for i in range(len(retrieved_docs['documents'][0])):
            # if retrieved_docs['distances'][0][i] < 0.5:

            result.append([retrieved_docs['documents'][0][i],retrieved_docs['distances'][0][i]])
        return result
    
if __name__ == "__main__":
    # time.sleep(5)
    # example usage: caculate the embedding of a sentence
    # print(embedding("observability product"))

    # knowledge_data = [
    #     {
    #         "content": "This paper investigates the impact of sales contest prize structures on sales performance (task) by addressing the untested marketing theory that contests should have multiple, rank-ordered prizes (problem), using laboratory and field economic experiments (method).", 
    #         "metadata": {"content": "This paper investigates the impact of sales contest prize structures on sales performance (task) by addressing the untested marketing theory that contests should have multiple, rank-ordered prizes (problem), using laboratory and field economic experiments (method)."}
    #     },
    #     {
    #         "content": "proemetheus is an observability product that integrates applications", 
    #         "metadata": {"content": "proemetheus is an observability product that integrates applications"}
    #     }
    # ]

    # time.sleep(3)

    cc = ChromaClient("vector_database_name_2")
    # cc.delete_document()
    for item in knowledge_data:
        cc.add_document(item["content"], item["metadata"])
    print(cc.query("observability product", top_k=1))

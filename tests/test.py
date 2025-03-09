import json
with open('src/article.txt', 'r') as fin:
    
    content = json.loads(fin.read())
    for i in content:
        print(i)
import json
import requests
import time

def get_openalex_id(name):
    base_url = "https://api.openalex.org/authors"
    params = {
        "search": name
    }
    response = requests.get(base_url, params=params)
    data = response.json()

    if data.get("results"):
        author = data["results"][0]  # 默认取第一个最匹配的
        return author["id"].split("/")[-1]
    return None

def process_professors(json_path, output_path):
    with open(json_path, "r", encoding="utf-8") as f:
        professors = json.load(f)

    for prof in professors:
        name = prof.get("name", "")
        if name:
            print(f"Searching OpenAlex ID for: {name}")
            openalex_id = get_openalex_id(name)
            print(openalex_id)
            prof["openalex_id"] = openalex_id or "Not Found"
            time.sleep(1)  # 避免 API 速率限制

    with open(output_path, "w", encoding="utf-8") as f_out:
        json.dump(professors, f_out, indent=2)
    print(f"Done! Results written to: {output_path}")

# 示例用法
process_professors("output.json", "nus_faculty_with_openalex_id.json")
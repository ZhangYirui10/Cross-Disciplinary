from openai import OpenAI
import os
import json

client = OpenAI(
    api_key="")

fail = []
def CallGPT(prompt):
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o-mini",
        )
        return chat_completion.choices[0].message.content if chat_completion.choices else ""
    except Exception as e:
        print(f"OpenAI API 调用错误: {e}")
        return ""


def ExtractPaper(task, problem, method, structured_results):
    # 组织 JSON 结构
    extracted_data = {
        "Entities": {
            "Task": task,
            "Problem": problem,
            "Method": method,
            "Results": structured_results
        }
    }

    # 将 JSON 转换为格式化字符串
    json_input = json.dumps(extracted_data, indent=4, ensure_ascii=False)

    prompt = (f"""{json_input}
- Extract only the key entities from the given input and categorize them into the appropriate categories.
- The extracted entities should be grouped under the following categories:
    - Task
    - Problem
    - Method
    - Results
- Each entity should be represented as a key-value pair where:
    - The key is the category name.
    - The value is the extracted entities.
- The extracted entities should be short and concise **keywords** (not full sentences or descriptions).
- The "Method" category should be a list containing only the key techniques used.
- The "Results" category should be structured as a dictionary with the following keys:
    - "Dataset": extracted professional dataset name entities.
    - "Model": extracted professional model name entities.
    - "Metric": extracted professional metric entities.
- The output should be a structured JSON object.
- Example format:
    {{
        "Entities": {{
            "Task": "Text Summarization",
            "Problem": ["Length control", "Exposure bias", "Loss-evaluation mismatch"],
            "Method": ["Sequence-to-sequence model", "Attention mechanism", "Reinforcement learning"],
            "Results": {{
                "Dataset": ["CNN/Daily Mail", "XSum"],
                "Model": ["BART", "Transformer"],
                "Metric": ["ROUGE-L", "ROUGE-2"]
            }}
        }}
    }}
- Ensure the output is valid JSON."""
)

    response = CallGPT(prompt)
    
    return response


if __name__ == "__main__":
    input_dir = "gptoutput_json"
    output_dir = "key_json_file"
    os.makedirs(output_dir, exist_ok=True)

    json_files = [f for f in os.listdir(input_dir) if f.endswith(".json")]  # 只处理 .json 文件

    for json_file in json_files:
        json_path = os.path.join(input_dir, json_file)
        json_file_filename = os.path.splitext(json_file)[0] + ".json"
        json_file_filepath = os.path.join(output_dir, json_file_filename)

        print(f"正在解析 {json_file} ...")
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        problem = data.get("Problem", "N/A")
        method = data.get("Method", "N/A")
        task = data.get("Task", "N/A")
        results_list = data.get("Results", [])

        structured_results = {
            "Dataset": [],
            "Model": [],
            "Metric": []
        }


        # 遍历 results_list 并归类
        for entry in results_list:
            if len(entry) == 4:  # 确保至少有4个字段
                dataset, model, metric, score = entry[:4]  # 只取前四个字段，避免额外数据
                structured_results["Dataset"].append(dataset)
                structured_results["Model"].append(model)
                structured_results["Metric"].append(metric)

        
        structured_results = json.dumps(structured_results, indent=4, ensure_ascii=False)

        # 生成 Prompt

        try:
            out = ExtractPaper(task, problem, method, structured_results)

            if not out:
                fail.append(json_file)
                print(f"警告：{json_file} 解析失败，跳过！")
                continue

            with open(json_file_filepath, "w", encoding="utf-8") as json_file_file:
                json_file_file.write(out)

            print(f"已解析并保存：{json_file_filepath}")

        except IOError as e:
            fail.append(json_file)
            print(f"文件处理错误 ({json_file})：{e}")
        except Exception as e:
            fail.append(json_file)
            print(f"解析 {json_file} 时发生未知错误：{e}")
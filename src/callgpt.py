from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("API_KEY"))


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


def ExtractPaper(fulltext):
    prompt = (
        f"{fulltext}\n"
        "- Provide 3-5 keywords summarizing the content, topic, and field of the paper.\n"
        "- Output as JSON: {'Keywords': ['Large Selective Kernel Network', 'Remote Sensing Object Detection', 'Deep Learning']}\n"
        "- Describe the problem the paper focuses on solving in max 50 words.\n"
        "- Output as JSON: {'Problem': 'Current methods fail to effectively incorporate the wide-range context of various objects in remote sensing images during object detection.'}\n"
        "- Summarize the method proposed in the paper in max 50 words.\n"
        "- Output as JSON: {'Method': 'The paper introduces a Large Selective Kernel Network that dynamically adjusts the receptive field in the feature extraction backbone to effectively model the context of different objects, giving improved object detection performance.'}\n"
        "- Determine whether the article proposes a new model and its name.\n"
        "- Output as JSON: {'Task': 'Remote sensing object detection'}\n"
        "- Identify the table with the main results (not ablation).\n"
        "- Output as JSON: {'Main Results Table': 'Table 2'}\n"
        "- Extract experimental datasets, evaluation metrics, and results.\n"
        "- Output as JSON list: {'Results': [[SQuAD, BERT, EM, 85.1%], [ImageNet, ResNet-50, Top-1 Accuracy, 76.2%], ...]}\n"
        "Output the extracted information as a single JSON object in the following format:\n\n"
        "{\n"
        '  "Keywords": ["keyword1", "keyword2", "keyword3"],\n'
        '  "Problem": "Short description of the problem",\n'
        '  "Method": "Short description of the method",\n'
        '  "Model": "Model Name" (or "NO" if no new model),\n'
        '  "Task": "Description of the task",\n'
        '  "Main Results Table": "Table X",\n'
        '  "Results": [\n'
        '    ["Dataset 1", "Model 1", "Metric 1", "Result 1"],\n'
        '    ["Dataset 2", "Model 2", "Metric 2", "Result 2"]\n'
        '  ]\n'
        "}\n\n"
        "Ensure the output is in valid JSON format."
    )

    response = CallGPT(prompt)
    
    return response

def extract_from_abstract(text):
    prompt = "This is the abstract of a research paper. analyze its content and summarize the key points. output in one sentence, describe the paper’s task, the problem it addresses, and the method it uses."
    prompt += f"<abstract>{text}</abstract>"
    return CallGPT(prompt)

if __name__ == "__main__":
    input_dir = "markdowns"
    output_dir = "gptoutput_json"
    os.makedirs(output_dir, exist_ok=True)

    md_files = [f for f in os.listdir(input_dir) if f.endswith(".md")]  # 只处理 .md 文件

    for md_file in md_files:
        md_path = os.path.join(input_dir, md_file)
        json_filename = os.path.splitext(md_file)[0] + ".json"
        json_filepath = os.path.join(output_dir, json_filename)

        print(f"正在解析 {md_file} ...")

        try:
            with open(md_path, "r", encoding="utf-8") as f:
                md_content = f.read()

            out = ExtractPaper(md_content)

            if not out:
                print(f"警告：{md_file} 解析失败，跳过！")
                continue

            with open(json_filepath, "w", encoding="utf-8") as json_file:
                json_file.write(out)

            print(f"已解析并保存：{json_filepath}")

        except IOError as e:
            print(f"文件处理错误 ({md_file})：{e}")
        except Exception as e:
            print(f"解析 {md_file} 时发生未知错误：{e}")
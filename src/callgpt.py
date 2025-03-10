from openai import OpenAI
import os

client = OpenAI(
    api_key= os.getenv("API_KEY") #  This is the default and can be omitted
)

def CallGPT(prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4o-mini",
    )
    try:
        return chat_completion.choices[0].message.content
    except:
        return ""
    
def ExtractPaper(fulltext):
    question = {
        "problem_prompt":f"Extract the paper with the fulltext",
        "method_prompt":f"Please provide the method section of the .",
        "metric_prompt":f"Please provide the metric section of the .",
        "dataset_prompt":f"Please provide the dataset section of the .",
        "task_prompt":f"Please provide the task section of the .",
        "model_prompt":f"Please provide the model section of the .",
        "results_prompt":f"Please provide the results section of the .",
        "innovation_prompt":f"Please provide the innovation section of the ."
    }
    question_list = list(question.values())
    prompt = f"{fulltext}\n" + "\n".join(question_list)
    return CallGPT(prompt)


if __name__ == "__main__":
    print(ExtractPaper("Ranking Outliers Using Symmetric Neighborhood"))
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
    
def ExtractPaper(title):
    question = {
        "problem_prompt":f"Extract the paper with the title: {title}",
        "method_prompt":f"Please provide the method section of the {title}.",
        "metric_prompt":f"Please provide the metric section of the {title}.",
        "dataset_prompt":f"Please provide the dataset section of the {title}.",
        "task_prompt":f"Please provide the task section of the {title}.",
        "model_prompt":f"Please provide the model section of the {title}.",
        "results_prompt":f"Please provide the results section of the {title}.",
        "innovation_prompt":f"Please provide the innovation section of the {title}."
    }
    for q in question:
        question[q] = CallGPT(question[q])

    return question


if __name__ == "__main__":
    print(ExtractPaper("Ranking Outliers Using Symmetric Neighborhood"))
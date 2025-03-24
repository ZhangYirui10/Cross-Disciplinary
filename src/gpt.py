from openai import OpenAI
import os
import re

client = OpenAI(
    api_key=os.getenv("API_KEY"))


def CallGPT(prompt):
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o",
        )
        return chat_completion.choices[0].message.content if chat_completion.choices else ""
    except Exception as e:
        print(f"OpenAI API 调用错误: {e}")
        return ""


def capability_analyze(project_description):
    prompt = f"""
    You are an expert in analyzing interdisciplinary research projects and identifying the technical capabilities required from Computer Science (CS) collaborators.

    Given a research project description—often in the field of biology, life sciences, or biomedical applications—your task is to extract the **top 3 key CS-related capabilities** that would be most important for collaborators from the computer science domain.

    Instructions:
    - Use **Computer Science terminology** only.
    - Do **not** include any biology-specific skills or domain knowledge.
    - Assume the collaborator has no expertise in biology, but is skilled at building algorithms, models, or systems.
    - Focus on general-purpose CS capabilities like "generative modeling", "multi-objective optimization", "representation learning", etc.
    - Output **exactly 3** capabilities, each followed by **one sentence explaining** how it contributes to the project.

    === Project Description ===
    {project_description}
    === Output Format ===

    1. [Capability Name]: Explanation...
    2. ...
    3. ...
    """
    response = CallGPT(prompt)
    keywords = re.findall(r"\d\.\s*(.*?):", response)
    
    return keywords, response

def get_final_answer(project_description, capability_list, capability_reasoning, capability_1_name, capability_1_results, capability_2_name, capability_2_results, capability_3_name, capability_3_results):
    prompt = f"""
    You are an expert in academic collaboration and faculty recommendation. Please help identify the most suitable researchers to collaborate on a specific project, based on capability-aligned search results across three technical dimensions.

    ### Project Description:
    {project_description}

    ### Required Capabilities (inferred by GPT based on the project description):
    Capabilities: {capability_list}

    Justifications for each capability:
    {capability_reasoning}

    ### Capability Search Results:

    #### Capability 1: {capability_1_name}
    {capability_1_results}

    #### Capability 2: {capability_2_name}
    {capability_2_results}

    #### Capability 3: {capability_3_name}
    {capability_3_results}

    ---

    Based on the capability-aligned results, please identify the **top three professors** most suitable for this project. For each professor, provide a **concise but detailed paragraph** that covers the following:

    - Start by summarizing which of the three capabilities this professor is strong in.  
    - Support this with **specific representative papers**, and explain how these works demonstrate the professor’s expertise in the corresponding areas.  
    - Then, based on their expertise and publication record, explain what **contributions** they can make to this specific project, and how their knowledge helps address the key goals or challenges in the project description.

    Please **rank** the three professors by overall suitability (1 to 3), and briefly compare their strengths and relevance to the project.

    Conclude with a final summary of why these three researchers are the **best fit** overall for the proposed project.
    """
    response = CallGPT(prompt)
    
    return response
    


if __name__ == "__main__":

    project_description = """
AI-informed design of antimicrobial
peptides for novel bacteria-trapping
nanonets 
• Accurate prediction of AMP sequences
capable of forming amyloid fibrils
• Identification of peptide-membrane
interactions which appear to be central to the
connection between antimicrobial activity
and amyloidogenicity of AMPs
• Prediction of large-scale self-assemblies of
AMP nanonets and other forms of
assemblies  
Project descriptions
Antimicrobial peptides (AMPs) are produced by several species as a first line of defence
against microbial infection. AMPs can have broad-spectrum efficacy against microbes
and may even have a lower likelihood to induce bacterial resistance. Hence, AMPs
have been widely studied as potential antibiotics, to be used either as alternatives to or
in combination with small molecule antibiotics. Interestingly, several AMPs self-
assemble into ordered fibrils with well-defined structures characteristic of amyloid fibrils.
There appears to be a link between anti-microbial activity and amyloidogenicity of
certain peptides. This project aims to utilize AI/ML to explore this relationship and
design functional amyloid-based AMPs.
Several factors appear to influence the relationship between anti-microbial activity and
amyloidogenicity, including peptide sequence, termination, secondary structure
propensity, solution environment and peptide-membrane interaction. Given the large
chemical space, it has been difficult to attribute specific parameters to an AMPs
propensity to form amyloids. Hence, a combined computational and experimental
approach is proposed.
Of the >15,000 AMPs that have been identified and hosted on publicly accessible
databases, only a few are known to be amyloidogenic. Several more AMPs could be
fibril forming and there may be unidentified sequences that are both anti-microbial and
amyloidogenic. In striking contrast to the AMP database, the database for known
amyloidogenic peptides is much smaller. 
"""
    response = capability_analyze(project_description)
    cleaned_list = [s.strip("*") for s in response]
    print(cleaned_list)

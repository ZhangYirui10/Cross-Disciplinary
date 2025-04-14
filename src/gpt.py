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

    Please identify the **top three professors** most suitable for this project. Select the professors based on a holistic comparison across all three capabilities and their demonstrated relevance in the provided information. Do not intentionally vary the selection across runs—choose the three professors who are most objectively and consistently suitable. 
    For each professor, provide structured information under the following headings. You must follow the output format strictly. Each professor's section must contain the **professor's full name**, their **relevant research**, a list of **selected publications (with paper titles)**, and their **potential contribution** to the project.
    ---

    Output Format (use EXACTLY this layout for each professor):

    Professor: <Full Name>

    Relevant Research:
    <One paragraph summarizing the professor's demonstrated research areas and strengths, with supporting context or examples>

    Selected Publications: 
    1. "<Paper Title 1>" – <One sentence on how it supports the capability>  
    2. "<Paper Title 2>" – <One sentence on how it supports the capability>  
    (Include up to 3 papers. Use quotes for the paper titles. Do not fabricate any publications—only include those explicitly mentioned in the provided search results.)

    Potential Contribution to Project:  
    <One paragraph explaining what the professor can bring to the project based on their expertise>

    ---
    """
    response = CallGPT(prompt)
    
    return response

def get_professor_analysis(input_data):
    """
    Analyzes professors based on their relevance to a project without making selection decisions.
    The professors are already selected and ranked by the scoring algorithm.
    
    Args:
        input_data (dict): Contains project description, capabilities, professors and papers
    
    Returns:
        str: Analysis of the professors' relevance to the project
    """
    project_description = input_data["project_description"]
    capabilities = input_data["capabilities"]
    capability_reasoning = input_data["capability_reasoning"]
    professors = input_data["professors"]
    papers = input_data["papers"]
    
    # Format professors with their scores
    professors_text = ""
    for prof in professors:
        prof_info = f"Professor: {prof.get('name', 'Unknown')}\n"
        prof_info += f"Score: {prof.get('score', 0)}\n"
        prof_info += f"Bio: {prof.get('Bio', 'N/A')}\n"
        prof_info += f"Research Areas: {prof.get('researcharea', 'N/A')}\n"
        prof_info += f"Interests: {prof.get('interests', 'N/A')}\n\n"
        professors_text += prof_info
    
    # Format papers
    papers_text = ""
    for paper in papers:
        paper_info = f"Title: {paper.get('name', 'Unknown')}\n"
        paper_info += f"Abstract: {paper.get('abstract', 'N/A')}\n\n"
        papers_text += paper_info
    
    prompt = f"""
    You are an expert in academic collaboration. You need to analyze professors' relevance to a specific project based on their profiles and papers.
    
    ### Project Description:
    {project_description}
    
    ### Required Capabilities (inferred based on the project description):
    {capabilities}
    
    Justifications for these capabilities:
    {capability_reasoning}
    
    ### Selected Professors (already ranked by algorithm based on relevance score):
    {professors_text}
    
    ### Relevant Papers:
    {papers_text}
    
    ---
    
    For each professor, provide an analysis addressing the following points:
    
    1. How their expertise aligns with the required capabilities
    2. What specific contributions they could make to the project
    3. How their previous work (papers, research areas) relates to the project
    
    Present your analysis in a structured format. Do not attempt to re-rank or select professors - they have already been ranked by a scoring algorithm.
    
    Keep your analysis factual and based on the provided information. For each professor, explain why they received a high relevance score.
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

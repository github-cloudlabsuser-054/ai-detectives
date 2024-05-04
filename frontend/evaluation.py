import openai
from openai import AzureOpenAI
import pandas as pd

# Set OpenAI API key for Azure

client = AzureOpenAI(
    api_key="c8751add6d5f406a95f91505279e33c6",
    api_version="2023-07-01-preview",
    azure_endpoint="https://hsbc-aiml-team-resource.openai.azure.com/"
)

# openai.api_type = "azure"
# openai.api_base = "https://hsbc-aiml-team-resource.openai.azure.com/"
# openai.api_version = "2023-07-01-preview"
# openai.api_key = "c8751add6d5f406a95f91505279e33c6"

# Evaluation prompt template based on G-Eval
EVALUATION_PROMPT_TEMPLATE = """
You will be given one summary written for an article. Your task is to provide review comments and to rate on one metric.
output should include both rating and review comments in max 2-3 lines.Please explain your reasoning.
Please make sure you read and understand these instructions very carefully. 
Please keep this document open while reviewing, and refer to it as needed.Please make sure that output format is strictly followed.

Evaluation Criteria:

{criteria}

Evaluation Steps:

{steps}

Example:

Source Text:

{document}

Summary:

{summary}

Evaluation Form (EVALs ONLY):

- {metric_name}
"""

# Metric 1: Relevance

RELEVANCY_EVAL_CRITERIA = """
Relevance(1-5) - selection of important content from the source. \
The summary should include only important information from the source document. \
Annotators were instructed to penalize summaries which contained redundancies and excess information.
"""

RELEVANCY_EVAL_STEPS = """
1. Read the summary and the source document carefully.
2. Compare the summary to the source document and identify the main points of the article.
3. Assess how well the summary covers the main points of the article, and how much irrelevant or redundant information it contains.
4. provide review comments and justification in max 5 lines.
5. Assign a relevance score from 1 to 5 in a new line with bold font.
6. Please make sure that output format is strictly followed.output should be in the below format:
<li>{review comment}</li><li>{score}</li>
 
"""

# Metric 2: Coherence

COHERENCE_EVAL_CRITERIA = """
Coherence - the collective quality of all sentences. \
We align this dimension with the DUC quality question of structure and coherence \
whereby "the summary should be well-structured and well-organized. \
The summary should not just be a heap of related information, but should build from sentence to a\
coherent body of information about a topic."
"""

COHERENCE_EVAL_STEPS = """
1. Read the article carefully and identify the main topic and key points.
2. Read the summary and compare it to the article. Check if the summary covers the main topic and key points of the article,
and if it presents them in a clear and logical order.
3. provide review comments and justification in max 5 lines.
4. Assign a score for coherence on a scale of 1 to 5, where 1 is the lowest and 5 is the highest based on the Evaluation Criteria in
in a new line with bold font
5. Please make sure that output format is strictly followed.output should be in the below format:
<li>{review comment}</li><li>{score}</li>
"""

# Metric 3: Consistency

CONSISTENCY_EVAL_CRITERIA = """
Consistency(1-5) - the factual alignment between the summary and the summarized source. \
A factually consistent summary contains only statements that are entailed by the source document. \
Annotators were also asked to penalize summaries that contained hallucinated facts.
"""

CONSISTENCY_EVAL_STEPS = """
1. Read the article carefully and identify the main facts and details it presents.
2. Read the summary and compare it to the article. Check if the summary contains any factual errors that are not supported by the article.
3. provide review comments and justification in max 5 lines.
4. Assign a score for consistency based on the Evaluation Criteria in a new line with bold font.
5. Please make sure that output format is strictly followed.output should be in the below format:
<li>{review comment}</li><li>{score}</li>
"""

# Metric 4: Fluency

FLUENCY_EVAL_CRITERIA = """
Fluency: the quality of the summary in terms of grammar, spelling, punctuation, word choice, and sentence structure.
1. Poor. The summary has many errors that make it hard to understand or sound unnatural.
2. Fair. The summary has some errors that affect the clarity or smoothness of the text, but the main points are still comprehensible.
3. Good. The summary has few or no errors and is easy to read and follow.
"""

FLUENCY_EVAL_STEPS = """
1. Read the summary and evaluate its fluency based on the given criteria. provide review comments and justification in max 5 lines.
2. Assign a fluency score from 1 to 3 in a new line with bold font.
3. Please make sure that output format is strictly followed.output should be in the below format:
<li>{review comment}</li><li>{score}</li>
"""


def get_geval_score(
    criteria: str, steps: str, document: str, summary: str, metric_name: str
):
    prompt = EVALUATION_PROMPT_TEMPLATE.format(
        criteria=criteria,
        steps=steps,
        metric_name=metric_name,
        document=document,
        summary=summary,
    )

    
    response = client.chat.completions.create(
        model="hsbchackathongpt432k2023",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=2500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    #print(response)
    return response.choices[0].message.content


evaluation_metrics = {
    "Relevance": (RELEVANCY_EVAL_CRITERIA, RELEVANCY_EVAL_STEPS),
    "Coherence": (COHERENCE_EVAL_CRITERIA, COHERENCE_EVAL_STEPS),
    "Consistency": (CONSISTENCY_EVAL_CRITERIA, CONSISTENCY_EVAL_STEPS),
    "Fluency": (FLUENCY_EVAL_CRITERIA, FLUENCY_EVAL_STEPS),
}



def get_eval_table(original_doc, summary):
    summaries = {"Summary 1": summary}

    data = {"Evaluation Type": [], "Summary Type": [],"Review Comment":[]}

    for eval_type, (criteria, steps) in evaluation_metrics.items():
        for summ_type, summary in summaries.items():
            data["Evaluation Type"].append(eval_type)
            data["Summary Type"].append(summ_type)
            result = get_geval_score(criteria, steps, original_doc, summary, eval_type)
            review_comment = result.strip()
            if len(review_comment) == 0:
                review_comment = "No Review Comments available"
            data["Review Comment"].append(review_comment)
    print(len(data["Evaluation Type"]),len(data["Summary Type"]),len(data["Review Comment"]))
    pivot_df = pd.DataFrame(data, index=None).pivot(
        index="Evaluation Type", columns="Summary Type", values="Review Comment")
    return pivot_df
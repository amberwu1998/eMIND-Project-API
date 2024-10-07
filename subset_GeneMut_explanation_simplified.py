import pandas as pd
from openai import OpenAI
import numpy as np
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score

def Validate_eMIND_Results(single_row):
    prompt_template = f"""
# Context #
The eMIND is a text-mining system developed to extract information on the impact of variants on Alzheimer’s disease and other relevant diseases. 
############
# Role #
You are a biologist and know well about gene and mutation information.
############
# Task #
You are given a table from eMIND with several columns. Your job is to verify if the mutation listed in Column 2 (in its normalized form) is mentioned in title and abstract in Column 8, and if this mutation is linked to the gene (in its normalized form) listed in Column 6.
############
#Criteria#
Mutation Matching: The mutation in Column 8 may be described differently than in Column 2. Recognize them as the same mutation, even if the names differ. For example, if Column 8 mentions "Arctic mutation" and Column 2 lists "p.Glu693Gly," these should be recognized as the same.
Gene Matching: The gene in Column 6 might not be explicitly named in Column 8. However, if Column 8 mentions a related subunit, receptor, or any alternative name that corresponds to the gene in Column 6, consider it a match.
Alternative Names and Symbols: Be aware that alternative names or symbols may be used for genes instead of normalized representation. Identify if they refer to the same gene.
Mutation IDs: If a mutation ID starting with "rs" is used, link it to the mutation name.
Gene-Mutation Relationship: Focus on verifying the gene-mutation relationship, irrespective of the disease context. Ignore disease references.
Careful Reading: Read Column 2, Column 6, and Column 8 carefully. Ensure that no information is ignored or misinterpreted, and pay close attention to similar strings and numbers.
############
#Response#
Provide a simple "yes" or "no" answer.
Explain your reasoning for the answer.
Separate the answer and explanation by &&&.
{single_row}
"""
    prompt = prompt_template.format(single_row=single_row)

    client = OpenAI(
        api_key=""
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a skilled bioinformatics engineer."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.2,
    )
    return response


data = pd.read_excel("/Users/amberwu/Desktop/Summer Internship 2024/eMIND API/subset_GeneMut_Abstract_simplified.xlsx")

# # Store the original column order
# original_columns = data.columns.tolist()

answer_list = []
exp_list = []
for _, row in data.iterrows():
    single_row = "\t".join([str(x) for x in row])
    response = Validate_eMIND_Results(single_row)
    summary = response.choices[0].message.content
    # print(response.choices[0].message.content)
    summary = str(summary)
    Answer = summary.split('&&&')[0]
    Exp = summary.split('&&&')[1]
    answer_list.append(Answer)
    exp_list.append(Exp)
    print(Answer, Exp)

# Update the "Validation Result" column with the summaries
data['validation result'] = answer_list
data['explanation'] = exp_list

# # Reorder the columns to match the original order, with new columns at the end
# new_column_order = original_columns + ['validation result', 'explanation']
# data = data[new_column_order]

# Save the updated DataFrame back to an Excel file
data.to_excel("/Users/amberwu/Desktop/Summer Internship 2024/eMIND API/Simplified_GeneMut_exp_results.xlsx", index=False)

# Correct output (ground truth)
correct_output = """yes yes yes yes yes yes yes yes no no no yes yes yes yes yes yes yes yes yes yes yes yes yes yes yes yes yes yes yes yes yes no yes yes yes yes yes yes yes yes yes yes yes yes yes yes yes no no yes yes yes yes yes yes yes yes yes yes yes yes no yes yes yes yes yes yes yes yes yes yes yes yes yes""".split()

# Convert the string to a list of individual answers and ensure they are lowercase
correct_output = [answer.lower().strip() for answer in correct_output]

# # Print original answer_list for debugging
# print("\nOriginal answer_list:")
# print(answer_list)

# Ensure answer_list only contains 'yes' or 'no' without changing the original answers
# Also strip any trailing spaces
answer_list_binary = ['yes' if answer.lower().strip() == 'yes' else 'no' for answer in answer_list]

# Calculate confusion matrix
cm = confusion_matrix(correct_output, answer_list_binary, labels=["yes", "no"])

# Print confusion matrix
print("\nConfusion Matrix:")
print("              Predicted")
print("             Yes    No")
print(f"Actual Yes   {cm[0][0]:<6} {cm[0][1]:<6}")
print(f"       No    {cm[1][0]:<6} {cm[1][1]:<6}")

# Calculate accuracy
accuracy = accuracy_score(correct_output, answer_list_binary)
print(f"\nAccuracy: {accuracy:.2f}")

# # Print some debug information
# print(f"\nLength of correct_output: {len(correct_output)}")
# print(f"Length of answer_list: {len(answer_list)}")
# print("\nFirst few items in correct_output:", correct_output[:5])
# print("First few items in answer_list:", [a.strip() for a in answer_list[:5]])
# print("First few items in answer_list_binary:", answer_list_binary[:5])
#
# # Count 'yes' and 'no' in both lists
# print(f"\nCorrect output - Yes: {correct_output.count('yes')}, No: {correct_output.count('no')}")
# print(f"Answer list - Yes: {answer_list_binary.count('yes')}, No: {answer_list_binary.count('no')}")

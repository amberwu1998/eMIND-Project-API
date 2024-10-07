import pandas as pd
from openai import OpenAI
import numpy as np
from sklearn.metrics import confusion_matrix

def Validate_eMIND_Results(single_row):
    prompt_template = f"""
# Context #
The eMIND tool is designed to extract information on the impact of variants on Alzheimer's disease and other related diseases. 
The attached file contains a subset of eMIND's extraction output.

############

# Objective #
Read the attached file and determine if the disease information in column 8 is mentioned in the title and abstract (column 10) and is related to the mutation in column 4. 
Return "yes" if both conditions are met; otherwise, return "no." 
Do not include any explanations, additional context, or other content in your reply.

############

# Requirements #
1. Validate only the data in column 8.
2. Ensure the disease in column 8 is specific and represents an actual disease, accounting for variations or abbreviations in names.
3. If column 8 contains "Not Applicable," return “no."
4. Maintain consistent output for identical prompts.

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


data = pd.read_excel("Disease_Val_FullTablew_Abstract_N_AinBlanks.xlsx")

# Ensure the 'Validation Result' column is of string data type
data['Validation Result'] = data['Validation Result'].astype(str)

answer_list = []
for _, row in data.iterrows():
    single_row = "\t".join([str(x) for x in row])
    response = Validate_eMIND_Results(single_row)
    summary = response.choices[0].message.content
    # print(response.choices[0].message.content)
    answer_list.append(summary)

# Update the "Validation Result" column with the summaries
data['Validation Result'] = answer_list

# Save the updated DataFrame back to an Excel file
data.to_excel("Updated_Disease_Val_FullTablew_Abstract.xlsx", index=False)

# Correct output
correct_output = """yes yes yes yes yes yes yes yes yes yes yes yes yes yes yes yes yes yes yes yes yes yes yes no no no yes yes yes yes yes yes yes yes yes yes yes yes yes yes yes yes yes yes yes yes no no no no no no no yes no no yes yes no no no no no no no no no no no no no no no no yes no yes no no""".split()

# Calculate confusion matrix
cm = confusion_matrix(correct_output, answer_list, labels=["yes", "no"])

# Print confusion matrix
print("\nConfusion Matrix:")
print("              Predicted")
print("             Yes    No")
print(f"Actual Yes   {cm[0][0]:<6} {cm[0][1]:<6}")
print(f"       No    {cm[1][0]:<6} {cm[1][1]:<6}")

# Calculate accuracy
accuracy = np.sum(np.diag(cm)) / np.sum(cm)
print(f"\nAccuracy: {accuracy:.2f}")

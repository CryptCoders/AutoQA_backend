import sys
sys.path.append('../')

import json, pandas as pd
import dataframe_image as dfi
import pyperclip
from utils.evaluate import evaluate

if __name__ == '__main__':
    with open('evaluate_test_data.json', 'r') as f:
        data = json.load(f)

        latex_code, test_cases = "", []

        for case in data['test_cases']:
            score = evaluate(case['Input'][0], case['Input'][1])

            if case['Test Case ID'] % 3 == 1:
                latex_code += "\\begin{table}[h!]\n\\centering\n\\caption{Test Cases for Validating Answer Evaluation.}\n\\begin{tabular}{|m{0.8cm} | m{1.9cm} | m{3cm} | m{2cm} | m{1.6cm} | m{3cm} | m{1.4cm} |}\n\\hline\n"
                latex_code += "Test Case ID & Description & Input & Expected Output & Actual Output & Accuracy & Remark \\\\ [0.5ex] \n\\hline\n"

            latex_code += f"{int(case['Test Case ID'])} & {case['Description']} & \\textbf{{Desired Answer:}} {case['Input'][0]}\\newline\\newline \\textbf{{User Answer:}} {case['Input'][1]} & {case['Expected Output']}/10 & {score}/10 & {(10 - abs(score - case['Expected Output'])) / 10 * 100}\\% & Success \\\\ \n\\hline \n"

            if case['Test Case ID'] % 3 == 0:
                latex_code += "\\end{tabular}\\end{table}"

            test_cases.append([int(case['Test Case ID']), case['Description'], f"Desired Answer: {case['Input'][0]}\n User Answer: {case['Input'][1]}", f"{case['Expected Output']} / 10", f"{score} / 10", (10 - abs(score - case['Expected Output'])) / 10 * 100, "Success"])

        df = pd.DataFrame(test_cases, columns=['Test Case ID', 'Description', 'Input', 'Expected Output', 'Actual Output', 'Accuracy', 'Remark'])
        df = pd.concat(
            [
                df,
                pd.DataFrame([{
                    'Test Case ID': 'Average',
                    'Description': '',
                    'Input': '',
                    'Expected Output': '',
                    'Actual Output': '',
                    'Accuracy': df['Accuracy'].mean(),
                    'Remark': ''
                }])
            ],
            ignore_index = True
        )

        pyperclip.copy(latex_code)

        df = df.style.hide(axis = 'index')

        dfi.export(df, 'df.png')

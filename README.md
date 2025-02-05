# Mental Health in the Tech Industry

Mental health is a critical component of overall well-being. This analysis seeks to leverage a dataset (https://www.kaggle.com/datasets/anth7310/mental-health-in-the-tech-industry) from Kaggle to better understand the sociodemographic features of survey respondents and their mental health experiences. By querying the dataset (`mental_health.sqlite`) with SQLite and analyzing the data in Python, this project aims to uncover meaningful insights about mental health prevalence.

## Dataset

The final loaded dataset contains the following features:
- **year**: Specifies the year the survey was conducted (e.g., 2014, 2016, 2017, 2018, 2019).
- **survey**: Indicates the specific survey from which the data was collected.
- **question_id**: An identifier for each question in the survey.
- **question_text**: The full text of the question asked in the survey.
- **user_id**: An identifier for each respondent participating in the survey.
- **answer_text**: The respondent's answer to the corresponding survey question.

## Installation

To run the code, follow these steps:

1. Navigate to the directory where you will save project files clone the repository:
```bash
git clone https://github.com/TuringCollegeSubmissions/slauri-DS.v3.2.1.5
```
2. Create the virtual environment (for example, venv):
```bash
python -m venv venv
```
3. Activate the virtual environment:
```bash
venv\Scripts\activate
```
4. Install the needed libraries using pip:
```bash
pip install -r requirements.txt
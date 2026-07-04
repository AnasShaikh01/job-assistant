from app.candidate.extractors.education import EducationExtractor

text = """
Bachelor of Engineering in Computer Science
XYZ University
2020 - 2024
CGPA: 8.75

Master of Science in Data Science
ABC University
2024 - Present
GPA: 9.2
"""

extractor = EducationExtractor()

result = extractor.extract(text)

for education in result:
    print(education.model_dump())
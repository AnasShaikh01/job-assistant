from app.candidate.extractors.certification import CertificationExtractor

text = """
AWS Certified Solutions Architect – Associate
Amazon Web Services
Issued: Jan 2024
https://www.credly.com/badges/aws-certification

Microsoft Azure Fundamentals
Issued by Microsoft
May 2023
https://learn.microsoft.com/certifications/azure-fundamentals

Google Data Analytics Professional Certificate
Coursera
2022
https://coursera.org/verify/google-data-analytics
"""

extractor = CertificationExtractor()

certifications = extractor.extract(text)

for cert in certifications:
    print(cert.model_dump())
    print("-" * 80)
from app.candidate.extractors.experience import ExperienceExtractor

text = """
Software Engineer
ABC Technologies
Jan 2023 - Present

Developed REST APIs using FastAPI.
Dockerized services.
Worked on PostgreSQL and Redis.
"""

extractor = ExperienceExtractor()

result = extractor.extract(text)

for exp in result:
    print(exp.model_dump())
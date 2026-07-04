from app.candidate.extractors.project import ProjectExtractor

text = """
AI Resume Analyzer
Developed an AI-powered ATS Resume Analyzer using FastAPI, Python and PostgreSQL.
Implemented semantic skill matching using Sentence Transformers.
GitHub: https://github.com/AnasShaikh01/ai-resume-analyzer
Live: https://ai-resume-analyzer.vercel.app

Job Assistant
Built an AI Job Assistant using FastAPI, Docker, Redis and PostgreSQL.
Implemented Resume Parsing, Candidate Knowledge Base and ATS Resume Generation.
GitHub: https://github.com/AnasShaikh01/job-assistant
Live: https://job-assistant.vercel.app
"""

extractor = ProjectExtractor()

projects = extractor.extract(text)

for project in projects:
    print(project.model_dump())
    print("-" * 80)
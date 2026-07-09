from app.candidate.extractors.links import LinksExtractor

text = """
GitHub: https://github.com/AnasShaikh01
LinkedIn: https://linkedin.com/in/anas-shaikh
Portfolio: https://anas.vercel.app
Blog: https://medium.com/@anas
"""

links = LinksExtractor.extract(text)

print(links.model_dump())
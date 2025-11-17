from app.services.pdf_parser import PDFParser

# Test the parser
parser = PDFParser()

# You'll need a sample PDF - we'll add some later
# For now, just verify the code runs

print("PDF Parser initialized successfully!")
print(f"Email pattern: {parser.email_pattern.pattern}")
print(f"Phone pattern: {parser.phone_pattern.pattern}")
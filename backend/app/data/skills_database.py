"""
Comprehensive skills database for resume analysis.
Categorized by domain and skill type.
"""

TECHNICAL_SKILLS = {
    "programming_languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "ruby",
        "go", "rust", "swift", "kotlin", "scala", "r", "matlab", "php",
        "perl", "shell", "bash", "powershell", "sql", "html", "css"
    ],
    
    "frameworks_libraries": [
        "react", "angular", "vue", "svelte", "next.js", "nuxt.js",
        "django", "flask", "fastapi", "spring", "spring boot", "express",
        "node.js", "nest.js", "rails", "laravel", "asp.net",
        "pytorch", "tensorflow", "keras", "scikit-learn", "pandas",
        "numpy", "scipy", "opencv", "nltk", "spacy", "hugging face",
        "transformers", "langchain", "jquery", "bootstrap", "tailwind"
    ],
    
    "databases": [
        "mysql", "postgresql", "mongodb", "redis", "cassandra", "dynamodb",
        "oracle", "sql server", "sqlite", "elasticsearch", "neo4j",
        "firebase", "supabase", "mariadb", "couchdb"
    ],
    
    "cloud_devops": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
        "jenkins", "gitlab ci", "github actions", "terraform", "ansible",
        "circleci", "travis ci", "heroku", "vercel", "netlify",
        "digital ocean", "cloudflare", "nginx", "apache"
    ],
    
    "ai_ml": [
        "machine learning", "deep learning", "neural networks", "nlp",
        "natural language processing", "computer vision", "reinforcement learning",
        "generative ai", "llm", "large language models", "bert", "gpt",
        "transformers", "cnn", "rnn", "lstm", "gru", "gan", "vae",
        "supervised learning", "unsupervised learning", "transfer learning",
        "feature engineering", "model deployment", "mlops", "a/b testing"
    ],
    
    "data_tools": [
        "tableau", "power bi", "looker", "metabase", "jupyter",
        "apache spark", "hadoop", "kafka", "airflow", "dbt",
        "snowflake", "databricks", "bigquery", "redshift"
    ],
    
    "version_control": [
        "git", "github", "gitlab", "bitbucket", "svn", "mercurial"
    ],
    
    "testing": [
        "pytest", "unittest", "jest", "mocha", "selenium", "cypress",
        "junit", "testng", "postman", "rest assured", "cucumber"
    ],
    
    "other_technical": [
        "rest api", "graphql", "grpc", "microservices", "agile", "scrum",
        "ci/cd", "tdd", "bdd", "oauth", "jwt", "websockets", "mqtt",
        "etl", "data pipeline", "system design", "architecture",
        "linux", "unix", "windows server", "blockchain", "web3",
        "ethereum", "solidity", "smart contracts"
    ]
}

SOFT_SKILLS = [
    # Leadership
    "leadership", "team management", "mentoring", "coaching", "delegation",
    "strategic planning", "decision making", "conflict resolution",
    
    # Communication
    "communication", "presentation", "public speaking", "technical writing",
    "documentation", "stakeholder management", "cross-functional collaboration",
    "negotiation", "active listening",
    
    # Problem Solving
    "problem solving", "critical thinking", "analytical thinking",
    "troubleshooting", "debugging", "root cause analysis", "innovation",
    "creativity", "research",
    
    # Project Management
    "project management", "time management", "prioritization", "planning",
    "organization", "multitasking", "deadline management", "risk management",
    
    # Interpersonal
    "teamwork", "collaboration", "interpersonal skills", "empathy",
    "adaptability", "flexibility", "emotional intelligence", "patience",
    
    # Work Ethic
    "self-motivated", "proactive", "reliable", "detail-oriented",
    "results-driven", "goal-oriented", "accountable", "professional",
    "work ethic", "initiative"
]

DOMAINS = [
    "software engineering", "data science", "machine learning",
    "artificial intelligence", "web development", "mobile development",
    "devops", "cloud computing", "cybersecurity", "data engineering",
    "frontend", "backend", "full stack", "embedded systems",
    "game development", "blockchain", "product management",
    "ui/ux design", "quality assurance", "site reliability"
]

# Common job titles for context
JOB_TITLES = [
    "software engineer", "senior software engineer", "staff engineer",
    "principal engineer", "engineering manager", "tech lead",
    "data scientist", "senior data scientist", "ml engineer",
    "ai engineer", "data engineer", "data analyst",
    "frontend developer", "backend developer", "full stack developer",
    "mobile developer", "ios developer", "android developer",
    "devops engineer", "sre", "cloud engineer", "platform engineer",
    "product manager", "technical product manager", "project manager",
    "qa engineer", "test engineer", "security engineer",
    "research scientist", "applied scientist", "research engineer"
]

# Education-related keywords
EDUCATION_KEYWORDS = [
    "bachelor", "master", "phd", "doctorate", "associate",
    "b.s.", "b.a.", "m.s.", "m.a.", "mba", "ph.d.",
    "computer science", "software engineering", "data science",
    "electrical engineering", "computer engineering", "mathematics",
    "statistics", "physics", "information technology", "information systems"
]

# Company indicators (for experience parsing)
COMPANY_INDICATORS = [
    "inc", "inc.", "llc", "ltd", "corporation", "corp", "company",
    "technologies", "systems", "solutions", "consulting", "services"
]


def get_all_technical_skills():
    """Flatten all technical skills into a single list."""
    all_skills = []
    for category in TECHNICAL_SKILLS.values():
        all_skills.extend(category)
    return list(set(all_skills))


def get_all_skills():
    """Get all skills (technical + soft)."""
    return get_all_technical_skills() + SOFT_SKILLS


def get_skill_category(skill):
    """Determine the category of a skill."""
    skill_lower = skill.lower()
    
    # Check technical categories
    for category, skills in TECHNICAL_SKILLS.items():
        if skill_lower in skills:
            return f"technical_{category}"
    
    # Check soft skills
    if skill_lower in SOFT_SKILLS:
        return "soft_skill"
    
    return "unknown"
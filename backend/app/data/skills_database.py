"""
Comprehensive skills database for resume analysis.
Categorized by domain and skill type.
Enhanced with acronyms, synonyms, and variations.
"""

TECHNICAL_SKILLS = {
    "programming_languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "ruby",
        "go", "golang", "rust", "swift", "kotlin", "scala", "r", "matlab", 
        "php", "perl", "shell", "bash", "powershell", "sql", "html", "css",
        "dart", "elixir", "haskell", "lua", "objective-c", "vb.net", "groovy"
    ],
    
    "frameworks_libraries": [
        "react", "react.js", "reactjs", "angular", "angularjs", "vue", "vue.js",
        "svelte", "next.js", "nextjs", "nuxt.js", "gatsby",
        "django", "flask", "fastapi", "spring", "spring boot", "express",
        "node.js", "nodejs", "nest.js", "rails", "ruby on rails", "laravel", "asp.net",
        "pytorch", "tensorflow", "keras", "scikit-learn", "sklearn", "pandas",
        "numpy", "scipy", "opencv", "nltk", "spacy", "hugging face", "huggingface",
        "transformers", "langchain", "jquery", "bootstrap", "tailwind", "tailwindcss",
        "material-ui", "mui", "chakra ui", "ant design", "redux", "mobx", "zustand",
        "graphql", "apollo", "prisma", "sequelize", "mongoose", "sqlalchemy"
    ],
    
    "databases": [
        "mysql", "postgresql", "postgres", "mongodb", "mongo", "redis", 
        "cassandra", "dynamodb", "oracle", "sql server", "sqlite", 
        "elasticsearch", "elastic", "neo4j", "firebase", "supabase", 
        "mariadb", "couchdb", "influxdb", "timescaledb", "cockroachdb"
    ],
    
    "cloud_devops": [
        "aws", "amazon web services", "azure", "microsoft azure", "gcp", 
        "google cloud", "google cloud platform", "docker", "kubernetes", "k8s",
        "jenkins", "gitlab ci", "github actions", "terraform", "ansible",
        "circleci", "travis ci", "heroku", "vercel", "netlify",
        "digital ocean", "cloudflare", "nginx", "apache", "vagrant",
        "helm", "istio", "prometheus", "grafana", "datadog", "new relic"
    ],
    
    "ai_ml": [
        "machine learning", "ml", "deep learning", "dl", "neural networks",
        "nlp", "natural language processing", "computer vision", "cv",
        "reinforcement learning", "rl", "generative ai", "gen ai",
        "llm", "large language models", "bert", "gpt", "transformers",
        "cnn", "convolutional neural networks", "rnn", "recurrent neural networks",
        "lstm", "gru", "gan", "generative adversarial networks", "vae",
        "supervised learning", "unsupervised learning", "transfer learning",
        "feature engineering", "model deployment", "mlops", "a/b testing",
        "hyperparameter tuning", "cross-validation", "ensemble methods",
        "random forest", "xgboost", "lightgbm", "gradient boosting"
    ],
    
    "data_tools": [
        "tableau", "power bi", "looker", "metabase", "jupyter", "jupyter notebook",
        "apache spark", "pyspark", "hadoop", "kafka", "airflow", "dbt",
        "snowflake", "databricks", "bigquery", "redshift", "hive", "presto",
        "pandas", "numpy", "matplotlib", "seaborn", "plotly", "d3.js"
    ],
    
    "version_control": [
        "git", "github", "gitlab", "bitbucket", "svn", "mercurial", "perforce"
    ],
    
    "testing": [
        "pytest", "unittest", "jest", "mocha", "chai", "selenium", "cypress",
        "junit", "testng", "postman", "rest assured", "cucumber", "jasmine",
        "karma", "enzyme", "react testing library", "playwright"
    ],
    
    "mobile": [
        "react native", "flutter", "swift", "swiftui", "kotlin", "android",
        "ios", "xamarin", "ionic", "cordova", "native script"
    ],
    
    "other_technical": [
        "rest api", "restful api", "graphql", "grpc", "soap", "websockets",
        "microservices", "monolith", "serverless", "lambda",
        "agile", "scrum", "kanban", "jira", "confluence",
        "ci/cd", "continuous integration", "continuous deployment",
        "tdd", "test driven development", "bdd", "behavior driven development",
        "oauth", "jwt", "saml", "openid", "authentication", "authorization",
        "mqtt", "amqp", "rabbitmq", "etl", "data pipeline", 
        "system design", "architecture", "design patterns",
        "linux", "unix", "ubuntu", "centos", "debian", "windows server",
        "blockchain", "web3", "ethereum", "solidity", "smart contracts",
        "vim", "emacs", "vscode", "intellij", "pycharm", "eclipse"
    ]
}

SOFT_SKILLS = [
    # Leadership
    "leadership", "team management", "people management", "mentoring", 
    "coaching", "delegation", "strategic planning", "decision making", 
    "conflict resolution", "change management",
    
    # Communication
    "communication", "written communication", "verbal communication",
    "presentation", "public speaking", "technical writing",
    "documentation", "stakeholder management", "cross-functional collaboration",
    "negotiation", "active listening", "client facing",
    
    # Problem Solving
    "problem solving", "critical thinking", "analytical thinking", "analytical skills",
    "troubleshooting", "debugging", "root cause analysis", "innovation",
    "creativity", "research", "attention to detail",
    
    # Project Management
    "project management", "time management", "prioritization", "planning",
    "organization", "organizational skills", "multitasking", "deadline management", 
    "risk management", "budget management", "resource allocation",
    
    # Interpersonal
    "teamwork", "collaboration", "team player", "interpersonal skills", 
    "empathy", "adaptability", "flexibility", "emotional intelligence", 
    "patience", "positive attitude",
    
    # Work Ethic
    "self-motivated", "self-starter", "proactive", "reliable", "detail-oriented",
    "results-driven", "goal-oriented", "accountable", "professional",
    "work ethic", "initiative", "ownership", "fast learner", "quick learner"
]

# Skill synonyms and variations
SKILL_SYNONYMS = {
    "javascript": ["js", "javascript", "ecmascript"],
    "typescript": ["ts", "typescript"],
    "python": ["python", "py", "python3"],
    "react": ["react", "react.js", "reactjs"],
    "node": ["node", "node.js", "nodejs"],
    "next": ["next", "next.js", "nextjs"],
    "vue": ["vue", "vue.js", "vuejs"],
    "angular": ["angular", "angularjs", "angular.js"],
    "postgresql": ["postgresql", "postgres", "psql"],
    "mongodb": ["mongodb", "mongo"],
    "aws": ["aws", "amazon web services"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "azure": ["azure", "microsoft azure"],
    "kubernetes": ["kubernetes", "k8s"],
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning", "dl"],
    "nlp": ["nlp", "natural language processing"],
    "computer vision": ["computer vision", "cv"],
    "reinforcement learning": ["reinforcement learning", "rl"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "tensorflow": ["tensorflow", "tf"],
    "ci/cd": ["ci/cd", "continuous integration", "continuous deployment", "cicd"],
}

# Common acronyms (helps with extraction)
ACRONYMS = {
    "ml": "machine learning",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "rl": "reinforcement learning",
    "ai": "artificial intelligence",
    "ui": "user interface",
    "ux": "user experience",
    "api": "application programming interface",
    "rest": "representational state transfer",
    "crud": "create read update delete",
    "orm": "object relational mapping",
    "sql": "structured query language",
    "nosql": "not only sql",
    "aws": "amazon web services",
    "gcp": "google cloud platform",
    "k8s": "kubernetes",
    "cicd": "continuous integration continuous deployment",
    "tdd": "test driven development",
    "bdd": "behavior driven development",
    "orm": "object relational mapping",
    "jwt": "json web token",
    "saas": "software as a service",
    "paas": "platform as a service",
    "iaas": "infrastructure as a service",
}

DOMAINS = [
    "software engineering", "software development", "data science", 
    "machine learning", "artificial intelligence", "web development", 
    "mobile development", "devops", "cloud computing", "cybersecurity", 
    "data engineering", "frontend", "backend", "full stack", 
    "embedded systems", "game development", "blockchain", 
    "product management", "ui/ux design", "quality assurance", 
    "site reliability", "platform engineering"
]

# Common job titles for context
JOB_TITLES = [
    "software engineer", "senior software engineer", "staff engineer",
    "principal engineer", "engineering manager", "tech lead", "lead engineer",
    "data scientist", "senior data scientist", "ml engineer", "machine learning engineer",
    "ai engineer", "data engineer", "data analyst", "business analyst",
    "frontend developer", "frontend engineer", "backend developer", "backend engineer",
    "full stack developer", "full stack engineer", "web developer",
    "mobile developer", "ios developer", "android developer",
    "devops engineer", "sre", "site reliability engineer", "cloud engineer", 
    "platform engineer", "infrastructure engineer",
    "product manager", "technical product manager", "project manager",
    "qa engineer", "quality assurance engineer", "test engineer", 
    "security engineer", "information security analyst",
    "research scientist", "applied scientist", "research engineer",
    "solutions architect", "software architect", "system architect"
]

# Education-related keywords
EDUCATION_KEYWORDS = [
    "bachelor", "master", "phd", "doctorate", "associate",
    "b.s.", "b.sc", "b.a.", "m.s.", "m.sc", "m.a.", "mba", "ph.d.",
    "computer science", "software engineering", "data science",
    "electrical engineering", "computer engineering", "mathematics",
    "statistics", "physics", "information technology", "information systems",
    "artificial intelligence", "machine learning", "cybersecurity"
]

# Company indicators (for experience parsing)
COMPANY_INDICATORS = [
    "inc", "inc.", "llc", "ltd", "limited", "corporation", "corp", "corp.",
    "company", "co.", "technologies", "tech", "systems", "solutions", 
    "consulting", "services", "group", "labs", "studio", "agency"
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


def normalize_skill(skill_text):
    """
    Normalize skill variations to canonical form.
    E.g., "JS" -> "javascript", "K8s" -> "kubernetes"
    """
    skill_lower = skill_text.lower().strip()
    
    # Check acronyms first
    if skill_lower in ACRONYMS:
        return ACRONYMS[skill_lower]
    
    # Check synonyms
    for canonical, variations in SKILL_SYNONYMS.items():
        if skill_lower in variations:
            return canonical
    
    return skill_text.lower()


def get_skill_variations(skill):
    """Get all variations of a skill."""
    skill_lower = skill.lower()
    
    # Return from synonyms if exists
    if skill_lower in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[skill_lower]
    
    # Check if skill is in any synonym list
    for canonical, variations in SKILL_SYNONYMS.items():
        if skill_lower in variations:
            return variations
    
    return [skill_lower]
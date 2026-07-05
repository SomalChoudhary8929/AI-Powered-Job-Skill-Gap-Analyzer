skills_list = [
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c", "c#",
    "go", "rust", "kotlin", "swift", "php", "ruby", "scala", "r",
    # Web / Frontend
    "html", "css", "react", "vue", "angular", "next.js", "svelte",
    "tailwind css", "bootstrap", "sass", "webpack", "vite",
    # Backend / Frameworks
    "flask", "django", "fastapi", "node.js", "express", "spring boot",
    "laravel", "ruby on rails", "graphql", "rest api", "api",
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite",
    "elasticsearch", "cassandra", "firebase",
    # Data / ML
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "keras", "xgboost", "lightgbm", "machine learning", "deep learning",
    "data science", "data analysis", "nlp", "computer vision",
    "feature engineering", "model deployment", "mlflow",
    # Data viz / BI
    "power bi", "tableau", "matplotlib", "seaborn", "plotly",
    "excel", "google sheets",
    # DevOps / Cloud
    "docker", "kubernetes", "aws", "azure", "gcp", "linux",
    "ci/cd", "github actions", "jenkins", "terraform", "ansible",
    "nginx", "git", "github",
    # Data Engineering
    "spark", "hadoop", "kafka", "airflow", "dbt", "etl",
    "data pipeline", "data warehouse", "bigquery",
    # Cybersecurity
    "network security", "penetration testing", "ethical hacking",
    "burp suite", "nmap", "wireshark", "siem", "soc",
    "vulnerability assessment", "owasp", "cryptography",
    # Mobile
    "android", "ios", "react native", "flutter",
    # AI / LLM
    "langchain", "openai api", "prompt engineering",
    "rag", "vector database", "llm",
    # Sales
    "sales", "crm", "salesforce", "hubspot", "lead generation",
    "cold calling", "negotiation", "account management", "b2b sales",
    "b2c sales", "pipeline management", "sales forecasting",
    "customer acquisition", "closing deals", "upselling", "cross-selling",
    "zoho crm", "outreach", "prospecting",
    # Marketing
    "digital marketing", "seo", "sem", "google ads", "facebook ads",
    "content marketing", "social media marketing", "email marketing",
    "marketing analytics", "google analytics", "a/b testing",
    "brand management", "copywriting", "marketing strategy",
    "campaign management", "influencer marketing", "affiliate marketing",
    "conversion rate optimization", "canva", "adobe creative suite",
    "market research", "product marketing",
    # Product Management
    "product management", "product roadmap", "user stories",
    "stakeholder management", "product strategy", "ux research",
    "wireframing", "figma", "notion", "confluence", "jira",
    "okrs", "kpis", "go-to-market",
    # UI/UX Design
    "ui design", "ux design", "adobe xd", "sketch",
    "user research", "prototyping", "usability testing",
    "design systems", "interaction design", "accessibility",
    # HR / Recruitment
    "recruitment", "talent acquisition", "onboarding", "hrms",
    "employee relations", "performance management", "payroll",
    "compensation", "training and development", "hr policy",
    "applicant tracking system", "linkedin recruiter",
    # Finance / Accounting
    "financial analysis", "financial modeling", "accounting",
    "budgeting", "forecasting", "risk management", "auditing",
    "tax", "tally", "quickbooks", "ms excel", "sap", "erp",
    "investment analysis", "valuation",
    # Business / Operations
    "business development", "operations management", "project management",
    "supply chain", "process improvement", "strategic planning",
    "presentation skills", "communication", "leadership",
    "agile", "scrum", "six sigma", "lean",
    # Customer Support
    "customer support", "customer service", "zendesk", "freshdesk",
    "ticketing system", "live chat", "conflict resolution",
    "problem solving", "technical support", "sla management",
    # General
    "ms office", "postman", "slack",
]

job_skill_map = {
    # ── TECH ──────────────────────────────────────────────────────
    "Data Scientist": [
        "python", "sql", "pandas", "numpy", "machine learning", "deep learning",
        "data science", "scikit-learn", "tensorflow", "pytorch",
        "matplotlib", "feature engineering", "mlflow",
    ],
    "Data Analyst": [
        "sql", "python", "excel", "power bi", "tableau", "pandas",
        "data analysis", "matplotlib", "seaborn", "google sheets",
    ],
    "Frontend Developer": [
        "html", "css", "javascript", "typescript", "react", "vue",
        "next.js", "tailwind css", "webpack", "git", "figma",
    ],
    "Backend Developer": [
        "python", "java", "sql", "flask", "django", "fastapi",
        "node.js", "express", "rest api", "docker", "postgresql", "redis",
    ],
    "Full Stack Developer": [
        "html", "css", "javascript", "typescript", "react", "node.js",
        "express", "sql", "mongodb", "rest api", "docker", "git",
    ],
    "Machine Learning Engineer": [
        "python", "machine learning", "deep learning", "tensorflow", "pytorch",
        "scikit-learn", "numpy", "pandas", "docker", "mlflow",
        "feature engineering", "model deployment", "git",
    ],
    "DevOps Engineer": [
        "linux", "docker", "kubernetes", "aws", "azure", "ci/cd",
        "github actions", "terraform", "ansible", "git", "jenkins", "nginx",
    ],
    "Data Engineer": [
        "python", "sql", "spark", "kafka", "airflow", "dbt", "etl",
        "data pipeline", "postgresql", "docker", "aws", "bigquery",
    ],
    "Software Developer": [
        "python", "java", "c++", "sql", "git", "github",
        "agile", "rest api", "docker",
    ],
    "Cybersecurity Analyst": [
        "network security", "penetration testing", "ethical hacking",
        "burp suite", "nmap", "wireshark", "siem", "soc",
        "vulnerability assessment", "owasp", "linux", "python",
    ],
    "Mobile Developer": [
        "android", "ios", "react native", "flutter", "kotlin", "swift",
        "javascript", "git", "rest api", "firebase",
    ],
    "AI / LLM Engineer": [
        "python", "langchain", "openai api", "prompt engineering",
        "rag", "vector database", "llm", "pytorch", "fastapi",
        "docker", "git",
    ],
    "UI/UX Designer": [
        "figma", "adobe xd", "sketch", "ui design", "ux design",
        "user research", "wireframing", "prototyping", "usability testing",
        "design systems", "interaction design", "accessibility", "canva",
    ],
    # ── SALES ─────────────────────────────────────────────────────
    "Sales Executive": [
        "sales", "crm", "salesforce", "hubspot", "lead generation",
        "cold calling", "negotiation", "account management", "b2b sales",
        "pipeline management", "closing deals", "upselling", "prospecting",
    ],
    "B2B Sales Manager": [
        "b2b sales", "crm", "salesforce", "account management",
        "sales forecasting", "pipeline management", "negotiation",
        "lead generation", "stakeholder management", "closing deals",
        "outreach", "strategic planning",
    ],
    "Business Development Manager": [
        "business development", "lead generation", "crm", "negotiation",
        "sales", "strategic planning", "stakeholder management",
        "market research", "account management", "presentation skills",
    ],
    # ── MARKETING ─────────────────────────────────────────────────
    "Digital Marketing Specialist": [
        "digital marketing", "seo", "sem", "google ads", "facebook ads",
        "content marketing", "social media marketing", "email marketing",
        "google analytics", "a/b testing", "copywriting",
        "campaign management", "conversion rate optimization",
    ],
    "SEO / SEM Specialist": [
        "seo", "sem", "google ads", "google analytics",
        "content marketing", "a/b testing", "conversion rate optimization",
        "copywriting", "html", "marketing analytics",
    ],
    "Marketing Manager": [
        "marketing strategy", "brand management", "campaign management",
        "digital marketing", "seo", "content marketing", "email marketing",
        "market research", "google analytics", "leadership",
        "a/b testing", "stakeholder management",
    ],
    "Content Marketing Specialist": [
        "content marketing", "copywriting", "seo", "social media marketing",
        "email marketing", "canva", "google analytics", "brand management",
        "influencer marketing",
    ],
    "Social Media Manager": [
        "social media marketing", "content marketing", "canva",
        "facebook ads", "influencer marketing",
        "campaign management", "google analytics", "copywriting",
        "brand management", "email marketing",
    ],
    # ── PRODUCT / DESIGN ──────────────────────────────────────────
    "Product Manager": [
        "product management", "product roadmap", "user stories",
        "stakeholder management", "product strategy", "ux research",
        "wireframing", "figma", "jira", "okrs", "kpis",
        "a/b testing", "go-to-market", "agile",
    ],
    # ── HR ────────────────────────────────────────────────────────
    "HR Manager": [
        "recruitment", "talent acquisition", "onboarding", "hrms",
        "employee relations", "performance management", "payroll",
        "training and development", "hr policy", "communication",
        "applicant tracking system", "leadership",
    ],
    "Recruiter / Talent Acquisition": [
        "recruitment", "talent acquisition", "linkedin recruiter",
        "applicant tracking system", "onboarding", "hr policy",
        "communication", "negotiation",
    ],
    # ── FINANCE ───────────────────────────────────────────────────
    "Financial Analyst": [
        "financial analysis", "financial modeling", "excel", "accounting",
        "budgeting", "forecasting", "risk management",
        "investment analysis", "valuation", "sap", "sql",
    ],
    "Accountant": [
        "accounting", "tally", "quickbooks", "excel", "tax",
        "auditing", "budgeting", "erp", "ms excel", "payroll",
    ],
    # ── OPERATIONS / SUPPORT ──────────────────────────────────────
    "Operations Manager": [
        "operations management", "supply chain", "process improvement",
        "strategic planning", "project management", "leadership",
        "agile", "scrum", "six sigma", "lean", "communication",
    ],
    "Customer Support Specialist": [
        "customer support", "customer service", "zendesk", "freshdesk",
        "ticketing system", "live chat", "conflict resolution",
        "problem solving", "technical support", "sla management",
        "communication",
    ],
}

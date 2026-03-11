# Master skills dictionary — updated to cover all sample JDs in the assignment

SKILLS = [
    # --- Programming Languages ---
    "Python", "Java", "Core Java", "JavaScript", "TypeScript", "C", "C++", "C#",
    "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB",
    "Perl", "Fortran", "Bash", "Shell", "PowerShell", "Hack",

    # --- Web / Markup ---
    "HTML", "CSS", "SASS", "LESS", "XML", "JSON", "YAML", "YML", "Protobuf",

    # --- Backend Frameworks ---
    "Node.js", "Express", "Express.js", "Django", "Flask", "FastAPI",
    "Spring", "Spring Boot", "Laravel", "Rails", "Ruby on Rails",
    "ASP.NET", ".NET", "NestJS", "Hapi", "Koa", "Fastify",

    # --- Frontend Frameworks ---
    "React", "Angular", "AngularJS", "Vue", "Vue.js", "Svelte",
    "Next.js", "Nuxt.js", "jQuery", "Bootstrap", "Tailwind CSS", "Material UI",

    # --- Databases ---
    "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Oracle",
    "SQL Server", "Microsoft SQL Server", "DynamoDB", "Cassandra",
    "Elasticsearch", "ElasticSearch", "Firebase", "MariaDB", "CouchDB",
    "Neo4j", "InfluxDB", "DB2", "UDB", "NoSQL", "SQL",

    # --- Cloud & DevOps ---
    "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes",
    "Jenkins", "Terraform", "Ansible", "Chef", "Puppet", "Helm",
    "ArgoCD", "GitHub Actions", "GitLab CI", "CircleCI", "Travis CI",
    "DevOps", "DevSecOps", "CI/CD",

    # --- Messaging / Streaming ---
    "Kafka", "RabbitMQ", "ActiveMQ", "SQS", "SNS",

    # --- APIs & Architecture ---
    "REST", "REST API", "RESTful", "GraphQL", "gRPC", "WebSocket", "SOAP",
    "Microservices", "OAuth", "JWT", "OpenAPI", "Swagger",

    # --- Tools ---
    "Git", "GitHub", "GitLab", "Bitbucket", "Postman",
    "Linux", "Unix", "Nginx", "Apache", "Jira", "Confluence",
    "ClearCase", "SVN",

    # --- Monitoring / Logging ---
    "ELK", "Kibana", "Logstash", "Prometheus", "Grafana",

    # --- AI / ML ---
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Keras",
    "scikit-learn", "Pandas", "NumPy", "NLP", "Computer Vision", "AI/ML",

    # --- Testing & Methodologies ---
    "Jest", "Mocha", "Chai", "JUnit", "Pytest", "Selenium", "Cypress",
    "Unit Testing", "TDD", "BDD", "Agile", "Scrum", "Kanban", "SDLC",

    # --- Parallel / HPC / Embedded ---
    "MPI", "OpenMP", "FPGA", "Embedded", "RTOS", "HPC",

    # --- Data / Analytics ---
    "Tableau", "Power BI", "Excel",

    # --- Other Tech ---
    "Full Stack", "OOP", "MVC", "Design Patterns",
    "Data Structures", "Algorithms", "System Design",
]

# Normalize to lowercase map for fast lookup
SKILLS_LOWER_MAP = {skill.lower(): skill for skill in SKILLS}
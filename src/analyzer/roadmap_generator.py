from typing import Any, Dict, List, Optional
from src.matcher.taxonomy import load_taxonomy

CURATED_ROADMAPS: Dict[str, Dict[str, Any]] = {
    "Docker": {
        "time_estimate": "1 - 2 Weeks",
        "difficulty": "Beginner to Intermediate",
        "summary": "Containerization platform to package applications and dependencies into standardized containers.",
        "milestones": [
            "Week 1 (Days 1-3): Container basics, images vs containers, Docker CLI commands (run, ps, stop, rm).",
            "Week 1 (Days 4-7): Writing production-ready multi-stage Dockerfiles and minimizing image layer sizes.",
            "Week 2 (Days 8-11): Multi-container orchestration using docker-compose, bridge networks, and volume persistence.",
            "Week 2 (Days 12-14): Container security best practices, healthchecks, and non-root user execution.",
        ],
        "free_resources": [
            {"title": "Docker Official Getting Started Guide", "url": "https://docs.docker.com/get-started/"},
            {"title": "freeCodeCamp Docker & Kubernetes Full Course", "url": "https://www.freecodecamp.org/news/docker-kubernetes-course/"},
            {"title": "Play with Docker (Free Interactive Sandbox)", "url": "https://labs.play-with-docker.com/"},
        ],
        "portfolio_project": {
            "title": "Multi-tier Microservices Containerization with Docker Compose",
            "description": "Containerize a full-stack web application (FastAPI backend + React frontend + PostgreSQL + Redis) using multi-stage Dockerfiles and docker-compose.",
            "bullet_point": "Containerized a multi-service web platform using Docker and multi-stage Dockerfiles, reducing build image size by 65% and enabling one-command local environment bootstrapping.",
        },
    },
    "Kubernetes": {
        "time_estimate": "3 - 4 Weeks",
        "difficulty": "Intermediate to Advanced",
        "summary": "Production-grade container orchestration system for automating application deployment, scaling, and management.",
        "milestones": [
            "Week 1: Kubernetes architecture (Control plane, Kubelet, etcd) and Pod lifecycle.",
            "Week 2: Deployments, ReplicaSets, Rolling updates, and rollback management.",
            "Week 3: Services (ClusterIP, NodePort, LoadBalancer), Ingress controllers, ConfigMaps, and Secrets.",
            "Week 4: Persistent Volumes (PV/PVC), Horizontal Pod Autoscaling (HPA), and Minikube/Kind testing.",
        ],
        "free_resources": [
            {"title": "Kubernetes Official Tutorials", "url": "https://kubernetes.io/docs/tutorials/"},
            {"title": "Kubernetes The Hard Way by Kelsey Hightower", "url": "https://github.com/kelseyhightower/kubernetes-the-hard-way"},
            {"title": "Nana Janashia Kubernetes 4-Hour Crash Course", "url": "https://www.youtube.com/watch?v=X48VuDVv0do"},
        ],
        "portfolio_project": {
            "title": "Zero-Downtime Microservices Deployment on Minikube / K3s",
            "description": "Deploy a stateless REST API with automated rolling updates, ConfigMaps, secrets, and an Ingress router.",
            "bullet_point": "Deployed and orchestrated microservices on a Kubernetes cluster with Horizontal Pod Autoscaling and Ingress routing, maintaining 99.9% uptime during rolling updates.",
        },
    },
    "Redis": {
        "time_estimate": "1 - 2 Weeks",
        "difficulty": "Beginner to Intermediate",
        "summary": "In-memory data structure store used as a high-performance database, cache, message broker, and streaming engine.",
        "milestones": [
            "Week 1 (Days 1-4): Redis data structures (Strings, Hashes, Lists, Sets, Sorted Sets) and Redis CLI.",
            "Week 1 (Days 5-7): Cache-aside pattern, Cache penetration/stampede prevention, and TTL expiration policies.",
            "Week 2 (Days 8-11): Pub/Sub messaging, Redis Streams, and distributed locking with Redlock.",
            "Week 2 (Days 12-14): Persistence strategies (RDB snapshots vs AOF logs) and benchmark latency tests.",
        ],
        "free_resources": [
            {"title": "Redis University Free Courses", "url": "https://university.redis.com/"},
            {"title": "Redis Official Documentation", "url": "https://redis.io/docs/"},
            {"title": "System Design Caching Strategies Guide", "url": "https://bytebytego.com/"},
        ],
        "portfolio_project": {
            "title": "High-Throughput Rate Limiter & Cache Layer",
            "description": "Build an API rate limiter (sliding window algorithm) and cache-aside layer in Python or Node.js using Redis.",
            "bullet_point": "Implemented a Redis cache-aside layer and sliding-window rate limiter, cutting database load by 70% and achieving sub-5ms cached response times.",
        },
    },
    "Data Structures & Algorithms": {
        "time_estimate": "4 - 8 Weeks",
        "difficulty": "Intermediate to Advanced",
        "summary": "Core foundational building blocks of software engineering, technical interviews, and algorithmic efficiency.",
        "milestones": [
            "Week 1-2: Arrays, Two Pointers, Sliding Window, Hashing, and Linked Lists.",
            "Week 3-4: Stacks, Queues, Binary Search, Recursion, and Divide & Conquer.",
            "Week 5-6: Binary Trees, Binary Search Trees (BST), Heaps / Priority Queues, and Graph traversals (BFS, DFS).",
            "Week 7-8: Dynamic Programming (Memoization & Tabulation), Greedy algorithms, and Dijkstra's Shortest Path.",
        ],
        "free_resources": [
            {"title": "NeetCode 150 Curated Problem Sheet", "url": "https://neetcode.io/practice"},
            {"title": "Striver's SDE Sheet (Take U Forward)", "url": "https://takeuforward.org/interviews/strivers-sde-sheet-top-coding-interview-problems/"},
            {"title": "MIT 6.006 Introduction to Algorithms (OpenCourseWare)", "url": "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/"},
        ],
        "portfolio_project": {
            "title": "Competitive Programming & Algorithmic Problem Solving Portfolio",
            "description": "Solve 300+ problems across standard patterns (Arrays, Graphs, DP) on LeetCode / Codeforces and document algorithmic complexities.",
            "bullet_point": "Solved 400+ algorithmic challenges on LeetCode across Graphs, Dynamic Programming, and Trees; achieved top 12% global contest rating.",
        },
    },
    "System Design": {
        "time_estimate": "3 - 4 Weeks",
        "difficulty": "Intermediate to Advanced",
        "summary": "Architecture of distributed systems, scalability, load balancing, sharding, and fault tolerance.",
        "milestones": [
            "Week 1: Vertical vs Horizontal scaling, Load Balancers (L4 vs L7), Reverse Proxies, and CDN caching.",
            "Week 2: Relational vs NoSQL databases, ACID properties, CAP Theorem, and database sharding/replication.",
            "Week 3: Message Queues (Kafka, RabbitMQ), Event-driven architectures, and idempotency.",
            "Week 4: Classic case studies: Design URL Shortener, Twitter Feed, Rate Limiter, and Distributed Cache.",
        ],
        "free_resources": [
            {"title": "System Design Primer by Donne Martin", "url": "https://github.com/donnemartin/system-design-primer"},
            {"title": "ByteByteGo System Design YouTube Channel", "url": "https://www.youtube.com/@ByteByteGo"},
            {"title": "High Scalability Architecture Case Studies", "url": "http://highscalability.com/"},
        ],
        "portfolio_project": {
            "title": "Scalable URL Shortener with Analytics & Caching",
            "description": "Design and build a scalable URL shortener with Base62 encoding, Redis caching, and PostgreSQL persistent store.",
            "bullet_point": "Architected a distributed URL shortening service with Base62 encoding and Redis caching, capable of serving 5,000 req/s with 99th percentile latency under 20ms.",
        },
    },
    "PostgreSQL": {
        "time_estimate": "2 Weeks",
        "difficulty": "Beginner to Intermediate",
        "summary": "Advanced open-source relational database supporting SQL, JSON queries, complex indexing, and ACID transactions.",
        "milestones": [
            "Week 1 (Days 1-4): Schema design, normalization (1NF-3NF), primary/foreign keys, and complex JOIN queries.",
            "Week 1 (Days 5-7): Window functions, Common Table Expressions (CTEs), and aggregation queries.",
            "Week 2 (Days 8-11): Query optimization using EXPLAIN ANALYZE, B-Tree vs GIN/GiST indexing, and vacuuming.",
            "Week 2 (Days 12-14): Transaction isolation levels, row-level locking, and connection pooling (PgBouncer).",
        ],
        "free_resources": [
            {"title": "PostgreSQL Official Tutorial", "url": "https://www.postgresql.org/docs/current/tutorial.html"},
            {"title": "SQLZoo Interactive SQL Practice", "url": "https://sqlzoo.net/"},
            {"title": "Use The Index, Luke (SQL Indexing Guide)", "url": "https://use-the-index-luke.com/"},
        ],
        "portfolio_project": {
            "title": "Normalized Relational Data Model & Query Performance Benchmark",
            "description": "Design an enterprise database schema for an e-commerce platform with 500k records and benchmark indexed vs unindexed query speeds.",
            "bullet_point": "Engineered a 3NF normalized PostgreSQL database schema with composite B-Tree indexes, improving 95th percentile query execution speed by 42%.",
        },
    },
    "FastAPI": {
        "time_estimate": "1 - 2 Weeks",
        "difficulty": "Beginner to Intermediate",
        "summary": "Modern, high-performance web framework for building APIs with Python based on standard type hints and Pydantic.",
        "milestones": [
            "Week 1 (Days 1-4): Routing, Pydantic request/response schemas, path/query parameters, and automatic OpenAPI docs.",
            "Week 1 (Days 5-7): Asynchronous endpoints (async/await), dependency injection system, and CORS configuration.",
            "Week 2 (Days 8-11): Database integration via SQLAlchemy / Tortoise ORM with connection pooling.",
            "Week 2 (Days 12-14): JWT authentication, OAuth2 password bearer flow, and automated Pytest test fixtures.",
        ],
        "free_resources": [
            {"title": "FastAPI Official Interactive Documentation", "url": "https://fastapi.tiangolo.com/tutorial/"},
            {"title": "freeCodeCamp FastAPI Full Course", "url": "https://www.youtube.com/watch?v=0sOvCWFmrtA"},
            {"title": "TestDriven.io FastAPI & Docker Tutorial", "url": "https://testdriven.io/blog/fastapi-crud/"},
        ],
        "portfolio_project": {
            "title": "Asynchronous REST API with JWT Auth & Swagger Documentation",
            "description": "Build an asynchronous CRUD API service with role-based JWT auth, PostgreSQL persistence, and automatic Swagger docs.",
            "bullet_point": "Developed an asynchronous REST API backend using FastAPI and PostgreSQL, serving 1,200+ req/s with automated OpenAPI Swagger documentation.",
        },
    },
    "CI/CD": {
        "time_estimate": "1 - 2 Weeks",
        "difficulty": "Beginner to Intermediate",
        "summary": "Continuous Integration and Continuous Deployment automation for reliable software build and release pipelines.",
        "milestones": [
            "Week 1 (Days 1-4): CI/CD fundamentals, Git hooks, and writing GitHub Actions YAML workflows.",
            "Week 1 (Days 5-7): Automated unit test execution, linting (flake8, eslint), and code coverage reporting.",
            "Week 2 (Days 8-11): Building and pushing Docker container images to Docker Hub / GitHub Container Registry.",
            "Week 2 (Days 12-14): Automated deployment triggers to cloud platforms (AWS, Render, Vercel) on main branch merge.",
        ],
        "free_resources": [
            {"title": "GitHub Actions Documentation & Quickstart", "url": "https://docs.github.com/en/actions"},
            {"title": "GitLab CI/CD Fundamentals", "url": "https://docs.gitlab.com/ee/ci/"},
            {"title": "freeCodeCamp CI/CD Pipeline Crash Course", "url": "https://www.youtube.com/watch?v=scEDHsr3APg"},
        ],
        "portfolio_project": {
            "title": "Automated Multi-Stage CI/CD Pipeline with GitHub Actions",
            "description": "Configure an automated GitHub Actions pipeline that lints code, runs unit tests, builds Docker images, and triggers deployment.",
            "bullet_point": "Configured automated GitHub Actions CI/CD workflows for linting, pytest test suites, and Docker image publishing, eliminating manual release steps.",
        },
    },
    "AWS": {
        "time_estimate": "2 - 3 Weeks",
        "difficulty": "Intermediate",
        "summary": "World's most comprehensive and broadly adopted cloud platform offering compute, storage, and networking services.",
        "milestones": [
            "Week 1: AWS Global Infrastructure, IAM users/roles/policies, and EC2 instance provisioning with SSH security groups.",
            "Week 2: S3 bucket storage, static website hosting, VPC networking fundamentals, and RDS relational database setup.",
            "Week 3: Serverless functions with AWS Lambda, API Gateway, CloudWatch monitoring, and CloudFront CDN.",
        ],
        "free_resources": [
            {"title": "AWS Skill Builder Free Digital Training", "url": "https://explore.skillbuilder.aws/"},
            {"title": "AWS Free Tier Hands-On Labs", "url": "https://aws.amazon.com/free/"},
            {"title": "freeCodeCamp AWS Cloud Practitioner Exam Guide", "url": "https://www.youtube.com/watch?v=SOTamWNgDKc"},
        ],
        "portfolio_project": {
            "title": "Cloud-Native Three-Tier Web Architecture on AWS",
            "description": "Deploy a 3-tier architecture with React on S3/CloudFront, FastAPI on EC2 behind an ALB, and managed RDS PostgreSQL.",
            "bullet_point": "Architected and deployed a three-tier cloud web application on AWS utilizing EC2, RDS PostgreSQL, and S3, ensuring secure IAM role-based access.",
        },
    },
    "PyTorch": {
        "time_estimate": "2 - 3 Weeks",
        "difficulty": "Intermediate",
        "summary": "Leading open-source deep learning framework providing seamless tensor computation and neural network modeling.",
        "milestones": [
            "Week 1: Tensor operations, GPU acceleration with CUDA, and Autograd automatic differentiation.",
            "Week 2: Building neural networks with torch.nn, custom Dataset & DataLoader classes, loss functions, and Adam optimizers.",
            "Week 3: Convolutional Neural Networks (CNNs) for vision, Transfer Learning with Torchvision ResNet, and model checkpoint saving.",
        ],
        "free_resources": [
            {"title": "PyTorch Official 60-Minute Blitz Tutorial", "url": "https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html"},
            {"title": "Deep Learning with PyTorch by Daniel Bourke", "url": "https://www.learnpytorch.io/"},
            {"title": "Stanford CS231n Deep Learning for Computer Vision", "url": "https://cs231n.github.io/"},
        ],
        "portfolio_project": {
            "title": "Computer Vision Classifier with Transfer Learning",
            "description": "Fine-tune a pretrained ResNet-50 network in PyTorch on a custom image dataset with data augmentation and ROC-AUC evaluation.",
            "bullet_point": "Trained and deployed a transfer learning vision model in PyTorch using ResNet-50, achieving 94.2% top-1 accuracy on a custom 15-class dataset.",
        },
    },
}


def get_skill_learning_plan(skill_name: str) -> Dict[str, Any]:
    """
    Retrieve or dynamically generate a structured learning plan for a given skill.
    """
    # Check exact match or case-insensitive match
    if skill_name in CURATED_ROADMAPS:
        return CURATED_ROADMAPS[skill_name]

    for k, v in CURATED_ROADMAPS.items():
        if k.lower() == skill_name.lower():
            return v

    # Dynamic generation based on taxonomy category
    tax = load_taxonomy()
    cat = tax.skill_to_category.get(skill_name.lower(), "technical")

    return {
        "time_estimate": "2 - 3 Weeks",
        "difficulty": "Intermediate",
        "summary": f"Comprehensive skill development track for {skill_name} in the {cat.replace('_', ' ').title()} domain.",
        "milestones": [
            f"Phase 1: Core foundational syntax, architecture, and basic setups for {skill_name}.",
            f"Phase 2: Intermediate patterns, best practices, error handling, and performance considerations.",
            f"Phase 3: Building a modular real-world component or service utilizing {skill_name}.",
            f"Phase 4: Writing unit tests, benchmarking performance, and documenting on GitHub.",
        ],
        "free_resources": [
            {"title": f"Official {skill_name} Documentation & Guides", "url": f"https://www.google.com/search?q={skill_name.replace(' ', '+')}+official+documentation"},
            {"title": f"freeCodeCamp {skill_name} Tutorials", "url": f"https://www.freecodecamp.org/news/search/?query={skill_name.replace(' ', '%20')}"},
            {"title": f"GitHub Awesome {skill_name} Curated List", "url": f"https://github.com/search?q=awesome+{skill_name.replace(' ', '+')}"},
        ],
        "portfolio_project": {
            "title": f"Hands-on {skill_name} Showcase Project",
            "description": f"Build a clean end-to-end open-source project leveraging {skill_name} with comprehensive unit tests and documentation.",
            "bullet_point": f"Implemented and integrated {skill_name} in an open-source student project, improving modularity and documented with full technical specifications.",
        },
    }


def generate_learning_roadmap(priority_skills: List[str], max_skills: int = 5) -> List[Dict[str, Any]]:
    """
    Generate student learning roadmap cards for the top prioritized missing skills.
    """
    roadmap = []
    selected_skills = priority_skills[:max_skills]

    for idx, skill in enumerate(selected_skills, start=1):
        plan = get_skill_learning_plan(skill)
        roadmap.append({
            "step": idx,
            "skill": skill,
            "time_estimate": plan["time_estimate"],
            "difficulty": plan["difficulty"],
            "summary": plan["summary"],
            "milestones": plan["milestones"],
            "free_resources": plan["free_resources"],
            "portfolio_project": plan["portfolio_project"],
        })

    return roadmap

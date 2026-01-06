import json
import random
import time
import uuid
import hashlib
import os
from datetime import datetime, timedelta

# =================CONFIGURATION=================
# User profiles with different characteristics
USER_PROFILES = [
    {
        "user_id": "user_demo_epistemic",
        "mode": "controlled_demo",
        "core_behaviors": [
            {
                "text": "prefers visual explanations for Python concepts",
                "occurrences": 8,
                "credibility_range": (0.82, 0.94),
                "templates": [
                    "Can you show me a diagram explaining {topic}?",
                    "I'd like a visual breakdown of {topic} in Python",
                    "Could you illustrate {topic} with a chart?",
                    "Show me a flowchart for {topic}",
                    "Draw a visual representation of {topic}",
                    "I prefer seeing {topic} as a diagram",
                    "Visual guide to {topic} please",
                    "Can you create an illustration of {topic}?"
                ],
                "topics": ["Python decorators", "Python generators", "Python context managers", 
                          "Python metaclasses", "Python descriptors", "async/await in Python"]
            },
            {
                "text": "focuses on debugging and error resolution",
                "occurrences": 9,
                "credibility_range": (0.78, 0.92),
                "templates": [
                    "I'm getting an error with {topic}, how do I fix it?",
                    "Help me troubleshoot {topic}",
                    "Why is {topic} throwing an exception?",
                    "Debug my {topic} implementation",
                    "What's causing this {topic} error?",
                    "Fix my broken {topic} code",
                    "Resolve {topic} issue",
                    "Troubleshooting {topic} problems",
                    "Error handling for {topic}"
                ],
                "topics": ["async functions", "database connections", "API calls", 
                          "memory leaks", "race conditions", "import errors", "type errors"]
            }
        ],
        "insufficient_behaviors": [
            {
                "text": "interested in system design patterns",
                "occurrences": 4,
                "credibility_range": (0.68, 0.83),
                "templates": [
                    "Tell me about {topic} in distributed systems",
                    "How does {topic} work in microservices?",
                    "Explain {topic} architecture pattern",
                    "System design for {topic}"
                ],
                "topics": ["load balancing", "caching strategies", "circuit breakers", "event sourcing"]
            },
            {
                "text": "asks about security best practices",
                "occurrences": 3,
                "credibility_range": (0.70, 0.85),
                "templates": [
                    "What are security considerations for {topic}?",
                    "How to secure {topic}?",
                    "Best practices for {topic} security"
                ],
                "topics": ["API authentication", "JWT tokens", "SQL injection prevention"]
            }
        ],
        "noise_behaviors": [
            {"text": "asks about football scores", "credibility": 0.35, "template": "What's the latest score in football?"},
            {"text": "inquires about weather", "credibility": 0.42, "template": "What's the weather today?"},
            {"text": "random blockchain question", "credibility": 0.51, "template": "How does blockchain work?"},
            {"text": "one-time recipe query", "credibility": 0.38, "template": "Recipe for chocolate cake?"},
            {"text": "movie recommendation", "credibility": 0.45, "template": "Recommend a good movie"},
            {"text": "random history fact", "credibility": 0.33, "template": "When did World War 2 end?"},
            {"text": "casual greeting", "credibility": 0.29, "template": "Hello, how are you?"},
            {"text": "stock market query", "credibility": 0.48, "template": "What's the stock market doing?"},
            {"text": "random math question", "credibility": 0.52, "template": "What's the square root of 144?"},
            {"text": "unrelated API syntax", "credibility": 0.44, "template": "API endpoint syntax for random service"},
            {"text": "travel question", "credibility": 0.37, "template": "Best time to visit Japan?"},
            {"text": "gaming query", "credibility": 0.41, "template": "Tips for playing chess?"},
            {"text": "music recommendation", "credibility": 0.39, "template": "Good jazz albums?"},
            {"text": "random trivia", "credibility": 0.36, "template": "What's the capital of Mongolia?"},
            {"text": "unrelated book query", "credibility": 0.43, "template": "Best science fiction books?"}
        ],
        "days_back": 14,
        "description": "DEMO: Controlled dataset showing CORE, INSUFFICIENT_EVIDENCE, and NOISE states"
    },
    {
        "user_id": "user_demo_single_core",
        "mode": "controlled_demo",
        "core_behaviors": [
            {
                "text": "prefers visual explanations for Python concepts",
                "occurrences": 6,
                "credibility_range": (0.84, 0.92),
                "templates": [
                    "Can you show me a diagram explaining {topic}?",
                    "I'd like a visual breakdown of {topic} in Python",
                    "Could you illustrate {topic} with a chart?",
                    "Show me a flowchart for {topic}",
                    "Draw a visual representation of {topic}",
                    "I prefer seeing {topic} as a diagram"
                ],
                "topics": ["Python decorators", "Python generators", "Python context managers", 
                          "async/await in Python", "Python descriptors", "list comprehensions"]
            },
            {
                "text": "likes diagrams when learning Python",
                "occurrences": 5,
                "credibility_range": (0.82, 0.90),
                "templates": [
                    "Diagram please for {topic}",
                    "I learn better with diagrams for {topic}",
                    "Visual guide to {topic} would help",
                    "Can you visualize {topic}?",
                    "Picture/diagram of {topic}"
                ],
                "topics": ["Python classes", "inheritance in Python", "Python modules", 
                          "virtual environments", "Python packaging"]
            },
            {
                "text": "prefers visual walkthroughs for Python topics",
                "occurrences": 4,
                "credibility_range": (0.80, 0.88),
                "templates": [
                    "Walk me through {topic} visually",
                    "Visual step-by-step for {topic}",
                    "Illustrated tutorial on {topic}",
                    "Show {topic} with visuals"
                ],
                "topics": ["function decorators", "Python iterators", "class methods vs static methods", 
                          "Python imports"]
            }
        ],
        "insufficient_behaviors": [
            {
                "text": "asks about testing frameworks occasionally",
                "occurrences": 3,
                "credibility_range": (0.68, 0.78),
                "templates": [
                    "How to test {topic}?",
                    "Unit testing for {topic}",
                    "Testing approach for {topic}"
                ],
                "topics": ["pytest fixtures", "mock objects", "integration tests"]
            },
            {
                "text": "inquires about performance optimization",
                "occurrences": 3,
                "credibility_range": (0.70, 0.80),
                "templates": [
                    "How to optimize {topic}?",
                    "Performance tips for {topic}",
                    "Speed up {topic}"
                ],
                "topics": ["list operations", "dictionary lookups", "string concatenation"]
            }
        ],
        "noise_behaviors": [
            {"text": "asks about football scores", "credibility": 0.34, "template": "What's the latest football match result?"},
            {"text": "inquires about weather", "credibility": 0.40, "template": "What's the weather forecast?"},
            {"text": "random blockchain question", "credibility": 0.49, "template": "Explain blockchain technology"},
            {"text": "one-time recipe query", "credibility": 0.36, "template": "How to make pasta carbonara?"},
            {"text": "movie recommendation", "credibility": 0.43, "template": "Good action movies?"},
            {"text": "random history fact", "credibility": 0.31, "template": "When did the Renaissance begin?"},
            {"text": "casual greeting", "credibility": 0.28, "template": "Hi there!"},
            {"text": "stock market query", "credibility": 0.46, "template": "How's the stock market today?"},
            {"text": "random math question", "credibility": 0.50, "template": "What's 15% of 240?"},
            {"text": "unrelated API syntax", "credibility": 0.42, "template": "REST API best practices?"},
            {"text": "travel question", "credibility": 0.35, "template": "Best beaches in Thailand?"},
            {"text": "gaming query", "credibility": 0.39, "template": "Tips for video game X?"},
            {"text": "music recommendation", "credibility": 0.37, "template": "Best classical music pieces?"},
            {"text": "random trivia", "credibility": 0.33, "template": "What's the tallest mountain?"},
            {"text": "unrelated book query", "credibility": 0.41, "template": "Best mystery novels?"}
        ],
        "days_back": 14,
        "description": "DEMO: Single CORE cluster with 3 paraphrased behaviors (visual Python learning)"
    },
    {
        "user_id": "user_small_dataset",
        "num_behaviors": 8,
        "min_prompts": 5,
        "max_prompts": 12,
        "noise_ratio": 0.10,
        "days_back": 15,
        "description": "Small dataset - few behaviors, low activity"
    },
    {
        "user_id": "user_medium_clear",
        "num_behaviors": 12,
        "min_prompts": 15,
        "max_prompts": 35,
        "noise_ratio": 0.08,
        "days_back": 30,
        "description": "Medium dataset - clear patterns, low noise"
    },
    {
        "user_id": "user_large_diverse",
        "num_behaviors": 18,
        "min_prompts": 10,
        "max_prompts": 45,
        "noise_ratio": 0.20,
        "days_back": 60,
        "description": "Large dataset - diverse behaviors, higher noise"
    },
    {
        "user_id": "user_noisy_explorer",
        "num_behaviors": 10,
        "min_prompts": 8,
        "max_prompts": 20,
        "noise_ratio": 0.35,
        "days_back": 45,
        "description": "Exploratory user - many unrelated queries"
    },
    {
        "user_id": "user_focused_specialist",
        "num_behaviors": 5,
        "min_prompts": 30,
        "max_prompts": 80,
        "noise_ratio": 0.05,
        "days_back": 90,
        "description": "Focused specialist - few but very strong behaviors"
    },
    {
        "user_id": "user_massive_dataset",
        "num_behaviors": 1000,
        "min_prompts": 3,
        "max_prompts": 15,
        "noise_ratio": 0.15,
        "days_back": 365,
        "description": "Massive dataset - 1000 behaviors, extensive activity over 1 year"
    },
    {
        "user_id": "user_preference_based_dev",
        "mode": "controlled_demo",
        "core_behaviors": [
            {
                "text": "prefers functional programming paradigms",
                "occurrences": 12,
                "credibility_range": (0.84, 0.93),
                "templates": [
                    "I prefer using functional {topic} over imperative",
                    "Show me functional approach to {topic}",
                    "I like functional programming for {topic}",
                    "Prefer immutable {topic} patterns",
                    "I favor pure functions when working with {topic}",
                    "Functional way to handle {topic}",
                    "I prefer declarative {topic} style",
                    "Like using higher-order functions for {topic}"
                ],
                "topics": ["array operations", "state management", "data transformations", 
                          "error handling", "async operations", "composition patterns"]
            },
            {
                "text": "likes TypeScript over JavaScript",
                "occurrences": 10,
                "credibility_range": (0.81, 0.91),
                "templates": [
                    "I prefer TypeScript for {topic}",
                    "How to implement {topic} in TypeScript?",
                    "I like TypeScript's type safety for {topic}",
                    "TypeScript version of {topic} please",
                    "Prefer using TS for {topic}",
                    "I favor TypeScript when building {topic}",
                    "Type-safe {topic} implementation",
                    "I like having types for {topic}"
                ],
                "topics": ["React components", "API clients", "utility functions", 
                          "configuration", "data models", "hooks"]
            },
            {
                "text": "prefers minimal and lightweight libraries",
                "occurrences": 8,
                "credibility_range": (0.79, 0.89),
                "templates": [
                    "I prefer lightweight solution for {topic}",
                    "Minimal library for {topic}?",
                    "I like keeping {topic} dependencies small",
                    "Prefer simple approach to {topic}",
                    "Lightweight alternative for {topic}",
                    "I favor minimal setup for {topic}",
                    "Simple and small {topic} solution"
                ],
                "topics": ["date handling", "HTTP requests", "state management", 
                          "routing", "validation", "testing"]
            }
        ],
        "insufficient_behaviors": [
            {
                "text": "enjoys experimenting with new frameworks",
                "occurrences": 4,
                "credibility_range": (0.70, 0.81),
                "templates": [
                    "I like trying new frameworks for {topic}",
                    "What's the latest framework for {topic}?",
                    "I enjoy exploring {topic} alternatives",
                    "New tech for {topic}?"
                ],
                "topics": ["frontend development", "backend APIs", "build tools", "testing"]
            },
            {
                "text": "prefers CLI tools over GUI",
                "occurrences": 3,
                "credibility_range": (0.68, 0.79),
                "templates": [
                    "I prefer command line for {topic}",
                    "CLI way to handle {topic}",
                    "I like using terminal for {topic}"
                ],
                "topics": ["git operations", "package management", "file operations"]
            }
        ],
        "noise_behaviors": [
            {"text": "random sports query", "credibility": 0.37, "template": "Who won the basketball game?"},
            {"text": "asks about recipes", "credibility": 0.41, "template": "How to make sushi?"},
            {"text": "weather inquiry", "credibility": 0.33, "template": "Will it rain tomorrow?"},
            {"text": "movie suggestion", "credibility": 0.44, "template": "Good sci-fi movies?"},
            {"text": "random trivia", "credibility": 0.38, "template": "What's the population of Tokyo?"},
            {"text": "music question", "credibility": 0.36, "template": "Best rock bands?"},
            {"text": "travel query", "credibility": 0.42, "template": "Cheap flights to Europe?"},
            {"text": "health question", "credibility": 0.39, "template": "Benefits of exercise?"},
            {"text": "random fact", "credibility": 0.35, "template": "How tall is Mount Everest?"},
            {"text": "unrelated question", "credibility": 0.40, "template": "What time is it in Paris?"}
        ],
        "days_back": 21,
        "description": "DEMO: Developer with strong preferences for functional programming, TypeScript, and minimal dependencies"
    },
    {
        "user_id": "user_learning_preferences",
        "mode": "controlled_demo",
        "core_behaviors": [
            {
                "text": "prefers learning through hands-on examples",
                "occurrences": 14,
                "credibility_range": (0.86, 0.95),
                "templates": [
                    "I prefer hands-on examples for {topic}",
                    "Show me practical example of {topic}",
                    "I like learning {topic} by doing",
                    "Give me working code for {topic}",
                    "I prefer interactive examples of {topic}",
                    "Hands-on tutorial for {topic}",
                    "I like to see {topic} in action",
                    "Real-world example of {topic} please",
                    "I prefer practical exercises for {topic}"
                ],
                "topics": ["machine learning algorithms", "API integration", "database queries", 
                          "authentication flows", "web scraping", "data visualization", "testing strategies"]
            },
            {
                "text": "likes concise documentation over verbose explanations",
                "occurrences": 11,
                "credibility_range": (0.83, 0.92),
                "templates": [
                    "I prefer concise docs for {topic}",
                    "Brief explanation of {topic}",
                    "I like short and clear {topic} guide",
                    "Quick reference for {topic}",
                    "I prefer TL;DR style for {topic}",
                    "Short doc on {topic}",
                    "I like quick overview of {topic}",
                    "Concise {topic} documentation"
                ],
                "topics": ["API endpoints", "configuration options", "CLI commands", 
                          "library methods", "syntax rules", "best practices"]
            },
            {
                "text": "prefers video tutorials over text-based content",
                "occurrences": 9,
                "credibility_range": (0.80, 0.90),
                "templates": [
                    "I prefer video tutorial for {topic}",
                    "Any video explaining {topic}?",
                    "I like watching tutorials on {topic}",
                    "Video walkthrough of {topic}",
                    "I prefer learning {topic} through videos",
                    "YouTube tutorial for {topic}",
                    "I like video demonstrations of {topic}"
                ],
                "topics": ["design patterns", "system architecture", "Docker setup", 
                          "CI/CD pipelines", "cloud deployment", "debugging techniques"]
            }
        ],
        "insufficient_behaviors": [
            {
                "text": "enjoys contributing to open source",
                "occurrences": 4,
                "credibility_range": (0.69, 0.80),
                "templates": [
                    "I like contributing to {topic} projects",
                    "How to contribute to {topic} repo?",
                    "I enjoy open source {topic} work",
                    "Good {topic} projects to contribute to?"
                ],
                "topics": ["Python libraries", "documentation", "testing frameworks", "utilities"]
            },
            {
                "text": "prefers pair programming for complex tasks",
                "occurrences": 3,
                "credibility_range": (0.67, 0.78),
                "templates": [
                    "I prefer pair programming for {topic}",
                    "I like collaborative work on {topic}",
                    "Best practices for pairing on {topic}"
                ],
                "topics": ["refactoring", "architecture decisions", "debugging"]
            }
        ],
        "noise_behaviors": [
            {"text": "asks about news", "credibility": 0.36, "template": "What's happening in the news?"},
            {"text": "gaming question", "credibility": 0.43, "template": "Best strategy games?"},
            {"text": "random calculation", "credibility": 0.39, "template": "What's 25% of 800?"},
            {"text": "book recommendation", "credibility": 0.41, "template": "Good fantasy books?"},
            {"text": "language query", "credibility": 0.34, "template": "How to say hello in Spanish?"},
            {"text": "historical fact", "credibility": 0.37, "template": "When was the printing press invented?"},
            {"text": "shopping question", "credibility": 0.40, "template": "Best laptop brands?"},
            {"text": "random science", "credibility": 0.38, "template": "How do magnets work?"},
            {"text": "geography query", "credibility": 0.35, "template": "Capital of Australia?"},
            {"text": "unrelated topic", "credibility": 0.42, "template": "How to train a dog?"},
            {"text": "food question", "credibility": 0.37, "template": "Healthy breakfast ideas?"}
        ],
        "days_back": 18,
        "description": "DEMO: Learner with strong preferences for hands-on examples, concise docs, and video tutorials"
    },
    {
        "user_id": "user_python_project_2month",
        "mode": "controlled_demo",
        "core_behaviors": [
            {
                "text": "debugging FastAPI endpoint issues and request validation",
                "occurrences": 15,
                "credibility_range": (0.84, 0.93),
                "templates": [
                    "FastAPI {topic} not working as expected",
                    "How to debug {topic} in FastAPI?",
                    "FastAPI {topic} returning wrong response",
                    "Troubleshoot FastAPI {topic} validation error",
                    "Why is my FastAPI {topic} failing?",
                    "Fix FastAPI {topic} exception",
                    "FastAPI {topic} best practices",
                    "Proper way to handle {topic} in FastAPI"
                ],
                "topics": ["request validation", "response models", "dependency injection", "background tasks",
                          "middleware", "exception handlers", "path parameters", "query parameters", 
                          "request body validation", "status codes", "CORS configuration"]
            },
            {
                "text": "working with SQLAlchemy ORM queries and relationships",
                "occurrences": 18,
                "credibility_range": (0.86, 0.94),
                "templates": [
                    "SQLAlchemy {topic} query example",
                    "How to implement {topic} in SQLAlchemy?",
                    "SQLAlchemy {topic} relationship",
                    "Optimize SQLAlchemy {topic} query",
                    "SQLAlchemy {topic} not loading correctly",
                    "Debug SQLAlchemy {topic}",
                    "Best way to query {topic} with SQLAlchemy",
                    "SQLAlchemy {topic} performance issue"
                ],
                "topics": ["eager loading", "lazy loading", "many-to-many relationships", "one-to-many relationships",
                          "join queries", "filter operations", "session management", "query optimization",
                          "relationship cascade", "backref", "foreign keys", "composite keys"]
            },
            {
                "text": "implementing async operations and background tasks",
                "occurrences": 12,
                "credibility_range": (0.82, 0.91),
                "templates": [
                    "Python async {topic} implementation",
                    "How to use asyncio for {topic}?",
                    "Async/await with {topic}",
                    "Background task for {topic}",
                    "Celery vs asyncio for {topic}",
                    "Async {topic} best practices",
                    "Handle {topic} asynchronously"
                ],
                "topics": ["database operations", "API calls", "file processing", "email sending",
                          "task queues", "concurrent requests", "event loops", "async context managers"]
            },
            {
                "text": "pytest fixtures and testing API endpoints",
                "occurrences": 11,
                "credibility_range": (0.80, 0.89),
                "templates": [
                    "How to test {topic} with pytest?",
                    "Pytest fixture for {topic}",
                    "Mock {topic} in pytest",
                    "Test FastAPI {topic} endpoint",
                    "Pytest {topic} best practices",
                    "Setup {topic} for testing",
                    "Integration test for {topic}"
                ],
                "topics": ["database connections", "API endpoints", "authentication", "external APIs",
                          "file uploads", "background tasks", "dependency injection", "request/response"]
            },
            {
                "text": "Docker containerization and deployment configuration",
                "occurrences": 9,
                "credibility_range": (0.78, 0.87),
                "templates": [
                    "Dockerfile for Python {topic}",
                    "Docker compose {topic} setup",
                    "Containerize {topic} application",
                    "Docker {topic} best practices",
                    "Multi-stage Docker build for {topic}",
                    "Docker environment variables for {topic}",
                    "Debug Docker {topic} issue"
                ],
                "topics": ["FastAPI app", "PostgreSQL", "Redis", "multi-service setup",
                          "production deployment", "development environment", "volume mounting"]
            }
        ],
        "insufficient_behaviors": [
            {
                "text": "exploring Redis caching strategies",
                "occurrences": 4,
                "credibility_range": (0.70, 0.82),
                "templates": [
                    "Redis caching for {topic}",
                    "How to cache {topic} with Redis?",
                    "Redis {topic} pattern",
                    "Implement {topic} caching strategy"
                ],
                "topics": ["API responses", "database queries", "session data", "rate limiting"]
            },
            {
                "text": "considering security and authentication patterns",
                "occurrences": 5,
                "credibility_range": (0.72, 0.83),
                "templates": [
                    "JWT authentication for {topic}",
                    "Secure {topic} implementation",
                    "OAuth2 with {topic}",
                    "Best practices for {topic} security",
                    "Protect {topic} endpoint"
                ],
                "topics": ["API endpoints", "user registration", "password hashing", "token refresh", "CORS"]
            },
            {
                "text": "investigating database migration tools",
                "occurrences": 3,
                "credibility_range": (0.68, 0.79),
                "templates": [
                    "Alembic {topic} migration",
                    "Database migration for {topic}",
                    "How to handle {topic} with Alembic?"
                ],
                "topics": ["schema changes", "data migration", "rollback strategies"]
            }
        ],
        "noise_behaviors": [
            # Development-related but not project-specific
            {"text": "quick Python syntax lookup", "credibility": 0.42, "template": "Python list comprehension syntax"},
            {"text": "git command reference", "credibility": 0.38, "template": "How to revert git commit?"},
            {"text": "VS Code extension question", "credibility": 0.35, "template": "Best Python linter for VS Code"},
            {"text": "random JavaScript question", "credibility": 0.44, "template": "JavaScript array methods"},
            {"text": "Linux command query", "credibility": 0.40, "template": "Find files in Linux recursively"},
            {"text": "regex pattern help", "credibility": 0.46, "template": "Regex to match email addresses"},
            {"text": "JSON parsing question", "credibility": 0.39, "template": "Parse nested JSON in Python"},
            {"text": "environment variable question", "credibility": 0.41, "template": "Set environment variables in bash"},
            
            # Completely unrelated noise
            {"text": "random news query", "credibility": 0.33, "template": "Latest tech news today"},
            {"text": "weather question", "credibility": 0.31, "template": "What's the weather tomorrow?"},
            {"text": "movie recommendation", "credibility": 0.36, "template": "Good movies to watch on Netflix"},
            {"text": "cooking recipe", "credibility": 0.29, "template": "Easy dinner recipes"},
            {"text": "travel question", "credibility": 0.34, "template": "Best places to visit in Europe"},
            {"text": "fitness query", "credibility": 0.32, "template": "Home workout routine"},
            {"text": "random trivia", "credibility": 0.30, "template": "What's the speed of light?"},
            {"text": "book recommendation", "credibility": 0.37, "template": "Good sci-fi books to read"},
            {"text": "music question", "credibility": 0.35, "template": "Best productivity music playlists"},
            {"text": "general knowledge", "credibility": 0.28, "template": "What is quantum computing?"},
            {"text": "shopping query", "credibility": 0.33, "template": "Best mechanical keyboards 2026"},
            {"text": "casual conversation", "credibility": 0.27, "template": "Tell me a joke"},
            
            # Occasional unrelated tech queries
            {"text": "blockchain question", "credibility": 0.43, "template": "How does blockchain work?"},
            {"text": "machine learning curiosity", "credibility": 0.45, "template": "What is deep learning?"},
            {"text": "mobile app question", "credibility": 0.42, "template": "React Native vs Flutter"},
            {"text": "random algorithm question", "credibility": 0.44, "template": "Explain quicksort algorithm"},
            {"text": "system design curiosity", "credibility": 0.46, "template": "How to design a URL shortener?"}
        ],
        "days_back": 60,
        "description": "REALISTIC: Python developer building a FastAPI project over 2 months with mixed queries"
    }
]
# ===============================================

# --- DATA POOLS FOR REALISM ---
TOPICS = [
    "React hooks", "Next.js routing", "Vue composition API", "Angular signals",
    "TypeScript generics", "JavaScript promises", "Python decorators", "Django models",
    "Flask blueprints", "FastAPI", "PostgreSQL", "MongoDB aggregation", "Redis caching",
    "Docker containers", "Kubernetes pods", "AWS Lambda", "Google Cloud Run", "Azure Functions",
    "GraphQL", "REST APIs", "gRPC", "WebSockets", "CI/CD pipelines", "Git workflows",
    "TDD", "Integration testing", "End-to-end testing", "Code coverage", "Linting",
    "SQL injection", "XSS prevention", "CSRF protection", "JWT authentication", "OAuth2",
    "Encryption", "Hashing", "Salting", "SSL/TLS", "OWASP Top 10", "Microservices",
    "Monoliths", "Serverless", "Event-driven architecture", "CQRS", "Event sourcing",
    "Clean Architecture", "SOLID principles", "Design patterns", "System design",
    "Load balancing", "Caching strategies", "Database sharding", "Replication",
    "CAP theorem", "ACID properties", "BASE consistency", "Binary search", "Merge sort",
    "Quick sort", "Breadth-first search", "Depth-first search", "Dijkstra's algorithm",
    "Dynamic programming", "Greedy algorithms", "Backtracking", "Recursion", "Big O notation",
    "Hash tables", "Linked lists", "Trees", "Graphs", "Stacks", "Queues", "Heaps"
]

# Archetypes define the "Behavior" and the "Templates" used to generate prompts for it.
BEHAVIOR_ARCHETYPES = [
    {
        "text": "prefers visual diagrams and flowcharts",
        "category": "visual",
        "templates": [
            "Show me a diagram of {topic}", "Visual breakdown of {topic}", 
            "Can you create a diagram explaining {topic}?", "Draw a flowchart for {topic}", 
            "Illustrate {topic} visually", "I need a visual representation of {topic}"
        ]
    },
    {
        "text": "requests code examples and snippets",
        "category": "code",
        "templates": [
            "Show me code examples for {topic}", "I need code samples for {topic}",
            "Write a function to handle {topic}", "Can you provide sample code for {topic}?",
            "Give me a code snippet for {topic}", "Example implementation of {topic}",
            "Show me how to code {topic}", "Working code for {topic}"
        ]
    },
    {
        "text": "prefers step-by-step instructions",
        "category": "step",
        "templates": [
            "I need a step-by-step tutorial on {topic}", "Walk me through {topic}",
            "What are the steps involved in {topic}?", "Guide me through {topic} one step at a time",
            "How do I implement {topic}? Step by step", "Can you explain {topic} step-by-step?",
            "Sequential instructions for {topic}", "Show me the steps to set up {topic}"
        ]
    },
    {
        "text": "focuses on debugging and troubleshooting",
        "category": "debug",
        "templates": [
            "I'm getting an error with {topic}", "Help me debug {topic}",
            "Why isn't {topic} working?", "Troubleshoot {topic}",
            "Fix my {topic} problem", "What's wrong with my {topic}?",
            "How to fix {topic} errors", "Troubleshooting guide for {topic}"
        ]
    },
    {
        "text": "prefers concise, brief explanations",
        "category": "concise",
        "templates": [
            "Short explanation of {topic}", "TL;DR for {topic}",
            "Quick summary of {topic}", "In brief: {topic}",
            "Concise guide to {topic}", "Quick answer: {topic}",
            "Brief intro to {topic}", "Brief overview of {topic}"
        ]
    },
    {
        "text": "requests detailed, comprehensive explanations",
        "category": "deep",
        "templates": [
            "Detailed breakdown of {topic}", "Deep dive into {topic}",
            "Comprehensive guide to {topic}", "Explain {topic} in detail",
            "Everything about {topic}", "Thorough explanation of {topic}",
            "In-depth analysis of {topic}", "Full explanation of {topic}"
        ]
    },
    # Adding more specific behaviors to hit the >11 requirement easily
    {
        "text": "frequently asks about security vulnerabilities",
        "category": "security",
        "templates": [
            "How to prevent attacks on {topic}", "Security vulnerabilities in {topic}",
            "Is {topic} secure?", "Best security practices for {topic}",
            "Securing {topic}"
        ]
    },
    {
        "text": "focuses on performance optimization",
        "category": "perf",
        "templates": [
            "How to optimize {topic}", "Improving performance of {topic}",
            "Latency issues with {topic}", "Speed up {topic}",
            "Benchmarking {topic}"
        ]
    },
    {
        "text": "prefers theoretical concepts over implementation",
        "category": "theory",
        "templates": [
            "What is the theory behind {topic}?", "Concept of {topic}",
            "Define {topic}", "History of {topic}", "Why use {topic}?"
        ]
    },
    {
        "text": "asks for comparisons between technologies",
        "category": "compare",
        "templates": [
            "Compare {topic} vs alternatives", "{topic} vs others",
            "Pros and cons of {topic}", "When to use {topic}",
            "Difference between {topic} and..."
        ]
    },
    {
        "text": "requests best practices and standards",
        "category": "best_practice",
        "templates": [
            "Best practices for {topic}", "Industry standards for {topic}",
            "Clean way to do {topic}", "Proper convention for {topic}"
        ]
    }
]

NOISE_TEMPLATES = [
    "I need help with {topic}", "Tell me about {topic}", "{topic}", 
    "Info on {topic}", "Can you help with {topic}?", "What is {topic}?",
    "About {topic}", "{topic} please"
]

# Global counter to ensure unique IDs
_id_counter = 0

def generate_short_id(prefix=""):
    """Generates a unique ID like 'prompt_09fba7_0001'"""
    global _id_counter
    _id_counter += 1
    unique_str = f"{uuid.uuid4()}-{time.time()}-{_id_counter}"
    hash_str = hashlib.md5(unique_str.encode()).hexdigest()[:8]  # Increased from 6 to 8 chars
    return f"{prefix}_{hash_str}_{_id_counter:06d}"

def generate_controlled_demo_dataset(profile, start_time):
    """Generate controlled demo dataset with specific CORE, INSUFFICIENT, and NOISE distributions"""
    prompts_list = []
    behaviors_list = []
    
    user_id = profile["user_id"]
    days_back = profile["days_back"]
    
    # Time phases for controlled distribution
    # Day 1-3: exploratory/noisy (20% of time)
    # Day 4-10: stable behaviors (50% of time)
    # Day 11-14: drift + some noise (30% of time)
    
    total_seconds = days_back * 24 * 3600
    phase1_end = start_time.timestamp() + (total_seconds * 0.2)   # Day 1-3
    phase2_end = start_time.timestamp() + (total_seconds * 0.7)   # Day 4-10
    phase3_end = start_time.timestamp() + total_seconds          # Day 11-14
    
    current_time = start_time.timestamp()
    
    # === GENERATE CORE BEHAVIORS ===
    for core_idx, core_behavior in enumerate(profile["core_behaviors"]):
        behavior_id = generate_short_id("beh")
        observation_id = generate_short_id("obs")
        session_id = f"sess_core_{core_idx:03d}"
        history_ids = []
        
        occurrences = core_behavior["occurrences"]
        templates = core_behavior["templates"]
        topics = core_behavior["topics"]
        cred_min, cred_max = core_behavior["credibility_range"]
        
        # Distribute occurrences across Phase 2 (Day 4-10) primarily, with some in Phase 3
        phase2_count = int(occurrences * 0.7)  # 70% in stable phase
        phase3_count = occurrences - phase2_count  # 30% in drift phase
        
        # Phase 2 occurrences (stable period)
        for i in range(phase2_count):
            prompt_id = generate_short_id("prompt")
            template = random.choice(templates)
            topic = random.choice(topics)
            text = template.format(topic=topic)
            
            # Random time within Phase 2
            timestamp = random.uniform(phase1_end, phase2_end)
            credibility = round(random.uniform(cred_min, cred_max), 2)
            
            p_obj = {
                "prompt_id": prompt_id,
                "prompt_text": text,
                "timestamp": int(timestamp),
                "tokens": round(random.uniform(8.0, 25.0), 1),
                "is_noise": False,
                "user_id": user_id,
                "session_id": session_id
            }
            prompts_list.append(p_obj)
            history_ids.append(prompt_id)
        
        # Phase 3 occurrences (drift period)
        for i in range(phase3_count):
            prompt_id = generate_short_id("prompt")
            template = random.choice(templates)
            topic = random.choice(topics)
            text = template.format(topic=topic)
            
            timestamp = random.uniform(phase2_end, phase3_end)
            credibility = round(random.uniform(cred_min, cred_max), 2)
            
            p_obj = {
                "prompt_id": prompt_id,
                "prompt_text": text,
                "timestamp": int(timestamp),
                "tokens": round(random.uniform(8.0, 25.0), 1),
                "is_noise": False,
                "user_id": user_id,
                "session_id": session_id
            }
            prompts_list.append(p_obj)
            history_ids.append(prompt_id)
        
        # Create behavior object
        avg_credibility = round((cred_min + cred_max) / 2, 2)
        b_obj = {
            "behavior_id": behavior_id,
            "observation_id": observation_id,
            "behavior_text": core_behavior["text"],
            "credibility": avg_credibility,
            "reinforcement_count": occurrences,
            "last_seen": int(max(p["timestamp"] for p in prompts_list if p["prompt_id"] in history_ids)),
            "prompt_history_ids": history_ids,
            "user_id": user_id,
            "session_id": session_id,
            "clarity_score": round(random.uniform(0.85, 0.97), 2),
            "confidence": round(min(0.5 + (occurrences * 0.04), 0.95), 2)
        }
        behaviors_list.append(b_obj)
    
    # === GENERATE INSUFFICIENT_EVIDENCE BEHAVIORS ===
    for insuff_idx, insuff_behavior in enumerate(profile["insufficient_behaviors"]):
        behavior_id = generate_short_id("beh")
        observation_id = generate_short_id("obs")
        session_id = f"sess_insuff_{insuff_idx:03d}"
        history_ids = []
        
        occurrences = insuff_behavior["occurrences"]
        templates = insuff_behavior["templates"]
        topics = insuff_behavior["topics"]
        cred_min, cred_max = insuff_behavior["credibility_range"]
        
        # Sparse occurrences spread across Phase 2 and Phase 3
        for i in range(occurrences):
            prompt_id = generate_short_id("prompt")
            template = random.choice(templates)
            topic = random.choice(topics)
            text = template.format(topic=topic)
            
            # Random time across stable and drift phases
            timestamp = random.uniform(phase1_end, phase3_end)
            credibility = round(random.uniform(cred_min, cred_max), 2)
            
            p_obj = {
                "prompt_id": prompt_id,
                "prompt_text": text,
                "timestamp": int(timestamp),
                "tokens": round(random.uniform(7.0, 20.0), 1),
                "is_noise": False,
                "user_id": user_id,
                "session_id": session_id
            }
            prompts_list.append(p_obj)
            history_ids.append(prompt_id)
        
        # Create behavior object
        avg_credibility = round((cred_min + cred_max) / 2, 2)
        b_obj = {
            "behavior_id": behavior_id,
            "observation_id": observation_id,
            "behavior_text": insuff_behavior["text"],
            "credibility": avg_credibility,
            "reinforcement_count": occurrences,
            "last_seen": int(max(p["timestamp"] for p in prompts_list if p["prompt_id"] in history_ids)),
            "prompt_history_ids": history_ids,
            "user_id": user_id,
            "session_id": session_id,
            "clarity_score": round(random.uniform(0.70, 0.85), 2),
            "confidence": round(0.5 + (occurrences * 0.03), 2)
        }
        behaviors_list.append(b_obj)
    
    # === GENERATE NOISE BEHAVIORS ===
    # Primarily in Phase 1 (exploratory) and some in Phase 3
    phase1_noise = int(len(profile["noise_behaviors"]) * 0.6)  # 60% in Phase 1
    phase3_noise = len(profile["noise_behaviors"]) - phase1_noise  # 40% in Phase 3
    
    noise_pool = profile["noise_behaviors"].copy()
    random.shuffle(noise_pool)
    
    for i, noise_behavior in enumerate(noise_pool):
        behavior_id = generate_short_id("beh")
        observation_id = generate_short_id("obs")
        prompt_id = generate_short_id("prompt")
        session_id = f"sess_noise_{i:03d}"
        
        # Decide phase
        if i < phase1_noise:
            timestamp = random.uniform(start_time.timestamp(), phase1_end)
        else:
            timestamp = random.uniform(phase2_end, phase3_end)
        
        p_obj = {
            "prompt_id": prompt_id,
            "prompt_text": noise_behavior["template"],
            "timestamp": int(timestamp),
            "tokens": round(random.uniform(3.0, 10.0), 1),
            "is_noise": True,
            "user_id": user_id,
            "session_id": session_id
        }
        prompts_list.append(p_obj)
        
        # Create behavior object (single occurrence)
        b_obj = {
            "behavior_id": behavior_id,
            "observation_id": observation_id,
            "behavior_text": noise_behavior["text"],
            "credibility": noise_behavior["credibility"],
            "reinforcement_count": 1,
            "last_seen": int(timestamp),
            "prompt_history_ids": [prompt_id],
            "user_id": user_id,
            "session_id": session_id,
            "clarity_score": round(random.uniform(0.40, 0.65), 2),
            "confidence": round(random.uniform(0.30, 0.50), 2)
        }
        behaviors_list.append(b_obj)
    
    # Sort prompts by timestamp
    prompts_list.sort(key=lambda x: x['timestamp'])
    
    return behaviors_list, prompts_list

def generate_dataset(user_id, num_behaviors, min_prompts, max_prompts, noise_ratio, start_time):
    prompts_list = []
    behaviors_list = []
    
    current_time = start_time.timestamp()
    
    # 1. Select Archetypes (ensure we have enough for the requested count)
    # If requested num_behaviors is higher than our unique archetypes, 
    # we create variations by combining archetypes with different topics
    selected_archetypes = []
    
    if num_behaviors <= len(BEHAVIOR_ARCHETYPES):
        # Use unique archetypes for small datasets
        selected_archetypes = random.sample(BEHAVIOR_ARCHETYPES, num_behaviors)
    else:
        # For large datasets, create variations by cycling through archetypes
        # and potentially modifying them slightly for diversity
        base_archetypes = BEHAVIOR_ARCHETYPES.copy()
        
        while len(selected_archetypes) < num_behaviors:
            if not base_archetypes:
                base_archetypes = BEHAVIOR_ARCHETYPES.copy()
            
            arch = base_archetypes.pop(0)
            # Create a variation by adding a topic-specific modifier for large datasets
            if num_behaviors > 50:  # Only for truly massive datasets
                topic_modifier = random.choice(TOPICS[:10])  # Use first 10 topics as modifiers
                modified_arch = arch.copy()
                modified_arch["text"] = f"{arch['text']} (related to {topic_modifier})"
                selected_archetypes.append(modified_arch)
            else:
                selected_archetypes.append(arch)

    # 2. Generate Data per Behavior
    for i, arch in enumerate(selected_archetypes):
        
        # Decide how strong this behavior is
        count = random.randint(min_prompts, max_prompts)
        behavior_id = generate_short_id("beh")
        observation_id = generate_short_id("obs")
        
        # We need to track which prompt IDs belong to this behavior
        history_ids = []
        
        # Generate Prompts for this behavior
        session_base = f"sess_{arch['category']}_{i:03d}"
        
        for _ in range(count):
            prompt_id = generate_short_id("prompt")
            topic = random.choice(TOPICS)
            template = random.choice(arch['templates'])
            text = template.format(topic=topic)
            
            # Increment time slightly (between 2 mins and 3 hours)
            current_time += random.randint(120, 10800)
            
            p_obj = {
                "prompt_id": prompt_id,
                "prompt_text": text,
                "timestamp": int(current_time),
                "tokens": round(random.uniform(1.3, 13.0), 1),
                "is_noise": False,
                "user_id": user_id,
                "session_id": session_base
            }
            prompts_list.append(p_obj)
            history_ids.append(prompt_id)

        # Generate the Behavior Object
        # Calculate scores based on volume
        credibility = min(0.5 + (count * 0.015), 0.98) # Cap at 0.98
        confidence = min(0.5 + (count * 0.015), 0.96)
        
        b_obj = {
            "behavior_id": behavior_id,
            "observation_id": observation_id,
            "behavior_text": arch["text"],
            "credibility": round(credibility, 2),
            "reinforcement_count": count,
            "last_seen": int(current_time),
            "prompt_history_ids": history_ids, # THE CONNECTION
            "user_id": user_id,
            "session_id": session_base,
            "clarity_score": round(random.uniform(0.7, 0.99), 2),
            "confidence": round(confidence, 2)
        }
        behaviors_list.append(b_obj)

    # 3. Generate Noise (Prompts not linked to behaviors)
    total_prompts = len(prompts_list)
    noise_count = int(total_prompts * noise_ratio)
    
    # Reset time to intersperse noise, or just add them at random times?
    # Better: Insert them with random timestamps within the range we just covered.
    min_ts = prompts_list[0]['timestamp']
    max_ts = prompts_list[-1]['timestamp']
    
    for i in range(noise_count):
        prompt_id = generate_short_id("prompt")
        topic = random.choice(TOPICS)
        text = random.choice(NOISE_TEMPLATES).format(topic=topic)
        ts = random.randint(min_ts, max_ts)
        
        p_obj = {
            "prompt_id": prompt_id,
            "prompt_text": text,
            "timestamp": ts,
            "tokens": round(random.uniform(1.0, 6.0), 1),
            "is_noise": True,
            "user_id": user_id,
            "session_id": f"sess_noise_{i:03d}"
        }
        prompts_list.append(p_obj)

    # 4. Sort prompts by timestamp
    prompts_list.sort(key=lambda x: x['timestamp'])

    return behaviors_list, prompts_list

def generate_all_datasets():
    """Generate datasets for all user profiles"""
    all_datasets = {}
    
    # Create output directory if it doesn't exist
    os.makedirs("realistic_evaluation_set", exist_ok=True)
    
    print("="*70)
    print("GENERATING TEST DATASETS FOR MULTIPLE USERS")
    print("="*70)
    
    for profile in USER_PROFILES:
        user_id = profile["user_id"]
        print(f"\n📊 Generating dataset for: {user_id}")
        print(f"   Description: {profile['description']}")
        
        start_time = datetime.now() - timedelta(days=profile["days_back"])
        
        # Check if this is a controlled demo dataset
        if profile.get("mode") == "controlled_demo":
            print(f"   🎯 CONTROLLED DEMO MODE")
            print(f"   CORE behaviors: {len(profile['core_behaviors'])}")
            print(f"   INSUFFICIENT_EVIDENCE behaviors: {len(profile['insufficient_behaviors'])}")
            print(f"   NOISE behaviors: {len(profile['noise_behaviors'])}")
            print(f"   Time span: {profile['days_back']} days")
            
            behaviors, prompts = generate_controlled_demo_dataset(profile, start_time)
        else:
            print(f"   Behaviors: {profile['num_behaviors']}, Prompts: {profile['min_prompts']}-{profile['max_prompts']}, Noise: {profile['noise_ratio']*100}%")
            
            # Progress indicator for large datasets
            if profile["num_behaviors"] > 100:
                print(f"   ⏳ Generating large dataset ({profile['num_behaviors']} behaviors)...")
            
            behaviors, prompts = generate_dataset(
                user_id=user_id,
                num_behaviors=profile["num_behaviors"],
                min_prompts=profile["min_prompts"],
                max_prompts=profile["max_prompts"],
                noise_ratio=profile["noise_ratio"],
                start_time=start_time
            )
        
        all_datasets[user_id] = {
            "behaviors": behaviors,
            "prompts": prompts,
            "profile": profile
        }
        
        # Save individual user files
        behaviors_file = f"realistic_evaluation_set/behaviors_{user_id}.json"
        prompts_file = f"realistic_evaluation_set/prompts_{user_id}.json"
        
        print(f"   💾 Saving {len(behaviors)} behaviors and {len(prompts)} prompts...")
        
        with open(behaviors_file, "w") as f:
            json.dump(behaviors, f, indent=2)
        with open(prompts_file, "w") as f:
            json.dump(prompts, f, indent=2)
            
        print(f"   ✅ Generated {len(behaviors)} behaviors, {len(prompts)} prompts")
        print(f"   📁 Saved to: {behaviors_file}, {prompts_file}")
    
    # Generate summary file
    summary = {
        "generated_at": datetime.now().isoformat(),
        "total_users": len(USER_PROFILES),
        "users": {}
    }
    
    for user_id, data in all_datasets.items():
        profile = data["profile"]
        
        # Handle controlled demo vs regular datasets
        if profile.get("mode") == "controlled_demo":
            summary["users"][user_id] = {
                "description": profile["description"],
                "mode": "controlled_demo",
                "behaviors_count": len(data["behaviors"]),
                "prompts_count": len(data["prompts"]),
                "core_behaviors": len(profile["core_behaviors"]),
                "insufficient_behaviors": len(profile["insufficient_behaviors"]),
                "noise_behaviors": len(profile["noise_behaviors"]),
                "time_span_days": profile["days_back"],
                "files": {
                    "behaviors": f"behaviors_{user_id}.json",
                    "prompts": f"prompts_{user_id}.json"
                }
            }
        else:
            summary["users"][user_id] = {
                "description": profile["description"],
                "behaviors_count": len(data["behaviors"]),
                "prompts_count": len(data["prompts"]),
                "noise_ratio": profile["noise_ratio"],
                "time_span_days": profile["days_back"],
                "files": {
                    "behaviors": f"behaviors_{user_id}.json",
                    "prompts": f"prompts_{user_id}.json"
                }
            }
    
    with open("realistic_evaluation_set/dataset_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "="*70)
    print("✅ ALL DATASETS GENERATED SUCCESSFULLY")
    print("="*70)
    print(f"\n📋 Summary saved to: realistic_evaluation_set/dataset_summary.json")
    print(f"\nGenerated {len(USER_PROFILES)} user datasets:")
    for user_id, info in summary["users"].items():
        print(f"  • {user_id}: {info['behaviors_count']} behaviors, {info['prompts_count']} prompts")
    print("\n")

if __name__ == "__main__":
    generate_all_datasets()
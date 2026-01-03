"""
Realistic Synthetic Behavior Data Generator for Research Evaluation

Generates diverse user personas with varying characteristics:
- Different dataset sizes (small, medium, large)
- Different clustering patterns (tight, dispersed, mixed)
- Realistic reinforcement distributions
- Real-world learning preferences and interaction patterns

This creates more realistic test data than random generation while
maintaining control over specific characteristics for evaluation purposes.
"""

import json
import random
import time
import hashlib
import os
from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta


# ==================== USER PERSONAS ====================

@dataclass
class UserPersona:
    """Defines a realistic user with specific learning/behavior preferences."""
    user_id: str
    name: str
    description: str
    core_preferences: List[Tuple[str, float]]  # (behavior, stability_target)
    peripheral_behaviors: List[str]
    interaction_style: str  # "frequent", "moderate", "sparse"
    session_count: int
    target_prompt_count: int
    noise_ratio: float  # 0.0 to 0.3


# ==================== REALISTIC BEHAVIOR PATTERNS ====================

# Learning styles with semantic clustering characteristics
LEARNING_STYLE_CLUSTERS = {
    "visual_learner": {
        "tight": [  # High semantic similarity = high stability
            "prefers diagrams and flowcharts",
            "learns best with visual examples",
            "likes infographics and charts",
        ],
        "credibility": 0.9
    },
    "procedural_learner": {
        "tight": [
            "prefers step-by-step instructions",
            "likes sequential guides",
            "wants ordered procedures",
        ],
        "credibility": 0.95
    },
    "conceptual_learner": {
        "medium": [  # Medium similarity = medium stability
            "wants theoretical explanations",
            "prefers understanding principles first",
            "interested in underlying concepts",
            "asks about design patterns",
        ],
        "credibility": 0.85
    },
    "practical_learner": {
        "medium": [
            "learns by doing",
            "prefers hands-on examples",
            "wants code samples",
            "likes working prototypes",
        ],
        "credibility": 0.88
    },
    "research_oriented": {
        "dispersed": [  # Low similarity = low stability
            "wants detailed documentation",
            "prefers academic papers",
            "interested in research citations",
            "asks for technical specifications",
            "needs architectural overviews",
        ],
        "credibility": 0.75
    }
}

# Common prompt templates for realistic interactions
PROMPT_TEMPLATES = {
    "visual_learner": [
        "Can you show me a diagram of {topic}?",
        "Draw me a flowchart for {topic}",
        "Visual representation of {topic} please",
        "Explain {topic} with pictures",
        "Create an infographic about {topic}",
    ],
    "procedural_learner": [
        "Step-by-step guide for {topic}",
        "Walk me through {topic}",
        "How do I implement {topic}? Step by step",
        "Sequential instructions for {topic}",
        "Break down {topic} into steps",
    ],
    "conceptual_learner": [
        "What's the theory behind {topic}?",
        "Explain the concept of {topic}",
        "Why does {topic} work this way?",
        "Design principles for {topic}",
        "Underlying architecture of {topic}",
    ],
    "practical_learner": [
        "Show me code for {topic}",
        "Hands-on example of {topic}",
        "Working prototype of {topic}",
        "Let me try {topic} myself",
        "Real-world implementation of {topic}",
    ],
    "research_oriented": [
        "Documentation for {topic}",
        "Technical specs of {topic}",
        "Research papers about {topic}",
        "Detailed architecture of {topic}",
        "Citations for {topic}",
    ],
    "noise": [  # Generic non-indicative prompts
        "Tell me about {topic}",
        "What is {topic}?",
        "Information on {topic}",
        "{topic} overview",
        "Quick question about {topic}",
    ]
}

# Technical topics for realistic domain
TECHNICAL_TOPICS = [
    "React hooks", "Docker containers", "REST APIs", "GraphQL", "microservices",
    "database indexing", "OAuth2", "CI/CD pipelines", "load balancing", "caching strategies",
    "async programming", "API design", "error handling", "testing patterns", "deployment",
    "monitoring", "logging", "security", "authentication", "authorization",
    "data structures", "algorithms", "SQL queries", "NoSQL databases", "message queues",
    "websockets", "serverless", "Kubernetes", "cloud architecture", "performance optimization"
]


# ==================== USER PERSONA DEFINITIONS ====================

def create_personas() -> List[UserPersona]:
    """Create diverse user personas for realistic testing."""
    
    personas = [
        # 1. Small dataset with tight clustering (should produce CORE)
        UserPersona(
            user_id="user_stable_01",
            name="Visual Viktor",
            description="Strong visual learner with consistent tight clustering",
            core_preferences=[
                ("prefers diagrams and flowcharts", 0.25),
                ("learns best with visual examples", 0.23),
            ],
            peripheral_behaviors=["likes infographics and charts"],
            interaction_style="moderate",
            session_count=3,
            target_prompt_count=18,
            noise_ratio=0.1
        ),
        
        # 2. Small dataset with dispersed clustering (like user_665390)
        UserPersona(
            user_id="user_sparse_01",
            name="Scattered Sam",
            description="Multiple weak preferences, high reinforcement but low stability",
            core_preferences=[
                ("prefers step-by-step instructions", 0.08),  # High count, low stability
                ("learns by doing", 0.06),
            ],
            peripheral_behaviors=[
                "wants code samples",
                "asks for examples",
                "prefers quick summaries",
            ],
            interaction_style="frequent",
            session_count=2,
            target_prompt_count=15,
            noise_ratio=0.15
        ),
        
        # 3. Medium dataset with mixed stability
        UserPersona(
            user_id="user_mixed_01",
            name="Balanced Beth",
            description="Mix of stable and unstable preferences",
            core_preferences=[
                ("wants theoretical explanations", 0.18),  # Medium stability
                ("prefers understanding principles first", 0.16),
                ("prefers hands-on examples", 0.09),  # Lower stability
            ],
            peripheral_behaviors=[
                "wants code samples",
                "asks about design patterns",
            ],
            interaction_style="moderate",
            session_count=4,
            target_prompt_count=28,
            noise_ratio=0.12
        ),
        
        # 4. Very small dataset (edge case)
        UserPersona(
            user_id="user_tiny_01",
            name="Minimal Mike",
            description="Very few interactions, testing small-N behavior",
            core_preferences=[
                ("likes sequential guides", 0.15),
            ],
            peripheral_behaviors=["wants ordered procedures"],
            interaction_style="sparse",
            session_count=2,
            target_prompt_count=10,
            noise_ratio=0.2
        ),
        
        # 5. Large stable dataset
        UserPersona(
            user_id="user_large_01",
            name="Dedicated Dana",
            description="Many interactions with strong consistent preferences",
            core_preferences=[
                ("prefers step-by-step instructions", 0.28),
                ("likes sequential guides", 0.26),
                ("wants ordered procedures", 0.24),
            ],
            peripheral_behaviors=[
                "learns best with visual examples",
                "wants code samples",
            ],
            interaction_style="frequent",
            session_count=6,
            target_prompt_count=45,
            noise_ratio=0.08
        ),
        
        # 6. Research-heavy user (dispersed, low stability)
        UserPersona(
            user_id="user_research_01",
            name="Academic Alice",
            description="Research-oriented, semantically dispersed behaviors",
            core_preferences=[
                ("wants detailed documentation", 0.05),  # Very low stability
                ("interested in research citations", 0.04),
                ("asks for technical specifications", 0.06),
            ],
            peripheral_behaviors=[
                "prefers academic papers",
                "needs architectural overviews",
            ],
            interaction_style="moderate",
            session_count=3,
            target_prompt_count=22,
            noise_ratio=0.18
        ),
    ]
    
    return personas


# ==================== DATA GENERATION ====================

def generate_id(prefix: str) -> str:
    """Generate unique ID with prefix."""
    seed = f"{random.random()}{time.time()}"
    return f"{prefix}_{hashlib.md5(seed.encode()).hexdigest()[:6]}"


def estimate_tokens(text: str) -> float:
    """Estimate token count from text length."""
    return round(len(text) / 4 + random.uniform(-1, 1), 1)


def generate_prompts_for_behavior(
    behavior_text: str,
    behavior_category: str,
    topic_pool: List[str],
    count: int
) -> List[Dict]:
    """Generate realistic prompts for a behavior."""
    prompts = []
    templates = PROMPT_TEMPLATES.get(behavior_category, PROMPT_TEMPLATES["noise"])
    
    for _ in range(count):
        template = random.choice(templates)
        topic = random.choice(topic_pool)
        prompt_text = template.format(topic=topic)
        
        prompts.append({
            "prompt_id": generate_id("prompt"),
            "prompt_text": prompt_text,
            "timestamp": int(time.time()) + random.randint(-86400, 0),  # Last 24h
            "tokens": estimate_tokens(prompt_text),
            "is_noise": False
        })
    
    return prompts


def generate_noise_prompts(count: int) -> List[Dict]:
    """Generate noise prompts (non-indicative)."""
    prompts = []
    
    for _ in range(count):
        template = random.choice(PROMPT_TEMPLATES["noise"])
        topic = random.choice(TECHNICAL_TOPICS)
        prompt_text = template.format(topic=topic)
        
        prompts.append({
            "prompt_id": generate_id("prompt"),
            "prompt_text": prompt_text,
            "timestamp": int(time.time()) + random.randint(-86400, 0),
            "tokens": estimate_tokens(prompt_text),
            "is_noise": True
        })
    
    return prompts


def infer_category_from_behavior(behavior_text: str) -> str:
    """Infer which category a behavior belongs to."""
    behavior_lower = behavior_text.lower()
    
    for category, cluster_info in LEARNING_STYLE_CLUSTERS.items():
        for behavior in cluster_info["tight"] if "tight" in cluster_info else cluster_info.get("medium", cluster_info.get("dispersed", [])):
            if behavior.lower() in behavior_lower or behavior_lower in behavior.lower():
                return category
    
    return "noise"


def generate_user_data(persona: UserPersona, output_dir: str):
    """Generate complete dataset for a user persona."""
    
    print(f"\nGenerating data for: {persona.name} ({persona.user_id})")
    print(f"  Description: {persona.description}")
    print(f"  Target prompts: {persona.target_prompt_count}")
    print(f"  Noise ratio: {persona.noise_ratio:.1%}")
    
    all_prompts = []
    behaviors = []
    
    # Calculate prompt distribution
    noise_prompt_count = int(persona.target_prompt_count * persona.noise_ratio)
    signal_prompt_count = persona.target_prompt_count - noise_prompt_count
    
    # Distribute prompts across core preferences
    total_weight = sum(1.0 for _ in persona.core_preferences)
    
    for behavior_text, target_stability in persona.core_preferences:
        # More prompts = higher reinforcement
        # Stability affects how tightly prompts cluster (but we control via behavior choice)
        prompt_count = int((signal_prompt_count / total_weight) * random.uniform(0.8, 1.2))
        
        category = infer_category_from_behavior(behavior_text)
        credibility = LEARNING_STYLE_CLUSTERS.get(category, {}).get("credibility", 0.8)
        
        # Generate prompts
        prompts = generate_prompts_for_behavior(
            behavior_text,
            category,
            TECHNICAL_TOPICS,
            prompt_count
        )
        
        # Create behavior record matching original structure
        base_credibility = credibility + random.uniform(-0.05, 0.05)
        behavior = {
            "behavior_id": generate_id("beh"),
            "behavior_text": behavior_text,
            "credibility": base_credibility,  # Small variation
            "reinforcement_count": len(prompts),
            "last_seen": max(p["timestamp"] for p in prompts) if prompts else int(time.time()),
            "prompt_history_ids": [p["prompt_id"] for p in prompts],
            "user_id": persona.user_id,
            "session_id": "sess_" + generate_id("")[:6],  # Will be updated to random session
            "clarity_score": min(0.99, base_credibility + random.uniform(0.0, 0.1)),  # Slightly higher than credibility
            "confidence": min(0.99, base_credibility + random.uniform(-0.05, 0.15))  # Varies around credibility
        }
        
        behaviors.append(behavior)
        all_prompts.extend(prompts)
    
    # Add peripheral behaviors (lower reinforcement)
    for behavior_text in persona.peripheral_behaviors:
        prompt_count = random.randint(2, 5)
        category = infer_category_from_behavior(behavior_text)
        credibility = LEARNING_STYLE_CLUSTERS.get(category, {}).get("credibility", 0.75)
        
        prompts = generate_prompts_for_behavior(
            behavior_text,
            category,
            TECHNICAL_TOPICS,
            prompt_count
        )
        
        base_credibility = credibility + random.uniform(-0.1, 0.05)
        behavior = {
            "behavior_id": generate_id("beh"),
            "behavior_text": behavior_text,
            "credibility": base_credibility,
            "reinforcement_count": len(prompts),
            "last_seen": max(p["timestamp"] for p in prompts) if prompts else int(time.time()),
            "prompt_history_ids": [p["prompt_id"] for p in prompts],
            "user_id": persona.user_id,
            "session_id": "sess_" + generate_id("")[:6],
            "clarity_score": min(0.99, base_credibility + random.uniform(0.0, 0.1)),
            "confidence": min(0.99, base_credibility + random.uniform(-0.05, 0.15))
        }
        
        behaviors.append(behavior)
        all_prompts.extend(prompts)
    
    # Add noise prompts
    noise_prompts = generate_noise_prompts(noise_prompt_count)
    all_prompts.extend(noise_prompts)
    
    # Add session IDs and user IDs to prompts
    session_ids = [f"sess_{generate_id('')[:6]}" for _ in range(persona.session_count)]
    for prompt in all_prompts:
        prompt["user_id"] = persona.user_id
        prompt["session_id"] = random.choice(session_ids)
    
    # Update behaviors with consistent session_ids (use session from first prompt)
    for behavior in behaviors:
        if behavior["prompt_history_ids"]:
            first_prompt_id = behavior["prompt_history_ids"][0]
            matching_prompt = next((p for p in all_prompts if p["prompt_id"] == first_prompt_id), None)
            if matching_prompt:
                behavior["session_id"] = matching_prompt["session_id"]
    
    # Sort by timestamp
    all_prompts.sort(key=lambda x: x["timestamp"])
    
    # Save files
    os.makedirs(output_dir, exist_ok=True)
    
    behaviors_file = os.path.join(output_dir, f"behaviors_{persona.user_id}.json")
    prompts_file = os.path.join(output_dir, f"prompts_{persona.user_id}.json")
    
    with open(behaviors_file, 'w') as f:
        json.dump(behaviors, f, indent=2)
    
    with open(prompts_file, 'w') as f:
        json.dump(all_prompts, f, indent=2)
    
    print(f"  ✓ Generated {len(behaviors)} behaviors, {len(all_prompts)} prompts")
    print(f"  ✓ Files: {behaviors_file}, {prompts_file}")
    
    return behaviors, all_prompts


def generate_metadata(personas: List[UserPersona], output_dir: str):
    """Generate metadata file describing the test dataset."""
    metadata = {
        "generation_date": datetime.now().isoformat(),
        "purpose": "Research evaluation for Bachelor's thesis - Conservative Preference Inference",
        "total_users": len(personas),
        "users": []
    }
    
    for persona in personas:
        user_info = {
            "user_id": persona.user_id,
            "name": persona.name,
            "description": persona.description,
            "expected_characteristics": {
                "prompt_count": persona.target_prompt_count,
                "core_preference_count": len(persona.core_preferences),
                "peripheral_behavior_count": len(persona.peripheral_behaviors),
                "interaction_style": persona.interaction_style,
                "noise_ratio": persona.noise_ratio
            },
            "expected_clustering": [
                {
                    "behavior": behavior,
                    "target_stability": stability
                }
                for behavior, stability in persona.core_preferences
            ]
        }
        metadata["users"].append(user_info)
    
    metadata_file = os.path.join(output_dir, "test_dataset_metadata.json")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✓ Metadata saved: {metadata_file}")


# ==================== MAIN ====================

def main():
    """Generate complete realistic test dataset."""
    
    output_dir = "./realistic_test_data"
    
    print("=" * 80)
    print("REALISTIC SYNTHETIC BEHAVIOR DATA GENERATOR")
    print("=" * 80)
    print("\nGenerating diverse user personas for research evaluation...")
    
    personas = create_personas()
    
    print(f"\nCreated {len(personas)} user personas:")
    for p in personas:
        print(f"  - {p.name:20} | {p.target_prompt_count:2} prompts | {p.description}")
    
    print("\n" + "=" * 80)
    
    # Generate data for each persona
    for persona in personas:
        generate_user_data(persona, output_dir)
    
    # Generate metadata
    generate_metadata(personas, output_dir)
    
    print("\n" + "=" * 80)
    print("✓ GENERATION COMPLETE")
    print("=" * 80)
    print(f"\nGenerated {len(personas)} realistic test users in: {output_dir}/")
    print("\nUser characteristics:")
    print("  1. user_stable_01   - Small dataset, tight clustering (expect CORE)")
    print("  2. user_sparse_01   - Small dataset, dispersed (expect INSUFFICIENT_EVIDENCE)")
    print("  3. user_mixed_01    - Medium dataset, mixed stability")
    print("  4. user_tiny_01     - Very small dataset (N~10)")
    print("  5. user_large_01    - Large dataset, stable preferences")
    print("  6. user_research_01 - Research-oriented, dispersed behaviors")
    print("\nNext steps:")
    print("  1. Load this data into MongoDB and Qdrant")
    print("  2. Run frequency baseline on all users")
    print("  3. Run stability system on all users")
    print("  4. Compare results and analyze disagreements")


if __name__ == "__main__":
    main()

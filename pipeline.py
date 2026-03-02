import argparse
from typing import Dict, Any, List

from data_adapter import DataAdapter
from topic_discovery import TopicDiscoverer
from temporal_analysis import TemporalAnalyzer
from confirmation_model import ConfirmationModel

class CBIEPipeline:
    """
    The orchestrator for the Core Behaviour Identification Engine.
    Executes the ingestion, analysis (NLP, Temporal, Confirmation), and output phases.
    """
    
    def __init__(self):
        self.data_adapter = DataAdapter()
        self.topic_discoverer = TopicDiscoverer()
        self.temporal_analyzer = TemporalAnalyzer()
        self.confirmation_model = ConfirmationModel()

    def generate_identity_prompt(self, profile: Dict[str, Any]) -> str:
        """
        Creates a rigid System Prompt string anchored to the user's Core Behaviour Profile.
        """
        user_id = profile.get("user_id", "Unknown")
        interests = profile.get("confirmed_interests", [])
        
        facts = [i for i in interests if i.get("status") == "Stable Fact"]
        stable = [i for i in interests if i.get("status") == "Stable"]
        emerging = [i for i in interests if i.get("status") == "Emerging"]
        archived = [i for i in interests if i.get("status") == "ARCHIVED_CORE"]
        
        # Extract topics
        def get_topics(items):
            res = []
            for item in items:
                topics = item.get("representative_topics", [])
                if topics:
                    res.append(topics[0])
            return res
            
        fact_topics = get_topics(facts)
        stable_topics = get_topics(stable)
        emerging_topics = get_topics(emerging)
        archived_topics = get_topics(archived)
        
        prompt_parts = [f"--- SYSTEM IDENTITY ANCHOR FOR USER: {user_id} ---"]
        prompt_parts.append("You are speaking with a user who has following core traits and constraints.")
        
        if fact_topics:
            prompt_parts.append(f"\nCRITICAL CONSTRAINTS (Never violate):")
            for f in fact_topics:
                prompt_parts.append(f"- {f}")
                
        if stable_topics:
            prompt_parts.append(f"\nVERIFIED STABLE PREFERENCES:")
            for s in stable_topics:
                prompt_parts.append(f"- {s}")
                
        if emerging_topics:
            prompt_parts.append(f"\nEMERGING INTERESTS (Needs more verification):")
            for e in emerging_topics:
                prompt_parts.append(f"- {e}")
                
        if archived_topics:
            prompt_parts.append(f"\nARCHIVED OUTDATED HABITS (Do not use as active context):")
            for a in archived_topics:
                prompt_parts.append(f"- {a}")
                
        return "\n".join(prompt_parts)

    def process_user(self, user_id: str) -> Dict[str, Any]:
        """
        Runs the full CBIE pipeline for a single user.
        """
        print(f"--- Starting CBIE Pipeline for User: {user_id} ---")
        
        # 1. Ingestion
        print("Fetching user history...")
        behaviors = self.data_adapter.fetch_user_history(user_id)
        if not behaviors:
            print("No behaviors found.")
            return {}
            
        # 2. Topic Discovery & Fact Isolation (Stage 1)
        print("Running Topic Discovery, Fact Extraction, and Clustering...")
        fact_behaviors, standard_behaviors, _, labels = self.topic_discoverer.process_behaviors(behaviors)
        
        # 3. Temporal Analysis & Confirmation (Stage 2 & 3)
        confirmed_interests = []
        
        # --- Handle Absolute Facts first ---
        if fact_behaviors:
            print(f"Adding {len(fact_behaviors)} absolute facts to profile.")
            for fb in fact_behaviors:
                # We do not generalize facts because they are literal constraints
                # (e.g. "cannot eat peanuts", "avoids processed foods").
                # Generalizing them merges them into generic unhelpful labels like "Food Preferences".
                raw_fact_text = fb.get('explicit_topics', [fb.get('source_text')])[0]
                
                interest_profile = {
                    "cluster_id": "absolute_fact",
                    "representative_topics": [raw_fact_text],
                    "frequency": 1,
                    "consistency_score": 0.0,
                    "trend_score": 0.0,
                    "core_score": 1.0,
                    "status": self.confirmation_model.determine_status(1.0, is_fact=True)
                }
                confirmed_interests.append(interest_profile)
        
        # --- Handle Standard Clusters ---
        # Group behaviors by cluster
        clusters: Dict[int, List[Dict[str, Any]]] = {}
        for b in standard_behaviors:
            c_id = b.get('cluster_id')
            if c_id == -1: continue # Skip noise
            if c_id not in clusters:
                clusters[c_id] = []
            clusters[c_id].append(b)
            
        print(f"Found {len(clusters)} valid interest clusters.")
        
        # 3. Temporal Analysis & Confirmation (Stage 2 & 3)
        print("Analyzing temporal consistency and confirming core interests...")
        
        max_freq = max([len(c) for c in clusters.values()]) if clusters else 0
        
        for cluster_id, cluster_behaviors in clusters.items():
            freq = len(cluster_behaviors)
            
            # Extract timestamps and scores
            timestamps = [b.get('timestamp') for b in cluster_behaviors if b.get('timestamp')]
            scores = [b.get('scores', {}).get('clarity_score', 0.5) for b in cluster_behaviors]
            
            # Compute average credibility for the cluster
            avg_credibility = sum(scores_obj.get('credibility', 0.5) for scores_obj in [b.get('scores', {}) for b in cluster_behaviors]) / freq
            
            # Temporal Analysis
            consistency = self.temporal_analyzer.calculate_consistency(timestamps)
            trend = self.temporal_analyzer.calculate_trend(scores)
            
            # Confirmation
            core_score = self.confirmation_model.calculate_core_score(consistency, trend, freq, max_freq, avg_credibility)
            status = self.confirmation_model.determine_status(core_score, is_fact=False)
            
            # Generate a cohesive label using Azure OpenAI
            raw_cluster_texts = [b.get('source_text', '') for b in cluster_behaviors if b.get('source_text')]
            generalized_label = self.topic_discoverer.generalize_cluster_topic(raw_cluster_texts)
            representative_topics = [generalized_label]
                
            interest_profile = {
                "cluster_id": cluster_id,
                "representative_topics": representative_topics,
                "frequency": freq,
                "consistency_score": consistency,
                "trend_score": trend,
                "core_score": core_score,
                "status": status
            }
            
            if status != "Noise":
                 confirmed_interests.append(interest_profile)
                 
        print(f"Total Confirmed Interests/Facts: {len(confirmed_interests)}")
        
        # 4. Finalizing Profile
        final_profile = {
            "user_id": user_id,
            "total_raw_behaviors": len(behaviors),
            "confirmed_interests": confirmed_interests
        }
        
        # 5. Generate Identity Anchor Prompt
        prompt_string = self.generate_identity_prompt(final_profile)
        final_profile["identity_anchor_prompt"] = prompt_string
        
        # 6. Save Output
        self.data_adapter.save_profile(user_id, final_profile)
        
        # Save prompt string to a .txt file
        import os
        prompt_path = os.path.join(self.data_adapter.output_dir, f"{user_id}_prompt.txt")
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt_string)
        print(f"Generated Identity Anchor prompt saved to: {prompt_path}")
        print("Pipeline execution complete.")
        return final_profile

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the CBIE Pipeline.")
    parser.add_argument("--user_id", type=str, required=True, help="The User ID to process.")
    args = parser.parse_args()
    
    pipeline = CBIEPipeline()
    pipeline.process_user(args.user_id)

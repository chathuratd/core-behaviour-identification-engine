"""
Threshold Sensitivity Analysis

Tests different stability thresholds (0.05, 0.10, 0.15, 0.20) to understand
how the classification changes and find appropriate calibration values.
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple
import requests

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database.mongodb_service import MongoDBService
from src.database.qdrant_service import QdrantService
from src.services.clustering_engine import ClusteringEngine
from src.models.schemas import BehaviorObservation

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ThresholdAnalyzer:
    """Analyzes stability system behavior across different thresholds"""
    
    def __init__(self):
        self.mongodb = MongoDBService()
        self.qdrant = QdrantService()
        self.clustering = ClusteringEngine()
        
        self.test_thresholds = [0.05, 0.10, 0.15, 0.20]
        
        self.test_users = [
            ("user_stable_01", "Visual Viktor - tight clustering"),
            ("user_large_01", "Dedicated Dana - many interactions"),
            ("user_mixed_01", "Balanced Beth - mixed stability"),
        ]
    
    def get_user_behaviors(self, user_id: str) -> Tuple[List[BehaviorObservation], List[Dict]]:
        """Fetch behaviors and their metadata from storage"""
        try:
            # Get from Qdrant
            qdrant_behaviors = self.qdrant.get_embeddings_by_user(user_id)
            if not qdrant_behaviors:
                return [], []
            
            observations = []
            metadata = []
            
            for qb in qdrant_behaviors:
                payload = qb["payload"]
                
                # Create observation
                obs = BehaviorObservation(
                    observation_id=payload.get("behavior_id"),
                    behavior_text=payload["behavior_text"],
                    embedding=qb["vector"],
                    credibility=payload.get("credibility", 1.0),
                    clarity_score=payload.get("clarity_score", 1.0),
                    extraction_confidence=payload.get("extraction_confidence", 1.0),
                    timestamp=payload.get("timestamp", payload.get("last_seen", 0)),
                    prompt_id="prompt_test",
                    decay_rate=payload.get("decay_rate", 0.0),
                    user_id=payload["user_id"],
                    session_id=payload.get("session_id", "session_test")
                )
                observations.append(obs)
                
                # Store metadata for reporting
                metadata.append({
                    "behavior_id": payload.get("behavior_id"),
                    "behavior_text": payload["behavior_text"],
                    "reinforcement_count": payload.get("reinforcement_count", 1),
                    "credibility": payload.get("credibility", 1.0)
                })
            
            return observations, metadata
        except Exception as e:
            logger.error(f"Error fetching behaviors for {user_id}: {e}")
            return [], []
    
    def analyze_clustering(self, observations: List[BehaviorObservation]) -> Dict[str, Any]:
        """Run clustering and extract detailed metrics"""
        try:
            if len(observations) < 2:
                return {
                    "clusters_formed": 0,
                    "stability_scores": [],
                    "cluster_sizes": [],
                    "noise_points": len(observations),
                    "error": "Too few observations for clustering"
                }
            
            # Extract embeddings and IDs
            embeddings = [obs.embedding for obs in observations if obs.embedding]
            behavior_ids = [obs.observation_id for obs in observations if obs.embedding]
            
            if len(embeddings) < 2:
                return {
                    "clusters_formed": 0,
                    "stability_scores": [],
                    "cluster_sizes": [],
                    "noise_points": len(observations),
                    "error": "No embeddings available"
                }
            
            # Run clustering with behavior IDs
            result = self.clustering.cluster_behaviors(embeddings, behavior_ids)
            
            # Extract stability scores from cluster_stabilities dict
            stability_scores = list(result.get("cluster_stabilities", {}).values())
            
            # Get cluster information
            clusters = result.get("clusters", {})
            num_clusters = result.get("num_clusters", 0)
            noise_behaviors = result.get("noise_behaviors", [])
            labels = result.get("labels", [])
            
            # Get cluster sizes
            cluster_sizes = [len(members) for members in clusters.values()]
            
            return {
                "clusters_formed": num_clusters,
                "stability_scores": stability_scores,
                "cluster_sizes": cluster_sizes,
                "noise_points": len(noise_behaviors),
                "labels": labels,
                "cluster_dict": clusters,
                "cluster_stabilities": result.get("cluster_stabilities", {})
            }
            
        except Exception as e:
            logger.error(f"Error in clustering analysis: {e}", exc_info=True)
            return {
                "clusters_formed": 0,
                "stability_scores": [],
                "cluster_sizes": [],
                "noise_points": len(observations),
                "error": str(e)
            }
    
    def classify_with_threshold(
        self, 
        observations: List[BehaviorObservation],
        metadata: List[Dict],
        clustering_result: Dict[str, Any],
        threshold: float
    ) -> Dict[str, Any]:
        """Apply threshold to classify behaviors"""
        
        cluster_stabilities = clustering_result.get("cluster_stabilities", {})
        labels = clustering_result.get("labels", [])
        
        core_behaviors = []
        secondary_behaviors = []
        insufficient_behaviors = []
        
        # Classify each behavior
        for i, (obs, meta) in enumerate(zip(observations, metadata)):
            label = labels[i] if i < len(labels) else -1
            stability = cluster_stabilities.get(label, 0.0) if label != -1 else 0.0
            
            behavior_info = {
                "behavior_id": meta["behavior_id"],
                "behavior_text": meta["behavior_text"],
                "reinforcement_count": meta["reinforcement_count"],
                "stability_score": stability,
                "cluster_label": label
            }
            
            if label == -1:  # Noise
                insufficient_behaviors.append(behavior_info)
            elif stability >= threshold:
                core_behaviors.append(behavior_info)
            elif stability >= threshold / 2:  # Secondary at half threshold
                secondary_behaviors.append(behavior_info)
            else:
                insufficient_behaviors.append(behavior_info)
        
        return {
            "threshold": threshold,
            "core_count": len(core_behaviors),
            "secondary_count": len(secondary_behaviors),
            "insufficient_count": len(insufficient_behaviors),
            "core_behaviors": core_behaviors,
            "secondary_behaviors": secondary_behaviors
        }
    
    def analyze_user_all_thresholds(self, user_id: str, description: str) -> Dict[str, Any]:
        """Analyze one user across all thresholds"""
        logger.info(f"\n{'='*80}")
        logger.info(f"Analyzing: {user_id} - {description}")
        logger.info(f"{'='*80}")
        
        # Get behaviors
        observations, metadata = self.get_user_behaviors(user_id)
        
        if not observations:
            return {
                "user_id": user_id,
                "description": description,
                "error": "No behaviors found"
            }
        
        logger.info(f"Loaded {len(observations)} behaviors")
        
        # Run clustering once
        logger.info("Running HDBSCAN clustering...")
        clustering_result = self.analyze_clustering(observations)
        
        logger.info(f"Clustering results:")
        logger.info(f"  - Clusters formed: {clustering_result.get('clusters_formed', 0)}")
        logger.info(f"  - Stability scores: {clustering_result.get('stability_scores', [])}")
        logger.info(f"  - Cluster sizes: {clustering_result.get('cluster_sizes', [])}")
        logger.info(f"  - Noise points: {clustering_result.get('noise_points', 0)}")
        logger.info(f"  - Min cluster size: {clustering_result.get('min_cluster_size', 'N/A')}")
        logger.info(f"  - Min samples: {clustering_result.get('min_samples', 'N/A')}")
        
        # Test each threshold
        threshold_results = []
        for threshold in self.test_thresholds:
            result = self.classify_with_threshold(observations, metadata, clustering_result, threshold)
            threshold_results.append(result)
            logger.info(f"  Threshold {threshold:.2f}: {result['core_count']} CORE, {result['secondary_count']} SECONDARY")
        
        return {
            "user_id": user_id,
            "description": description,
            "total_behaviors": len(observations),
            "clustering": clustering_result,
            "threshold_results": threshold_results
        }
    
    def run_analysis(self) -> List[Dict[str, Any]]:
        """Run analysis on all test users"""
        results = []
        
        logger.info("\n" + "="*80)
        logger.info("THRESHOLD SENSITIVITY ANALYSIS")
        logger.info("="*80)
        logger.info(f"Testing thresholds: {self.test_thresholds}")
        logger.info(f"Test users: {len(self.test_users)}\n")
        
        for user_id, description in self.test_users:
            result = self.analyze_user_all_thresholds(user_id, description)
            results.append(result)
        
        return results
    
    def generate_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate markdown report"""
        report = []
        report.append("# Threshold Sensitivity Analysis Results\n")
        report.append(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**Thresholds tested:** {', '.join(str(t) for t in self.test_thresholds)}\n")
        report.append("---\n")
        
        # Summary table
        report.append("## Summary: CORE Behavior Counts by Threshold\n")
        report.append("| User | Total Behaviors | 0.05 | 0.10 | 0.15 | 0.20 | Clusters | Max Stability |\n")
        report.append("|------|----------------|------|------|------|------|----------|---------------|")
        
        for r in results:
            if "error" in r:
                continue
            
            user_id = r["user_id"]
            total = r["total_behaviors"]
            clusters = r["clustering"].get("clusters_formed", 0)
            stabilities = r["clustering"].get("stability_scores", [0.0])
            max_stability = max(stabilities) if stabilities else 0.0
            
            counts = []
            for thresh_result in r["threshold_results"]:
                counts.append(str(thresh_result["core_count"]))
            
            report.append(f"| {user_id} | {total} | {' | '.join(counts)} | {clusters} | {max_stability:.3f} |")
        
        report.append("\n---\n")
        
        # Detailed per-user results
        report.append("## Detailed Results\n")
        
        for r in results:
            if "error" in r:
                report.append(f"\n### {r['user_id']} - {r['description']}\n")
                report.append(f"**ERROR:** {r['error']}\n")
                continue
            
            report.append(f"\n### {r['user_id']} - {r['description']}\n")
            
            # Clustering info
            clustering = r["clustering"]
            report.append("**Clustering Analysis:**\n")
            report.append(f"- Clusters formed: {clustering.get('clusters_formed', 0)}")
            report.append(f"- Cluster sizes: {clustering.get('cluster_sizes', [])}")
            report.append(f"- Stability scores: {[f'{s:.3f}' for s in clustering.get('stability_scores', [])]}")
            report.append(f"- Noise points: {clustering.get('noise_points', 0)}")
            report.append(f"- HDBSCAN params: min_cluster_size={clustering.get('min_cluster_size', 'N/A')}, min_samples={clustering.get('min_samples', 'N/A')}\n")
            
            if "error" in clustering:
                report.append(f"**Clustering Error:** {clustering['error']}\n")
            
            # Threshold results
            report.append("**Classification by Threshold:**\n")
            for thresh_result in r["threshold_results"]:
                threshold = thresh_result["threshold"]
                report.append(f"\n*Threshold: {threshold:.2f}*")
                report.append(f"- CORE: {thresh_result['core_count']}")
                report.append(f"- SECONDARY: {thresh_result['secondary_count']}")
                report.append(f"- INSUFFICIENT: {thresh_result['insufficient_count']}")
                
                if thresh_result['core_behaviors']:
                    report.append(f"- **CORE Behaviors:**")
                    for b in thresh_result['core_behaviors']:
                        report.append(f"  - \"{b['behavior_text']}\" (N={b['reinforcement_count']}, stability={b['stability_score']:.3f}, cluster={b['cluster_label']})")
            
            report.append("\n---\n")
        
        # Analysis
        report.append("## Key Findings\n")
        
        # Count total CORE across all thresholds
        threshold_totals = {t: 0 for t in self.test_thresholds}
        for r in results:
            if "error" not in r:
                for thresh_result in r["threshold_results"]:
                    threshold_totals[thresh_result["threshold"]] += thresh_result["core_count"]
        
        report.append("**Total CORE behaviors across all users:**\n")
        for threshold, total in threshold_totals.items():
            report.append(f"- Threshold {threshold:.2f}: {total} CORE behaviors")
        
        report.append("\n**Clustering Observations:**")
        no_clusters_count = sum(1 for r in results if "error" not in r and r["clustering"].get("clusters_formed", 0) == 0)
        report.append(f"- Users with 0 clusters: {no_clusters_count}/{len(results)}")
        
        max_stabilities = []
        for r in results:
            if "error" not in r:
                stabilities = r["clustering"].get("stability_scores", [])
                if stabilities:
                    max_stabilities.append(max(stabilities))
        
        if max_stabilities:
            report.append(f"- Highest stability score observed: {max(max_stabilities):.3f}")
            report.append(f"- Average max stability: {sum(max_stabilities)/len(max_stabilities):.3f}")
        
        report.append("\n**Recommendation:**")
        if threshold_totals[0.05] > 0:
            report.append(f"- Use threshold 0.05 or 0.10 for this dataset (0.15 too strict)")
        else:
            report.append(f"- Current data produces very low stability scores")
            report.append(f"- Issue may be: (1) HDBSCAN parameters too strict, (2) embeddings not clusterable, (3) data too small")
        
        return "\n".join(report)
    
    def save_results(self, results: List[Dict[str, Any]], report: str):
        """Save results to files"""
        output_dir = Path(__file__).parent / "evaluation_results"
        output_dir.mkdir(exist_ok=True)
        
        # Save JSON
        json_file = output_dir / f"threshold_analysis_{int(time.time())}.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"\n✓ Saved JSON: {json_file}")
        
        # Save markdown
        md_file = output_dir / f"threshold_analysis_{int(time.time())}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"✓ Saved report: {md_file}")
    
    def run(self):
        """Main execution"""
        try:
            # Connect
            logger.info("Connecting to databases...")
            self.mongodb.connect()
            self.qdrant.connect()
            logger.info("✓ Connected\n")
            
            # Run analysis
            results = self.run_analysis()
            
            # Generate report
            logger.info("\n" + "="*80)
            logger.info("Generating report...")
            logger.info("="*80)
            report = self.generate_report(results)
            
            # Save
            self.save_results(results, report)
            
            # Summary
            logger.info("\n" + "="*80)
            logger.info("ANALYSIS COMPLETE")
            logger.info("="*80)
            logger.info(f"Analyzed {len(results)} users across {len(self.test_thresholds)} thresholds\n")
            
        except Exception as e:
            logger.error(f"Error during analysis: {e}", exc_info=True)
        finally:
            self.mongodb.disconnect()
            self.qdrant.disconnect()


if __name__ == "__main__":
    analyzer = ThresholdAnalyzer()
    analyzer.run()

"""
Evaluation Comparison Runner

Runs both frequency baseline and stability system on all 6 test users,
then compares results for Bachelor's thesis evaluation.
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Any
import requests

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.evaluation.frequency_baseline import FrequencyBaseline, FrequencyStatus
from src.database.mongodb_service import MongoDBService
from src.database.qdrant_service import QdrantService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ComparisonRunner:
    """Runs and compares frequency baseline vs stability system"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.frequency_baseline = FrequencyBaseline()
        self.mongodb = MongoDBService()
        self.qdrant = QdrantService()
        
        # Test users in order of expected characteristics
        self.test_users = [
            ("user_stable_01", "Visual Viktor - tight clustering"),
            ("user_large_01", "Dedicated Dana - many interactions"),
            ("user_mixed_01", "Balanced Beth - mixed stability"),
            ("user_sparse_01", "Scattered Sam - high reinf, low stability"),
            ("user_research_01", "Academic Alice - dispersed behaviors"),
            ("user_tiny_01", "Minimal Mike - very few interactions")
        ]
    
    def get_behaviors_from_storage(self, user_id: str) -> List[Dict[str, Any]]:
        """Fetch behaviors from Qdrant"""
        try:
            qdrant_behaviors = self.qdrant.get_embeddings_by_user(user_id)
            behaviors = []
            for qb in qdrant_behaviors:
                payload = qb["payload"]
                behaviors.append({
                    "behavior_id": payload.get("behavior_id"),
                    "behavior_text": payload["behavior_text"],
                    "reinforcement_count": payload.get("reinforcement_count", 1),
                    "credibility": payload.get("credibility", 1.0),
                    "user_id": payload["user_id"]
                })
            return behaviors
        except Exception as e:
            logger.error(f"Error fetching behaviors for {user_id}: {e}")
            return []
    
    def run_frequency_baseline(self, user_id: str) -> Dict[str, Any]:
        """Run frequency baseline classification"""
        try:
            behaviors = self.get_behaviors_from_storage(user_id)
            if not behaviors:
                return {"error": "No behaviors found", "core_count": 0, "secondary_count": 0}
            
            # Convert to format expected by frequency_baseline
            # It expects behaviors with "description" and "prompts" array
            # But our behaviors have "behavior_text" and flat "reinforcement_count"
            formatted_behaviors = []
            for b in behaviors:
                formatted_behaviors.append({
                    "behavior_id": b["behavior_id"],
                    "description": b["behavior_text"],
                    "prompts": [{"reinforcement_count": b["reinforcement_count"]}]
                })
            
            classification = self.frequency_baseline.classify_behaviors(formatted_behaviors)
            stats = self.frequency_baseline.get_summary_stats(classification)
            
            return {
                "total_behaviors": len(behaviors),
                "core_count": stats["core_count"],
                "secondary_count": stats["secondary_count"],
                "noise_count": stats["noise_count"],
                "core_behaviors": [
                    {
                        "text": c.behavior_description,
                        "reinforcement_count": c.total_reinforcements,
                        "confidence": c.confidence
                    }
                    for c in classification if c.status == FrequencyStatus.CORE
                ]
            }
        except Exception as e:
            logger.error(f"Frequency baseline error for {user_id}: {e}")
            return {"error": str(e)}
    
    def run_stability_system(self, user_id: str) -> Dict[str, Any]:
        """Run stability system via API"""
        try:
            url = f"{self.api_base_url}/api/v1/analyze-behaviors-from-storage"
            response = requests.post(url, params={"user_id": user_id}, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "total_behaviors": data["statistics"]["total_behaviors_analyzed"],
                    "core_count": len(data.get("primary_behaviors", [])),
                    "secondary_count": len(data.get("secondary_behaviors", [])),
                    "clusters_formed": data["statistics"]["clusters_formed"],
                    "core_behaviors": [
                        {
                            "text": b.get("behavior_text", ""),
                            "stability_score": b.get("stability_score", 0.0),
                            "evidence_quality": b.get("evidence_quality", "UNKNOWN")
                        }
                        for b in data.get("primary_behaviors", [])
                    ]
                }
            else:
                return {"error": f"API error: {response.status_code}", "core_count": 0}
        except Exception as e:
            logger.error(f"Stability system error for {user_id}: {e}")
            return {"error": str(e), "core_count": 0}
    
    def compare_user(self, user_id: str, description: str) -> Dict[str, Any]:
        """Run both systems on one user and compare"""
        logger.info(f"\n{'='*80}")
        logger.info(f"Comparing: {user_id} - {description}")
        logger.info(f"{'='*80}")
        
        # Run frequency baseline
        logger.info("Running frequency baseline...")
        freq_result = self.run_frequency_baseline(user_id)
        
        # Run stability system
        logger.info("Running stability system...")
        stab_result = self.run_stability_system(user_id)
        
        # Calculate disagreement
        agreement = "N/A"
        if "error" not in freq_result and "error" not in stab_result:
            freq_core = freq_result.get("core_count", 0)
            stab_core = stab_result.get("core_count", 0)
            if freq_core == stab_core:
                agreement = "AGREE"
            elif freq_core > stab_core:
                agreement = f"FREQ OVER-PROMOTES ({freq_core} vs {stab_core})"
            else:
                agreement = f"STAB OVER-PROMOTES ({stab_core} vs {freq_core})"
        
        result = {
            "user_id": user_id,
            "description": description,
            "frequency_baseline": freq_result,
            "stability_system": stab_result,
            "agreement": agreement
        }
        
        # Log summary
        logger.info(f"\nResults:")
        logger.info(f"  Frequency Baseline: {freq_result.get('core_count', 'ERROR')} CORE behaviors")
        logger.info(f"  Stability System:   {stab_result.get('core_count', 'ERROR')} CORE behaviors")
        logger.info(f"  Agreement: {agreement}")
        
        return result
    
    def run_all_comparisons(self) -> List[Dict[str, Any]]:
        """Run comparison on all test users"""
        results = []
        
        logger.info("\n" + "="*80)
        logger.info("EVALUATION COMPARISON: Frequency Baseline vs Stability System")
        logger.info("="*80 + "\n")
        
        for user_id, description in self.test_users:
            result = self.compare_user(user_id, description)
            results.append(result)
            time.sleep(1)  # Brief pause between users
        
        return results
    
    def generate_summary_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate markdown summary report"""
        report = []
        report.append("# Evaluation Results: Frequency Baseline vs Stability System\n")
        report.append(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append("**Dataset:** 6 synthetic users with controlled characteristics\n")
        report.append("---\n")
        
        # Summary table
        report.append("## Summary Table\n")
        report.append("| User | Description | Frequency CORE | Stability CORE | Agreement |\n")
        report.append("|------|-------------|----------------|----------------|-----------|")
        
        for r in results:
            freq_core = r["frequency_baseline"].get("core_count", "ERR")
            stab_core = r["stability_system"].get("core_count", "ERR")
            report.append(f"| {r['user_id']} | {r['description']} | {freq_core} | {stab_core} | {r['agreement']} |")
        
        report.append("\n---\n")
        
        # Detailed results per user
        report.append("## Detailed Results\n")
        
        for r in results:
            report.append(f"\n### {r['user_id']} - {r['description']}\n")
            
            # Frequency baseline
            report.append("**Frequency Baseline:**\n")
            freq = r["frequency_baseline"]
            if "error" in freq:
                report.append(f"- ERROR: {freq['error']}\n")
            else:
                report.append(f"- Total behaviors: {freq['total_behaviors']}")
                report.append(f"- CORE: {freq['core_count']} (≥5 reinforcements)")
                report.append(f"- SECONDARY: {freq['secondary_count']} (2-4 reinforcements)")
                report.append(f"- NOISE: {freq['noise_count']} (1 reinforcement)\n")
                
                if freq['core_behaviors']:
                    report.append("- **CORE Behaviors:**")
                    for b in freq['core_behaviors']:
                        report.append(f"  - \"{b['text']}\" (N={b['reinforcement_count']}, conf={b['confidence']:.2f})")
                report.append("")
            
            # Stability system
            report.append("**Stability System:**\n")
            stab = r["stability_system"]
            if "error" in stab:
                report.append(f"- ERROR: {stab['error']}\n")
            else:
                report.append(f"- Total behaviors: {stab['total_behaviors']}")
                report.append(f"- CORE: {stab['core_count']} (stability ≥0.15)")
                report.append(f"- SECONDARY: {stab['secondary_count']}")
                report.append(f"- Clusters formed: {stab['clusters_formed']}\n")
                
                if stab['core_behaviors']:
                    report.append("- **CORE Behaviors:**")
                    for b in stab['core_behaviors']:
                        report.append(f"  - \"{b['text']}\" (stability={b['stability_score']:.3f}, quality={b['evidence_quality']})")
                report.append("")
            
            report.append(f"**Agreement:** {r['agreement']}\n")
            report.append("---\n")
        
        # Analysis
        report.append("## Analysis\n")
        
        total_freq_core = sum(r["frequency_baseline"].get("core_count", 0) for r in results)
        total_stab_core = sum(r["stability_system"].get("core_count", 0) for r in results)
        
        report.append(f"- **Total CORE behaviors across all users:**")
        report.append(f"  - Frequency Baseline: {total_freq_core}")
        report.append(f"  - Stability System: {total_stab_core}")
        report.append(f"  - Difference: {abs(total_freq_core - total_stab_core)}\n")
        
        if total_freq_core > total_stab_core:
            report.append("**Key Finding:** Frequency baseline promotes more behaviors to CORE than stability system.")
            report.append("This suggests the stability system is more conservative, filtering out high-reinforcement")
            report.append("behaviors with low semantic clustering stability.\n")
        elif total_stab_core > total_freq_core:
            report.append("**Key Finding:** Stability system promotes more behaviors to CORE than frequency baseline.")
            report.append("This suggests semantic clustering identifies stable patterns even at lower reinforcement counts.\n")
        else:
            report.append("**Key Finding:** Both methods classify the same number of CORE behaviors overall,")
            report.append("though they may disagree on specific cases.\n")
        
        return "\n".join(report)
    
    def save_results(self, results: List[Dict[str, Any]], report: str):
        """Save results to files"""
        output_dir = Path(__file__).parent / "evaluation_results"
        output_dir.mkdir(exist_ok=True)
        
        # Save JSON results
        json_file = output_dir / f"comparison_results_{int(time.time())}.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"\n✓ Saved JSON results: {json_file}")
        
        # Save markdown report
        md_file = output_dir / f"comparison_report_{int(time.time())}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"✓ Saved markdown report: {md_file}")
    
    def run(self):
        """Main execution"""
        try:
            # Connect to databases
            logger.info("Connecting to databases...")
            self.mongodb.connect()
            self.qdrant.connect()
            logger.info("✓ Connected\n")
            
            # Run comparisons
            results = self.run_all_comparisons()
            
            # Generate report
            logger.info("\n" + "="*80)
            logger.info("Generating summary report...")
            logger.info("="*80)
            report = self.generate_summary_report(results)
            
            # Save results
            self.save_results(results, report)
            
            # Print summary
            logger.info("\n" + "="*80)
            logger.info("EVALUATION COMPLETE")
            logger.info("="*80)
            logger.info(f"Compared {len(results)} users")
            logger.info("Results saved to src/evaluation/evaluation_results/\n")
            
        except Exception as e:
            logger.error(f"Error during evaluation: {e}", exc_info=True)
        finally:
            # Disconnect
            self.mongodb.disconnect()
            self.qdrant.disconnect()


if __name__ == "__main__":
    runner = ComparisonRunner()
    runner.run()

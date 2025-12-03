from typing import List, Dict, Any
import logging

from src.models.schemas import BehaviorCluster, TierEnum

logger = logging.getLogger(__name__)


class LLMContextService:
    """Service for formatting behavior data for LLM context injection"""
    
    def __init__(self, max_tokens: int = 2000):
        self.max_tokens = max_tokens
    
    def format_for_llm(
        self,
        clusters: List[BehaviorCluster],
        archetype: Dict[str, Any]
    ) -> str:
        """
        Format clusters and archetype for LLM context window
        
        Args:
            clusters: List of BehaviorCluster objects
            archetype: Archetype information dict
            
        Returns:
            Formatted string for LLM context
        """
        logger.info(f"Formatting {len(clusters)} clusters for LLM context")
        
        # Sort clusters by tier and strength
        primary = [c for c in clusters if c.tier == TierEnum.PRIMARY]
        secondary = [c for c in clusters if c.tier == TierEnum.SECONDARY]
        
        primary.sort(key=lambda x: x.cluster_strength, reverse=True)
        secondary.sort(key=lambda x: x.cluster_strength, reverse=True)
        
        # Build context
        context_lines = [
            "# User Behavior Profile",
            "",
            f"**User ID**: {archetype['user_id']}",
            f"**Primary Behaviors**: {archetype['primary_behaviors']}",
            f"**Secondary Behaviors**: {archetype['secondary_behaviors']}",
            f"**Confidence**: {archetype['confidence_score']:.2f}",
            "",
            "## Primary Behaviors (Core Patterns)",
            ""
        ]
        
        for cluster in primary[:10]:  # Top 10 primary
            context_lines.append(
                f"- **{cluster.canonical_label}** "
                f"(strength: {cluster.cluster_strength:.2f}, "
                f"confidence: {cluster.confidence:.2f}, "
                f"observations: {cluster.cluster_size})"
            )
        
        if secondary:
            context_lines.extend([
                "",
                "## Secondary Behaviors (Supporting Patterns)",
                ""
            ])
            
            for cluster in secondary[:5]:  # Top 5 secondary
                context_lines.append(
                    f"- {cluster.canonical_label} "
                    f"(strength: {cluster.cluster_strength:.2f})"
                )
        
        context = "\n".join(context_lines)
        
        # Truncate if needed (rough token estimate: ~4 chars per token)
        max_chars = self.max_tokens * 4
        if len(context) > max_chars:
            context = context[:max_chars] + "\n\n[Truncated...]"
        
        logger.info(f"Generated LLM context: {len(context)} characters")
        
        return context
    
    def format_compact(self, clusters: List[BehaviorCluster]) -> str:
        """
        Generate compact format for token-constrained contexts
        
        Args:
            clusters: List of BehaviorCluster objects
            
        Returns:
            Compact formatted string
        """
        primary = [c for c in clusters if c.tier == TierEnum.PRIMARY]
        primary.sort(key=lambda x: x.cluster_strength, reverse=True)
        
        labels = [c.canonical_label for c in primary[:15]]
        
        return "User behaviors: " + "; ".join(labels)

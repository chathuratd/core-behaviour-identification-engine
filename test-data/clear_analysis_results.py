"""
Clear Analysis Results Script

This script removes ONLY the clustering/analysis results while preserving
all input data including embeddings.

What gets deleted:
1. Cluster assignments from behaviors collection (cluster_id, epistemic_state, etc.)
2. All documents in profiles collection
3. All documents in clusters collection

What gets preserved:
- Original behaviors (behavior_text, credibility, reinforcement_count, etc.)
- Original prompts
- Embeddings in Qdrant (these are input data for clustering, not results)
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "cbie_db")


async def clear_mongodb_analysis_data():
    """Clear analysis results from MongoDB"""
    print("=" * 70)
    print("CLEARING MONGODB ANALYSIS RESULTS")
    print("=" * 70)
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[MONGODB_DB]
    
    try:
        # 1. Remove cluster-related fields from behaviors collection
        print("\n1. Removing cluster assignments from behaviors collection...")
        result = await db.behaviors.update_many(
            {},  # All documents
            {
                "$unset": {
                    "cluster_id": "",
                    "epistemic_state": "",
                    "cluster_strength": "",
                    "confidence": "",
                    "cluster_stability": "",
                    "consistency_score": "",
                    "reinforcement_score": "",
                    "clarity_trend": "",
                    "recency_factor": "",
                    "last_updated": ""
                }
            }
        )
        print(f"   ✅ Updated {result.modified_count} behaviors (removed cluster fields)")
        
        # 2. Delete all profiles
        print("\n2. Deleting all documents from profiles collection...")
        profiles_count = await db.profiles.count_documents({})
        result = await db.profiles.delete_many({})
        print(f"   ✅ Deleted {result.deleted_count} profile documents (had {profiles_count} total)")
        
        # 3. Delete all clusters
        print("\n3. Deleting all documents from clusters collection...")
        clusters_count = await db.clusters.count_documents({})
        result = await db.clusters.delete_many({})
        print(f"   ✅ Deleted {result.deleted_count} cluster documents (had {clusters_count} total)")
        
        # 4. Count remaining behaviors and prompts (should be unchanged)
        print("\n4. Verifying input data preservation...")
        behaviors_count = await db.behaviors.count_documents({})
        prompts_count = await db.prompts.count_documents({})
        print(f"   ✅ Preserved {behaviors_count} behaviors (input data)")
        print(f"   ✅ Preserved {prompts_count} prompts (input data)")
        
    except Exception as e:
        print(f"\n❌ Error during MongoDB cleanup: {e}")
        raise
    finally:
        client.close()




async def main():
    """Main cleanup function"""
    print("\n" + "=" * 70)
    print("CBIE ANALYSIS RESULTS CLEANUP")
    print("=" * 70)
    print("\nThis script will remove ONLY clustering/analysis results.")
    print("\nWhat will be deleted:")
    print("  • Cluster assignments from behaviors")
    print("  • All profiles")
    print("  • All clusters")
    print("\nWhat will be preserved:")
    print("  • Original behaviors (text, credibility, etc.)")
    print("  • Original prompts")
    print("  • Embeddings in Qdrant (needed for re-clustering)")
    
    # Ask for confirmation
    print("\n" + "=" * 70)
    response = input("\nProceed with cleanup? (yes/no): ").strip().lower()
    
    if response != "yes":
        print("\n❌ Cleanup cancelled by user")
        return
    
    print("\n🔄 Starting cleanup...\n")
    
    try:
        # Clear MongoDB data only
        await clear_mongodb_analysis_data()
        
        print("\n" + "=" * 70)
        print("✅ CLEANUP COMPLETE")
        print("=" * 70)
        print("\nAll clustering/analysis results have been removed.")
        print("Input data (behaviors, prompts, and embeddings) has been preserved.")
        print("\nYou can now run clustering again on the existing embeddings.\n")
        
    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ CLEANUP FAILED")
        print("=" * 70)
        print(f"\nError: {e}")
        print("\nSome data may have been partially cleaned.")
        print("Please check MongoDB manually.\n")


if __name__ == "__main__":
    asyncio.run(main())

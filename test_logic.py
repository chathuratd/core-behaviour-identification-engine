import numpy as np
from src.database.mongodb_service import mongodb_service

mongodb_service.connect()
profile = mongodb_service.get_profile_with_clusters('user_demo_single_core')

if profile:
    clusters_data = profile.get('behavior_clusters', [])
    
    # Extract stabilities
    stabilities = [c.get('cluster_stability', 0.0) for c in clusters_data]
    median_stability = np.median(stabilities)
    
    print(f"Stabilities: {[round(s, 4) for s in stabilities]}")
    print(f"Median: {median_stability:.4f}")
    print(f"Threshold: 0.15")
    print("\nCORE classification (stability >= median AND >= 0.15):")
    
    for c in clusters_data:
        stab = c.get('cluster_stability', 0.0)
        is_core = stab >= median_stability and stab >= 0.15
        print(f"  {c.get('cluster_id')}: {stab:.4f} >= {median_stability:.4f} AND >= 0.15 = {is_core}")

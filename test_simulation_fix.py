from src.database.mongodb_service import mongodb_service

mongodb_service.connect()
profile = mongodb_service.get_profile_with_clusters('user_demo_single_core')

if profile:
    clusters = profile.get('behavior_clusters', [])
    print(f"Profile found for user: {profile.get('user_id')}")
    print(f"Number of clusters: {len(clusters)}")
    for c in clusters:
        print(f"  - {c.get('cluster_id')}: stability={c.get('cluster_stability')}, state={c.get('epistemic_state')}")
else:
    print("No profile found")

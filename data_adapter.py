import json
import os
import pandas as pd
import numpy as np
import ast
from typing import List, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class DataAdapter:
    """
    Simulates fetching behavioral logs from a hybrid database and saving the final
    Core Behaviour Profile. In a real scenario, this would connect to MongoDB/SQL.
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.output_dir = os.path.join(self.data_dir, "profiles")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize Supabase Client
        url: str = os.environ.get("SUPABASE_URL", "")
        key: str = os.environ.get("SUPABASE_KEY", "")
        if not url or not key:
            print("Warning: Missing Supabase credentials in .env file. DB connection will fail.")
            self.supabase: Client = None
        else:
            self.supabase: Client = create_client(url, key)

    def fetch_user_history(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves the time-series objects of behaviors for a given user directly from Supabase.
        """
        if not self.supabase:
            print("Supabase client not initialized. Cannot fetch data.")
            return []
            
        print(f"Querying Supabase database for user {user_id}...")
        try:
            # Table name 'behaviors' is assumed based on standard BAC schema names
            response = self.supabase.table('behaviors').select('*').eq('user_id', user_id).eq('behavior_state', 'ACTIVE').execute()
        except Exception as e:
            print(f"Error querying Supabase API: {e}")
            return []
            
        records = response.data
        if not records:
             print(f"No records found in Supabase for user {user_id}.")
             return []
             
        user_logs = []
        for record in records:
            # Map specific Supabase schema fields to the internal representations needed
            # Fallback to defaults to prevent crashes if schema is slightly off
            log = {
                "event_id": record.get("behavior_id", f"beh_{np.random.randint(1000)}"),
                "user_id": record.get("user_id", user_id),
                "timestamp": record.get("created_at"), 
                "source_text": record.get("behavior_text", ""),
                "intent": record.get("intent", ""),
                "target": record.get("target", ""),
                "context": record.get("context", "general"),
                "polarity": record.get("polarity", ""),
                "scores": {
                    "credibility": float(record.get("credibility", 0.5)),
                    "clarity_score": float(record.get("clarity_score", 0.5)),
                    "extraction_confidence": float(record.get("extraction_confidence", 0.5))
                }
            }
            
            # Attempt to safely parse the embeddings
            # Depending on how the DB stores embeddings (vector type vs jsonb), it might come back as a string or list
            embedding_data = record.get("embedding")
            if embedding_data is not None:
                if isinstance(embedding_data, str) and embedding_data.startswith("["):
                    try:
                        emb_list = ast.literal_eval(embedding_data)
                        log["text_embedding"] = np.array(emb_list, dtype=np.float32)
                    except Exception as e:
                        print(f"Could not parse string embedding for row {log['event_id']}: {e}")
                        log["text_embedding"] = None
                elif isinstance(embedding_data, list):
                    # Native JSON parsed array
                     log["text_embedding"] = np.array(embedding_data, dtype=np.float32)
                else:
                    log["text_embedding"] = None
            else:
                 log["text_embedding"] = None
                
            user_logs.append(log)
            
        # Ensure logs are sorted by time 
        user_logs.sort(key=lambda x: str(x.get('timestamp', '')))
        return user_logs

    def save_profile(self, user_id: str, profile: Dict[str, Any]) -> str:
        """
        Persists the finalized Core Behaviour Profile to local storage AND to Supabase.
        """
        # 1. Save locally
        file_path = os.path.join(self.output_dir, f"{user_id}_profile.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=4)
        print(f"Profile saved locally to {file_path}")
        
        # 2. Save to Supabase
        if self.supabase:
            try:
                db_record = {
                    "user_id": user_id,
                    "total_raw_behaviors": profile.get("total_raw_behaviors", 0),
                    "confirmed_interests": json.dumps(profile.get("confirmed_interests", [])),
                    "updated_at": "now()"
                }
                self.supabase.table("core_behavior_profiles").upsert(
                    db_record, on_conflict="user_id"
                ).execute()
                print(f"Profile saved to Supabase 'core_behavior_profiles' table.")
            except Exception as e:
                print(f"Warning: Could not save profile to Supabase: {e}")
        
        return file_path

import numpy as np
import spacy
import os
from openai import AzureOpenAI
from typing import List, Dict, Any, Tuple
from transformers import pipeline
import time
from sklearn.metrics.pairwise import cosine_distances

class TopicDiscoverer:
    """
    Implements Stage 1 of the CBIE Methodology: Information Extraction & Topic Discovery.
    Uses Sentence Transformers for embeddings, HDBSCAN for clustering, and spaCy for domain adaptation.
    """

    def __init__(self, spacy_model: str = 'en_core_web_sm', zero_shot_model: str = 'facebook/bart-large-mnli'):
        print(f"Initializing Azure OpenAI Client...")
        self.openai_client = AzureOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            api_version=os.getenv("OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("OPENAI_API_BASE")
        )
        self.embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL")
        # Ensure we have a working chat model to fall back to
        self.chat_model = "gpt-4o-mini" # Confirmed to be available
        
        
        print(f"Loading Zero-Shot Classifier: {zero_shot_model}...")
        self.classifier = pipeline("zero-shot-classification", model=zero_shot_model)
        
        print(f"Loading spaCy model: {spacy_model}...")
        try:
            self.nlp = spacy.load(spacy_model)
        except OSError:
            print(f"spaCy model {spacy_model} not found. Attempting to download...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", spacy_model], check=True)
            self.nlp = spacy.load(spacy_model)
            
        # Initialize EntityRuler for domain adaptation
        self.ruler = self.nlp.add_pipe("entity_ruler", before="ner")
        # Example domain-specific terms (this would ideally be configurable)
        patterns = [
            {"label": "TECH", "pattern": "kubernetes"},
            {"label": "TECH", "pattern": "docker"},
            {"label": "ALGO", "pattern": "dbscan"},
            {"label": "ALGO", "pattern": "hdbscan"}
        ]
        self.ruler.add_patterns(patterns)

    def process_behaviors(self, behaviors: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], np.ndarray, np.ndarray]:
        """
        Takes raw behaviors, extracts entities, and isolates facts vs standard behaviors.
        Then clusters standard behaviors safely.
        Returns: (fact_behaviors, standard_behaviors, embeddings, cluster_labels)
        """
        if not behaviors:
            return [], [], np.array([]), np.array([])
            
        # 1. Isolate Absolute Facts
        fact_behaviors, standard_behaviors = self.isolate_absolute_facts(behaviors)
        
        # 2. Process Standard Behaviors
        embeddings_list = []
        texts_to_embed = []
        indices_to_embed = []
        
        for i, b in enumerate(standard_behaviors):
            b['extracted_entities'] = self.extract_entities(b.get('source_text', ''))
            
            # Use precomputed if available
            emb = b.get('text_embedding')
            if emb is not None and isinstance(emb, np.ndarray) and len(emb) > 0:
                embeddings_list.append(emb)
            else:
                # Placeholder, will fill in next step
                embeddings_list.append(None)
                texts_to_embed.append(b.get('source_text', ''))
                indices_to_embed.append(i)
                
        # Generate missing embeddings
        if texts_to_embed:
            print(f"Generating missing embeddings for {len(texts_to_embed)} behaviors...")
            new_embeddings = self.generate_embeddings(texts_to_embed)
            for idx, new_emb in zip(indices_to_embed, new_embeddings):
                embeddings_list[idx] = new_emb
                
        # Format for clustering
        final_embeddings = np.array(embeddings_list)
        
        # 3. Cluster Behaviors
        labels = np.array([])
        if len(final_embeddings) > 0:
            print(f"Clustering {len(final_embeddings)} standard behaviors using HDBSCAN...")
            polarities = [b.get('polarity', 'NEUTRAL') for b in standard_behaviors]
            labels = self.cluster_behaviors(final_embeddings, polarities)
            
            # Attach labels
            for i, label in enumerate(labels):
                standard_behaviors[i]['cluster_id'] = int(label)
            
        return fact_behaviors, standard_behaviors, final_embeddings, labels

    def isolate_absolute_facts(self, behaviors: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Separates absolute facts (permanent identity constraints like allergies, 
        dietary restrictions, medical conditions) from regular behavioral habits.
        
        Uses Zero-Shot NLP Classification to dynamically evaluate the text against 
        conceptual labels, completely eliminating hardcoded keyword arrays.
        """
        facts = []
        standards = []
        
        # We classify against generic conceptual labels rather than specific keywords
        candidate_labels = [
            "medical condition or severe allergy",
            "strict dietary restriction",
            "hobby or regular habit",
            "personal preference",
            "informational query"
        ]
        
        for b in behaviors:
            text = b.get('source_text', '')
            fact_confidence = 0.0
            detection_reasons = []
            
            # ================================================================
            # LAYER 1: Zero-Shot Classification (Primary Signal)
            # ================================================================
            if text.strip():
                # multi_label=True ensures each label gets an independent probability (sigmoid) 
                # instead of competing against each other (softmax).
                result = self.classifier(text, candidate_labels, multi_label=True)
                scores_dict = dict(zip(result['labels'], result['scores']))
                
                # Check how strongly the model believes this is a fact-like concept
                med_score = scores_dict.get("medical condition or severe allergy", 0.0)
                diet_score = scores_dict.get("strict dietary restriction", 0.0)
                
                # We take the max confidence across the fact-like labels
                zero_shot_score = max(med_score, diet_score)
                fact_confidence += zero_shot_score
                
                if zero_shot_score > 0.5:
                    top_label = max(
                        ("medical condition", med_score),
                        ("dietary restriction", diet_score),
                        key=lambda x: x[1]
                    )[0]
                    detection_reasons.append(f"zero_shot_{top_label.replace(' ', '_')}: {zero_shot_score:.2f}")
            
            # ================================================================
            # LAYER 2: BAC Metadata (Secondary Confidence Boost Only)
            # ================================================================
            intent = b.get('intent', '').upper()
            polarity = str(b.get('polarity', '') or '').upper()
            
            if intent == "CONSTRAINT":
                fact_confidence += 0.1
                detection_reasons.append("bac_intent_constraint")
            
            if polarity == "NEGATIVE" and intent == "CONSTRAINT":
                fact_confidence += 0.05
                detection_reasons.append("bac_negative_constraint")
            
            # ================================================================
            # DECISION: Classify as Fact if combined confidence >= 0.70
            # ================================================================
            FACT_THRESHOLD = 0.70
            
            if fact_confidence >= FACT_THRESHOLD:
                b['fact_confidence'] = round(fact_confidence, 3)
                b['fact_detection_reasons'] = detection_reasons
                facts.append(b)
            else:
                standards.append(b)
        
        print(f"Isolated {len(facts)} Absolute Facts from {len(behaviors)} total records.")
        if facts:
            for f in facts:
                print(f"  FACT (conf={f['fact_confidence']}): \"{f.get('source_text', '')[:60]}\" "
                      f"[{', '.join(f.get('fact_detection_reasons', []))}]")
        return facts, standards

    def extract_entities(self, text: str) -> List[Dict[str, str]]:
        """
        Extracts named entities using spaCy, including custom domain terms via EntityRuler.
        """
        doc = self.nlp(text)
        return [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Vectorizes source_text using Azure OpenAI text-embedding-3-large.
        """
        # OpenAI API has limits, we can batch them.
        embeddings = []
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            # Handle rate limits
            retries = 3
            while retries > 0:
                try:
                    response = self.openai_client.embeddings.create(
                        input=batch,
                        model=self.embedding_model
                    )
                    embeddings.extend([r.embedding for r in response.data])
                    break
                except Exception as e:
                    print(f"Azure OpenAI Error formatting embeddings: {e}. Retrying...")
                    time.sleep(2)
                    retries -= 1
            if retries == 0:
                raise Exception("Failed to get embeddings from Azure OpenAI after 3 retries.")
                
        return np.array(embeddings)

    def generalize_cluster_topic(self, texts: List[str]) -> str:
        """
        Uses an LLM (gpt-4o-mini) to look at a list of raw behaviors in a cluster
        and return a generalized, cohesive 3-5 word trait/topic name.
        """
        # Just send a representative sample if the cluster is huge to save tokens
        sample = texts[:25] 
        prompt = (
            "You are an AI identity analyst building a behavioral profile for a user.\n"
            "Below is a list of their recent activities/queries that belong to a single cluster.\n"
            "Identify the cohesive, overarching theme connecting them and return a generalized "
            "classification label (maximum 4-5 words).\n\n"
            "Respond ONLY with the generalized label, nothing else.\n\n"
            "Examples:\n"
            " - 'Creating a custom middleware in FastAPI', 'Handling CORS issues in a Python API' -> Python Backend Development\n"
            " - 'Dune book review', 'Best sci-fi books' -> Science Fiction Literature\n"
            " - 'WDT distribution technique', 'How to text milk' -> Espresso Brewing\n\n"
            "Raw Behaviors:\n"
        )
        for t in sample:
            prompt += f"- {t}\n"
            
        try:
            response = self.openai_client.chat.completions.create(
                model=self.chat_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=20
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Azure OpenAI Chat Error: {e}")
            # Fallback to the most frequent string if LLM fails
            from collections import Counter
            counts = Counter(texts)
            return counts.most_common(1)[0][0]

    def cluster_behaviors(self, embeddings: np.ndarray, polarities: List[str] = None, min_cluster_size: int = 2, min_samples: int = 1) -> np.ndarray:
        """
        Uses HDBSCAN to find latent topic clusters. HDBSCAN is robust to noise and 
        varying cluster densities.
        Applies a 'Polarity Penalty' to prevent POSITIVE and NEGATIVE sentiments
        from clustering together.
        """
        
        from sklearn.metrics.pairwise import euclidean_distances
        dist_matrix = euclidean_distances(embeddings).astype(np.float64)
        
        # Apply Polarity Penalty
        if polarities and len(polarities) == len(embeddings):
            n = len(embeddings)
            for i in range(n):
                for j in range(i+1, n):
                    p1 = str(polarities[i] or '').upper()
                    p2 = str(polarities[j] or '').upper()
                    
                    if (p1 == 'POSITIVE' and p2 == 'NEGATIVE') or (p1 == 'NEGATIVE' and p2 == 'POSITIVE'):
                        dist_matrix[i, j] = 1000.0
                        dist_matrix[j, i] = 1000.0

        # High-dimensional space (384-dim) without UMAP causes HDBSCAN to fail 
        # at finding density valleys, merging diverse topics. 
        # Standard DBSCAN heavily thresholded at eps=1.1 perfectly isolates STS topics.
        from sklearn.cluster import DBSCAN
        clusterer = DBSCAN(eps=1.1, min_samples=3, metric='precomputed')
        return clusterer.fit_predict(dist_matrix)

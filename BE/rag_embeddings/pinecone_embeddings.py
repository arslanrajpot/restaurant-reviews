import os
import pandas as pd
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX = os.environ.get("PINECONE_INDEX")

# Prefer the model bundled in the repo (local_models/) over a Hub download —
# see ai_assistants/restaurant_reviews.py for why. Must match that module's
# model so queries and stored vectors stay in the same embedding space.
_LOCAL_EMBEDDING_MODEL = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "local_models", "all-MiniLM-L6-v2",
)
EMBEDDING_MODEL = (
    _LOCAL_EMBEDDING_MODEL
    if os.path.isdir(_LOCAL_EMBEDDING_MODEL)
    else os.environ.get("EMBEDDING_MODEL")
)


class PineconeEmbeddings:
    def __init__(self):
        self.index_name = PINECONE_INDEX
        self.embedding_model = EMBEDDING_MODEL
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.index = self._initialize_pinecone()
        self.model = SentenceTransformer(self.embedding_model)
        self.max_tokens = 256

    def _initialize_pinecone(self):
        if self.index_name not in self.pc.list_indexes().names():
            print("Creating Pinecone index...")
            self.pc.create_index(
                name=self.index_name,
                dimension=384,  # Dimension for all-MiniLM-L6-v2
                metric="cosine",
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )
        else:
            print("Pinecone index already exists.")
        return self.pc.Index(self.index_name)

    @staticmethod
    def read_csv(file_path):
        df = pd.read_csv(file_path)
        df.fillna("", inplace=True)
        return df.to_dict(orient="records")

    @staticmethod
    def format_text(row):
        parts = [
            f"Restaurant: {row['Restaurant Name']}",
            f"Total Rating: {row['Total Rating']}" if row["Total Rating"] else "",
            f"Average Price: {row['Average Price']}" if row["Average Price"] else "",
            f"Location: {row['Restaurant Location']}" if row["Restaurant Location"] else "",
            f"Neighbourhood: {row['Neighbourhood']}" if row["Neighbourhood"] else "",
            f"Hours: {row['Hours of Operation']}" if row["Hours of Operation"] else "",
            f"Cuisine: {row['Cuisine']}" if row["Cuisine"] else "",
            f"Tags: {row['Tags']}" if row["Tags"] else "",
            f"Reviewer: {row['Reviewer Name']}" if row["Reviewer Name"] else "",
            f"Reviewer Location: {row['Reviewer Location']}" if row["Reviewer Location"] else "",
            f"Overall Rating: {row['Overall Rating']}/5" if row["Overall Rating"] else "",
            f"Food Rating: {row['Food Rating']}/5" if row["Food Rating"] else "",
            f"Service Rating: {row['Service Rating']}/5" if row["Service Rating"] else "",
            f"Ambience Rating: {row['Ambience Rating']}/5" if row["Ambience Rating"] else "",
            f"Review Date: {row['Review Date']}" if row["Review Date"] else "",
            f"Review: {row['Review Text']}" if row["Review Text"] else "",
        ]
        return " | ".join([p for p in parts if p])

    def split_text_into_chunks(self, text):
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.max_tokens):
            chunks.append(" ".join(words[i:i + self.max_tokens]))
        return chunks

    def generate_embedding(self, text):
        return self.model.encode(text).tolist()

    def process_and_upload(self, csv_file_path, batch_size=200):
        data = self.read_csv(csv_file_path)
        upsert_data = []

        for i, row in enumerate(data):
            text = self.format_text(row)

            if text:
                chunks = self.split_text_into_chunks(text)
                embedding_vectors = [self.generate_embedding(chunk) for chunk in chunks]

                for j, embedding in enumerate(embedding_vectors):
                    vector_id = f"{i}-{j}"
                    upsert_data.append({
                        "id": vector_id,
                        "values": embedding,
                        "metadata": {"text": chunks[j]}
                    })
                    print({"id": vector_id, "metadata": {"text": chunks[j]}})

                    if len(upsert_data) >= batch_size:
                        self._upload_batch(upsert_data)
                        upsert_data = []

        if upsert_data:
            self._upload_batch(upsert_data)

    def _upload_batch(self, upsert_data):
        try:
            self.index.upsert(vectors=upsert_data)
            print(f"Uploaded {len(upsert_data)} vectors.")
        except Exception as e:
            print(f"Error uploading batch: {e}")

    def upload_search_data(self, restaurant_data, reviews_data=None):
        """Upload restaurant search data to Pinecone"""
        texts = []

        # Convert restaurant data
        restaurant_name = restaurant_data.get('title', restaurant_data.get('name', ''))
        types = restaurant_data.get('type', [])
        if isinstance(types, str):
            types = [types]
        elif not isinstance(types, list):
            types = []

        cuisine = types[0] if types else 'NaN'
        tags = ', '.join(types) if types else 'NaN'

        # Create restaurant row
        restaurant_row = {
            'Restaurant Name': restaurant_name,
            'Total Rating': restaurant_data.get('rating', ''),
            'Average Price': restaurant_data.get('price', ''),
            'Restaurant Location': restaurant_data.get('address', ''),
            'Neighbourhood': restaurant_data.get('neighborhood', ''),
            'Hours of Operation': restaurant_data.get('hours', ''),
            'Cuisine': cuisine,
            'Tags': tags,
            'Reviewer Name': '',
            'Reviewer Location': '',
            'Overall Rating': restaurant_data.get('rating', ''),
            'Food Rating': '',
            'Service Rating': '',
            'Ambience Rating': '',
            'Review Date': '',
            'Review Text': ''
        }

        restaurant_text = self.format_text(restaurant_row)
        if restaurant_text:
            texts.append(restaurant_text)

        if reviews_data:
            for review in reviews_data[:50]:
                review_row = {
                    'Restaurant Name': restaurant_name,
                    'Total Rating': restaurant_data.get('rating', ''),
                    'Average Price': restaurant_data.get('price', ''),
                    'Restaurant Location': restaurant_data.get('address', ''),
                    'Neighbourhood': restaurant_data.get('neighborhood', ''),
                    'Hours of Operation': restaurant_data.get('hours', ''),
                    'Cuisine': cuisine,
                    'Tags': tags,
                    'Reviewer Name': review.get('user', {}).get('name', ''),
                    'Reviewer Location': review.get('user', {}).get('location', ''),
                    'Overall Rating': review.get('rating', ''),
                    'Food Rating': '',
                    'Service Rating': '',
                    'Ambience Rating': '',
                    'Review Date': review.get('date', ''),
                    'Review Text': review.get('snippet', '')
                }
                
                review_text = self.format_text(review_row)
                if review_text:
                    texts.append(review_text)

        # Process and upload
        upsert_data = []
        total_processed = 0

        for i, text in enumerate(texts):
            if text:
                chunks = self.split_text_into_chunks(text)
                for j, chunk in enumerate(chunks):
                    embedding = self.generate_embedding(chunk)
                    vector_id = f"{restaurant_name.replace(' ', '_')}_{i}_{j}_{int(pd.Timestamp.now().timestamp())}"
                    upsert_data.append({
                        "id": vector_id,
                        "values": embedding,
                        "metadata": {
                            "text": chunk,
                            "restaurant_name": restaurant_name,
                            "source": "search_data"
                        }
                    })
                    total_processed += 1

                    if len(upsert_data) >= 100:
                        self._upload_batch(upsert_data)
                        upsert_data = []

        if upsert_data:
            self._upload_batch(upsert_data)

        return total_processed


# reviews_file_path = os.getenv("REVIEWS_CSV_PATH")

# uploader = PineconeEmbeddings()
# uploader.process_and_upload(reviews_file_path)
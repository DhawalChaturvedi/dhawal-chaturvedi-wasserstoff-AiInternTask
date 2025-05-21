from sklearn.cluster import KMeans
from langchain_openai import OpenAIEmbeddings
from app.config import OPENAI_API_KEY
import numpy as np

# Initialize OpenAI embedding model 
embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

def cluster_texts_with_citations(chunks, n_clusters=3):
    """
    Function :
    using kmeans clustering the chunks are clustered into theme


    Returns:
    Mapping of cluster label (int) to list of chunk dicts belonging to that cluster.
    """
    # Extract text content from each chunk
    texts = [c['text'] for c in chunks]

    # Compute embeddings for each text
    embeddings = [embedding_model.embed_documents([t])[0] for t in texts]
    X = np.array(embeddings)

    # Perform KMeans clustering on embeddings
    kmeans = KMeans(n_clusters=n_clusters)
    labels = kmeans.fit_predict(X)

    # Group chunks by cluster label
    clustered = {}
    for i, label in enumerate(labels):
        clustered.setdefault(label, []).append(chunks[i])
    return clustered

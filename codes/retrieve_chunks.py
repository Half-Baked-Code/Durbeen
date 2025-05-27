import time
import requests


def query_database(query, limit=10):
    params = {"query": query, "limit": limit}
    api_url = f"http://rag-api.ai-iscp.com//durbeen_bot/query"
    start_time = time.time()
    try:
        response = requests.get(api_url, params=params, timeout=10)
        end_time = time.time()
        if response.status_code == 200:
            data = response.json()
            # print("Retrieved Chunks:")
            retrieved_chunks = []
            for i, chunk in enumerate(data, 1):
                print(f"{i}. {chunk}")
                retrieved_chunks.append(chunk)

            print(
                f"\nTime taken to retrieve chunks: {end_time - start_time:.2f} seconds"
            )
            return retrieved_chunks, query
        else:
            print(
                f"Failed to retrieve chunks. Status: {response.status_code}, Response: {response.text}"
            )
            return None, query
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None



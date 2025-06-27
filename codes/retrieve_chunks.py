import time
import requests


def get_chunk(source, chunkid):
    params = {"source_name": source, "chunkid": chunkid}
    api_url = f"http://rag-api.ai-iscp.com//durbeen_bot/get_chunk"
    start_time = time.time()
    try:
        response = requests.get(api_url, params=params, timeout=10)
        end_time = time.time()
        if response.status_code == 200:
            data = response.json()
            print(
                f"\nTime taken to retrieve chunks: {end_time - start_time:.2f} seconds"
            )
            print(data)
            return data
        else:
            print(
                f"Failed to retrieve chunks. Status: {response.status_code}, Response: {response.text}"
            )
            print(data)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

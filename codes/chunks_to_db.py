import requests
from get_all_chunks import get_all_course_chunks


def add_chunks_to_db(api_url):
    chunks = get_all_course_chunks()
    print(f"Total chunks: {len(chunks)}")

    for chunk in chunks:
        payload = {"chunk": chunk["content"], "item_data": chunk["metadata"]}
        try:
            response = requests.post(api_url, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"Successfully added chunk {chunk['metadata']['chunk_id']}")
            else:
                print(
                    f"Failed to add chunk {chunk['metadata']['chunk_id']}, Status: {response.status_code}, Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")


api_endpoint = "http://192.168.1.9:7077/durbeen_bot/add"
add_chunks_to_db(api_endpoint)

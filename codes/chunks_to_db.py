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


api_endpoint = "http://rag-api.ai-iscp.com//durbeen_bot/add"
add_chunks_to_db(api_endpoint)


# Loaded 243 chunks from a_review_of_literature_chunks.json.
# Loaded 80 chunks from a_review_of_multiple_choice_item_writing_chunks.json.
# Loaded 17 chunks from a_teacher's_guide_chunks.json.
# Loaded 45 chunks from can_a_picture_ruin_thousand_words_chunks.json.
# Loaded 63 chunks from clarifying_the_purpose_of_edu_assessment_chunks.json.
# Loaded 58 chunks from criteria_compassion_chunks.json.
# Loaded 61 chunks from deficiency_contamination_chunks.json.
# Loaded 42 chunks from does_washback_exists_chunks.json.
# Loaded 110 chunks from language_effects_chunks.json.
# Loaded 61 chunks from macro_micro_chunks.json.
# Loaded 61 chunks from ongoing_issues_chunks.json.
# Loaded 51 chunks from portfolio_purposes_chunks.json.
# Loaded 55 chunks from threats_to_valid_use_chunks.json.
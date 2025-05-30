import requests
import os
import json


def load_chunks_from_folder(folder_path):
    all_chunks = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    chunks = json.load(f)
                    if isinstance(chunks, list):
                        all_chunks.extend(chunks)
                        print(f"Loaded {len(chunks)} chunks from {filename}.")
                    else:
                        print(f"Warning: {filename} does not contain a list.")
                except json.JSONDecodeError:
                    print(f"Error decoding JSON in {filename}")

    print(f"\n✅ Total chunks loaded from folder: {len(all_chunks)}")
    return all_chunks


def get_all_course_chunks():
    all_chunks = []

    researcharticle_chunks = load_chunks_from_folder(
        r"C:\Users\user\Desktop\Tasks\Durbeen\ResearchArticles\chunks"
    )
    # referencebook_chunks = load_chunks_from_folder(
    #     r"C:\Users\user\Desktop\Tasks\Durbeen\ReferenceBooks\chunks"
    # )
    # corebook_chunks = load_chunks_from_folder(
    #   r"C:\Users\user\Desktop\Tasks\Durbeen\CoreTextbooks\chunks"
    # )

    all_chunks.extend(researcharticle_chunks)
    # all_chunks.extend(referencebook_chunks)
    # all_chunks.extend(corebook_chunks)

    print(f"Total chunks combined: {len(all_chunks)}")
    return all_chunks


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

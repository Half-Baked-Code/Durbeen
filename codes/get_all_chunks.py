import os
import json


def load_chunks_from_folder(folder_path):
    all_chunks = []

    # Loop through all .json files in the folder
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
        r"C:\Users\user\Desktop\Tasks\Durbeen\CoreTextbooks\chunks"
    )
    referencebook_chunks = load_chunks_from_folder(
        r"C:\Users\user\Desktop\Tasks\Durbeen\ReferenceBooks\chunks"
    )
    corebook_chunks = load_chunks_from_folder(
        r"C:\Users\user\Desktop\Tasks\Durbeen\ResearchArticles\chunks"
    )

    # Combine all chunks
    all_chunks.extend(researcharticle_chunks)
    all_chunks.extend(referencebook_chunks)
    all_chunks.extend(corebook_chunks)

    print(f"Total chunks combined: {len(all_chunks)}")

    if all_chunks:
        print("\n🔝 Top 5 chunks:")
        for i, chunk in enumerate(all_chunks[:5], start=1):
            print(f"{i}. {chunk}")

        print("\n🔚 Last 5 chunks:")
        for i, chunk in enumerate(all_chunks[-5:], start=len(all_chunks) - 4):
            print(f"{i}. {chunk}")
    else:
        print("⚠️ No chunks found.")
    return all_chunks

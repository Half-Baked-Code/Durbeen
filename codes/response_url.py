# import os
# import time
# from dotenv import load_dotenv
# import openai
# import requests


# def query_database(query, limit=10):
#     params = {"query": query, "limit": limit}
#     api_url = f"http://rag-api.ai-iscp.com//durbeen_bot/query"
#     start_time = time.time()
#     try:
#         response = requests.get(api_url, params=params, timeout=10)
#         end_time = time.time()
#         if response.status_code == 200:
#             data = response.json()
#             # print("Retrieved Chunks:")
#             retrieved_chunks = []
#             for i, chunk in enumerate(data, 1):
#                 print(f"{i}. {chunk}")
#                 retrieved_chunks.append(chunk)

#             print(
#                 f"\nTime taken to retrieve chunks: {end_time - start_time:.2f} seconds"
#             )
#             return retrieved_chunks
#         else:
#             print(
#                 f"Failed to retrieve chunks. Status: {response.status_code}, Response: {response.text}"
#             )
#             return None
#     except requests.exceptions.RequestException as e:
#         print(f"Error: {e}")
#         return None


# def get_response(question, history=None):
#     load_dotenv()
#     openai_api_key = os.getenv("OPENAI_API_KEY")

#     chunks = query_database(query=question)

#     # ✅ Step 1: Add hyperlink to each chunk
#     formatted_chunks = []
#     for chunk in chunks:
#         chunk_id = chunk["item_data"].get("chunk_id")
#         source = chunk["item_data"].get("source", "Unknown Source")
#         chapter = chunk["item_data"].get("chapter", "")
#         page = chunk["item_data"].get("page", "Unspecified")

#         # Construct the URL based on chunk ID
#         chunk_url = f"http://localhost:5173/viewer?chunk={chunk_id}"

#         # Append reference to chunk text
#         reference_text = (
#             f"\n\n[Source: {source}, Chapter: {chapter}, Page: {page}]({chunk_url})"
#         )
#         combined = chunk["chunk"] + reference_text

#         formatted_chunks.append(combined)

#     # Combine all chunks into one block
#     chunks_text = "\n\n---\n\n".join(formatted_chunks)

#     system_prompt = """
#     You are an educational assistant supporting B.Ed. (Bachelor of Education) students in Pakistan. Your role is to help them understand their course content, especially when they are confused or stressed. These students may have different levels of English proficiency and academic confidence. Your job is to provide clear, kind, and accurate explanations — always based on the content provided.
#     ✅ Your Response Strategy — Think Step-by-Step:
#     + Use Markdown formatting for any source links. Show them clearly and naturally, for example:
#     + [Source: StudyGuide, Chapter 2](http://localhost:5173/viewer?chunk=123)
#     Only Use the Shared Content
#     Stick strictly to the information given to you. Do not invent, assume, or add any content that is not part of the material provided.
#     If the question can't be answered based on the current content, reply with:
#     “I'm sorry, but I can only answer questions based on the information provided. The current content doesn't cover this topic.”
#     Use Friendly, Student-Relevant References
#     If it helps the student, mention references like the source name, page number, chapter, section, or subsection.
#     ❌ Never mention chunk IDs, file names
#     Start with a Clear and Simple Explanation
#     Assume the student may be encountering this topic for the first time. Begin your response as if you’re explaining it to someone who’s struggling.
#     🟢 Use plain language and a supportive tone.
#     ✅ Then, optionally, provide a more detailed or technical explanation for students who want to go deeper.
#     Let the Question Shape the Format
#     Do not force a rigid structure like “Simple Explanation” or “Detailed Explanation.”
#     Use headings only when they naturally help understanding, and craft them based on the student’s question, such as:
#     “What This Means”
#     “Why It Matters”
#     “Think of It Like This”
#     “The Key Idea”
#     “In the Classroom”
#     If no heading is needed, write a natural paragraph that feels like a conversation.
#     Explain Hard Ideas Using Relatable Examples
#     If the topic is technical or abstract, simplify it using examples from everyday life or the Pakistani education context.
#     Classroom examples, local teaching situations, or common analogies work best.
#     Be Human, Encouraging, and Respectful
#     Keep your tone gentle, respectful, and confidence-building.
#     Reassure them that it’s okay to ask questions or feel stuck.
#     🎯 Remember:
#     You are not just giving answers. You are helping students build understanding and confidence. Your mindset should be:
#     “How would I explain this to a worried but curious student sitting across from me, who really wants to understand?”
#     """

#     messages = [{"role": "system", "content": system_prompt}]

#     if history:
#         for turn in history:
#             if turn.question and turn.answer:
#                 messages.append({"role": "user", "content": turn.question})
#                 messages.append({"role": "assistant", "content": turn.answer})

#     user_prompt = f"""I’m a B.Ed. student studying in Pakistan. Please help me understand the following topic or question based on the content you have. Explain it step by step building up on the concept. If the topic includes any reference from chapters or pages, mention that too.

# Content to answer the question:
# {chunks_text}

# User's Question:
# {question}

# If you think it is a follow-up question, please refer to the conversation history.

# Conversation History:
# {messages}
# """

#     messages.append({"role": "user", "content": user_prompt})

#     client = openai.OpenAI(api_key=openai_api_key)

#     start_time = time.time()
#     response = client.chat.completions.create(
#         model="gpt-4.1",
#         messages=messages,
#         temperature=0.3,
#     )
#     end_time = time.time()
#     print(f"Response time: {end_time - start_time:.2f} seconds")

#     reply = response.choices[0].message.content
#     print(reply)
#     return reply

import os
import time
import re
from dotenv import load_dotenv
import openai
import requests
from urllib.parse import urlencode


# 🔧 Utility: Slugify metadata for URL-safe paths
def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def construct_url(metadata):
    base_url = "http://localhost:5173/docs"

    # Required
    book_slug = slugify(metadata.get("source", ""))

    # Slugify and include only non-empty path parts
    parts = []
    for key in ["book_section", "chapter", "section", "subsection", "sub_subsection"]:
        value = metadata.get(key)
        if value:
            parts.append(slugify(value))

    # Build path
    path = f"{base_url}/{book_slug}/{'/'.join(parts)}"

    # Optional: append chunkid as query param if available
    chunk_id = metadata.get("chunk_id")
    if chunk_id is not None:
        query_string = urlencode({"chunkid": chunk_id})
        return f"{path}?{query_string}"

    return path


# 🔍 Chunk retrieval and metadata enrichment
def query_database(query, limit=10):
    params = {"query": query, "limit": limit}
    api_url = f"http://rag-api.ai-iscp.com//durbeen_bot/query"
    start_time = time.time()

    try:
        response = requests.get(api_url, params=params, timeout=10)
        end_time = time.time()

        if response.status_code == 200:
            data = response.json()
            retrieved_chunks = []

            for i, chunk in enumerate(data, 1):
                metadata = chunk.get("item_data", {})
                link = construct_url(metadata)
                chunk["link"] = link  # Add the generated link
                retrieved_chunks.append(chunk)

            print(
                f"\nTime taken to retrieve chunks: {end_time - start_time:.2f} seconds"
            )
            print(retrieved_chunks)
            return retrieved_chunks
        else:
            print(
                f"Failed to retrieve chunks. Status: {response.status_code}, Response: {response.text}"
            )
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


# 🤖 LLM query + link-enhanced prompt
def get_response(question, history=None):
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")

    chunks = query_database(query=question)

    if not chunks:
        return "No relevant content could be retrieved to answer the question."

    # 📦 Format chunks with markdown links
    chunk_texts = []
    for chunk in chunks:
        content = chunk.get("chunk", "").strip()
        metadata = chunk.get("item_data", {})
        link = chunk.get("link", "")

        # Use chapter as the most visible label for reference
        chapter = metadata.get("chapter", "Unknown Chapter")
        reference = f"\n\n(Source: [{chapter}]({link}))" if link else ""
        chunk_texts.append(f"{content}{reference}")

    formatted_chunks = "\n\n---\n\n".join(chunk_texts)
    print("Formatted Chunks:")
    print(formatted_chunks)

    # 🧠 Prompt construction
    system_prompt = """
       You are an educational assistant supporting B.Ed. (Bachelor of Education) students in Pakistan. Your role is to help them understand their course content, especially when they are confused or stressed. These students may have different levels of English proficiency and academic confidence. Your job is to provide clear, kind, and accurate explanations — always based on the content provided.
      ✅ Your Response Strategy — Think Step-by-Step:
      If references to sources or chapters are available with links, **include them using markdown link format** so the student can click and read further. For example: [Chapter 3: Assessment](http://...).
      Only Use the Shared Content
      Stick strictly to the information given to you. Do not invent, assume, or add any content that is not part of the material provided.
      If the question can't be answered based on the current content, reply with:
      “I'm sorry, but I can only answer questions based on the information provided. The current content doesn't cover this topic.”
      Use Friendly, Student-Relevant References
      If it helps the student, mention references like the source name, page number, chapter, section, or subsection.
      ❌ Never mention chunk IDs, file names
      Start with a Clear and Simple Explanation
      Assume the student may be encountering this topic for the first time. Begin your response as if you’re explaining it to someone who’s struggling.
      🟢 Use plain language and a supportive tone.
      ✅ Then, optionally, provide a more detailed or technical explanation for students who want to go deeper.
      Let the Question Shape the Format
      Do not force a rigid structure like “Simple Explanation” or “Detailed Explanation.”
      Use headings only when they naturally help understanding, and craft them based on the student’s question, such as:
      “What This Means”
      “Why It Matters”
      “Think of It Like This”
      “The Key Idea”
      “In the Classroom”
      If no heading is needed, write a natural paragraph that feels like a conversation.
      Explain Hard Ideas Using Relatable Examples
      If the topic is technical or abstract, simplify it using examples from everyday life or the Pakistani education context.
      Classroom examples, local teaching situations, or common analogies work best.
      Be Human, Encouraging, and Respectful
      Keep your tone gentle, respectful, and confidence-building.
      Reassure them that it’s okay to ask questions or feel stuck.
      🎯 Remember:
      You are not just giving answers. You are helping students build understanding and confidence. Your mindset should be:
      “How would I explain this to a worried but curious student sitting across from me, who really wants to understand?”
"""
    messages = [{"role": "system", "content": system_prompt}]

    if history:
        for turn in history:
            if turn.question and turn.answer:
                messages.append({"role": "user", "content": turn.question})
                messages.append({"role": "assistant", "content": turn.answer})

    user_prompt = f"""I’m a B.Ed. student studying in Pakistan. Please help me understand the following topic or question based on the content you have. Explain it step by step building up on the concept. If the topic includes any reference from chapters or pages, mention that too.

Content to answer the question:
{formatted_chunks}
User's Question:
{question}
If you think it is a follow-up question, please refer to the conversation history.
Conversation History:
{messages}
"""

    messages.append({"role": "user", "content": user_prompt})
    print("messages:", messages)

    client = openai.OpenAI(api_key=openai_api_key)

    start_time = time.time()
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.3,
    )
    end_time = time.time()
    print(f"Response time: {end_time - start_time:.2f} seconds")

    reply = response.choices[0].message.content
    print(reply)
    return reply

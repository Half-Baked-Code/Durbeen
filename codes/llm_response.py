import os
import time
from dotenv import load_dotenv
import openai
from retrieve_chunks import query_database


def get_response():
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")

    chunks, query = query_database(
        query="What is a potential pitfall of including superfluous images in exam questions?"
    )

    # Define system and user prompts
    system_prompt = """You are an intelligent academic assistant. Your goal is to:
1. Analyze the user's question to assess their level of understanding based on their phrasing.
2. Respond with an informative, appropriately detailed answer drawn strictly from the provided content chunks.
3. Include tables from the chunks in your response if they are relevant.
4. Use the metadata (e.g., source, page number) of each chunk when stating any fact or conclusion, to properly reference the source of information.

Be concise, accurate, and appropriately formal based on the user's knowledge level.
You are a helpful assistant specialized in summarizing academic content and identifying key insights."""

    user_prompt = f"""Below are content chunks retrieved from a knowledge base. Each chunk may include associated metadata (e.g., source or page number).

Your task is to answer the user's question using the content from the chunks. You should also assess the user's level of understanding based on how the question is framed, and tailor the explanation accordingly. If a table is present in the chunks and is relevant, include it in your response. Always cite the source using metadata when making factual claims.

Chunks:
{chunks}

User's Question:
{query}
"""

    client = openai.OpenAI(api_key=openai_api_key)

    start_time = time.time()
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )
    end_time = time.time()
    duration = end_time - start_time
    print(f"Response time: {duration:.2f} seconds")
    return response.choices[0].message.content

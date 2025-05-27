# from retrieve_chunks import query_database
# from openai import OpenAI
# import os
# from dotenv import load_dotenv
# import json

# # Load API key from environment
# load_dotenv()
# openai_api_key = os.getenv("OPENAI_API_KEY")


# def generate_augmented_answer(
#     query,
#     context,
#     user_queries,
#     bot_responses,
#     sys_prompt,
#     prompt_status,
#     model="gpt-4-1106-preview",  # GPT-4.1 model
# ):
#     system_prompt = sys_prompt

#     prompt = f"""
#     Given the following law book excerpt and the student's question, respond as a law professor would when explaining a legal concept to a student. Your response should be clear, accurate, and engaging, just like a professor explaining in a classroom or during office hours.

#     Student's Question: {query}

#     Law Book Excerpt: {context}
#     """

#     messages = [{"role": "system", "content": system_prompt}]
#     num_past_interactions = len(bot_responses)
#     start_index = max(0, num_past_interactions - 4)

#     if prompt_status != "new":
#         for i in range(start_index, num_past_interactions):
#             messages.append({"role": "user", "content": user_queries[i]})
#             messages.append({"role": "assistant", "content": bot_responses[i]})

#     messages.append({"role": "user", "content": prompt})

#     # Debugging
#     with open("response_track.json", "w", encoding="utf-8") as json_file:
#         json.dump(messages, json_file, ensure_ascii=False, indent=2)

#     client = OpenAI(api_key=openai_api_key)
#     response = client.chat.completions.create(
#         model=model,
#         messages=messages,
#         temperature=0.7,
#     )

#     return response.choices[0].message.content


# def get_answer(user_query, user_queries, botresponses, sysprompt, prompt_stat):
#     print("User queries so far:", user_queries)
#     print("Bot responses so far:", botresponses)

#     # Directly query database using user's question
#     chunks = query_database(user_query)

#     # Prepare context
#     chunk_text = [{"chunk": chunk.get("chunk", "")} for chunk in chunks]

#     print("System prompt:")
#     print(sysprompt)

#     # Get response
#     response = generate_augmented_answer(
#         query=user_query,
#         context=chunk_text,
#         user_queries=user_queries,
#         bot_responses=botresponses,
#         sys_prompt=sysprompt,
#         prompt_status=prompt_stat,
#     )

#     print("\nAssistant Response:")
#     print(response)
#     return response

import os
import time
from dotenv import load_dotenv
import openai
from retrieve_chunks import query_database

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

#  return response.choices[0].message.content

print("\nResponse from model:\n")
print(response.choices[0].message.content)
print(f"\nTime taken to get LLM response: {duration:.2f} seconds")

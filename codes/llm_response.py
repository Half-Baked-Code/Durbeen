from retrieve_chunks import query_database
from openai import OpenAI
import os
from dotenv import load_dotenv
import json

# Load API key from environment
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


def generate_augmented_answer(
    query,
    context,
    user_queries,
    bot_responses,
    sys_prompt,
    prompt_status,
    model="gpt-4-1106-preview",  # GPT-4.1 model
):
    system_prompt = sys_prompt

    prompt = f"""
    Given the following law book excerpt and the student's question, respond as a law professor would when explaining a legal concept to a student. Your response should be clear, accurate, and engaging, just like a professor explaining in a classroom or during office hours.

    Student's Question: {query}

    Law Book Excerpt: {context}
    """

    messages = [{"role": "system", "content": system_prompt}]
    num_past_interactions = len(bot_responses)
    start_index = max(0, num_past_interactions - 4)

    if prompt_status != "new":
        for i in range(start_index, num_past_interactions):
            messages.append({"role": "user", "content": user_queries[i]})
            messages.append({"role": "assistant", "content": bot_responses[i]})

    messages.append({"role": "user", "content": prompt})

    # Debugging
    with open("response_track.json", "w", encoding="utf-8") as json_file:
        json.dump(messages, json_file, ensure_ascii=False, indent=2)

    client = OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
    )

    return response.choices[0].message.content


def get_answer(user_query, user_queries, botresponses, sysprompt, prompt_stat):
    print("User queries so far:", user_queries)
    print("Bot responses so far:", botresponses)

    # Directly query database using user's question
    chunks = query_database(user_query)

    # Prepare context
    chunk_text = [{"chunk": chunk.get("chunk", "")} for chunk in chunks]

    print("System prompt:")
    print(sysprompt)

    # Get response
    response = generate_augmented_answer(
        query=user_query,
        context=chunk_text,
        user_queries=user_queries,
        bot_responses=botresponses,
        sys_prompt=sysprompt,
        prompt_status=prompt_stat,
    )

    print("\nAssistant Response:")
    print(response)
    return response

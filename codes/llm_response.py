import os
import time
from dotenv import load_dotenv
import openai
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
            return retrieved_chunks
        else:
            print(
                f"Failed to retrieve chunks. Status: {response.status_code}, Response: {response.text}"
            )
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


def get_response(question, history=None):
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")

    chunks = query_database(query=question)

    system_prompt = """
    You are an educational assistant supporting B.Ed. (Bachelor of Education) students in Pakistan. Your role is to help them understand their course content, especially when they are confused or stressed. These students may have different levels of English proficiency and academic confidence. Your job is to provide clear, kind, and accurate explanations — always based on the content provided.
    ✅ Your Response Strategy — Think Step-by-Step:
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

    # Build the conversation history
    messages = [{"role": "system", "content": system_prompt}]

    if history:
        for turn in history:
            if turn.question and turn.answer:
                messages.append({"role": "user", "content": turn.question})
                messages.append({"role": "assistant", "content": turn.answer})

    # print("History messages:", history)
    print("messages:", messages)

    # Add the current question with chunk content
    user_prompt = f"""I’m a B.Ed. student studying in Pakistan. Please help me understand the following topic or question based on the content you have. Explain it step by step building up on the concept. If the topic includes any reference from chapters or pages, mention that too.
    Content to answer the question:
    {chunks}
    User's Question:
    {question}
    if you think it is a followup question please refer to the conversation history 
    Conversation History:
    {messages}
    """

    messages.append({"role": "user", "content": user_prompt})

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

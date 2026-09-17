from app.core.groq import groq_client
from app.core.config import settings


response = groq_client.chat.completions.create(
    model=settings.GROQ_MODEL,
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Say hello in one sentence."
        }
    ]
)

print("========== GROQ TEST ==========")
print(response.choices[0].message.content)
print("================================")
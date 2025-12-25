from langchain.prompts import PromptTemplate

RAG_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are an official information assistant.
Answer strictly using the provided context.
If the answer is not found, say:
"Information is currently not available."

Context:
{context}

Question:
{question}

Answer:
"""
)

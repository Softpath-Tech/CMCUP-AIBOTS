from langchain.text_splitter import RecursiveCharacterTextSplitter


def chunk_documents(documents):
    """
    Split documents into overlapping chunks for RAG
    """

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    chunks = text_splitter.split_documents(documents)

    return chunks

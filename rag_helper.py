from sentence_transformers import SentenceTransformer
from hybrid_search import load_vector_index, vector_search, reciprocal_rank_fusion


INSTRUCTIONS = """
You are a GeoAI research assistant. Use the context to find relevant information and provide accurate
answers. 

When possible:
- Mention paper titles.
- Highlight the main contributions.
- Compare different approaches.
- Identify research trends.
- Mention limitations or open challenges.
- If multiple papers disagree, explain the differences.
- End with a short "Key Takeaways" section.

If the answer is not found in the context,
respond with "I don't know."
"""

PROMPT_TEMPLATE = """
QUESTION: {question}

CONTEXT:
{context}
""".strip()


class RAGBase:

    def __init__(
            self,
            index,
            documents,
            embeddings,
            encoder,
            llm_client,
            instructions = INSTRUCTIONS,
            prompt_template = PROMPT_TEMPLATE,
            model = "qwen/qwen3-32b",
    ):
        self.index = index
        self.llm_client = llm_client
        self.instructions = instructions
        self.prompt_template = prompt_template
        self.model = model
        self.documents = documents
        self.embeddings = embeddings
        self.encoder = encoder

    def search(self, query, num_results=5):

        keyword_results = self.index.search(
            query,
            num_results=num_results * 2,
            boost_dict={"title": 2.0, "topic": 1.0},
        )

        vector_results = vector_search(
            query,
            self.documents,
            self.embeddings,
            self.encoder,
            num_results=num_results * 2,
        )

        fused = reciprocal_rank_fusion(keyword_results, vector_results)
        return fused[:num_results]
    
    def build_context(self, search_results):

        lines = []

        for doc in search_results:
           
            lines.append(f"Topic: {doc['topic']}")
            lines.append(f"Title: {doc['title']}")

            if "authors" in doc:
                lines.append(f"Authors: {doc['authors']}")

            if "year" in doc:
                lines.append(f"Year: {doc['year']}")

            lines.append(f"Answer: {doc['answer']}")
            lines.append("")

        return "\n".join(lines).strip()

    def build_prompt(self, query, search_results):

        context = self.build_context(search_results)
        return self.prompt_template.format(
            question=query, 
            context=context
        )
    
    def llm(self, prompt):

        input_messages = [
            {"role": "developer", "content": self.instructions},
            {"role": "user", "content": prompt}
        ]

        response = self.llm_client.responses.create(
            model=self.model,
            input=input_messages
        )

        return response.output_text
    
    def rag(self, query):

        search_results = self.search(query)
        prompt = self.build_prompt(query, search_results)
        answer = self.llm(prompt)
        return answer
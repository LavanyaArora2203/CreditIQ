# """
# Custom CrewAI tool that searches a local info.txt file for content relevant
# to a query, using paragraph-level keyword scoring. No external embedding
# API or internet access is required, which keeps the sales agent fast and
# self-contained.

# If you'd rather do semantic/vector search, swap InfoFileSearchTool for
# crewai_tools.TXTSearchTool (requires an OpenAI key for embeddings) — see
# the comment at the bottom of this file.
# """

# import os
# import re
# from typing import Type

# from crewai.tools import BaseTool
# from pydantic import BaseModel, Field

# DEFAULT_INFO_PATH = os.path.join(os.path.dirname(__file__), "info.txt")


# class InfoSearchInput(BaseModel):
#     query: str = Field(..., description="The search query / question to look up in info.txt")


# # class InfoFileSearchTool(BaseTool):
# #     name: str = "Info File Search Tool"
# #     description: str = (
# #         "Searches info.txt for paragraphs relevant to a query and returns the "
# #         "top matching passages. Use this whenever you need facts about "
# #         "products, pricing, policies, or support to answer a question."
# #     )
# #     args_schema: Type[BaseModel] = InfoSearchInput
# #     file_path: str = DEFAULT_INFO_PATH

# #     def _run(self, query: str) -> str:
# #         if not os.path.exists(self.file_path):
# #             return f"Error: info file not found at {self.file_path}"

# #         with open(self.file_path, "r", encoding="utf-8") as f:
# #             content = f.read()

# #         # Split into paragraphs (blank-line separated blocks)
# #         paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

# #         # Simple keyword scoring: count occurrences of each query word
# #         # (len > 2 filters out stray articles/prepositions) in each paragraph.
# #         keywords = [w.lower() for w in re.findall(r"\w+", query) if len(w) > 2]
# #         if not keywords:
# #             return "Query too short/generic to search. Please provide more detail."

# #         scored = []
# #         for p in paragraphs:
# #             p_lower = p.lower()
# #             score = sum(p_lower.count(k) for k in keywords)
# #             if score > 0:
# #                 scored.append((score, p))

# #         if not scored:
# #             return "No relevant information found in info.txt for this query."

# #         scored.sort(key=lambda x: x[0], reverse=True)
# #         top_matches = [p for _, p in scored[:3]]
# #         return "\n\n---\n\n".join(top_matches)


# # # --- Alternative: semantic search using CrewAI's built-in RAG tool -------
# # # from crewai_tools import TXTSearchTool
# # # info_search_tool = TXTSearchTool(txt=DEFAULT_INFO_PATH)   # needs OPENAI_API_KEY
# # # Use this instead of InfoFileSearchTool() if info.txt is large/unstructured
# # # and you want embedding-based semantic retrieval rather than keyword scoring.
from typing import Literal
from exa_py import Exa
import os

exa_client: Exa = Exa(api_key=os.getenv("EXA_API_KEY"))

def search_web(
    query,
    num_results=10,
    search_type: Literal["neural", "keyword"] = "neural",
    category: Literal[
        "company",
        "research paper",
        "news",
        "pdf",
        "github",
        "tweet",
        "personal site",
        "linkedin profile",
        "financial report",
    ] = "web",
):
    result = exa_client.search_and_contents(
        query,
        num_results=num_results,
        use_autoprompt=True,
        type=search_type,
        category=category,
        summary=True,
    )
    return result


if __name__ == "__main__":
    print(search_web("what is the weather in tokyo"))

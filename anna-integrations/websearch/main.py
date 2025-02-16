from typing import Literal, Optional
from exa_py import Exa
import os
import fastapi
from dotenv import load_dotenv

load_dotenv()

app = fastapi.FastAPI()

exa_client: Exa = Exa(api_key=os.getenv("EXA_API_KEY"))


def search_web(
    query,
    num_results=5,
    search_type: Literal["neural", "keyword", "auto"] = "auto",
    category: Optional[
        Literal[
            "company",
            "research paper",
            "news",
            "pdf",
            "github",
            "tweet",
            "personal site",
            "linkedin profile",
            "financial report",
        ]
    ] = None,
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


@app.get("/search")
def search(
    query: str,
    num_results: int = 5,
    search_type: Literal["neural", "keyword"] = "neural",
    category: Optional[
        Literal[
            "company",
            "research paper",
            "news",
            "pdf",
            "github",
            "tweet",
            "personal site",
            "linkedin profile",
            "financial report",
        ]
    ] = None,
):
    return search_web(query, num_results, search_type, category)


if __name__ == "__main__":
    print(search_web("what is the weather in tokyo"))

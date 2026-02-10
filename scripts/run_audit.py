from app.main import main
from app.utils.llm import llm
from pprint import pprint

if __name__ == "__main__":
    query = "Does Google share user data with third parties?"
    result = main(query, llm)
    pprint(result)

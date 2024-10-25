from dotenv import load_dotenv
import os
from lib.utils import display
from challenge import Challenge

load_dotenv()


candidate_id = os.getenv("CANDIDATE_ID", "")
base_url = os.getenv("BASE_URL", "")

challenge = Challenge(candidate_id, base_url)

display(challenge.get_goal())

challenge.solve()

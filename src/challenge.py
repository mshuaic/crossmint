from ratelimit import limits, sleep_and_retry
from backoff import on_exception, expo

from typing import List, Optional
import json
import requests
from lib.megaverse import Megaverse
from lib.errors import TooManyRequests, InvalidObject, APIError


class Challenge:
    """
    Challenge class to interact with the API
    """

    def __init__(self, candidate_id: str, base_url: str):
        self.candidate_id = candidate_id
        self.base_url = base_url

    @on_exception(expo, TooManyRequests, max_tries=8)
    @sleep_and_retry
    @limits(calls=1, period=1)
    def _call_api(
        self,
        endpoint: str,
        row: int,
        column: int,
        color: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> None:
        """
        Call the API to update the board
        """

        headers = {
            "Content-Type": "application/json",
        }
        data = {
            "candidateId": self.candidate_id,
            "row": row,
            "column": column,
        }
        if color:
            data["color"] = color
        if direction:
            data["direction"] = direction
        try:
            response = requests.post(
                f"{self.base_url}/{endpoint}", headers=headers, data=json.dumps(data)
            )
            match response.status_code:
                case 429:
                    raise TooManyRequests()
                case 200:
                    pass
                case _:
                    raise APIError(response.status_code)
        except Exception as e:
            print(e, f"{endpoint=} {row=} {column=} {color=} {direction=}")

    def get_goal(self) -> Optional[List[List[str]]]:
        """
        Get the goal from the API
        """
        url = f"{self.base_url}/map/{self.candidate_id}/goal"
        data = None
        try:
            response = requests.get(url)
            data = response.json()["goal"]
        except Exception as e:
            print(e)
        return data

    def solve(self) -> None:
        """
        Solve the challenge
        """
        goal: Optional[List[List[str]]] = self.get_goal()
        if not goal:
            return

        for row in range(len(goal)):
            for col in range(len(goal[row])):
                obj: str = goal[row][col]
                if obj not in Megaverse:
                    raise InvalidObject(obj)
                endpoint: str = Megaverse[obj].endpoint
                color: str = Megaverse[obj].color
                direction: str = Megaverse[obj].direction
                if not endpoint:
                    continue
                self._call_api(endpoint, row, col, color, direction)

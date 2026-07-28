from pathlib import Path
import json
import re

from app.models.tournament import TournamentData


class WorldCupParser:

    def __init__(self, folder: str):
        self.folder = Path(folder)

    def load(self, folder: str | None = None) -> TournamentData:
        if folder is not None:
            self.folder = Path(folder)

        cup = self._load("worldcup.json")
        name = cup["name"]

        return TournamentData(
            year=self._extract_year(name),
            name=name,
            matches=cup["matches"],
            groups=self._load_optional("worldcup.groups.json", "groups"),
            stadiums=self._load_optional("worldcup.stadiums.json", "stadiums"),
        )

    def _load(self, filename: str):
        with open(self.folder / filename, encoding="utf-8") as f:
            return json.load(f)

    def _load_optional(self, filename: str, key: str) -> list:
        path = self.folder / filename
        if not path.exists():
            return []

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        return data.get(key, [])

    def _extract_year(self, tournament_name: str) -> int:
        match = re.search(r"\b(19|20)\d{2}\b", tournament_name)
        if not match:
            raise ValueError(f"Could not extract year from tournament name: {tournament_name}")
        return int(match.group(0))

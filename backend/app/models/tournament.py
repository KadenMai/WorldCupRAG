from dataclasses import dataclass, field


@dataclass(frozen=True)
class TournamentData:
    year: int
    name: str
    matches: list[dict] = field(default_factory=list)
    groups: list[dict] = field(default_factory=list)
    stadiums: list[dict] = field(default_factory=list)

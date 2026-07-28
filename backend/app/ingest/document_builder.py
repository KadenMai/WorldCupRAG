import re
import unicodedata
from collections import defaultdict
from datetime import datetime

from app.models.document import Document
from app.models.tournament import TournamentData


class DocumentBuilder:
    def build(self, tournament: TournamentData) -> list[Document]:
        year = tournament.year
        documents: list[Document] = []

        for match in tournament.matches:
            documents.append(
                Document(
                    id=self._build_id(year, match),
                    title=self._build_title(year, match),
                    content=self._build_content(year, match),
                    metadata=self._build_metadata(year, match),
                )
            )

        return documents

    def _build_id(self, year: int, match: dict) -> str:
        round_name = match.get("round", "unknown-round")
        team_a = match.get("team1", "unknown-team-a")
        team_b = match.get("team2", "unknown-team-b")
        date = match.get("date", "unknown-date")

        return "-".join(
            [
                str(year),
                self._slugify(round_name),
                self._slugify(team_a),
                "vs",
                self._slugify(team_b),
                date,
            ]
        )

    def _build_title(self, year: int, match: dict) -> str:
        round_name = match.get("round", "Unknown Round")
        team_a = match.get("team1", "Unknown Team")
        team_b = match.get("team2", "Unknown Team")

        return f"{year} {round_name}: {team_a} vs {team_b}"

    def _build_content(self, year: int, match: dict) -> str:
        round_name = match.get("round", "Unknown Round")
        date = match.get("date")
        team_a = match.get("team1", "Unknown Team")
        team_b = match.get("team2", "Unknown Team")
        group = match.get("group")
        stadium = match.get("ground", "an unknown stadium")
        score = match.get("score", {})
        goals_a = match.get("goals1", [])
        goals_b = match.get("goals2", [])

        sections = [
            self._build_match_summary(year, round_name, team_a, team_b, date, stadium, group),
            self._build_result_section(team_a, team_b, score),
            self._build_goal_section(team_a, goals_a),
            self._build_goal_section(team_b, goals_b),
            self._build_shootout_section(team_a, team_b, score),
        ]

        return "\n\n".join(section for section in sections if section)

    def _build_metadata(self, year: int, match: dict) -> dict:
        round_name = match.get("round")
        group = match.get("group")
        team_a = match.get("team1")
        team_b = match.get("team2")
        stadium = match.get("ground")
        date = match.get("date")
        time = match.get("time")
        score = match.get("score", {})
        full_time = score.get("ft") or [None, None]

        return {
            "year": year,
            "round": round_name,
            "group": group,
            "team_a": team_a,
            "team_b": team_b,
            "teams": [team_a, team_b],
            "stadium": stadium,
            "date": date,
            "time": time,
            "score_a": full_time[0],
            "score_b": full_time[1],
            "has_penalties": self._has_penalties(match),
            "has_shootout": "p" in score,
        }

    def _build_match_summary(
        self,
        year: int,
        round_name: str,
        team_a: str,
        team_b: str,
        date: str | None,
        stadium: str,
        group: str | None,
    ) -> str:
        pretty_date = self._format_date(date)

        if round_name.lower() == "final":
            return (
                f"The {year} FIFA World Cup Final was played on {pretty_date} "
                f"at {stadium}."
            )

        if group:
            return (
                f"In {group} of the {year} FIFA World Cup, {team_a} faced {team_b} "
                f"on {pretty_date} at {stadium}."
            )

        return (
            f"In the {year} FIFA World Cup {round_name}, {team_a} faced {team_b} "
            f"on {pretty_date} at {stadium}."
        )

    def _build_result_section(self, team_a: str, team_b: str, score: dict) -> str:
        full_time = score.get("ft")
        extra_time = score.get("et")
        penalties = score.get("p")

        if not full_time or len(full_time) != 2:
            return f"{team_a} played against {team_b}."

        score_a, score_b = full_time

        if penalties and extra_time:
            return (
                f"{self._winner(team_a, team_b, penalties)} defeated "
                f"{self._loser(team_a, team_b, penalties)} on penalties after "
                f"drawing {extra_time[0]}-{extra_time[1]} following extra time."
            )

        if extra_time:
            winner = self._winner(team_a, team_b, extra_time)
            loser = self._loser(team_a, team_b, extra_time)
            return (
                f"{winner} defeated {loser} "
                f"{extra_time[0]}-{extra_time[1]} after extra time."
            )

        if score_a == score_b:
            return f"The match ended in a {score_a}-{score_b} draw."

        winner = self._winner(team_a, team_b, full_time)
        loser = self._loser(team_a, team_b, full_time)
        return f"{winner} defeated {loser} {max(score_a, score_b)}-{min(score_a, score_b)}."

    def _build_goal_section(self, team: str, goals: list[dict]) -> str:
        if not goals:
            return f"{team} did not score."

        sentences: list[str] = []
        goals_by_player: dict[str, list[dict]] = defaultdict(list)

        for goal in goals:
            name = goal.get("name", "Unknown scorer")
            goals_by_player[name].append(goal)

        for player, player_goals in goals_by_player.items():
            minutes = [self._format_minute_phrase(goal) for goal in player_goals]
            sentences.append(self._build_scorer_sentence(player, minutes, player_goals))

        return "\n\n".join(sentences)

    def _build_scorer_sentence(
        self,
        player: str,
        minutes: list[str],
        goals: list[dict],
    ) -> str:
        all_penalties = all(goal.get("penalty") for goal in goals)

        if len(minutes) == 1:
            minute = minutes[0]
            if all_penalties:
                return f"{player} scored from the penalty spot in the {minute}."
            return f"{player} scored in the {minute}."

        # minutes are like "23rd" or "90+5" — join without repeating "minute"
        ordinals = [m.removesuffix(" minute") for m in minutes]

        if len(ordinals) == 2:
            joined = f"{ordinals[0]} and {ordinals[1]}"
        else:
            joined = ", ".join(ordinals[:-1]) + f", and {ordinals[-1]}"

        if all_penalties:
            return f"{player} scored from the penalty spot in the {joined} minutes."

        return f"{player} scored in the {joined} minutes."

    def _build_shootout_section(self, team_a: str, team_b: str, score: dict) -> str:
        penalties = score.get("p")
        if not penalties or len(penalties) != 2:
            return ""

        winner = self._winner(team_a, team_b, penalties)
        winner_score = max(penalties)
        loser_score = min(penalties)
        return f"{winner} won the penalty shootout {winner_score}-{loser_score}."

    def _winner(self, team_a: str, team_b: str, score: list[int]) -> str:
        return team_a if score[0] > score[1] else team_b

    def _loser(self, team_a: str, team_b: str, score: list[int]) -> str:
        return team_b if score[0] > score[1] else team_a

    def _format_date(self, date: str | None) -> str:
        if not date:
            return "an unknown date"

        try:
            return datetime.strptime(date, "%Y-%m-%d").strftime("%d %B %Y").lstrip("0")
        except ValueError:
            return date

    def _format_minute_phrase(self, goal: dict) -> str:
        minute = goal.get("minute", "?")
        offset = goal.get("offset")

        if offset:
            return f"{minute}+{offset} minute"

        return f"{self._ordinal(minute)} minute"

    def _ordinal(self, value: int | str) -> str:
        try:
            number = int(value)
        except (TypeError, ValueError):
            return str(value)

        if 10 <= number % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")

        return f"{number}{suffix}"

    def _has_penalties(self, match: dict) -> bool:
        goals_a = match.get("goals1", [])
        goals_b = match.get("goals2", [])
        all_goals = goals_a + goals_b

        return any(goal.get("penalty") for goal in all_goals)

    def _slugify(self, value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized.lower()).strip("-")
        return slug or "unknown"

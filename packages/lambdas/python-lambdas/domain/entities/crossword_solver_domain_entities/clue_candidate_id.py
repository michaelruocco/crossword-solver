from dataclasses import dataclass


@dataclass(frozen=True)
class ClueCandidateId:
    text: str
    pattern: str

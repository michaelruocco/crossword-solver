from crossword_solver_domain_entities.candidates import Candidates
from crossword_solver_domain_entities.clue import Clue
from crossword_solver_domain_entities.clue_candidate_id import ClueCandidateId
from crossword_solver_domain_use_case.candidate_clue_hash_factory import CandidateClueHashFactory
from crossword_solver_domain_use_case.candidate_repository import CandidateRepository

from .candidate_item_converter import CandidateItemConverter
from .dynamodb_resource import create_dynamodb_resource


class DynamoCandidateRepository(CandidateRepository):
    def __init__(
        self,
        table_name: str,
        dynamodb=None,
        hash_factory: CandidateClueHashFactory | None = None,
        converter: CandidateItemConverter | None = None,
    ):
        self.table = (dynamodb or create_dynamodb_resource()).Table(table_name)
        self.hash_factory = hash_factory or CandidateClueHashFactory()
        self.converter = converter or CandidateItemConverter()

    def save(self, candidates: Candidates) -> None:
        candidate_id = self.hash_factory.to_hash(candidates.clue)
        self.table.put_item(Item=self.converter.to_item(candidates, candidate_id))

    def get(self, clue: Clue) -> Candidates | None:
        candidate_id = self.hash_factory.to_hash(clue)
        item = self.table.get_item(Key={"candidate_id": candidate_id}, ConsistentRead=True).get("Item")
        return self.converter.to_candidates(item, clue) if item else None

    def delete_all(self) -> None:
        response = self.table.scan(ProjectionExpression="candidate_id")
        items = response["Items"]
        while "LastEvaluatedKey" in response:
            response = self.table.scan(
                ProjectionExpression="candidate_id",
                ExclusiveStartKey=response["LastEvaluatedKey"],
            )
            items.extend(response["Items"])

        if items:
            with self.table.batch_writer() as batch:
                for item in items:
                    batch.delete_item(Key={"candidate_id": item["candidate_id"]})

    def delete(self, candidate_id: ClueCandidateId) -> None:
        key = self.hash_factory.to_hash(candidate_id)
        self.table.delete_item(Key={"candidate_id": key})

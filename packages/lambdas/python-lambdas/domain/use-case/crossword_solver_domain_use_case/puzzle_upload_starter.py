import uuid as uid

from crossword_solver_domain_entities.puzzle_import import PuzzleImport
from crossword_solver_domain_entities.puzzle_import_status import PuzzleImportStatus

from .clock import Clock, system_clock
from .image_upload_store import ImageUploadStore
from .image_validator import ImageValidator
from .puzzle_import_repository import PuzzleImportRepository
from .puzzle_upload import PuzzleUpload


class PuzzleUploadStarter:
    def __init__(
        self,
        repository: PuzzleImportRepository,
        upload_store: ImageUploadStore,
        validator: ImageValidator | None = None,
        clock: Clock = system_clock,
    ):
        self.repository = repository
        self.upload_store = upload_store
        self.validator = validator or ImageValidator()
        self.clock = clock

    def start(self, filename: str) -> PuzzleUpload:
        self.validator.validate_filename(filename)
        import_id = uid.uuid4()
        upload = self.upload_store.create_upload(import_id, filename, self.validator.max_size_in_bytes)
        now = self.clock()
        puzzle_import = PuzzleImport(
            id=import_id,
            image_url=upload.image_url,
            status=PuzzleImportStatus.AWAITING_UPLOAD,
            created_at=now,
            updated_at=now,
        )
        self.repository.save(puzzle_import)
        return PuzzleUpload(puzzle_import, upload)

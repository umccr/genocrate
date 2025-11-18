import os.path

import rocrate_validator.log as logging
from rocrate_validator.models import ValidationContext
from rocrate_validator.requirements.python import (PyFunctionCheck, check,
                                                   requirement)

# set up logging
logger = logging.getLogger(__name__)


@requirement(name="File data entity must have identifier which is the filename")
class FileIdentifierMatchesFilenameRequirement(PyFunctionCheck):
    """Validates that each File entity's identifier matches its filename."""

    @check(name="File listing completeness")
    def validate_file_identifier_matches_filename(self, context: ValidationContext) -> bool:
        is_check_fail = False

        crate_files = context.ro_crate.metadata.get_entities_by_type(['File'])

        for file_entity in crate_files:

            filename = os.path.basename(file_entity.id)
            identifier = file_entity.get_property('identifier', None)

            if identifier is None:
                context.result.add_issue(
                    f"File @id ({file_entity.id}) do not have identifier", self)
                is_check_fail = True
                continue

            if identifier != filename:
                context.result.add_issue(
                    f"File @id ({file_entity.id}) identifier ({identifier}) does not match filename ({filename})", self)
                is_check_fail = True

        if is_check_fail:
            return False
        return True

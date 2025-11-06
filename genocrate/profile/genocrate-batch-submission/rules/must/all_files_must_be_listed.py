import os.path

import rocrate_validator.log as logging
from rocrate_validator.models import ValidationContext
from rocrate_validator.requirements.python import (PyFunctionCheck, check,
                                                   requirement)

# set up logging
logger = logging.getLogger(__name__)


@requirement(name="RO-Crate File Listing and Typing")
class AllFilesMustBeListed(PyFunctionCheck):
    """Validates that all files in the directory are listed as File entities in RO-Crate metadata and vice versa."""

    @check(name="File listing completeness")
    def check_all_files_listed(self, context: ValidationContext) -> bool:
        """Checks that every physical file is declared as a File entity in metadata, and every File entity exists in the directory."""


        ro_crate_metadata_files = ["ro-crate-metadata.json", "ro-crate-preview.html"]
        directory_files = [os.path.basename(i) for i in context.ro_crate.list_files()]
        crate_files = [f.id for f in context.ro_crate.metadata.get_entities_by_type(['File'])]

        missing_in_crate = set(directory_files) - set(crate_files) - set(ro_crate_metadata_files)
        missing_in_directory = set(crate_files) - set(directory_files)

        if missing_in_directory or missing_in_crate:
            for f in missing_in_directory:
                context.result.add_issue(
                    f"File entity '{f}' declared in ro-crate-metadata.json but missing in directory", self)

            for f in missing_in_crate:
                context.result.add_issue(
                    f"Physical file '{f}' present in directory but not declared as File entity in ro-crate-metadata.json",
                    self)
            return False

        return True

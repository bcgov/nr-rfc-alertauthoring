"""
a simple utility to delete data from the database that has been created
by manual testing etc.

To use, just populate the alert_ids_delete variable with the alert ids that you 
wish to permanently delete from the database.

This will delete all the related records in the database for the alert id, including
* cap 
* cap history
* alert history
* alert areas / alert levels linking table records
"""

import logging
import logging.config
import os
import sys

# logging setup
cur_path = os.path.dirname(__file__)
log_config_path = os.path.join(cur_path, "logging.config")

logging.config.fileConfig(log_config_path, disable_existing_loggers=False)
LOGGER = logging.getLogger(__name__)
LOGGER.info(f"starting {__name__}")
LOGGER.debug("test debug message")
LOGGER.info(f"name: {__name__}")

# calculate path to the helper functions
testPath2Add = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "test"))
rootPath2Add = os.path.dirname(testPath2Add)
LOGGER.debug(f"testPath2Add: {testPath2Add}")
LOGGER.debug(f"{rootPath2Add=}")

sys.path.append(testPath2Add)
sys.path.append(rootPath2Add)

# now add the helper functions
import helpers.db_helpers
import src.db.session

session_gen = src.db.session.get_db()
session = next(session_gen)
victor_the_cleaner = helpers.db_helpers.db_cleanup(session)

alert_ids_delete = [229, 115]


for id_2_delete in alert_ids_delete:
    victor_the_cleaner.cleanup(alert_id=id_2_delete)
    LOGGER.info(f"deleted alert id: {id_2_delete}")
    session.commit()

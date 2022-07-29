#!/usr/bin/python3
import logging

from datetime import datetime

logging.basicConfig(level=logging.INFO)
_test_logger = logging.getLogger()

MODULE_NAME = "commonutils"

def _format_log_message(module_name, log_message):
    return log_message

def log_error(module_name, log_message):
    log_message = _format_log_message(module_name=module_name, log_message=log_message)
    _test_logger.error(log_message)

def log_warning(module_name, log_message):
    log_message = _format_log_message(module_name=module_name, log_message=log_message)
    _test_logger.warning(log_message)

def log_info(module_name, log_message):
    log_message = _format_log_message(module_name=module_name, log_message=log_message)
    _test_logger.info(log_message)


# Oso Configuration
def policies_directory_path():
    return "./policies"

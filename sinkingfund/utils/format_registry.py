"""
Format Registry
===============

Centralized registry for all supported file formats and their associated
readers. This provides a single source of truth for format configuration
and makes it easy to add new formats.
"""

########################################################################
## IMPORTS
########################################################################

from .readers import read_csv_to_dict, read_excel_to_dict, read_json_to_dict

########################################################################
## CONSTANTS
########################################################################

# Single source of truth for all format configuration.
SUPPORTED_FORMATS = {
    'csv': {
        'extensions': ['.csv'],
        'reader': read_csv_to_dict,
        'description': 'Comma-separated values'
    },
    'excel': {
        'extensions': ['.xlsx', '.xls'],
        'reader': read_excel_to_dict,
        'description': 'Microsoft Excel spreadsheet'
    },
    'json': {
        'extensions': ['.json'],
        'reader': read_json_to_dict,
        'description': 'JavaScript Object Notation'
    }
}

########################################################################
## FUNCTIONS
########################################################################

def get_format_from_extension(extension: str) -> str:
    """
    Get format name from file extension.
    """

    # Convert the extension to lowercase.
    extension = extension.lower()

    # Iterate over the supported formats and return the format name
    # if the extension is found.
    for format_name, config in SUPPORTED_FORMATS.items():
        if extension in config['extensions']:
            return format_name

    # If the extension is not found, return None.
    return None

def get_reader_for_format(format_name: str):
    """
    Get reader function for format.
    """

    # Return the reader function for the format.
    return SUPPORTED_FORMATS[format_name]['reader']

def get_supported_extensions() -> list[str]:
    """
    Get list of all supported file extensions.
    """

    # Initialize the list of extensions.
    extensions = []

    # Iterate over the supported formats and add the extensions to
    # the list.
    for config in SUPPORTED_FORMATS.values():
        extensions.extend(config['extensions'])

    # Return the list of extensions.
    return extensions
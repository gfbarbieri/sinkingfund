# In sinkingfund/utils/__init__.py
"""
Utils Architecture
==================

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│    readers      │    │ format_registry  │    │   file_utils    │
│                 │    │                  │    │                 │
│ read_csv_to_    │◀───│ imports readers  │───▶│ imports         │
│ dict()          │    │                  │    │ format_registry │
│ read_excel_to_  │    │ SUPPORTED_       │    │                 │
│ dict()          │    │ FORMATS = {      │    │ detect_file_    │
│ read_json_to_   │    │   'csv': {       │    │ format()        │
│ dict()          │    │     reader: fn   │    │                 │
│                 │    │   }              │    │                 │
└─────────────────┘    │ }                │    └─────────────────┘
                       └──────────────────┘             │
                                │                       │
                                ▼                       ▼
                       ┌─────────────────────────────────────────┐
                       │              loaders                    │
                       │                                         │
                       │ imports file_utils                      │
                       │ imports format_registry                 │
                       │                                         │
                       │ load_bills_from_file()                  │
                       │ load_bills_from_data()                  │
                       └─────────────────────────────────────────┘

For detailed explanation, see docs/architecture/utils_architecture.md
"""
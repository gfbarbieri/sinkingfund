┌─────────────────────────────────────────────────────────────────┐
│                        UTILS ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   file_utils    │    │ format_registry  │    │    readers      │
│                 │    │                  │    │                 │
│ detect_file_    │───▶│ SUPPORTED_       │◀───│ read_csv_to_    │
│ format()        │    │ FORMATS = {      │    │ dict()          │
│                 │    │   'csv': {       │    │                 │
│                 │    │     extensions,  │    │ read_excel_to_  │
│                 │    │     reader       │    │ dict()          │
│                 │    │   },             │    │                 │
│                 │    │   'excel': {...} │    │ read_json_to_   │
│                 │    │   'json': {...}  │    │ dict()          │
│                 │    │ }                │    │                 │
│                 │    │                  │    │                 │
│                 │    │ get_format_from_ │    │                 │
│                 │    │ extension()      │    │                 │
│                 │    │                  │    │                 │
│                 │    │ get_reader_for_  │    │                 │
│                 │    │ format()         │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       ▲                       ▲
         │                       │                       │
         │              ┌────────┴───────────────────────┘
         │              │
         ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         loaders                                 │
│                                                                 │
│  load_bills_from_file(path) ──┐                                │
│         │                     │                                │
│         ▼                     │                                │
│  1. detect_file_format()      │  load_bills_from_data(dicts)   │
│  2. get_reader_for_format()   │         │                      │
│  3. reader(path)              │         ▼                      │
│  4. load_bills_from_data() ───┘  Creates Bill objects          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      models/bills       │
                    │                         │
                    │     Bill objects        │
                    └─────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         DATA FLOW                               │
└─────────────────────────────────────────────────────────────────┘

file.csv ──┐
file.xlsx ──┼──▶ load_bills_from_file() ──▶ [Bill, Bill, Bill]
file.json ──┘

OR

API/dict ────▶ load_bills_from_data() ──▶ [Bill, Bill, Bill]
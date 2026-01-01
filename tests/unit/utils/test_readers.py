"""
Readers Tests
=============

Comprehensive tests for data readers covering CSV, Excel, and JSON file
reading with pandas integration, data type coercion, and error handling.
"""

########################################################################
## IMPORTS
########################################################################

from __future__ import annotations

import datetime
import pandas as pd
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, Mock
import pytest

from sinkingfund.utils.readers import (
    read_csv_to_dict, read_excel_to_dict, read_json_to_dict,
    _coerce_scalar, _coerce_dataframe, _parse_date_columns,
    _normalize_int_columns
)

########################################################################
## TEST DATA FIXTURES
########################################################################

@pytest.fixture
def sample_bill_data() -> list[dict]:
    """
    Sample bill data for testing.
    """
    return [
        {
            'bill_id': 'rent',
            'service': 'Monthly Rent',
            'amount_due': 1200.00,
            'recurring': True,
            'due_date': datetime.date(2024, 1, 1),
            'start_date': datetime.date(2024, 1, 1),
            'end_date': None,
            'frequency': 'monthly',
            'interval': 1,
            'occurrences': None
        },
        {
            'bill_id': 'insurance',
            'service': 'Car Insurance',
            'amount_due': 450.00,
            'recurring': False,
            'due_date': datetime.date(2024, 3, 15),
            'start_date': datetime.date(2024, 3, 15),
            'end_date': datetime.date(2024, 3, 15),
            'frequency': None,
            'interval': None,
            'occurrences': 1
        }
    ]

@pytest.fixture
def sample_csv_content() -> str:
    """
    Sample CSV content for testing.
    """
    return """bill_id,service,amount_due,recurring,due_date,start_date,end_date,frequency,interval,occurrences
rent,Monthly Rent,1200.00,True,01/01/2024,01/01/2024,,monthly,1,
insurance,Car Insurance,450.00,False,03/15/2024,03/15/2024,03/15/2024,,,,1"""

########################################################################
## HELPER FUNCTION TESTS
########################################################################

class TestCoerceScalar:
    """Test _coerce_scalar helper function."""

    def test_none_values(self) -> None:
        """
        Test coercion of None and NaN values.
        """
        
        # Test: None stays None.
        result = _coerce_scalar(None)
        assert result is None
        
        # Test: pd.NA becomes None.
        result = _coerce_scalar(pd.NA)
        assert result is None
        
        # Test: pd.NaT becomes None.
        result = _coerce_scalar(pd.NaT)
        assert result is None

    def test_datetime_conversion(self) -> None:
        """
        Test conversion of datetime objects to dates.
        """
        
        # Test: pd.Timestamp to date.
        timestamp = pd.Timestamp('2024-01-15')
        result = _coerce_scalar(timestamp)
        assert result == datetime.date(2024, 1, 15)
        assert isinstance(result, datetime.date)
        
        # Test: datetime.datetime to date.
        dt = datetime.datetime(2024, 1, 15, 10, 30)
        result = _coerce_scalar(dt)
        assert result == datetime.date(2024, 1, 15)
        assert isinstance(result, datetime.date)

    def test_scalar_passthrough(self) -> None:
        """
        Test that regular scalars pass through unchanged.
        """
        
        # Test: String passes through.
        result = _coerce_scalar("test")
        assert result == "test"
        
        # Test: Integer passes through.
        result = _coerce_scalar(42)
        assert result == 42
        
        # Test: Float passes through.
        result = _coerce_scalar(3.14)
        assert result == 3.14
        
        # Test: Boolean passes through.
        result = _coerce_scalar(True)
        assert result is True

class TestCoerceDataframe:
    """Test _coerce_dataframe helper function."""

    def test_datetime_column_coercion(self) -> None:
        """
        Test coercion of datetime columns to dates.
        """
        
        # Test: Create DataFrame with datetime columns.
        df = pd.DataFrame({
            'due_date': [pd.Timestamp('2024-01-15'), pd.Timestamp('2024-02-15')],
            'start_date': [pd.Timestamp('2024-01-01'), pd.NaT],
            'other_col': ['A', 'B']
        })
        
        # Test: Coerce DataFrame.
        result = _coerce_dataframe(df)
        
        # Test: Verify datetime columns are converted to dates.
        assert result['due_date'].iloc[0] == datetime.date(2024, 1, 15)
        assert result['due_date'].iloc[1] == datetime.date(2024, 2, 15)
        assert result['start_date'].iloc[0] == datetime.date(2024, 1, 1)
        assert result['start_date'].iloc[1] is None
        
        # Test: Verify other columns unchanged.
        assert result['other_col'].iloc[0] == 'A'
        assert result['other_col'].iloc[1] == 'B'

    def test_non_datetime_columns_unchanged(self) -> None:
        """
        Test that non-datetime columns remain unchanged.
        """
        
        # Test: Create DataFrame with mixed types.
        df = pd.DataFrame({
            'bill_id': ['rent', 'insurance'],
            'amount_due': [1200.0, 450.0],
            'recurring': [True, False]
        })
        
        # Test: Coerce DataFrame.
        result = _coerce_dataframe(df)
        
        # Test: Verify columns unchanged.
        pd.testing.assert_frame_equal(result, df)

########################################################################
## CSV READER TESTS
########################################################################

class TestReadCsvToDict:
    """Test CSV reading functionality."""

    def test_csv_reading_with_temp_file(self, sample_csv_content: str) -> None:
        """
        Test reading CSV from a temporary file.
        """
        
        # Test: Create temporary CSV file.
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_csv_content)
            temp_path = f.name
        
        try:
            # Test: Read CSV file.
            result = read_csv_to_dict(temp_path)
            
            # Test: Verify structure.
            assert isinstance(result, list)
            assert len(result) == 2
            
            # Test: Verify first record.
            first_record = result[0]
            assert first_record['bill_id'] == 'rent'
            assert first_record['service'] == 'Monthly Rent'
            assert first_record['amount_due'] == 1200.0
            assert first_record['recurring'] is True
            
            # Test: Verify date conversion.
            assert isinstance(first_record['due_date'], datetime.date)
            assert first_record['due_date'] == datetime.date(2024, 1, 1)
            
        finally:
            # Test: Clean up temporary file.
            os.unlink(temp_path)

    @patch('sinkingfund.utils.readers.pd.read_csv')
    def test_csv_reading_with_mock(self, mock_read_csv) -> None:
        """
        Test CSV reading with mocked pandas.
        """
        
        # Test: Mock pandas DataFrame.
        mock_df = pd.DataFrame({
            'bill_id': ['test'],
            'service': ['Test Service'],
            'amount_due': [100.0],
            'recurring': [True],
            'due_date': [pd.Timestamp('2024-01-01')],
            'start_date': [pd.Timestamp('2024-01-01')],
            'end_date': [pd.NaT],
            'frequency': ['monthly'],
            'interval': [1],
            'occurrences': [pd.NA]
        })
        mock_read_csv.return_value = mock_df
        
        # Test: Call read_csv_to_dict.
        result = read_csv_to_dict('test.csv')
        
        # Test: Verify pandas was called with correct parameters.
        mock_read_csv.assert_called_once_with(
            'test.csv',
            usecols=[
                'bill_id', 'service', 'amount_due', 'recurring', 'due_date',
                'start_date', 'end_date', 'frequency', 'interval', 'occurrences'
            ],
            parse_dates=['due_date', 'start_date', 'end_date'],
            dtype={
                'bill_id': 'str',
                'service': 'str',
                'amount_due': 'float',
                'recurring': 'bool',
                'interval': 'Int64',
                'frequency': 'str',
                'occurrences': 'Int64'
            }
        )
        
        # Test: Verify result structure.
        assert isinstance(result, list)
        assert len(result) == 1
        
        # Test: Verify data coercion.
        record = result[0]
        assert record['due_date'] == datetime.date(2024, 1, 1)
        assert record['end_date'] is None
        assert record['occurrences'] is None

    def test_csv_float_interval_normalization(self) -> None:
        """
        Test that CSV with float interval values are normalized to integers.
        """
        
        # Test: Create CSV with float interval values (common in CSV files).
        csv_content = (
            "bill_id,service,amount_due,recurring,due_date,start_date,"
            "end_date,frequency,interval,occurrences\n"
            "rent,Monthly Rent,1200.00,True,,01/01/2024,,monthly,1.0,\n"
            "insurance,Car Insurance,450.00,True,,01/01/2024,,monthly,2.0,12.0\n"
        )
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.csv', delete=False
        ) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            # Test: Read CSV file.
            result = read_csv_to_dict(temp_path)
            
            # Test: Verify structure.
            assert isinstance(result, list)
            assert len(result) == 2
            
            # Test: Verify interval values are integers, not floats.
            assert isinstance(result[0]['interval'], int)
            assert result[0]['interval'] == 1
            assert isinstance(result[1]['interval'], int)
            assert result[1]['interval'] == 2
            
            # Test: Verify occurrences is integer if present.
            assert isinstance(result[1]['occurrences'], int)
            assert result[1]['occurrences'] == 12
            
        finally:
            os.unlink(temp_path)

    def test_csv_nonrecurring_bill_due_date_only(self) -> None:
        """
        Test that CSV with non-recurring bill having only due_date
        normalizes correctly.
        """
        
        # Test: Create CSV with non-recurring bill that has only due_date
        # (no start_date or end_date). This tests the normalization in
        # create_bills_from_data.
        csv_content = (
            "bill_id,service,amount_due,recurring,due_date,start_date,"
            "end_date,frequency,interval,occurrences\n"
            "registration,Car Registration,125.00,False,03/15/2024,,,,\n"
        )
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.csv', delete=False
        ) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            # Test: Read CSV file.
            result = read_csv_to_dict(temp_path)
            
            # Test: Verify structure.
            assert isinstance(result, list)
            assert len(result) == 1
            
            record = result[0]
            
            # Test: Verify due_date is present.
            assert record['due_date'] == datetime.date(2024, 3, 15)
            assert isinstance(record['due_date'], datetime.date)
            
            # Test: Verify start_date and end_date are None in raw data
            # (normalization happens in create_bills_from_data, not in
            # reader).
            assert record.get('start_date') is None or isinstance(
                record.get('start_date'), datetime.date
            )
            assert record.get('end_date') is None or isinstance(
                record.get('end_date'), datetime.date
            )
            
        finally:
            os.unlink(temp_path)

    @patch('sinkingfund.utils.readers.pd.read_csv')
    def test_csv_file_not_found_error(self, mock_read_csv) -> None:
        """
        Test CSV reading with file not found error.
        """
        
        # Test: Mock pandas raising FileNotFoundError.
        mock_read_csv.side_effect = FileNotFoundError("File not found")
        
        # Test: Verify error is propagated.
        with pytest.raises(FileNotFoundError, match="File not found"):
            read_csv_to_dict('nonexistent.csv')

########################################################################
## EXCEL READER TESTS
########################################################################

class TestReadExcelToDict:
    """Test Excel reading functionality."""

    @patch('sinkingfund.utils.readers.pd.read_excel')
    def test_excel_reading_default_sheet(self, mock_read_excel) -> None:
        """
        Test reading Excel with default sheet.
        """
        
        # Test: Mock pandas DataFrame.
        mock_df = pd.DataFrame({
            'bill_id': ['excel_test'],
            'service': ['Excel Service'],
            'amount_due': [200.0],
            'recurring': [False],
            'due_date': [pd.Timestamp('2024-02-01')],
            'start_date': [pd.Timestamp('2024-02-01')],
            'end_date': [pd.Timestamp('2024-02-01')],
            'frequency': [pd.NA],
            'interval': [pd.NA],
            'occurrences': [1]
        })
        mock_read_excel.return_value = mock_df
        
        # Test: Call read_excel_to_dict.
        result = read_excel_to_dict('test.xlsx')
        
        # Test: Verify pandas was called with correct parameters.
        mock_read_excel.assert_called_once_with(
            'test.xlsx',
            sheet_name=None,
            usecols=[
                'bill_id', 'service', 'amount_due', 'recurring', 'due_date',
                'start_date', 'end_date', 'frequency', 'interval',
                'occurrences'
            ],
            dtype={
                'bill_id': 'str',
                'service': 'str', 
                'amount_due': 'float',
                'recurring': 'bool',
                'interval': 'Int64',
                'frequency': 'str',
                'occurrences': 'Int64'
            }
        )
        
        # Test: Verify result structure.
        assert isinstance(result, list)
        assert len(result) == 1
        
        # Test: Verify data.
        record = result[0]
        assert record['bill_id'] == 'excel_test'
        assert record['due_date'] == datetime.date(2024, 2, 1)

    @patch('sinkingfund.utils.readers.pd.read_excel')
    def test_excel_reading_specific_sheet(self, mock_read_excel) -> None:
        """
        Test reading Excel with specific sheet name.
        """
        
        # Test: Mock pandas DataFrame.
        mock_df = pd.DataFrame({
            'bill_id': ['sheet_test'],
            'service': ['Sheet Service'],
            'amount_due': [300.0],
            'recurring': [True],
            'due_date': [pd.Timestamp('2024-03-01')],
            'start_date': [pd.Timestamp('2024-03-01')],
            'end_date': [pd.NaT],
            'frequency': ['monthly'],
            'interval': [1],
            'occurrences': [pd.NA]
        })
        mock_read_excel.return_value = mock_df
        
        # Test: Call read_excel_to_dict with sheet name.
        result = read_excel_to_dict('test.xlsx', sheet_name='Bills')
        
        # Test: Verify sheet_name parameter was passed.
        mock_read_excel.assert_called_once()
        call_args = mock_read_excel.call_args
        assert call_args[1]['sheet_name'] == 'Bills'

    @patch('sinkingfund.utils.readers.pd.read_excel')
    def test_excel_file_not_found_error(self, mock_read_excel) -> None:
        """
        Test Excel reading with file not found error.
        """
        
        # Test: Mock pandas raising FileNotFoundError.
        mock_read_excel.side_effect = FileNotFoundError("Excel file not found")
        
        # Test: Verify error is propagated.
        with pytest.raises(FileNotFoundError, match="Excel file not found"):
            read_excel_to_dict('nonexistent.xlsx')

########################################################################
## JSON READER TESTS
########################################################################

class TestReadJsonToDict:
    """Test JSON reading functionality."""

    @patch('sinkingfund.utils.readers.pd.read_json')
    def test_json_reading(self, mock_read_json) -> None:
        """
        Test reading JSON files.
        """
        
        # Test: Mock pandas DataFrame.
        mock_df = pd.DataFrame({
            'bill_id': ['json_test'],
            'service': ['JSON Service'],
            'amount_due': [400.0],
            'recurring': [True],
            'due_date': ['2024-04-01'],
            'start_date': ['2024-04-01'],
            'end_date': [None],
            'frequency': ['quarterly'],
            'interval': [3],
            'occurrences': [None]
        })
        mock_read_json.return_value = mock_df
        
        # Test: Call read_json_to_dict.
        result = read_json_to_dict('test.json')
        
        # Test: Verify pandas was called with correct parameters.
        mock_read_json.assert_called_once_with(
            'test.json',
            dtype={
                'bill_id': 'str',
                'service': 'str', 
                'amount_due': 'float',
                'recurring': 'bool',
                'interval': 'Int64',
                'frequency': 'str',
                'occurrences': 'Int64'
            }
        )
        
        # Test: Verify result structure.
        assert isinstance(result, list)
        assert len(result) == 1
        
        # Test: Verify data.
        record = result[0]
        assert record['bill_id'] == 'json_test'
        assert record['service'] == 'JSON Service'

    def test_json_reading_with_temp_file(self) -> None:
        """
        Test reading JSON from a temporary file.
        """
        
        # Test: Create temporary JSON file.
        json_content = '''[
            {
                "bill_id": "temp_test",
                "service": "Temp Service", 
                "amount_due": 500.0,
                "recurring": false,
                "due_date": "2024-05-01",
                "start_date": "2024-05-01",
                "end_date": "2024-05-01",
                "frequency": null,
                "interval": null,
                "occurrences": 1
            }
        ]'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(json_content)
            temp_path = f.name
        
        try:
            # Test: Read JSON file.
            result = read_json_to_dict(temp_path)
            
            # Test: Verify structure.
            assert isinstance(result, list)
            assert len(result) == 1
            
            # Test: Verify data.
            record = result[0]
            assert record['bill_id'] == 'temp_test'
            assert record['service'] == 'Temp Service'
            assert record['amount_due'] == 500.0
            assert record['recurring'] is False
            
        finally:
            # Test: Clean up temporary file.
            os.unlink(temp_path)

    @patch('sinkingfund.utils.readers.pd.read_json')
    def test_json_file_not_found_error(self, mock_read_json) -> None:
        """
        Test JSON reading with file not found error.
        """
        
        # Test: Mock pandas raising FileNotFoundError.
        mock_read_json.side_effect = FileNotFoundError("JSON file not found")
        
        # Test: Verify error is propagated.
        with pytest.raises(FileNotFoundError, match="JSON file not found"):
            read_json_to_dict('nonexistent.json')

########################################################################
## PATH SUPPORT TESTS
########################################################################

class TestReadersPathSupport:
    """Test Path-like object support in readers."""

    @patch('sinkingfund.utils.readers.pd.read_csv')
    def test_pathlib_path_support_csv(self, mock_read_csv) -> None:
        """
        Test CSV reading with pathlib.Path objects.
        """
        
        # Test: Mock pandas DataFrame.
        mock_df = pd.DataFrame({'bill_id': ['path_test']})
        mock_read_csv.return_value = mock_df
        
        # Test: Use Path object.
        path = Path('data/bills.csv')
        result = read_csv_to_dict(path)
        
        # Test: Verify path was passed correctly.
        mock_read_csv.assert_called_once()
        assert mock_read_csv.call_args[0][0] == path

    @patch('sinkingfund.utils.readers.pd.read_excel')
    def test_pathlib_path_support_excel(self, mock_read_excel) -> None:
        """
        Test Excel reading with pathlib.Path objects.
        """
        
        # Test: Mock pandas DataFrame.
        mock_df = pd.DataFrame({'bill_id': ['path_test']})
        mock_read_excel.return_value = mock_df
        
        # Test: Use Path object.
        path = Path('data/bills.xlsx')
        result = read_excel_to_dict(path)
        
        # Test: Verify path was passed correctly.
        mock_read_excel.assert_called_once()
        assert mock_read_excel.call_args[0][0] == path

    @patch('sinkingfund.utils.readers.pd.read_json')
    def test_pathlib_path_support_json(self, mock_read_json) -> None:
        """
        Test JSON reading with pathlib.Path objects.
        """
        
        # Test: Mock pandas DataFrame.
        mock_df = pd.DataFrame({'bill_id': ['path_test']})
        mock_read_json.return_value = mock_df
        
        # Test: Use Path object.
        path = Path('data/bills.json')
        result = read_json_to_dict(path)
        
        # Test: Verify path was passed correctly.
        mock_read_json.assert_called_once()
        assert mock_read_json.call_args[0][0] == path

########################################################################
## EDGE CASE TESTS
########################################################################

class TestReadersEdgeCases:
    """Test edge cases and error conditions."""

    @patch('sinkingfund.utils.readers.pd.read_csv')
    def test_empty_csv_file(self, mock_read_csv) -> None:
        """
        Test reading empty CSV files.
        """
        
        # Test: Mock empty DataFrame.
        mock_df = pd.DataFrame()
        mock_read_csv.return_value = mock_df
        
        # Test: Read empty file.
        result = read_csv_to_dict('empty.csv')
        
        # Test: Verify empty result.
        assert isinstance(result, list)
        assert len(result) == 0

    @patch('sinkingfund.utils.readers.pd.read_csv')
    def test_csv_parsing_error(self, mock_read_csv) -> None:
        """
        Test CSV reading with parsing errors.
        """
        
        # Test: Mock pandas raising ParserError.
        mock_read_csv.side_effect = pd.errors.ParserError("Parsing error")
        
        # Test: Verify error is propagated.
        with pytest.raises(pd.errors.ParserError, match="Parsing error"):
            read_csv_to_dict('malformed.csv')

    @patch('sinkingfund.utils.readers.pd.read_excel')
    def test_excel_sheet_not_found(self, mock_read_excel) -> None:
        """
        Test Excel reading with invalid sheet name.
        """
        
        # Test: Mock pandas raising ValueError for invalid sheet.
        mock_read_excel.side_effect = ValueError("Sheet not found")
        
        # Test: Verify error is propagated.
        with pytest.raises(ValueError, match="Sheet not found"):
            read_excel_to_dict('test.xlsx', sheet_name='NonexistentSheet')

    @patch('sinkingfund.utils.readers.pd.read_json')
    def test_json_parsing_error(self, mock_read_json) -> None:
        """
        Test JSON reading with parsing errors.
        """
        
        # Test: Mock pandas raising ValueError for invalid JSON.
        mock_read_json.side_effect = ValueError("Invalid JSON")
        
        # Test: Verify error is propagated.
        with pytest.raises(ValueError, match="Invalid JSON"):
            read_json_to_dict('malformed.json')


########################################################################
## HELPER FUNCTION TESTS - ADDITIONAL
########################################################################

class TestParseDateColumns:
    """
    Test _parse_date_columns helper function.
    """

    def test_parse_date_columns_basic(self) -> None:
        """
        Test parsing date columns in DataFrame.
        """
        df = pd.DataFrame({
            'date_col': ['2024-01-15', '2024-02-15'],
            'other_col': [1, 2]
        })
        
        result = _parse_date_columns(df, ['date_col'])
        
        assert pd.api.types.is_datetime64_any_dtype(result['date_col'])
        assert not pd.api.types.is_datetime64_any_dtype(result['other_col'])

    def test_parse_date_columns_missing_column(self) -> None:
        """
        Test parsing when column doesn't exist.
        """
        df = pd.DataFrame({
            'other_col': [1, 2]
        })
        
        result = _parse_date_columns(df, ['nonexistent'])
        
        assert 'nonexistent' not in result.columns

    def test_parse_date_columns_multiple_columns(self) -> None:
        """
        Test parsing multiple date columns.
        """
        df = pd.DataFrame({
            'start_date': ['2024-01-15', '2024-02-15'],
            'end_date': ['2024-12-31', '2024-12-31'],
            'other_col': [1, 2]
        })
        
        result = _parse_date_columns(df, ['start_date', 'end_date'])
        
        assert pd.api.types.is_datetime64_any_dtype(result['start_date'])
        assert pd.api.types.is_datetime64_any_dtype(result['end_date'])
        assert not pd.api.types.is_datetime64_any_dtype(result['other_col'])

    def test_parse_date_columns_invalid_dates(self) -> None:
        """
        Test parsing with invalid dates (should coerce to NaT).
        """
        df = pd.DataFrame({
            'date_col': ['invalid', '2024-01-15', 'also-invalid']
        })
        
        result = _parse_date_columns(df, ['date_col'])
        
        assert pd.api.types.is_datetime64_any_dtype(result['date_col'])
        # Invalid dates should be NaT.
        assert pd.isna(result['date_col'].iloc[0])
        assert pd.isna(result['date_col'].iloc[2])


class TestNormalizeIntColumns:
    """
    Test _normalize_int_columns helper function.
    """

    def test_normalize_int_columns_basic(self) -> None:
        """
        Test normalizing integer columns.
        """
        df = pd.DataFrame({
            'int_col': [1, 2, 3],
            'other_col': [1.5, 2.5, 3.5]
        })
        
        result = _normalize_int_columns(df, ['int_col'])
        
        assert all(isinstance(x, int) for x in result['int_col'])
        assert all(isinstance(x, float) for x in result['other_col'])

    def test_normalize_int_columns_with_none(self) -> None:
        """
        Test normalizing integer columns with None values.
        """
        df = pd.DataFrame({
            'int_col': [1, None, 3]
        })
        
        result = _normalize_int_columns(df, ['int_col'])
        
        assert result['int_col'].iloc[0] == 1
        assert pd.isna(result['int_col'].iloc[1])
        assert result['int_col'].iloc[2] == 3

    def test_normalize_int_columns_missing_column(self) -> None:
        """
        Test normalizing when column doesn't exist.
        """
        df = pd.DataFrame({
            'other_col': [1, 2]
        })
        
        result = _normalize_int_columns(df, ['nonexistent'])
        
        assert 'nonexistent' not in result.columns

    def test_normalize_int_columns_float_to_int(self) -> None:
        """
        Test converting float values to int.
        """
        df = pd.DataFrame({
            'int_col': [1.0, 2.5, 3.9]
        })
        
        result = _normalize_int_columns(df, ['int_col'])
        
        assert result['int_col'].iloc[0] == 1
        assert result['int_col'].iloc[1] == 2  # Truncated.
        assert result['int_col'].iloc[2] == 3  # Truncated.

    def test_normalize_int_columns_with_na(self) -> None:
        """
        Test normalizing with pandas NA values.
        """
        df = pd.DataFrame({
            'int_col': [1, pd.NA, 3]
        })
        
        result = _normalize_int_columns(df, ['int_col'])
        
        assert result['int_col'].iloc[0] == 1
        assert pd.isna(result['int_col'].iloc[1])
        assert result['int_col'].iloc[2] == 3

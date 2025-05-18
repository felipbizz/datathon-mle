import pandas as pd
from src.preprocess_data import clean_data
import numpy as np
from datetime import datetime


def test_clean_data_text_columns():
    # Test data
    df = pd.DataFrame(
        {
            'text_col': ['  TeXt   ', 'UPPER text', 'special!@#', None],
            'other_col': [1, 2, 3, 4],
        }
    )

    # Clean data with text columns
    result = clean_data(df, colunas_texto=['text_col'])

    # Check if text was cleaned properly
    expected = ['text', 'upper text', 'special', None]
    pd.testing.assert_series_equal(
        result['text_col'], pd.Series(expected, name='text_col')
    )


def test_clean_data_date_columns():
    # Test data with dates
    df = pd.DataFrame({'date_col': ['2023-01-01', '2023-12-31', 'invalid_date', None]})

    # Clean data with date columns
    result = clean_data(df, colunas_data=['date_col'])

    # Check if dates were converted properly
    assert pd.api.types.is_datetime64_dtype(result['date_col'])
    assert pd.isna(result.loc[2, 'date_col'])  # invalid date should be NaT
    assert pd.isna(result.loc[3, 'date_col'])  # None should be NaT


def test_clean_data_year_columns():
    # Test data with years
    df = pd.DataFrame({'year_col': ['2023', '2020', 'invalid', None]})

    # Clean data with year columns
    result = clean_data(df, colunas_anos=['year_col'])

    # Check if years were converted properly
    expected = pd.Series([2023.0, 2020.0, np.nan, np.nan], name='year_col')
    pd.testing.assert_series_equal(result['year_col'], expected)


def test_clean_data_numeric_columns():
    # Test data with numeric values
    df = pd.DataFrame({'num_col': ['1,234.56', '2.000,00', 'invalid', None]})

    # Clean data with numeric columns
    result = clean_data(df, colunas_numeros=['num_col'])

    # Check if numbers were converted properly
    expected = pd.Series([1234.56, 2000.00, np.nan, np.nan], name='num_col')
    pd.testing.assert_series_equal(result['num_col'], expected)


def test_clean_data_all_columns():
    # Test data with all types of columns
    df = pd.DataFrame(
        {
            'text': ['  TEXT  ', 'UPPER text'],
            'date': ['2023-01-01', '2023-12-31'],
            'year': ['2023', '2020'],
            'number': ['1,234.56', '2.000,00'],
        }
    )

    # Clean all types of columns
    result = clean_data(
        df,
        colunas_texto=['text'],
        colunas_data=['date'],
        colunas_anos=['year'],
        colunas_numeros=['number'],
    )

    # Check results
    assert result['text'].tolist() == ['text', 'upper text']
    assert all(isinstance(d, datetime) for d in result['date'].dropna())
    assert result['year'].tolist() == [2023.0, 2020.0]
    assert result['number'].tolist() == [1234.56, 2000.00]

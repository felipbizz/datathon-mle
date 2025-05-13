import pytest
import pandas as pd
import numpy as np
from src.consolidar_dados import consolidar_dados

@pytest.fixture
def sample_data():
    """Create sample vagas and prospects data"""
    df_vagas = pd.DataFrame({
        'cod_vaga': [1, 2, 3],
        'titulo_vaga': ['Dev Python', 'Data Scientist', 'ML Engineer'],
        'tipo_contratacao': ['CLT', 'PJ', 'CLT']
    })
    
    df_prospects = pd.DataFrame({
        'cod_vaga': [1, 1, 2],
        'titulo': ['Python Developer', 'Backend Dev', 'Data Scientist'],
        'situacao_candidado': ['contratado', 'desistiu', 'em processo']
    })
    
    return df_vagas, df_prospects

def test_merge_vagas_prospects(sample_data):
    """Test merging vagas with prospects data"""
    df_vagas, df_prospects = sample_data
    
    # Test merge
    df_merged = pd.merge(
        df_vagas,
        df_prospects,
        on='cod_vaga',
        how='inner'
    )
    
    # Check merge results
    assert len(df_merged) == len(df_prospects)  # Should have same number of rows as prospects
    assert 'titulo_vaga' in df_merged.columns  # Should have columns from vagas
    assert 'situacao_candidado' in df_merged.columns  # Should have columns from prospects
    
    # Check that all cod_vaga values in prospects exist in vagas
    assert set(df_prospects['cod_vaga']).issubset(set(df_vagas['cod_vaga']))

def test_data_consistency(sample_data):
    """Test data consistency after merge"""
    df_vagas, df_prospects = sample_data
    
    # Merge datasets
    df_merged = pd.merge(
        df_vagas,
        df_prospects,
        on='cod_vaga',
        how='inner'
    )
    
    # Check that no data was lost for matching records
    for cod_vaga in df_merged['cod_vaga'].unique():
        vaga_data = df_vagas[df_vagas['cod_vaga'] == cod_vaga].iloc[0]
        merged_data = df_merged[df_merged['cod_vaga'] == cod_vaga].iloc[0]
        
        assert vaga_data['titulo_vaga'] == merged_data['titulo_vaga']
        assert vaga_data['tipo_contratacao'] == merged_data['tipo_contratacao']

def test_handle_missing_values(sample_data):
    """Test handling of missing values in the merge"""
    df_vagas, df_prospects = sample_data
    
    # Add a row with missing values
    df_vagas.loc[len(df_vagas)] = [4, np.nan, np.nan]
    df_prospects.loc[len(df_prospects)] = [4, np.nan, np.nan]
    
    # Merge datasets
    df_merged = pd.merge(
        df_vagas,
        df_prospects,
        on='cod_vaga',
        how='inner'
    )
    
    # Check that rows with missing values were merged correctly
    merged_row = df_merged[df_merged['cod_vaga'] == 4]
    assert not merged_row.empty
    assert pd.isna(merged_row['titulo_vaga'].iloc[0])
    assert pd.isna(merged_row['situacao_candidado'].iloc[0])

def test_no_duplicate_columns(sample_data):
    """Test that there are no duplicate columns after merge"""
    df_vagas, df_prospects = sample_data
    
    # Add a common column with different values
    df_vagas['common_col'] = ['A', 'B', 'C']
    df_prospects['common_col'] = ['X', 'Y', 'Z']
    
    # Merge datasets
    df_merged = pd.merge(
        df_vagas,
        df_prospects,
        on='cod_vaga',
        how='inner'
    )
    
    # Check for duplicate column names
    assert len(df_merged.columns) == len(set(df_merged.columns))
    
    # Check that common columns are properly suffixed
    common_cols = [col for col in df_merged.columns if 'common_col' in col]
    assert len(common_cols) == 2  # Should have two columns with suffixes

def test_merge_empty_dataframes():
    """Test merging behavior with empty dataframes"""
    empty_vagas = pd.DataFrame(columns=['cod_vaga', 'titulo_vaga', 'tipo_contratacao'])
    empty_prospects = pd.DataFrame(columns=['cod_vaga', 'titulo', 'situacao_candidado'])
    
    # Merge empty dataframes
    df_merged = pd.merge(
        empty_vagas,
        empty_prospects,
        on='cod_vaga',
        how='inner'
    )
    
    # Check results
    assert len(df_merged) == 0  # Should be empty
    assert 'cod_vaga' in df_merged.columns  # Should maintain structure
    assert 'titulo_vaga' in df_merged.columns
    assert 'situacao_candidado' in df_merged.columns

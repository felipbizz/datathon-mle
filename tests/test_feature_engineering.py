import pytest
import pandas as pd
from src.feature_engineering import (
    coluna_valida,
    tamanho_texto,
    n_palavras,
    conta_palavras_chave,
    conta_cursos,
    TextFeatureGenerator,
)


def test_coluna_valida():
    # Test with valid and invalid dataframes
    df_valid = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
    df_empty = pd.DataFrame()

    assert coluna_valida(df_valid, 'col1') == True
    assert coluna_valida(df_valid, 'col2') == True
    assert coluna_valida(df_valid, 'non_existent') == False
    assert coluna_valida(df_empty, 'col1') == False


def test_tamanho_texto():
    assert tamanho_texto('Hello world') == 11
    assert tamanho_texto('') == 0
    assert tamanho_texto(None) == 0
    assert tamanho_texto(123) == 0  # Non-string input


def test_n_palavras():
    assert n_palavras('Hello world') == 2
    assert n_palavras('One two   three') == 3
    assert n_palavras('') == 0
    assert n_palavras(None) == 0
    assert n_palavras(123) == 0  # Non-string input


def test_conta_palavras_chave():
    texto = 'Python programming and data science with Python'
    palavras = ['python', 'data']
    assert conta_palavras_chave(texto, palavras) == 2
    assert conta_palavras_chave('', palavras) == 0
    assert conta_palavras_chave(None, palavras) == 0
    assert conta_palavras_chave(texto, []) == 0


def test_conta_cursos():
    assert conta_cursos('Curso de Python, Curso de Data Science') == 2
    assert conta_cursos('No courses here') == 0
    assert conta_cursos('') == 0
    assert conta_cursos(None) == 0


@pytest.fixture
def text_feature_generator():
    return TextFeatureGenerator()


def test_text_feature_generator_transform(text_feature_generator):
    # Create a sample dataframe
    df = pd.DataFrame(
        {
            'text_col1': ['Python programming', 'Data science'],
            'text_col2': ['Machine learning', 'Deep learning'],
            'other_col': [1, 2],
        }
    )

    # Test transform with text columns
    resultado = text_feature_generator.transform(df, ['text_col1', 'text_col2'])

    # Update expected feature names to match implementation
    expected_features = [
        'text_col1_nchar',
        'text_col1_nwords',
        'text_col2_nchar',
        'text_col2_nwords',
    ]

    for feature in expected_features:
        assert feature in resultado.columns


def test_text_feature_generator_adicionar_similaridade_titulo_vaga(
    text_feature_generator,
):
    # Create a sample dataframe
    df = pd.DataFrame(
        {
            'titulo': ['Python Developer', 'Data Scientist'],
            'titulo_vaga': ['Senior Python Developer', 'Machine Learning Engineer'],
        }
    )

    resultado = text_feature_generator.adicionar_similaridade_titulo_vaga(df)

    # Update expected column name
    assert 'sim_titulo_vs_vaga' in resultado.columns
    assert len(resultado['sim_titulo_vs_vaga']) == len(df)
    # Similarities should be between 0 and 1
    assert all(0 <= x <= 1 for x in resultado['sim_titulo_vs_vaga'])

import pandas as pd
import numpy as np
from src.definir_target import (
    situacao_candidado_nao_aprovado,
    situacao_candidado_aprovado,
    situacao_candidado_desistente,
    situacao_candidato_inicial,
)


def test_target_mapping_consistency():
    """Test that situation categories are mutually exclusive"""
    all_situations = (
        situacao_candidado_nao_aprovado
        + situacao_candidado_aprovado
        + situacao_candidado_desistente
        + situacao_candidato_inicial
    )

    # Check for duplicates
    assert len(all_situations) == len(set(all_situations)), (
        'Found duplicate situations across categories'
    )


def test_target_categorization():
    # Create sample data
    df = pd.DataFrame(
        {
            'situacao_candidado': [
                'contratado decision',  # aprovado
                'nao aprovado rh',  # não aprovado
                'desistiu',  # desistente
                'inscrito',  # inicial
                'situacao_invalida',  # invalida
            ]
        }
    )

    # Map situations to target
    df['target'] = df['situacao_candidado'].apply(
        lambda x: (
            1
            if x in situacao_candidado_aprovado
            else 0
            if x in situacao_candidado_nao_aprovado
            else np.nan
            if x in situacao_candidado_desistente
            else np.nan
            if x in situacao_candidato_inicial
            else np.nan
        )
    )

    # Check results using pandas testing functions
    pd.testing.assert_series_equal(
        df['target'], pd.Series([1.0, 0.0, np.nan, np.nan, np.nan], name='target')
    )


def test_aprovado_situations():
    """Test that approved situations are correctly identified"""
    sample_situations = [
        'contratado decision',
        'prospect',
        'entrevista tecnica',
        'proposta aceita',
    ]

    for situation in sample_situations:
        assert situation in situacao_candidado_aprovado


def test_nao_aprovado_situations():
    """Test that rejected situations are correctly identified"""
    sample_situations = [
        'nao aprovado rh',
        'nao aprovado cliente',
        'nao aprovado requisitante',
        'recusado',
    ]

    for situation in sample_situations:
        assert situation in situacao_candidado_nao_aprovado


def test_desistente_situations():
    """Test that dropout situations are correctly identified"""
    sample_situations = ['desistiu', 'desistiu contratacao', 'avaliacao rh']

    for situation in sample_situations:
        assert situation in situacao_candidado_desistente


def test_inicial_situations():
    """Test that initial situations are correctly identified"""
    sample_situations = ['encaminhado requisitante', 'interesse nesta vaga', 'inscrito']

    for situation in sample_situations:
        assert situation in situacao_candidato_inicial

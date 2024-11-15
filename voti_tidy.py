import polars as pl
import streamlit as st
from statsmodels.tsa.statespace.tools import prepare_trend_data


def get_raw_data():
    file = "Europee2024.txt"
    voti = pl.read_csv(file, separator=";")

    # togliamo una colonna inutile e rinominiamo per semplificarci la vita
    # questo sarà il dataframe che rappresenta l'linformazione iniziale "raw"
    # indico il tipo atteso altrimenti pycharm si confonde
    voti: pl.dataframe = (voti
    .drop("DATA_ELEZIONE")
    .rename({
        "DESCCIRCEUROPEA": "CIRCOSCRIZIONE",
        "DESCREGIONE": "REGIONE",
        "DESCPROVINCIA": "PROVINCIA",
        "DESCCOMUNE": "COMUNE"
    }))
    return voti


# vediamo che ci sono 7896 comuni e 15 partiti totali, non tutti presenti in ogni circoscrizione
# notiamo la differenza tra un valone null, che indica che il partito non era candidato in quel comune
# (perché non si è candidato in quella circoscrizione)
# e il valore 0 che indica che il partito non ha raccolto voti nel comune indicato (ma era candidato)


@st.cache_data
def data_preprocessing():
    voti = get_raw_data()

    # effettuamo un pivot per rendere il singolo comune l'unità statistica e il numero di voti di ogni lista una variabile
    Abs: pl.DataFrame = (voti.pivot(on="DESCLISTA", values="NUMVOTI")
    .with_columns(
        VOTI_VALIDI=pl.sum_horizontal(partiti)
    ))

    # inizializzia il dataframe per le percentuali di voto per partito
    Perc: pl.DataFrame = Abs.select(
        ["CIRCOSCRIZIONE", "REGIONE", "PROVINCIA", "COMUNE", "ELETTORI", "ELETTORI_M"])
    # crea il dataframe votiPerc aggiungendo alle colonne delle caratteristiche dei comuni le percentuali di ogni partito
    for partito in partiti:
        Perc = Perc.with_columns([
            (Abs[partito] / Abs["VOTI_VALIDI"] * 100).round(2).alias(partito)])  # da rivedere rounding
    return Abs, Perc


partiti = [
    "FRATELLI D'ITALIA",
    "PARTITO DEMOCRATICO",
    "MOVIMENTO 5 STELLE",
    "FORZA ITALIA - NOI MODERATI - PPE",
    "LEGA SALVINI PREMIER",
    "ALLEANZA VERDI E SINISTRA",
    "STATI UNITI D'EUROPA",
    "AZIONE - SIAMO EUROPEI",
    "PACE TERRA DIGNITA'",
    "LIBERTA'",
    "SÜDTIROLER VOLKSPARTEI (SVP)",
    "ALTERNATIVA POPOLARE",
    "DEMOCRAZIA SOVRANA POPOLARE",
    "PARTITO ANIMALISTA - ITALEXIT PER L'ITALIA",
    "RASSEMBLEMENT VALDÔTAIN"
]

votiAbs, votiPerc = data_preprocessing()

if __name__ == "__main__":
    pl.Config.set_tbl_width_chars(200)
    pl.Config(tbl_cols=20)
    print("VOTI:")
    print(get_raw_data())
    print("-" * 20)
    print("votiABS:")
    print(votiAbs)
    print("-" * 20)
    print("votiPERC:")
    print(votiPerc)

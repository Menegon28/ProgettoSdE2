import polars as pl
import altair as alt
import streamlit as st
from voti_tidy import votiPerc


@st.cache_data
def coord_preprocessing():
    cities = pl.read_csv("cities_coord_original.csv")

    processed = cities.with_columns(
        pl.col("name")
        .str.replace_all(r"à", "a'")
        .str.replace_all(r"è", "e'")
        .str.replace_all(r"é", "e'")
        .str.replace_all(r"ì", "i'")
        .str.replace_all(r"ò", "o'")
        .str.replace_all(r"ù", "u'")
        .str.replace("Rome", "Roma")
        .str.replace("Milan", "Milano")
        .str.replace("Naples", "Napoli")
        .str.replace("Turin", "Torino")
        .str.replace("Genoa", "Genova")
        .str.replace("Florence", "Firenze")
        .str.replace("Venice", "Venezia")
        .str.replace("Reggio Calabria", "Reggio di Calabria")
        .str.replace("Bolzano", "Bolzano/Bozen")
        .str.replace("Fiumicino-Isola Sacra", "Fiumicino")
        .str.replace("Carpi Centro", "Carpi")
        .str.replace("San Remo", "Sanremo")

    )
    # with pl.Config(tbl_rows=50):
    #     print(processed.select("name"))
    processed.write_csv("cities_coord_prepr.csv")


@st.cache_data
def get_coord():
    cities = pl.read_csv("cities_coord_prepr.csv")

    coord = (cities.select(["name", "location"])
             .with_columns(
        pl.col("location").str.json_decode(),
        pl.col("name").str.to_uppercase()
        ).unnest("location")
        .drop("__type")
        .unique(subset="name", keep="none")
        .sort("name"))
    pl.Config(tbl_rows=50)
    # per trovare i comuni mancanti più popolosi (e contarli)
    # print(votiPerc.join(coord, left_on="COMUNE", right_on="name", how="anti")
    #       .select(["COMUNE", "ELETTORI"]).sort("ELETTORI", descending=True))
    return votiPerc.join(coord, left_on="COMUNE", right_on="name")


@st.cache_data
def get_topo_data(livello):
    if livello == "REGIONE":
        geo = alt.topo_feature(
            "https://raw.githubusercontent.com/openpolis/geojson-italy/master/topojson/limits_IT_regions.topo.json",
            "regions")
        label = "properties.reg_name"
    else:  # elif chLiv == "COMUNE":
        geo = alt.topo_feature(
            "https://raw.githubusercontent.com/openpolis/geojson-italy/master/topojson/limits_IT_provinces.topo.json",
            "provinces")
        label = "properties.prov_name"
    return geo, label

coord_preprocessing()
votiCoord = get_coord()


if __name__ == "__main__":
    pass



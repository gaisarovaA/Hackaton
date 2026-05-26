import pandas as pd


def normalize(value, min_value, max_value):

    if max_value - min_value == 0:
        return 0

    return (value - min_value) / (max_value - min_value)


def calculate_region_score(row, df, params):

    score = 0

    # =========================================
    # ЛОГИСТИКА
    # =========================================

    if params["railway_required"]:

        if row["railway"]:
            score += 20
        else:
            score -= 20

    highway_score = max(
        0,
        15 - row["distance_to_highway"]
    )

    score += highway_score

    # =========================================
    # ЭНЕРГЕТИКА
    # =========================================

    power_score = normalize(
        row["free_power_kva"],
        df["free_power_kva"].min(),
        df["free_power_kva"].max()
    ) * 20

    score += power_score

    tariff_score = (
        10 -
        normalize(
            row["energy_tariff"],
            df["energy_tariff"].min(),
            df["energy_tariff"].max()
        ) * 10
    )

    score += tariff_score

    # =========================================
    # ГАЗ
    # =========================================

    if row["gas_available"]:
        score += 10

    # =========================================
    # ЭКОНОМИКА
    # =========================================

    salary_score = (
        10 -
        normalize(
            row["salary"],
            df["salary"].min(),
            df["salary"].max()
        ) * 10
    )

    score += salary_score

    rent_score = (
        10 -
        normalize(
            row["housing_rent"],
            df["housing_rent"].min(),
            df["housing_rent"].max()
        ) * 10
    )

    score += rent_score

    # =========================================
    # СОЦИАЛЬНАЯ ИНФРАСТРУКТУРА
    # =========================================

    score += row["kindergarten_index"] * 0.1

    score += row["urban_environment_index"] * 0.05

    score += row["colleges"] * 2

    # =========================================
    # ЛЬГОТЫ
    # =========================================

    if row["special_economic_zone"]:
        score += 15

    score += row["tax_benefits"]

    # =========================================
    # ЭКОЛОГИЯ
    # =========================================

    eco_score = row["eco_index"] * 2

    score += eco_score

    # =========================================
    # БЮДЖЕТ
    # =========================================

    if row["site_price_mln"] <= params["budget"]:
        score += 20
    else:
        score -= 15

    # =========================================
    # ЛОГИСТИКА СЫРЬЯ
    # =========================================

    steel_score = (
        10 -
        normalize(
            row["distance_to_steel"],
            df["distance_to_steel"].min(),
            df["distance_to_steel"].max()
        ) * 10
    )

    score += steel_score

    insulation_score = (
        10 -
        normalize(
            row["distance_to_insulation"],
            df["distance_to_insulation"].min(),
            df["distance_to_insulation"].max()
        ) * 10
    )

    score += insulation_score

    return round(score, 2)


def rank_regions(df, params):

    df["total_score"] = df.apply(
        lambda row: calculate_region_score(
            row,
            df,
            params
        ),
        axis=1
    )

    ranked = df.sort_values(
        by="total_score",
        ascending=False
    )

    return ranked

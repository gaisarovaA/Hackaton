import pandas as pd


def calculate_region_score(row, params):
    score = 0

    # Логистика
    if params["railway_required"] and row["railway"]:
        score += 20

    if row["distance_to_highway"] <= params["max_distance_highway"]:
        score += 15

    # Электричество
    if row["free_power_kva"] >= 500:
        score += 15

    # Газ
    if row["gas_available"]:
        score += 10

    # Льготы
    if row["special_economic_zone"]:
        score += 15

    # Социальная инфраструктура
    score += row["kindergarten_index"] * 0.1
    score += row["urban_environment_index"] * 0.05

    # Стоимость подключения
    score += max(0, 15 - row["connection_price"] / 1000)

    return round(score, 2)



def rank_regions(df, params):
    df["total_score"] = df.apply(
        lambda row: calculate_region_score(row, params),
        axis=1
    )

    return df.sort_values(by="total_score", ascending=False)
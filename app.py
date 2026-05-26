import json
from pathlib import Path

import pandas as pd
import streamlit as st
import folium

from streamlit_folium import st_folium

from ranking import rank_regions
from calculations import calculate_areas, calculate_estimate


# =========================================
# Настройка страницы
# =========================================

st.set_page_config(
    page_title="Наследие индустрии",
    layout="wide"
)

st.title("🏭 Наследие индустрии")
st.subheader("Подбор промышленной площадки и аналитика региона")


# =========================================
# Пути к файлам
# =========================================

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "regions.json"


# =========================================
# Загрузка данных
# =========================================

with open(DATA_FILE, "r", encoding="utf-8") as f:
    regions = json.load(f)

df = pd.DataFrame(regions)


# =========================================
# Sidebar
# =========================================

st.sidebar.header("Параметры инвестора")

volume = st.sidebar.slider(
    "Объем выпуска (тыс. м²/год)",
    100,
    1000,
    400
)

employees = st.sidebar.slider(
    "Количество сотрудников",
    10,
    500,
    100
)

budget = st.sidebar.slider(
    "Бюджет (млн ₽)",
    10,
    500,
    150
)

railway_required = st.sidebar.checkbox(
    "Требуется ж/д ветка",
    value=True
)

max_distance_highway = st.sidebar.slider(
    "Максимальное расстояние до трассы (км)",
    1,
    100,
    20
)

housing_percent = st.sidebar.selectbox(
    "Обеспечение жильем сотрудников (%)",
    [0, 30, 50, 70]
)

kindergarten_places = st.sidebar.selectbox(
    "Мест в детском саду на 100 сотрудников",
    [0, 15, 30, 50]
)
# =========================================
# Session State
# =========================================

if "run_analysis" not in st.session_state:
    st.session_state.run_analysis = False

# =========================================
# Кнопка запуска анализа
# =========================================

if st.sidebar.button(
        "🔍 Получить результат",
        use_container_width=True
):
    st.session_state.run_analysis = True

# =========================================
# Анализ
# =========================================

if st.session_state.run_analysis:
    params = {
        "railway_required": railway_required,
        "max_distance_highway": max_distance_highway,
        "budget": budget
    }

    ranked_df = rank_regions(
        df.copy(),
        params
    )

    top3 = ranked_df.head(3)

    st.success("Анализ завершён")
    # =========================================
    # Карта
    # =========================================

    st.header("📍 ТОП-3 региона")

    m = folium.Map(
        location=[56.0, 60.0],
        zoom_start=4
    )

    for _, row in top3.iterrows():

        popup_text = f"""
        <b>{row['region']}</b><br>
        Город: {row['city']}<br>
        Рейтинг: {row['total_score']}<br>
        Электричество: {row['free_power_kva']} кВА<br>
        Газ: {'Да' if row['gas_available'] else 'Нет'}
        """

        folium.Marker(
            [row["lat"], row["lon"]],
            popup=popup_text,
            tooltip=row["region"]
        ).add_to(m)

    st_folium(
        m,
        width=1200,
        height=500
    )

    # =========================================
    # Таблица рейтинга
    # =========================================

    st.header("📊 Рейтинг регионов")

    rating_table = top3[[
        "region",
        "city",
        "total_score",
        "energy_tariff",
        "free_power_kva",
        "salary",
        "housing_rent"
    ]]

    rating_table.columns = [
        "Регион",
        "Город",
        "Рейтинг",
        "Тариф",
        "Свободная мощность",
        "Средняя зарплата",
        "Аренда жилья"
    ]

    st.dataframe(
        rating_table,
        use_container_width=True
    )

    # =========================================
    # Выбор региона
    # =========================================

    selected_region = st.selectbox(
        "Выберите регион для аналитики",
        top3["region"].tolist()
    )

    region_data = top3[
        top3["region"] == selected_region
    ].iloc[0]

    # =========================================
    # Аналитическая справка
    # =========================================

    st.header("📑 Аналитическая справка")

    # =========================================
    # Социальный блок
    # =========================================

    st.subheader("🏙 Социальный паспорт")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Индекс городской среды",
        region_data["urban_environment_index"]
    )

    col2.metric(
        "Колледжи",
        region_data["colleges"]
    )

    col3.metric(
        "Средняя аренда",
        f"{region_data['housing_rent']} ₽"
    )

    # =========================================
    # Экономика
    # =========================================

    st.subheader("💼 Экономика региона")

    st.write(
        f"Энерготариф: {region_data['energy_tariff']} ₽/кВт·ч"
    )

    st.write(
        f"Средняя зарплата: {region_data['salary']} ₽"
    )

    st.write(
        f"Налоговые льготы: {region_data['tax_benefits']}/10"
    )

    # =========================================
    # Сетевая инфраструктура
    # =========================================

    st.subheader("⚡ Сетевая инфраструктура")

    st.write(
        f"Газоснабжение: {'Да' if region_data['gas_available'] else 'Нет'}"
    )

    st.write(
        f"Свободная мощность: {region_data['free_power_kva']} кВА"
    )

    st.write(
        f"Стоимость подключения: {region_data['connection_price']} ₽/кВт"
    )

    # =========================================
    # Логистика
    # =========================================

    st.subheader("🚛 Логистика сырья")

    st.write(
        f"Расстояние до поставщика стали: "
        f"{region_data['distance_to_steel']} км"
    )

    st.write(
        f"Расстояние до поставщика утеплителя: "
        f"{region_data['distance_to_insulation']} км"
    )

    # =========================================
    # Расчет площадей
    # =========================================

    st.header("📐 Расчет площадей")

    areas = calculate_areas(
        volume,
        employees,
        housing_percent,
        kindergarten_places
    )

    areas_df = pd.DataFrame(
        list(areas.items()),
        columns=["Объект", "Площадь (м²)"]
    )

    st.dataframe(
        areas_df,
        use_container_width=True
    )

    # =========================================
    # Предварительная смета
    # =========================================

    estimate = calculate_estimate(areas)

    st.header("💰 Предварительная смета")

    st.metric(
        "Ориентировочная стоимость",
        f"{estimate:,.0f} ₽"
    )

    # =========================================
    # Рекомендации
    # =========================================

    st.header("🧠 Рекомендации")

    recommendations = []

    if region_data["housing_rent"] > 30000:
        recommendations.append(
            "Рекомендуется строительство общежития для сотрудников."
        )

    if region_data["distance_to_highway"] > 15:
        recommendations.append(
            "Рекомендуется корпоративный транспорт."
        )

    if region_data["urban_environment_index"] < 190:
        recommendations.append(
            "Рекомендуется дополнительное благоустройство."
        )

    if len(recommendations) == 0:
        recommendations.append(
            "Регион соответствует требованиям инвестора."
        )

    for rec in recommendations:
        st.success(rec)

else:

    st.info(
        "Введите параметры инвестора и нажмите "
        "«Получить результат»"
    )


# =========================================
# Footer
# =========================================

st.divider()

st.caption(
    "MVP платформы анализа промышленной инфраструктуры"
)

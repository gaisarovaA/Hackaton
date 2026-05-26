def calculate_areas(volume, employees, housing_percent, kindergarten_places):
    workshop = volume * 0.4
    warehouse = workshop * 0.35
    abk = workshop * 0.02
    parking = employees * 0.5 * 25
    roads = (workshop + warehouse) * 0.25
    housing = employees * (housing_percent / 100) * 25
    kindergarten = (employees / 100) * kindergarten_places * 15
    canteen = employees * 0.5
    medical = max(20, employees * 0.1)

    return {
        "Цех": workshop,
        "Склад": warehouse,
        "АБК": abk,
        "Парковка": parking,
        "Дороги": roads,
        "Жильё": housing,
        "Детский сад": kindergarten,
        "Столовая": canteen,
        "Медпункт": medical
    }



def calculate_estimate(areas):
    prices = {
        "Цех": 35000,
        "Склад": 35000,
        "АБК": 55000,
        "Жильё": 70000,
        "Детский сад": 50000,
        "Столовая": 35000,
        "Медпункт": 45000,
        "Парковка": 5000,
        "Дороги": 5000
    }

    total = 0

    for key, area in areas.items():
        if key in prices:
            total += area * prices[key]

    return round(total)

import matplotlib.pyplot as plt
import numpy as np
from consts import PROJECT_MODES, DRIVERS_DEFAULT_VALUES, LEVELS, LEVEL_TO_INDEX
import sys

def calcEAF(drivers: dict):
    result = 1
    for value in drivers.values():
        result *= value
    return result

def calcWork(mode: dict, eaf: float, kloc: int):
    return mode["c1"] * eaf * (kloc ** mode["p1"])

def calcTime(mode: dict, work: float):
    return mode["c2"] * (work ** mode["p2"])

def calculate_cocomo(mode_name: str, kloc: int, drivers_levels: dict):
    mode_params = PROJECT_MODES[mode_name]
    eaf = calcEAF(drivers_levels)
    effort = calcWork(mode_params, eaf, kloc)
    time = calcTime(mode_params, effort)
    return effort, time, eaf

def get_base_drivers():
    """Базовые драйверы со значениями по умолчанию (номинальные)"""
    drivers = {}
    for driver in ['RELY', 'DATA', 'CPLX', 'TIME', 'STOR', 'VIRT', 'TURN',
                   'ACAP', 'AEXP', 'PCAP', 'VEXP', 'LEXP', 'MODP', 'TOOL', 'SCED']:
        drivers[driver] = 1.0  # номинальное значение
    return drivers

"""Получение числового значения драйвера по индексу уровня"""
def get_driver_value(driver_name, level_index):
    values = DRIVERS_DEFAULT_VALUES[driver_name]
    if level_index >= len(values):
        return values[-1]
    return values[level_index]

"""Исследование влияния драйверов на трудоемкость и время"""
def research_influence():
    KLOC = 100  # фиксированный размер проекта
    MODE = "intermediate"  # промежуточный тип проекта
    LEVELS_RU = ['Очень низкий', 'Низкий', 'Номинальный', 'Высокий', 'Очень высокий']
    drivers_to_study = {
        'MODP': 'Использование современных методов',
        'TOOL': 'Использование программных инструментов',
        'ACAP': 'Способности аналитика',
        'PCAP': 'Способности программиста'
    }
    
    results = {driver: {'effort': [], 'time': [], 'eaf': []} for driver in drivers_to_study}
    for driver_id, driver_name in drivers_to_study.items():
        print(f"\nИсследование драйвера: {driver_id} - {driver_name}")
        
        values_list = DRIVERS_DEFAULT_VALUES[driver_id]
        max_levels = len(values_list)
        
        for level_idx in range(max_levels):
            drivers = get_base_drivers()
            drivers[driver_id] = values_list[level_idx]
            effort, time, eaf = calculate_cocomo(MODE, KLOC, drivers)
            
            results[driver_id]['effort'].append(effort)
            results[driver_id]['time'].append(time)
            results[driver_id]['eaf'].append(eaf)
            
            level_name = LEVELS_RU[level_idx] if level_idx < len(LEVELS_RU) else LEVELS_RU[-1]
            print(f"  {level_name}: EAF={eaf:.3f}, Трудозатраты={effort:.1f} чел.-мес., Время={time:.1f} мес.")
    
    return results, drivers_to_study

"""Построение графиков результатов исследования"""
def plot_research_results(results, drivers_to_study):  
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['font.size'] = 12
    LEVELS_RU = ['Оч.низкий', 'Низкий', 'Номин.', 'Высокий', 'Оч.высокий']
    colors = {'MODP': '#3498db', 'TOOL': '#e74c3c', 'ACAP': '#2ecc71', 'PCAP': '#f39c12'}
    markers = {'MODP': 'o', 'TOOL': 's', 'ACAP': '^', 'PCAP': 'd'}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    for driver_id in drivers_to_study:
        efforts = results[driver_id]['effort']
        x = range(len(efforts))
        ax1.plot(x, efforts, marker=markers[driver_id], color=colors[driver_id],
                linewidth=2, markersize=8, label=drivers_to_study[driver_id])
    
    ax1.set_xlabel('Уровень драйвера', fontsize=14)
    ax1.set_ylabel('Трудозатраты (чел.-мес.)', fontsize=14)
    ax1.set_title('Влияние драйверов на трудозатраты\n(размер проекта = 100 KLOC)', fontsize=14)
    ax1.set_xticks(range(len(LEVELS_RU)))
    ax1.set_xticklabels(LEVELS_RU, rotation=0)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='best', fontsize=12)
    
    for driver_id in drivers_to_study:
        times = results[driver_id]['time']
        x = range(len(times))
        ax2.plot(x, times, marker=markers[driver_id], color=colors[driver_id],
                linewidth=2, markersize=8, label=drivers_to_study[driver_id])
    
    ax2.set_xlabel('Уровень драйвера', fontsize=14)
    ax2.set_ylabel('Время разработки (мес.)', fontsize=14)
    ax2.set_title('Влияние драйверов на время разработки\n(размер проекта = 100 KLOC)', fontsize=14)
    ax2.set_xticks(range(len(LEVELS_RU)))
    ax2.set_xticklabels(LEVELS_RU, rotation=0)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='best', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('research_drivers_influence.png', dpi=150, bbox_inches='tight')
    plt.show()

"""Сравнение влияния автоматизации и персонала при сокращении срока"""
def compare_automation_vs_personnel():
    KLOC = 100
    MODE = "intermediate"
    
    # Базовый случай (все номинальное)
    base_drivers = get_base_drivers()
    base_effort, base_time, _ = calculate_cocomo(MODE, KLOC, base_drivers)
    
    print("Сравнение влияния автоматизации и персонала")
    print(f"Базовый случай (все номинальное):")
    print(f"  Трудозатраты: {base_effort:.1f} чел.-мес.")
    print(f"  Время: {base_time:.1f} мес.")
    
    # Случай 1: Высокая автоматизация
    high_auto_drivers = get_base_drivers()
    high_auto_drivers['MODP'] = DRIVERS_DEFAULT_VALUES['MODP'][3]  # Высокий
    high_auto_drivers['TOOL'] = DRIVERS_DEFAULT_VALUES['TOOL'][3]  # Высокий
    
    auto_effort, auto_time, _ = calculate_cocomo(MODE, KLOC, high_auto_drivers)
    
    print(f"\nВысокая автоматизация (MODP и TOOL = Высокий):")
    print(f"  Трудозатраты: {auto_effort:.1f} чел.-мес. (снижение на {(1 - auto_effort/base_effort)*100:.1f}%)")
    print(f"  Время: {auto_time:.1f} мес. (снижение на {(1 - auto_time/base_time)*100:.1f}%)")
    
    # Случай 2: Высокие способности персонала
    high_personnel_drivers = get_base_drivers()
    high_personnel_drivers['ACAP'] = DRIVERS_DEFAULT_VALUES['ACAP'][3]  # Высокий
    high_personnel_drivers['PCAP'] = DRIVERS_DEFAULT_VALUES['PCAP'][3]  # Высокий
    
    personnel_effort, personnel_time, _ = calculate_cocomo(MODE, KLOC, high_personnel_drivers)
    
    print(f"\nВысокие способности персонала (ACAP и PCAP = Высокий):")
    print(f"  Трудозатраты: {personnel_effort:.1f} чел.-мес. (снижение на {(1 - personnel_effort/base_effort)*100:.1f}%)")
    print(f"  Время: {personnel_time:.1f} мес. (снижение на {(1 - personnel_time/base_time)*100:.1f}%)")

"""Сравнение влияния RELY и TIME при высокой автоматизации"""
def compare_rely_vs_time():
    KLOC = 100
    MODE = "intermediate"
    
    # База: высокая автоматизация
    base_auto_drivers = get_base_drivers()
    base_auto_drivers['MODP'] = DRIVERS_DEFAULT_VALUES['MODP'][3]  # Высокий
    base_auto_drivers['TOOL'] = DRIVERS_DEFAULT_VALUES['TOOL'][3]  # Высокий
    
    base_effort, base_time, _ = calculate_cocomo(MODE, KLOC, base_auto_drivers)
    
    print("Сравнение влияния RELY и TIME при высокой автоматизации")
    print(f"Базовый случай (высокая автоматизация, RELY и TIME номинальные):")
    print(f"  Трудозатраты: {base_effort:.1f} чел.-мес.")
    print(f"  Время: {base_time:.1f} мес.")
    
    # Случай 1: Высокая надежность (RELY)
    high_rely_drivers = base_auto_drivers.copy()
    high_rely_drivers['RELY'] = DRIVERS_DEFAULT_VALUES['RELY'][3]  # Высокий
    
    rely_effort, rely_time, _ = calculate_cocomo(MODE, KLOC, high_rely_drivers)
    
    print(f"\nВысокая надежность (RELY = Высокий, 1.15):")
    print(f"  Трудозатраты: {rely_effort:.1f} чел.-мес. (увеличение на {(rely_effort/base_effort - 1)*100:.1f}%)")
    print(f"  Время: {rely_time:.1f} мес. (увеличение на {(rely_time/base_time - 1)*100:.1f}%)")
    
    # Случай 2: Высокое ограничение времени (TIME)
    high_time_drivers = base_auto_drivers.copy()
    high_time_drivers['TIME'] = DRIVERS_DEFAULT_VALUES['TIME'][3]  # Высокий 
    
    time_effort, time_result, _ = calculate_cocomo(MODE, KLOC, high_time_drivers)
    
    print(f"\nВысокое ограничение времени (TIME = Высокий, 1.11):")
    print(f"  Трудозатраты: {time_effort:.1f} чел.-мес. (увеличение на {(time_effort/base_effort - 1)*100:.1f}%)")
    print(f"  Время: {time_result:.1f} мес. (увеличение на {(time_result/base_time - 1)*100:.1f}%)")

def main():
    print("Исследование влияния драйверов затрат")
    
    print("\n1. Исследование влияния драйверов на трудоемкость и время...")
    results, drivers_to_study = research_influence()
    plot_research_results(results, drivers_to_study)
    
    # 3. Сравнение автоматизации и персонала
    compare_automation_vs_personnel()
    
    # 4. Сравнение RELY и TIME
    compare_rely_vs_time()

    print("График сохранен в файл: research_drivers_influence.png")


if __name__ == "__main__":
    main()
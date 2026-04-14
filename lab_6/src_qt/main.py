import sys
import math
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from consts import *


def calcEAF(drivers: dict):
    result = 1
    for value in drivers.values():
        result *= value
    return result


def calcWork(mode: dict, eaf: float, kloc: int):
    return mode["c1"] * eaf * (kloc ** mode["p1"])


def calcTime(mode: dict, work: float):
    return mode["c2"] * (work ** mode["p2"])


def convert_drivers_to_values(drivers_levels: dict) -> dict:
    result = {}
    for name, level_str in drivers_levels.items():
        index = LEVEL_TO_INDEX[level_str]
        values_list = DRIVERS_DEFAULT_VALUES[name]
        if index >= len(values_list):
            index = len(values_list) - 1
        result[name] = values_list[index]
    return result


def calculate_cocomo(mode_name: str, kloc: int, drivers_levels: dict):
    mode_params = PROJECT_MODES[mode_name]
    drivers_values = convert_drivers_to_values(drivers_levels)
    
    eaf = calcEAF(drivers_values)
    effort = calcWork(mode_params, eaf, kloc)
    time = calcTime(mode_params, effort)
    effort = round(effort, 2)
    time = round(time, 2)
    eaf = round(eaf, 2)
    
    return effort, time, eaf


class CocomoCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_effort = 0
        self.current_time = 0
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("COCOMO Calculator")
        self.setGeometry(100, 100, 1200, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Верхняя панель
        top_frame = QFrame()
        top_layout = QHBoxLayout(top_frame)
        
        # KLOC
        kloc_label = QLabel("KLOC (тысячи строк кода):")
        self.kloc_entry = QLineEdit()
        self.kloc_entry.setFixedWidth(150)
        self.kloc_entry.setText("50")
        top_layout.addWidget(kloc_label)
        top_layout.addWidget(self.kloc_entry)
        top_layout.addSpacing(20)
        
        # Зарплата
        cost_label = QLabel("Средняя зп (тыс. руб.):")
        self.cost_entry = QLineEdit()
        self.cost_entry.setText("150")
        self.cost_entry.setFixedWidth(150)
        top_layout.addWidget(cost_label)
        top_layout.addWidget(self.cost_entry)
        top_layout.addSpacing(20)
        
        # Режим проекта
        mode_label = QLabel("Режим проекта:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(list(PROJECT_MODES.keys()))
        self.mode_combo.setFixedWidth(250)
        self.mode_label_display = QLabel("(Обычный)")
        
        top_layout.addWidget(mode_label)
        top_layout.addWidget(self.mode_combo)
        top_layout.addWidget(self.mode_label_display)
        top_layout.addStretch()
        
        self.mode_combo.currentTextChanged.connect(self.update_mode_display)
        
        main_layout.addWidget(top_frame)

        # Основная панель
        bottom_panel = QWidget()
        bottom_layout = QHBoxLayout(bottom_panel)
        
        # Левая панель - драйверы
        left_panel = QGroupBox("Драйверы стоимости (Cost Drivers)")
        left_layout = QVBoxLayout(left_panel)
        
        # Scroll area для драйверов
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setAlignment(Qt.AlignTop)
        
        self.driver_vars = {}
        
        for group_name, drivers in DRIVER_GROUPS.items():
            group_label = QLabel(f"━━━ {group_name} ━━━")
            group_label.setStyleSheet("background-color: #ecf0f1; padding: 5px; font-weight: bold;")
            scroll_layout.addWidget(group_label)
            
            for driver_id in drivers:
                driver_name = DRIVERS_NAMES[driver_id]
                levels_for_driver = DRIVER_LEVELS_MAP[driver_id]
                
                row_widget = QWidget()
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(10, 2, 10, 2)
                
                label_text = f"{driver_id}: {driver_name}"
                label = QLabel(label_text)
                label.setFixedWidth(550)
                
                combo = QComboBox()
                combo.addItems(levels_for_driver)
                combo.setCurrentText("Номинальный")
                combo.setFixedWidth(250)
                self.driver_vars[driver_id] = combo
                
                row_layout.addWidget(label)
                row_layout.addWidget(combo)
                row_layout.addStretch()
                scroll_layout.addWidget(row_widget)
        
        scroll_area.setWidget(scroll_widget)
        left_layout.addWidget(scroll_area)
        bottom_layout.addWidget(left_panel, 1)
        
        # Правая панель - таблицы
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.create_distribution_table(right_layout)
        self.create_budget_table(right_layout)
        
        bottom_layout.addWidget(right_panel, 2)
        main_layout.addWidget(bottom_panel)
        
         # Панель результатов расчета
        result_frame = QFrame()
        result_frame.setFrameStyle(QFrame.Box | QFrame.Raised)
        result_layout = QHBoxLayout(result_frame)
        
        # Трудозатраты
        effort_label = QLabel("Трудозатраты:")
        self.effort_value_label = QLabel("—")
        self.effort_unit_label = QLabel("чел.-мес.")
        
        # Время
        time_label = QLabel("Время разработки:")
        self.time_value_label = QLabel("—")
        self.time_unit_label = QLabel("мес.")
        
        # EAF
        eaf_label = QLabel("EAF:")
        self.eaf_value_label = QLabel("—")
        
        result_layout.addWidget(effort_label)
        result_layout.addWidget(self.effort_value_label)
        result_layout.addWidget(self.effort_unit_label)
        result_layout.addSpacing(30)
        result_layout.addWidget(time_label)
        result_layout.addWidget(self.time_value_label)
        result_layout.addWidget(self.time_unit_label)
        result_layout.addSpacing(30)
        result_layout.addWidget(eaf_label)
        result_layout.addWidget(self.eaf_value_label)
        result_layout.addStretch()
        
        main_layout.addWidget(result_frame)

        calc_button = QPushButton("Рассчитать")
        calc_button.clicked.connect(self.calculate)
        main_layout.addWidget(calc_button)

        chart_button = QPushButton("Показать диаграмму")
        chart_button.clicked.connect(self.show_staff_chart_window)
        main_layout.addWidget(chart_button)
    
    def update_mode_display(self, mode_key):
        if mode_key in PROJECT_MODES:
            self.mode_label_display.setText(f"({PROJECT_MODES[mode_key]['name']})")
    
    def create_distribution_table(self, parent_layout):
        table_group = QGroupBox("Распределение по этапам")
        layout = QVBoxLayout(table_group)
        
        headers = ["Вид деятельности", "Трудозатраты (%)", "Трудозатраты (чел.-мес.)", "Время (%)", "Время (мес.)"]
        
        table_widget = QTableWidget()
        table_widget.setColumnCount(len(headers))
        table_widget.setHorizontalHeaderLabels(headers)
        table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        
        self.table_cells = []
        current_row = 0
        
        for stage, effort_pct, time_pct in STAGES:
            table_widget.insertRow(current_row)
            
            table_widget.setItem(current_row, 0, QTableWidgetItem(stage))
            table_widget.setItem(current_row, 1, QTableWidgetItem(f"{effort_pct}%"))
            
            effort_item = QTableWidgetItem("—")
            time_item = QTableWidgetItem("—")
            table_widget.setItem(current_row, 2, effort_item)
            table_widget.setItem(current_row, 3, QTableWidgetItem(f"{time_pct}%"))
            table_widget.setItem(current_row, 4, time_item)
            
            self.table_cells.append({
                'type': 'stage',
                'effort_item': effort_item,
                'time_item': time_item,
                'effort_pct': effort_pct,
                'time_pct': time_pct
            })
            current_row += 1
        
        # ИТОГО
        table_widget.insertRow(current_row)
        table_widget.setItem(current_row, 0, QTableWidgetItem("ИТОГО"))
        table_widget.setItem(current_row, 1, QTableWidgetItem("100%"))
        self.total_effort_item = QTableWidgetItem("—")
        table_widget.setItem(current_row, 2, self.total_effort_item)
        table_widget.setItem(current_row, 3, QTableWidgetItem("100%"))
        self.total_time_item = QTableWidgetItem("—")
        table_widget.setItem(current_row, 4, self.total_time_item)
        current_row += 1
        
        # ИТОГО с планированием
        table_widget.insertRow(current_row)
        table_widget.setItem(current_row, 0, QTableWidgetItem("ИТОГО (с планированием)"))
        table_widget.setItem(current_row, 1, QTableWidgetItem("108%"))
        self.total_with_planning_effort_item = QTableWidgetItem("—")
        table_widget.setItem(current_row, 2, self.total_with_planning_effort_item)
        table_widget.setItem(current_row, 3, QTableWidgetItem("136%"))
        self.total_with_planning_time_item = QTableWidgetItem("—")
        table_widget.setItem(current_row, 4, self.total_with_planning_time_item)
        
        # table_widget.horizontalHeader().setStretchLastSection(True)
        table_widget.setColumnWidth(0, 500)
        for col in range(1, 5):
            table_widget.setColumnWidth(col, 200)
        
        layout.addWidget(table_widget)
        parent_layout.addWidget(table_group)
    
    def update_distribution_table(self, total_effort, total_time):
        planning_effort_pct = STAGES[0][1]
        planning_time_pct = STAGES[0][2]
        
        planning_effort = total_effort * planning_effort_pct / 100
        planning_time = total_time * planning_time_pct / 100
        
        sum_effort_other = 0
        sum_time_other = 0
        
        for i, cell in enumerate(self.table_cells):
            if i == 0:
                effort_at_stage = planning_effort
                time_at_stage = planning_time
            else:
                effort_at_stage = total_effort * cell['effort_pct'] / 100
                time_at_stage = total_time * cell['time_pct'] / 100
                sum_effort_other += effort_at_stage
                sum_time_other += time_at_stage
            
            cell['effort_item'].setText(f"{effort_at_stage:.1f}")
            cell['time_item'].setText(f"{time_at_stage:.1f}")
        
        self.total_effort_item.setText(f"{sum_effort_other:.1f}")
        self.total_time_item.setText(f"{sum_time_other:.1f}")
        
        total_with_planning_effort = sum_effort_other + planning_effort
        total_with_planning_time = sum_time_other + planning_time
        
        self.total_with_planning_effort_item.setText(f"{total_with_planning_effort:.1f}")
        self.total_with_planning_time_item.setText(f"{total_with_planning_time:.1f}")
    
    def create_budget_table(self, parent_layout):
        table_group = QGroupBox("Распределение бюджета")
        layout = QVBoxLayout(table_group)
        
        headers = ["Вид деятельности", "Бюджет (%)", "Чел.-мес.", "Затраты"]
        
        table_widget = QTableWidget()
        table_widget.setColumnCount(len(headers))
        table_widget.setHorizontalHeaderLabels(headers)
        table_widget.setEditTriggers(QTableWidget.NoEditTriggers)

        self.budget_cells = []
        row = 0
        
        for name, pct in BUDGET_STAGES:
            table_widget.insertRow(row)
            table_widget.setItem(row, 0, QTableWidgetItem(name))
            table_widget.setItem(row, 1, QTableWidgetItem(f"{pct}%"))
            
            effort_item = QTableWidgetItem("—")
            cost_item = QTableWidgetItem("—")
            table_widget.setItem(row, 2, effort_item)
            table_widget.setItem(row, 3, cost_item)
            
            self.budget_cells.append({
                "pct": pct,
                "effort_item": effort_item,
                "cost_item": cost_item
            })
            row += 1
        
        # ИТОГО
        table_widget.insertRow(row)
        table_widget.setItem(row, 0, QTableWidgetItem("ИТОГО"))
        table_widget.setItem(row, 1, QTableWidgetItem("100%"))
        self.total_budget_effort_item = QTableWidgetItem("—")
        self.total_budget_cost_item = QTableWidgetItem("—")
        table_widget.setItem(row, 2, self.total_budget_effort_item)
        table_widget.setItem(row, 3, self.total_budget_cost_item)
        
        table_widget.setColumnWidth(0, 500)
        for col in range(1, 4):
            table_widget.setColumnWidth(col, 200)
        
        layout.addWidget(table_widget)
        parent_layout.addWidget(table_group)
    
    def update_budget_table(self, total_effort):
        try:
            cost_per_pm = float(self.cost_entry.text()) * 1000
            if cost_per_pm <= 0:
                QMessageBox.warning(self, "Ошибка", "COST должен быть положительным числом")
                return False
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректное значение зарплаты")
            return False
        
        total_cost = total_effort * cost_per_pm
        
        for cell in self.budget_cells:
            effort = total_effort * cell["pct"] / 100
            cost = effort * cost_per_pm
            
            cell["effort_item"].setText(f"{effort:.1f}")
            cell["cost_item"].setText(f"{cost:.0f}")
        
        self.total_budget_effort_item.setText(f"{total_effort:.1f}")
        self.total_budget_cost_item.setText(f"{total_cost:.0f}")
        return True
    
    def calculate(self):
        try:
            kloc = float(self.kloc_entry.text())
            if kloc <= 0:
                QMessageBox.warning(self, "Ошибка", "KLOC должен быть положительным числом")
                return
            
            mode_key = self.mode_combo.currentText()
            
            drivers_levels = {name: combo.currentText() for name, combo in self.driver_vars.items()}
            
            effort, time, eaf = calculate_cocomo(mode_key, kloc, drivers_levels)
            
            self.current_effort = effort
            self.current_time = time
            
            self.update_distribution_table(effort, time)
            self.update_budget_table(effort)
            
            self.effort_value_label.setText(f"{effort:.2f}")
            self.time_value_label.setText(f"{time:.2f}")
            self.eaf_value_label.setText(f"{eaf:.2f}")
            
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка ввода: {e}\nВведите корректное число KLOC (>0)")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Непредвиденная ошибка: {e}")
    
    def show_staff_chart_window(self):
        if self.current_effort == 0:
            QMessageBox.warning(self, "Предупреждение", "Сначала выполните расчёт проекта!")
            return

        plt.rcParams.update({
            'font.size': 20,         
            'axes.titlesize': 24,      
            'axes.labelsize': 20,      
            'xtick.labelsize': 20,     
            'ytick.labelsize': 20,     
            'legend.fontsize': 20,    
        })
        
        chart_window = QDialog(self)
        chart_window.setWindowTitle("Диаграмма привлечения сотрудников")
        chart_window.resize(900, 700)
        
        layout = QVBoxLayout(chart_window)
        
        stages_names = []
        staff_counts = []
        
        for stage_name, effort_pct, time_pct in STAGES:
            effort = self.current_effort * effort_pct / 100
            time = self.current_time * time_pct / 100
            
            staff = max(1, round(effort / time)) if time > 0 else 1
            
            stages_names.append(stage_name)
            staff_counts.append(staff)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        
        x = np.arange(len(stages_names))
        bars = ax.bar(x, staff_counts, color="#346edb")
        
        ax.set_title("Распределение сотрудников по стадиям")
        ax.set_xlabel("Стадии")
        ax.set_ylabel("Количество сотрудников")
        ax.set_xticks(x)
        ax.set_xticklabels(stages_names, rotation=10, ha="right")
        ax.grid(axis="y", alpha=0.3)
        
        for bar, val in zip(bars, staff_counts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                    str(val), ha='center', va='bottom')
        
        plt.tight_layout()
        
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(chart_window.accept)
        layout.addWidget(close_button)
        
        chart_window.exec_()


def main():
    app = QApplication(sys.argv)
    font = app.font()
    font.setPointSize(11) 
    app.setFont(font)
    app.setStyle('Fusion')
    window = CocomoCalculator()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
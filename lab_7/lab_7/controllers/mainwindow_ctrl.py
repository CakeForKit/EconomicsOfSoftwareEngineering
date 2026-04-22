from PyQt5.QtWidgets import QMainWindow, QComboBox, QSpinBox, QPushButton, QMessageBox
import view.mainwindow as mwd
from function_point import FunctionPointMethod
from controllers.cocomo2_dialog_ctrl import Cocomo2Dialog
from math import floor
import config


class Cocomo2Mainwindow(QMainWindow):
    def __init__(self):
        super(Cocomo2Mainwindow, self).__init__()
        self.ui = mwd.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.run)
        self.__build()
        self.__load_and_apply_config()
        self.__set_coefs()

        # Connect add language button
        self.ui.add_lang_button.clicked.connect(self.__add_language_row)

    def __build(self):
        # System params and quantity matrix setup remains the same...
        self.lang_combos = []
        self.lang_perc_spins = []
        self.lang_remove_buttons = []
        # No initial rows - they're created based on config

        # Remove original predefined language widgets to avoid duplicates
        original_widgets = [
            self.ui.first_lang_comboBox, self.ui.first_lang_perc_spinBox,
            self.ui.second_lang_comboBox, self.ui.second_lang_perc_spinBox,
            self.ui.third_lang_comboBox, self.ui.third_lang_perc_spinBox,
        ]
        for w in original_widgets:
            self.ui.gridLayout_3.removeWidget(w)
            w.hide()
            w.deleteLater()

        self.complexity_matrix_quantity = [
            [self.ui.simple_ei_spinBox,
             self.ui.med_ei_spinBox,
             self.ui.hard_ei_spinBox],
            [self.ui.simple_eo_spinBox,
             self.ui.med_eo_spinBox,
             self.ui.hard_eo_spinBox],
            [self.ui.simple_eq_spinBox,
             self.ui.med_eq_spinBox,
             self.ui.hard_eq_spinBox],
            [self.ui.simple_ilf_spinBox,
             self.ui.med_ilf_spinBox,
             self.ui.hard_ilf_spinBox],
            [self.ui.simple_eif_spinBox,
             self.ui.med_eif_spinBox,
             self.ui.hard_eif_spinBox]
        ]
        self.complexity_matrix_koef = [
            [self.ui.simple_ei_label,
             self.ui.med_ei_label,
             self.ui.hard_ei_label],
            [self.ui.simple_eo_label,
             self.ui.med_eo_label,
             self.ui.hard_eo_label],
            [self.ui.simple_eq_label,
             self.ui.med_eq_label,
             self.ui.hard_eq_label],
            [self.ui.simple_ilf_label,
             self.ui.med_ilf_label,
             self.ui.hard_ilf_label],
            [self.ui.simple_eif_label,
             self.ui.med_eif_label,
             self.ui.hard_eif_label]
        ]
        self.complexity_matrix_total = [
            self.ui.total_ei_label,
            self.ui.total_eo_label,
            self.ui.total_eq_label,
            self.ui.total_ilf_label,
            self.ui.total_eif_label,
            self.ui.total_label
        ]

        self.sys_params_input = [
            self.ui.sys_1_spinBox,
            self.ui.sys_2_spinBox,
            self.ui.sys_3_spinBox,
            self.ui.sys_4_spinBox,
            self.ui.sys_5_spinBox,
            self.ui.sys_6_spinBox,
            self.ui.sys_7_spinBox,
            self.ui.sys_8_spinBox,
            self.ui.sys_9_spinBox,
            self.ui.sys_10_spinBox,
            self.ui.sys_11_spinBox,
            self.ui.sys_12_spinBox,
            self.ui.sys_13_spinBox,
            self.ui.sys_14_spinBox,
        ]

    def __create_language_row(self, row_index, percentage):
        """Create a new language row dynamically."""
        combo = QComboBox()
        combo.setObjectName(f"lang_combo_{row_index}")
        for lang in FunctionPointMethod.Languages:
            combo.addItem(lang.name)

        perc_spin = QSpinBox()
        perc_spin.setObjectName(f"lang_perc_{row_index}")
        perc_spin.setMaximum(100)
        perc_spin.setValue(percentage)

        remove_btn = QPushButton("×")
        remove_btn.setObjectName(f"remove_lang_{row_index}")
        remove_btn.setFixedSize(30, 30)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
        """)
        remove_btn.clicked.connect(lambda checked, idx=row_index: self.__remove_language_row(idx))

        # Row index is the current count before adding
        row = len(self.lang_combos)
        self.ui.gridLayout_3.addWidget(combo, row, 1, 1, 1)
        self.ui.gridLayout_3.addWidget(perc_spin, row, 2, 1, 1)
        self.ui.gridLayout_3.addWidget(remove_btn, row, 4, 1, 1)  # column 4 to avoid overlapping label at col 3

        self.lang_combos.append(combo)
        self.lang_perc_spins.append(perc_spin)
        self.lang_remove_buttons.append(remove_btn)

    def __position_add_button(self):
        # Remove and re-add the add button at the correct row
        self.ui.gridLayout_3.removeWidget(self.ui.add_lang_button)
        self.ui.gridLayout_3.addWidget(self.ui.add_lang_button, len(self.lang_combos), 0, 1, 1)

    def __add_language_row(self):
        row_index = len(self.lang_combos)
        self.__create_language_row(row_index, 0)
        self.__position_add_button()

    def __remove_language_row(self, index):
        if len(self.lang_combos) <= 1:
            return  # Keep at least one row

        combo = self.lang_combos.pop(index)
        perc = self.lang_perc_spins.pop(index)
        btn = self.lang_remove_buttons.pop(index)

        # Remove from layout
        self.ui.gridLayout_3.removeWidget(combo)
        self.ui.gridLayout_3.removeWidget(perc)
        self.ui.gridLayout_3.removeWidget(btn)

        combo.deleteLater()
        perc.deleteLater()
        btn.deleteLater()

        # Rebuild all rows to fix indices and button connections
        self.__rebuild_language_section()

    def __rebuild_language_section(self):
        """Clear and rebuild all language rows from current data."""
        # Store current values
        values = []
        for i in range(len(self.lang_combos)):
            values.append({
                'lang_idx': self.lang_combos[i].currentIndex(),
                'perc': self.lang_perc_spins[i].value()
            })

        # Remove all language widgets from gridLayout_3 and clear lists
        while self.lang_combos:
            combo = self.lang_combos.pop(0)
            perc = self.lang_perc_spins.pop(0)
            btn = self.lang_remove_buttons.pop(0)
            self.ui.gridLayout_3.removeWidget(combo)
            self.ui.gridLayout_3.removeWidget(perc)
            self.ui.gridLayout_3.removeWidget(btn)
            combo.deleteLater()
            perc.deleteLater()
            btn.deleteLater()

        # Recreate rows with stored values
        for i, val in enumerate(values):
            self.__create_language_row(i, val['perc'])
            self.lang_combos[i].setCurrentIndex(val['lang_idx'])
        self.__position_add_button()

    def run(self):
        quantity = self.__get_quantity()
        sys_params = self.__get_sys_params()
        total = FunctionPointMethod.count_function_points(quantity)
        self.__set_total(total)
        fp = total[len(total) - 1]
        corrected_fp = FunctionPointMethod.corrected_function_points(fp, sys_params)
        lang_idx = self.__get_lang_idxs()
        lang_perc = self.__get_lang_perc()
        loc = FunctionPointMethod.cfp_to_loc(corrected_fp, lang_idx, lang_perc)
        QMessageBox.information(self, "Debug Info", f"fp = {fp}, corrected fp = {corrected_fp}, loc = {loc}")
        kloc = self.__loc_to_kloc(loc)
        cocomo2_dialog = Cocomo2Dialog(self, kloc)
        cocomo2_dialog.show()

    def __get_lang_perc(self):
        lang_perc = []
        n = len(self.lang_perc_spins)
        for i in range(n):
            lang_perc.append(self.lang_perc_spins[i].value())
        return lang_perc

    def __get_lang_idxs(self):
        lang_idxs = []
        n = len(self.lang_combos)
        for i in range(n):
            lang_idxs.append(self.lang_combos[i].currentIndex())
        return lang_idxs

    def __loc_to_kloc(self, loc):
        kloc = floor(loc / 1000)
        return kloc

    def __set_total(self, total):
        n = len(self.complexity_matrix_total)
        for i in range(n):
            self.complexity_matrix_total[i].setText(str(total[i]))

    def __get_sys_params(self) -> []:
        sys_params = []
        n = len(self.sys_params_input)
        for i in range(n):
            val = self.sys_params_input[i].value()
            sys_params.append(val)
        return sys_params

    def __get_quantity(self) -> []:
        quantity = []
        n = len(self.complexity_matrix_quantity)
        m = len(self.complexity_matrix_quantity[0])
        for i in range(n):
            quantity.append([])
            for j in range(m):
                val = self.complexity_matrix_quantity[i][j].value()
                quantity[i].append(val)
        return quantity

    def __set_coefs(self):
        n = len(FunctionPointMethod.Coefficients)
        m = len(FunctionPointMethod.Coefficients[0])
        for i in range(n):
            for j in range(m):
                self.complexity_matrix_koef[i][j].setText(str(FunctionPointMethod.Coefficients[i][j]))

    def __load_and_apply_config(self):
        cfg = config.load_config()

        # Apply system parameters
        for i, spin in enumerate(self.sys_params_input):
            if i < len(cfg["system_params"]):
                spin.setValue(cfg["system_params"][i])

        # Apply quantity matrix
        for i, row in enumerate(self.complexity_matrix_quantity):
            if i < len(cfg["quantity"]):
                for j, spin in enumerate(row):
                    if j < len(cfg["quantity"][i]):
                        spin.setValue(cfg["quantity"][i][j])

        # Apply language data
        lang_data = cfg.get("languages", [])
        if not lang_data:
            # Fallback to old format or defaults - create 3 rows
            lang_data = []
            selections = cfg.get("lang_selections", [0, 0, 0])
            percentages = cfg.get("lang_percentages", [34, 33, 33])
            for i in range(3):
                lang_data.append({
                    'lang_idx': selections[i] if i < len(selections) else 0,
                    'perc': percentages[i] if i < len(percentages) else (100 if i == 0 else 0)
                })

        # Create rows matching config count
        for i, val in enumerate(lang_data):
            self.__create_language_row(i, val.get('perc', 0))
            self.lang_combos[i].setCurrentIndex(val.get('lang_idx', 0))
        self.__position_add_button()

    def closeEvent(self, event):
        self.__save_config()
        super().closeEvent(event)

    def __save_config(self):
        # Collect quantity matrix
        quantity = [
            [spin.value() for spin in row]
            for row in self.complexity_matrix_quantity
        ]

        # Collect system params
        system_params = [spin.value() for spin in self.sys_params_input]

        # Collect languages
        languages = []
        for i in range(len(self.lang_combos)):
            languages.append({
                'lang_idx': self.lang_combos[i].currentIndex(),
                'perc': self.lang_perc_spins[i].value()
            })

        cfg = {
            "quantity": quantity,
            "system_params": system_params,
            "languages": languages,
        }
        config.save_config(cfg)

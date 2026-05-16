# # # # # # ==============================================================================
# # # # # # FILE LOCATION: Dynamic_Scorecard_System/scorecard_ui.py
# # # # # # ==============================================================================

# # # # # import sys
# # # # # import json
# # # # # import traceback
# # # # # import os
import threading
from concurrent.futures import ThreadPoolExecutor
# # # # # import io
# # # # # import contextlib
# # # # # import shutil
# # # # # import pandas as pd
# # # # # import numpy as np

# # # # # # Force the working directory to be where the EXE is located (or script if running raw)
# # # # # if getattr(sys, 'frozen', False):
# # # # #     application_path = os.path.dirname(sys.executable)
# # # # # else:
# # # # #     application_path = os.path.dirname(os.path.abspath(__file__))

# # # # # os.chdir(application_path)

# # # # # from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
# # # # #                              QHBoxLayout, QPushButton, QLabel, QFileDialog, 
# # # # #                              QTableView, QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem,
# # # # #                              QComboBox, QTextEdit, QLineEdit, QMessageBox, QGroupBox, 
# # # # #                              QInputDialog, QTabWidget, QHeaderView, QSplitter, QAction,
# # # # #                              QDialog, QFormLayout, QCheckBox, QDialogButtonBox, QAbstractItemView,
# # # # #                              QDockWidget, QStackedWidget, QScrollArea, QFrame, QGridLayout)
# # # # # from PyQt5.QtCore import QAbstractTableModel, Qt, QThread, pyqtSignal, QEvent
# # # # # from PyQt5.QtGui import QFont

# # # # # # Make sure these are accessible in your environment
# # # # # try:
# # # # #     from dynamic_engine import DynamicPipelineEngine, prompt_file
# # # # # except ImportError:
# # # # #     # Dummy classes to allow UI to run if engine isn't present
# # # # #     class DynamicPipelineEngine: pass
# # # # #     prompt_file = None

# # # # # try:
# # # # #     from excel_analyzer import analyze_workbook
# # # # # except ImportError:
# # # # #     analyze_workbook = None

# # # # # class TerminalInput(QLineEdit):
# # # # #     """Enhanced QLineEdit with command history (Up/Down arrows)"""
# # # # #     def __init__(self, *args, **kwargs):
# # # # #         super().__init__(*args, **kwargs)
# # # # #         self.history = []
# # # # #         self.history_index = -1
# # # # #         self.temp_cmd = ""

# # # # #     def keyPressEvent(self, event):
# # # # #         if event.key() == Qt.Key_Up:
# # # # #             if not self.history:
# # # # #                 return
# # # # #             if self.history_index == -1:
# # # # #                 self.temp_cmd = self.text()
            
# # # # #             if self.history_index < len(self.history) - 1:
# # # # #                 self.history_index += 1
# # # # #                 self.setText(self.history[self.history_index])
        
# # # # #         elif event.key() == Qt.Key_Down:
# # # # #             if self.history_index > -1:
# # # # #                 self.history_index -= 1
# # # # #                 if self.history_index == -1:
# # # # #                     self.setText(self.temp_cmd)
# # # # #                 else:
# # # # #                     self.setText(self.history[self.history_index])
        
# # # # #         else:
# # # # #             super().keyPressEvent(event)
# # # # #             if event.key() != Qt.Key_Return and event.key() != Qt.Key_Enter:
# # # # #                 self.history_index = -1

# # # # #     def add_to_history(self, cmd):
# # # # #         if cmd.strip():
# # # # #             # Remove existing occurrence to move it to the front
# # # # #             if cmd in self.history:
# # # # #                 self.history.remove(cmd)
# # # # #             self.history.insert(0, cmd)
# # # # #         self.history_index = -1
# # # # #         self.temp_cmd = ""

# # # # # class PandasModel(QAbstractTableModel):
# # # # #     def __init__(self, data):
# # # # #         super().__init__()
# # # # #         self._data = data

# # # # #     def rowCount(self, parent=None): return self._data.shape[0]
# # # # #     def columnCount(self, parent=None): return self._data.shape[1]
# # # # #     def data(self, index, role=Qt.DisplayRole):
# # # # #         if index.isValid() and role == Qt.DisplayRole:
# # # # #             val = self._data.iloc[index.row(), index.column()]
# # # # #             return str(val) if not pd.isna(val) else ""
# # # # #         return None
# # # # #     def headerData(self, col, orientation, role):
# # # # #         if orientation == Qt.Horizontal and role == Qt.DisplayRole:
# # # # #             return str(self._data.columns[col])
# # # # #         return None

# # # # # class StepPreviewWorker(QThread):
# # # # #     result_ready = pyqtSignal(dict, dict)
# # # # #     error_occurred = pyqtSignal(str)

# # # # #     def __init__(self, dfs_dict, vars_dict, step):
# # # # #         super().__init__()
# # # # #         self.dfs_dict = {k: v.copy() for k, v in dfs_dict.items()}
# # # # #         self.vars_dict = {k: v for k, v in vars_dict.items()}
# # # # #         self.step = step
# # # # #         self.engine = DynamicPipelineEngine()

# # # # #     def run(self):
# # # # #         try:
# # # # #             new_dfs, new_vars = self.engine._apply_step(self.dfs_dict, self.vars_dict, self.step)
# # # # #             self.result_ready.emit(new_dfs, new_vars)
# # # # #         except Exception as e:
# # # # #             self.error_occurred.emit(traceback.format_exc())

# # # # # class PipelineRestoreWorker(QThread):
# # # # #     progress_update = pyqtSignal(str)
# # # # #     result_ready = pyqtSignal(dict, dict)
# # # # #     error_occurred = pyqtSignal(str)

# # # # #     def __init__(self, processes):
# # # # #         super().__init__()
# # # # #         self.processes = processes
# # # # #         self.engine = DynamicPipelineEngine()

# # # # #     def run(self):
# # # # #         dfs_dict = {}
# # # # #         vars_dict = {}
# # # # #         try:
# # # # #             for proc_name, steps in self.processes.items():
# # # # #                 self.progress_update.emit(f"\n--- Running Process: {proc_name} ---")
# # # # #                 for step in steps:
# # # # #                     self.progress_update.emit(f">>> Executing [{step['step_id']}] {step['action']}...")
                    
# # # # #                     original_prompt = step.get('params', {}).get('prompt_at_runtime', False)
# # # # #                     if 'params' in step:
# # # # #                         step['params']['prompt_at_runtime'] = False
                        
# # # # #                     dfs_dict, vars_dict = self.engine._apply_step(dfs_dict, vars_dict, step)
                    
# # # # #                     if 'params' in step:
# # # # #                         step['params']['prompt_at_runtime'] = original_prompt

# # # # #             self.result_ready.emit(dfs_dict, vars_dict)
# # # # #         except Exception as e:
# # # # #             self.error_occurred.emit(traceback.format_exc())

# # # # # class ExcelAnalysisWorker(QThread):
# # # # #     result_ready = pyqtSignal(dict)
# # # # #     error_occurred = pyqtSignal(str)

# # # # #     def __init__(self, file_path):
# # # # #         super().__init__()
# # # # #         self.file_path = file_path

# # # # #     def run(self):
# # # # #         try:
# # # # #             config = analyze_workbook(self.file_path)
# # # # #             self.result_ready.emit(config)
# # # # #         except Exception as e:
# # # # #             self.error_occurred.emit(str(e))

# # # # # class ExportConfigDialog(QDialog):
# # # # #     """Custom Dialog for selecting which DataFrames to export to Excel"""
# # # # #     def __init__(self, all_dfs, selected_dfs, parent=None):
# # # # #         super().__init__(parent)
# # # # #         self.setWindowTitle("Configure Headless Export")
# # # # #         self.resize(450, 500) # Sets a default size allowing space for lists
        
# # # # #         layout = QVBoxLayout(self)
        
# # # # #         if not all_dfs:
# # # # #             layout.addWidget(QLabel("No DataFrames currently available.\nRun the pipeline or load data first."))
# # # # #         else:
# # # # #             header_lbl = QLabel("Select which DataFrames to export to Excel\nduring automated Headless execution:")
# # # # #             header_lbl.setStyleSheet("margin-bottom: 5px;")
# # # # #             layout.addWidget(header_lbl)
            
# # # # #             # Action Buttons for Quick Selection
# # # # #             btn_layout = QHBoxLayout()
# # # # #             btn_select_all = QPushButton("☑ Select All")
# # # # #             btn_select_all.clicked.connect(self.select_all)
# # # # #             btn_deselect_all = QPushButton("☐ Deselect All")
# # # # #             btn_deselect_all.clicked.connect(self.deselect_all)
            
# # # # #             btn_layout.addWidget(btn_select_all)
# # # # #             btn_layout.addWidget(btn_deselect_all)
# # # # #             layout.addLayout(btn_layout)
            
# # # # #             # Scrollable List Widget with Checkboxes
# # # # #             self.list_widget = QListWidget()
# # # # #             self.list_widget.setSelectionMode(QAbstractItemView.NoSelection) # Prevent highlighting, rely purely on checkboxes
            
# # # # #             for df_name in all_dfs:
# # # # #                 item = QListWidgetItem(df_name)
# # # # #                 item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                
# # # # #                 # If selected_dfs is empty but we have dfs, default to checked (fallback)
# # # # #                 if df_name in selected_dfs or (not selected_dfs and df_name in all_dfs):
# # # # #                     item.setCheckState(Qt.Checked)
# # # # #                 else:
# # # # #                     item.setCheckState(Qt.Unchecked)
                    
# # # # #                 self.list_widget.addItem(item)
                
# # # # #             layout.addWidget(self.list_widget)
            
# # # # #         self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
# # # # #         self.buttons.accepted.connect(self.accept)
# # # # #         self.buttons.rejected.connect(self.reject)
# # # # #         layout.addWidget(self.buttons)

# # # # #     def select_all(self):
# # # # #         if hasattr(self, 'list_widget'):
# # # # #             for i in range(self.list_widget.count()):
# # # # #                 self.list_widget.item(i).setCheckState(Qt.Checked)
            
# # # # #     def deselect_all(self):
# # # # #         if hasattr(self, 'list_widget'):
# # # # #             for i in range(self.list_widget.count()):
# # # # #                 self.list_widget.item(i).setCheckState(Qt.Unchecked)

# # # # #     def get_selected(self):
# # # # #         if not hasattr(self, 'list_widget'):
# # # # #             return []
        
# # # # #         selected = []
# # # # #         for i in range(self.list_widget.count()):
# # # # #             item = self.list_widget.item(i)
# # # # #             if item.checkState() == Qt.Checked:
# # # # #                 selected.append(item.text())
# # # # #         return selected

# # # # # class EditLoadDialog(QDialog):
# # # # #     """Custom Dialog for editing an existing 'load_file' step"""
# # # # #     def __init__(self, step_params, active_files=None, parent=None):
# # # # #         super().__init__(parent)
# # # # #         self.active_files = active_files or []
# # # # #         self.setWindowTitle("Edit Load File Step")
# # # # #         self.setMinimumWidth(550)
        
# # # # #         layout = QFormLayout(self)
        
# # # # #         self.filepath_input = QLineEdit(step_params.get("filepath", ""))
        
# # # # #         # File Path Buttons
# # # # #         btn_layout = QHBoxLayout()
# # # # #         btn_layout.setContentsMargins(0, 0, 0, 0)
        
# # # # #         browse_btn = QPushButton("📁 Browse New")
# # # # #         browse_btn.clicked.connect(self.browse)
# # # # #         btn_layout.addWidget(browse_btn)
        
# # # # #         if self.active_files:
# # # # #             active_btn = QPushButton("📄 Select Active File")
# # # # #             active_btn.clicked.connect(self.select_active)
# # # # #             btn_layout.addWidget(active_btn)
            
# # # # #         fp_layout = QVBoxLayout()
# # # # #         fp_layout.setContentsMargins(0, 0, 0, 0)
# # # # #         fp_layout.addWidget(self.filepath_input)
# # # # #         fp_layout.addLayout(btn_layout)
        
# # # # #         layout.addRow("File Path:", fp_layout)
        
# # # # #         # Sheet Selection Layout
# # # # #         self.sheet_input = QLineEdit(str(step_params.get("sheet", 0)))
# # # # #         self.sheet_input.setPlaceholderText("0 for first sheet, or 'Sheet1'")
        
# # # # #         sheet_layout = QHBoxLayout()
# # # # #         sheet_layout.setContentsMargins(0, 0, 0, 0)
# # # # #         sheet_layout.addWidget(self.sheet_input)
        
# # # # #         inspect_btn = QPushButton("🔍 Select Sheet")
# # # # #         inspect_btn.clicked.connect(self.list_sheets)
# # # # #         sheet_layout.addWidget(inspect_btn)
        
# # # # #         layout.addRow("Sheet Name/Index:", sheet_layout)
        
# # # # #         self.alias_input = QLineEdit(step_params.get("alias", ""))
# # # # #         layout.addRow("DataFrame Alias:", self.alias_input)
        
# # # # #         self.header_input = QLineEdit(str(step_params.get("header", 0)))
# # # # #         self.header_input.setPlaceholderText("0 for first row (default)")
# # # # #         layout.addRow("Header Row (Index):", self.header_input)
        
# # # # #         self.prompt_cb = QCheckBox("Prompt user to select this file at runtime (Filepath becomes a placeholder)")
# # # # #         self.prompt_cb.setChecked(step_params.get("prompt_at_runtime", False))
# # # # #         layout.addRow("", self.prompt_cb)
        
# # # # #         self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
# # # # #         self.buttons.accepted.connect(self.accept)
# # # # #         self.buttons.rejected.connect(self.reject)
# # # # #         layout.addRow(self.buttons)

# # # # #     def browse(self):
# # # # #         fp, _ = QFileDialog.getOpenFileName(self, "Select Excel/CSV", "", "Data Files (*.xlsx *.csv)")
# # # # #         if fp:
# # # # #             self.filepath_input.setText(fp)
            
# # # # #     def select_active(self):
# # # # #         if not self.active_files: return
# # # # #         fp, ok = QInputDialog.getItem(self, "Select Active File", "Choose an existing file from the pipeline:", self.active_files, 0, False)
# # # # #         if ok and fp:
# # # # #             self.filepath_input.setText(fp)

# # # # #     def list_sheets(self):
# # # # #         fp = self.filepath_input.text().strip()
# # # # #         if not fp or not os.path.exists(fp):
# # # # #             QMessageBox.warning(self, "File Not Found", "Cannot read sheets. Please ensure the file path is correct and accessible on your machine.")
# # # # #             return
# # # # #         if not fp.endswith(('.xlsx', '.xlsm')):
# # # # #             QMessageBox.information(self, "Not an Excel File", "Only Excel files have multiple sheets to select from.")
# # # # #             return
            
# # # # #         try:
# # # # #             xl = pd.ExcelFile(fp)
# # # # #             sheet, ok = QInputDialog.getItem(self, "Select Sheet", f"Available Sheets in {os.path.basename(fp)}:", xl.sheet_names, 0, False)
# # # # #             if ok and sheet:
# # # # #                 self.sheet_input.setText(sheet)
# # # # #         except Exception as e:
# # # # #             QMessageBox.critical(self, "Error", f"Could not read sheets:\n{e}")

# # # # #     def get_params(self):
# # # # #         sheet_val = self.sheet_input.text()
# # # # #         if sheet_val.isdigit():
# # # # #             sheet_val = int(sheet_val)
            
# # # # #         header_val = 0
# # # # #         if self.header_input.text().isdigit():
# # # # #             header_val = int(self.header_input.text())
            
# # # # #         fp = self.filepath_input.text().strip()
# # # # #         if not fp and self.prompt_cb.isChecked():
# # # # #             fp = "RUNTIME_PROMPT_ONLY.xlsx"
            
# # # # #         return {
# # # # #             "filepath": fp,
# # # # #             "sheet": sheet_val,
# # # # #             "header": header_val,
# # # # #             "alias": self.alias_input.text(),
# # # # #             "prompt_at_runtime": self.prompt_cb.isChecked()
# # # # #         }

# # # # # class ConfigCard(QGroupBox):
# # # # #     """A visually appealing card representing a pipeline configuration"""
# # # # #     edit_requested = pyqtSignal(str)
# # # # #     run_requested = pyqtSignal(str)
# # # # #     delete_requested = pyqtSignal(str)

# # # # #     def __init__(self, file_path, config_data):
# # # # #         title = config_data.get("pipeline_name", os.path.basename(file_path))
# # # # #         super().__init__(title)
# # # # #         self.file_path = file_path
# # # # #         self.setObjectName("ConfigCard")
        
# # # # #         layout = QVBoxLayout(self)
        
# # # # #         # Metadata
# # # # #         proc_count = len(config_data.get("processes", {}))
# # # # #         step_count = sum(len(steps) for steps in config_data.get("processes", {}).values())
        
# # # # #         self.info_lbl = QLabel(f"Processes: {proc_count} | Total Steps: {step_count}")
# # # # #         self.info_lbl.setObjectName("cardMetadata")
# # # # #         layout.addWidget(self.info_lbl)
        
# # # # #         self.path_lbl = QLabel(os.path.basename(file_path))
# # # # #         self.path_lbl.setObjectName("cardPath")
# # # # #         layout.addWidget(self.path_lbl)
        
# # # # #         layout.addStretch()
        
# # # # #         # Action Buttons
# # # # #         btn_layout = QHBoxLayout()
        
# # # # #         self.btn_run = QPushButton("▶ Run")
# # # # #         self.btn_run.setObjectName("btnSuccess")
# # # # #         self.btn_run.clicked.connect(lambda: self.run_requested.emit(self.file_path))
        
# # # # #         self.btn_edit = QPushButton("✏ Edit")
# # # # #         self.btn_edit.setObjectName("btnPrimary")
# # # # #         self.btn_edit.clicked.connect(lambda: self.edit_requested.emit(self.file_path))
        
# # # # #         self.btn_del = QPushButton("🗑")
# # # # #         self.btn_del.setObjectName("btnDanger")
# # # # #         self.btn_del.setFixedWidth(40)
# # # # #         self.btn_del.clicked.connect(lambda: self.delete_requested.emit(self.file_path))
        
# # # # #         btn_layout.addWidget(self.btn_run)
# # # # #         btn_layout.addWidget(self.btn_edit)
# # # # #         btn_layout.addWidget(self.btn_del)
        
# # # # #         layout.addLayout(btn_layout)

# # # # # class DashboardWidget(QWidget):
# # # # #     """The landing screen for the application"""
# # # # #     create_new_requested = pyqtSignal()
# # # # #     auto_generate_requested = pyqtSignal()
# # # # #     edit_config_requested = pyqtSignal(str)
# # # # #     run_config_requested = pyqtSignal(str)

# # # # #     def __init__(self, parent=None):
# # # # #         super().__init__(parent)
# # # # #         self.init_ui()

# # # # #     def init_ui(self):
# # # # #         main_layout = QVBoxLayout(self)
# # # # #         main_layout.setContentsMargins(40, 40, 40, 40)
# # # # #         main_layout.setSpacing(20)
        
# # # # #         # Header
# # # # #         header_layout = QHBoxLayout()
# # # # #         self.title_lbl = QLabel("Dynamic Scorecard System")
# # # # #         self.title_lbl.setObjectName("mainTitle")
# # # # #         header_layout.addWidget(self.title_lbl)
        
# # # # #         header_layout.addStretch()
        
# # # # #         self.btn_new = QPushButton("➕ Create New Configuration")
# # # # #         self.btn_new.setObjectName("btnPrimary")
# # # # #         self.btn_new.setMinimumHeight(50)
# # # # #         self.btn_new.clicked.connect(self.create_new_requested.emit)
# # # # #         header_layout.addWidget(self.btn_new)
        
# # # # #         self.btn_auto = QPushButton("🪄 Auto-Generate from Excel")
# # # # #         self.btn_auto.setObjectName("btnSuccess")
# # # # #         self.btn_auto.setMinimumHeight(50)
# # # # #         self.btn_auto.clicked.connect(self.auto_generate_requested.emit)
# # # # #         header_layout.addWidget(self.btn_auto)
        
# # # # #         self.btn_import_config = QPushButton("📥 Import Config")
# # # # #         self.btn_import_config.setMinimumHeight(50)
# # # # #         self.btn_import_config.clicked.connect(self.import_config)
# # # # #         header_layout.addWidget(self.btn_import_config)
        
# # # # #         self.btn_refresh = QPushButton("🔄 Refresh")
# # # # #         self.btn_refresh.setMinimumHeight(50)
# # # # #         self.btn_refresh.setFixedWidth(120)
# # # # #         self.btn_refresh.clicked.connect(self.refresh_configs)
# # # # #         header_layout.addWidget(self.btn_refresh)
        
# # # # #         main_layout.addLayout(header_layout)
        
# # # # #         # Divider
# # # # #         self.divider = QFrame()
# # # # #         self.divider.setObjectName("mainDivider")
# # # # #         self.divider.setFrameShape(QFrame.HLine)
# # # # #         self.divider.setFrameShadow(QFrame.Sunken)
# # # # #         main_layout.addWidget(self.divider)
        
# # # # #         # Scroll Area for Configs
# # # # #         self.scroll = QScrollArea()
# # # # #         self.scroll.setObjectName("dashboardScroll")
# # # # #         self.scroll.setWidgetResizable(True)
        
# # # # #         self.container = QWidget()
# # # # #         self.container.setObjectName("dashboardContainer")
# # # # #         self.flow_layout = QGridLayout(self.container) # Using grid for card layout
# # # # #         self.flow_layout.setSpacing(20)
        
# # # # #         self.scroll.setWidget(self.container)
# # # # #         main_layout.addWidget(self.scroll)
        
# # # # #         self.refresh_configs()

# # # # #     def import_config(self):
# # # # #         file_path, _ = QFileDialog.getOpenFileName(self, "Select Configuration to Import", "", "JSON Files (*.json)")
# # # # #         if file_path:
# # # # #             config_dir = "Config"
# # # # #             if not os.path.exists(config_dir):
# # # # #                 os.makedirs(config_dir)
# # # # #             dest_path = os.path.join(config_dir, os.path.basename(file_path))
# # # # #             if os.path.abspath(file_path) != os.path.abspath(dest_path):
# # # # #                 try:
# # # # #                     shutil.copy2(file_path, dest_path)
# # # # #                     QMessageBox.information(self, "Success", f"Config imported into application:\n{dest_path}")
# # # # #                     self.refresh_configs()
# # # # #                 except Exception as e:
# # # # #                     QMessageBox.critical(self, "Error", f"Could not import config:\n{e}")

# # # # #     def refresh_configs(self):
# # # # #         # Clear existing
# # # # #         for i in reversed(range(self.flow_layout.count())): 
# # # # #             self.flow_layout.itemAt(i).widget().setParent(None)
            
# # # # #         config_dir = "Config"
# # # # #         if not os.path.exists(config_dir):
# # # # #             os.makedirs(config_dir)
            
# # # # #         configs = [f for f in os.listdir(config_dir) if f.endswith(".json")]
        
# # # # #         if not configs:
# # # # #             empty_lbl = QLabel("No configurations found. Create your first pipeline to get started!")
# # # # #             empty_lbl.setAlignment(Qt.AlignCenter)
# # # # #             empty_lbl.setObjectName("emptyMsg")
# # # # #             self.flow_layout.addWidget(empty_lbl, 0, 0)
# # # # #             return

# # # # #         col_limit = 3
# # # # #         for idx, filename in enumerate(configs):
# # # # #             path = os.path.join(config_dir, filename)
# # # # #             try:
# # # # #                 with open(path, 'r') as f:
# # # # #                     data = json.load(f)
                
# # # # #                 card = ConfigCard(path, data)
# # # # #                 card.edit_requested.connect(self.edit_config_requested.emit)
# # # # #                 card.run_requested.connect(self.run_config_requested.emit)
# # # # #                 card.delete_requested.connect(self.delete_config)
                
# # # # #                 self.flow_layout.addWidget(card, idx // col_limit, idx % col_limit)
# # # # #             except Exception as e:
# # # # #                 print(f"Error loading {filename}: {e}")

# # # # #         col_limit = 3
# # # # #         for idx, filename in enumerate(configs):
# # # # #             path = os.path.join(config_dir, filename)
# # # # #             try:
# # # # #                 with open(path, 'r') as f:
# # # # #                     data = json.load(f)
                
# # # # #                 card = ConfigCard(path, data)
# # # # #                 card.edit_requested.connect(self.edit_config_requested.emit)
# # # # #                 card.run_requested.connect(self.run_config_requested.emit)
# # # # #                 card.delete_requested.connect(self.delete_config)
                
# # # # #                 self.flow_layout.addWidget(card, idx // col_limit, idx % col_limit)
# # # # #             except Exception as e:
# # # # #                 print(f"Error loading {filename}: {e}")

# # # # #     def delete_config(self, path):
# # # # #         reply = QMessageBox.question(self, 'Delete Configuration', 
# # # # #                                      f"Are you sure you want to delete '{os.path.basename(path)}'?\nThis cannot be undone.",
# # # # #                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
# # # # #         if reply == QMessageBox.Yes:
# # # # #             try:
# # # # #                 os.remove(path)
# # # # #                 self.refresh_configs()
# # # # #             except Exception as e:
# # # # #                 QMessageBox.critical(self, "Error", f"Could not delete file: {e}")

# # # # # class ScorecardUI(QMainWindow):
# # # # #     def __init__(self):
# # # # #         super().__init__()
# # # # #         self.setWindowTitle("Dynamic Scorecard System - Dashboard")
# # # # #         self.resize(1600, 1000)
        
# # # # #         self.processes = {"Main_Process": []} 
# # # # #         self.current_process = "Main_Process"
# # # # #         self.export_dfs = [] 
# # # # #         self.current_config_path = None
        
# # # # #         self.global_dfs = {}
# # # # #         self.global_vars = {}
# # # # #         self.preview_dfs = {} 
# # # # #         self.preview_vars = {}
# # # # #         self.pending_step = None 
        
# # # # #         # State Management
# # # # #         self.stacked_widget = QStackedWidget()
# # # # #         self.setCentralWidget(self.stacked_widget)
        
# # # # #         self.init_ui()
# # # # #         self.apply_dark_theme()
        
# # # # #         # Start at Dashboard
# # # # #         self.show_dashboard()

# # # # #     def show_dashboard(self):
# # # # #         self.dashboard.refresh_configs()
# # # # #         self.stacked_widget.setCurrentIndex(0)
# # # # #         self.setWindowTitle("Dynamic Scorecard System - Dashboard")
        
# # # # #         # Hide Editor Docks
# # # # #         self.dock_pipeline.hide()
# # # # #         self.dock_sandbox.hide()
# # # # #         self.dock_terminal.hide()
        
# # # # #     def show_editor(self, config_path=None):
# # # # #         self.stacked_widget.setCurrentIndex(1)
# # # # #         self.dock_pipeline.show()
# # # # #         self.dock_sandbox.show()
# # # # #         self.dock_terminal.show()
        
# # # # #         if config_path:
# # # # #             self.load_config_from_path(config_path)
# # # # #             self.setWindowTitle(f"Pipeline Editor - {os.path.basename(config_path)}")
# # # # #         else:
# # # # #             self.new_config()
# # # # #             self.setWindowTitle("Pipeline Editor - New Configuration")

# # # # #     def new_config(self):
# # # # #         self.processes = {"Main_Process": []}
# # # # #         self.current_process = "Main_Process"
# # # # #         self.export_dfs = []
# # # # #         self.current_config_path = None
# # # # #         self.global_dfs = {}
# # # # #         self.global_vars = {}
# # # # #         self.preview_dfs = {}
# # # # #         self.preview_vars = {}
        
# # # # #         self.combo_processes.blockSignals(True)
# # # # #         self.combo_processes.clear()
# # # # #         self.combo_processes.addItem("Main_Process")
# # # # #         self.combo_processes.blockSignals(False)
        
# # # # #         self.refresh_step_list()
# # # # #         self.update_tabs()

# # # # #     def run_config_from_dashboard(self, path):
# # # # #         export_dir = QFileDialog.getExistingDirectory(self, "Select Export Folder for Final Data")
# # # # #         if not export_dir: return # User cancelled
# # # # #         self.show_editor(path)
# # # # #         self.run_full_restore(export_dir)

# # # # #     def apply_dark_theme(self):
# # # # #         dark_qss = """
# # # # #         QMainWindow, QWidget { 
# # # # #             background-color: #1e1e1e; 
# # # # #             color: #d4d4d4; 
# # # # #             font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; 
# # # # #             font-size: 10pt; 
# # # # #         }
        
# # # # #         /* Dashboard Specifics */
# # # # #         QLabel#mainTitle { font-size: 26pt; font-weight: bold; color: #ffffff; padding-bottom: 5px; }
# # # # #         QLabel#emptyMsg { color: #888888; font-size: 14pt; margin-top: 50px; }
# # # # #         QFrame#mainDivider { background-color: #333333; height: 1px; border: none; }
# # # # #         QScrollArea#dashboardScroll { background-color: transparent; border: none; }
# # # # #         QWidget#dashboardContainer { background-color: transparent; }

# # # # #         /* Config Card Specifics */
# # # # #         QGroupBox#ConfigCard {
# # # # #             background-color: #2d2d30;
# # # # #             border: 2px solid #3e3e42;
# # # # #             border-radius: 12px;
# # # # #             margin-top: 20px;
# # # # #             padding-top: 15px;
# # # # #             font-size: 11pt;
# # # # #         }
# # # # #         QGroupBox#ConfigCard:hover { border: 2px solid #007acc; background-color: #333337; }
# # # # #         QGroupBox#ConfigCard::title {
# # # # #             subcontrol-origin: margin;
# # # # #             subcontrol-position: top left;
# # # # #             left: 15px;
# # # # #             padding: 0 8px;
# # # # #             color: #007acc;
# # # # #             font-weight: bold;
# # # # #         }
# # # # #         QLabel#cardMetadata { color: #a0a0a0; font-size: 9pt; font-weight: 500; }
# # # # #         QLabel#cardPath { color: #666666; font-style: italic; font-size: 8pt; }

# # # # #         /* Editor Specifics */
# # # # #         QDockWidget::title { 
# # # # #             text-align: left; 
# # # # #             background: #252526; 
# # # # #             padding: 8px 12px; 
# # # # #             border-top-left-radius: 8px;
# # # # #             border-top-right-radius: 8px;
# # # # #             font-weight: bold; 
# # # # #             color: #007acc; 
# # # # #         }
# # # # #         QDockWidget { border: 1px solid #333333; border-radius: 12px; }
# # # # #         QGroupBox { 
# # # # #             border: 1px solid #333333; 
# # # # #             border-radius: 10px; 
# # # # #             margin-top: 20px; 
# # # # #             font-weight: bold; 
# # # # #             color: #007acc; 
# # # # #             padding-top: 10px;
# # # # #         }
# # # # #         QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 10px; left: 15px; }
        
# # # # #         QPushButton { 
# # # # #             background-color: #333333; 
# # # # #             color: #ffffff; 
# # # # #             border: 1px solid #444444; 
# # # # #             padding: 10px 18px; 
# # # # #             border-radius: 8px; 
# # # # #             font-weight: 600; 
# # # # #         }
# # # # #         QPushButton:hover { background-color: #404040; border-color: #007acc; }
# # # # #         QPushButton#btnPrimary { background-color: #007acc; border: none; }
# # # # #         QPushButton#btnPrimary:hover { background-color: #1a8ad4; }
# # # # #         QPushButton#btnSuccess { background-color: #2da44e; border: none; }
# # # # #         QPushButton#btnSuccess:hover { background-color: #2cbe4e; }
# # # # #         QPushButton#btnDanger { background-color: #cf222e; border: none; }
        
# # # # #         QLineEdit, QTextEdit, QComboBox { 
# # # # #             background-color: #252526; 
# # # # #             border: 1px solid #3c3c3c; 
# # # # #             border-radius: 8px; 
# # # # #             padding: 8px; 
# # # # #             color: #d4d4d4; 
# # # # #         }
# # # # #         QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border: 2px solid #007acc; background-color: #2d2d30; }
        
# # # # #         QTabWidget::pane { border: 1px solid #333333; border-radius: 10px; background: #1e1e1e; top: -1px; }
# # # # #         QTabBar::tab { 
# # # # #             background: #2d2d30; 
# # # # #             border: 1px solid #333333; 
# # # # #             padding: 10px 20px; 
# # # # #             color: #808080; 
# # # # #             border-top-left-radius: 8px; 
# # # # #             border-top-right-radius: 8px;
# # # # #             margin-right: 4px;
# # # # #         }
# # # # #         QTabBar::tab:selected { background: #1e1e1e; color: #ffffff; border-bottom: 3px solid #007acc; font-weight: bold; }

# # # # #         /* Table & Data Views */
# # # # #         QTableView, QTableWidget {
# # # # #             background-color: #1e1e1e;
# # # # #             gridline-color: #333333;
# # # # #             border: 1px solid #333333;
# # # # #             border-radius: 8px;
# # # # #             color: #d4d4d4;
# # # # #         }
# # # # #         QHeaderView::section {
# # # # #             background-color: #252526;
# # # # #             color: #007acc;
# # # # #             padding: 8px;
# # # # #             border: 1px solid #333333;
# # # # #             font-weight: bold;
# # # # #         }
# # # # #         QHeaderView {
# # # # #             background-color: #1e1e1e;
# # # # #         }
# # # # #         QTableCornerButton::section {
# # # # #             background-color: #252526;
# # # # #             border: 1px solid #333333;
# # # # #         }
# # # # #         QScrollBar:vertical { border: none; background: #1e1e1e; width: 12px; border-radius: 6px; }
# # # # #         QScrollBar::handle:vertical { background: #3e3e42; min-height: 20px; border-radius: 6px; }
# # # # #         QScrollBar::handle:vertical:hover { background: #4e4e52; }
# # # # #         """
# # # # #         self.setStyleSheet(dark_qss)
# # # # #         if hasattr(self, 'terminal_output'):
# # # # #             self.terminal_output.setStyleSheet("background-color: #0a0a0a; border-radius: 10px; color: #4CAF50; padding: 10px; font-family: 'Consolas';")
# # # # #             self.terminal_input.setStyleSheet("background-color: #0a0a0a; border: 1px solid #007acc; border-radius: 8px; color: #FFFFFF; padding: 8px;")
        
# # # # #         if hasattr(self, 'dashboard'):
# # # # #             self.dashboard.setStyleSheet(dark_qss)

# # # # #     def apply_white_theme(self):
# # # # #         white_qss = """
# # # # #         QMainWindow, QWidget { 
# # # # #             background-color: #f8f9fa; 
# # # # #             color: #212529; 
# # # # #             font-family: 'Segoe UI', system-ui, sans-serif; 
# # # # #             font-size: 10pt; 
# # # # #         }
        
# # # # #         /* Dashboard Specifics */
# # # # #         QLabel#mainTitle { font-size: 26pt; font-weight: bold; color: #1a1a1a; padding-bottom: 5px; }
# # # # #         QLabel#emptyMsg { color: #6c757d; font-size: 14pt; margin-top: 50px; }
# # # # #         QFrame#mainDivider { background-color: #dee2e6; height: 1px; border: none; }
# # # # #         QScrollArea#dashboardScroll { background-color: transparent; border: none; }
# # # # #         QWidget#dashboardContainer { background-color: transparent; }

# # # # #         /* Config Card Specifics */
# # # # #         QGroupBox#ConfigCard {
# # # # #             background-color: #ffffff;
# # # # #             border: 1px solid #dee2e6;
# # # # #             border-radius: 12px;
# # # # #             margin-top: 20px;
# # # # #             padding-top: 15px;
# # # # #             font-size: 11pt;
# # # # #         }
# # # # #         QGroupBox#ConfigCard:hover { border: 1px solid #007acc; background-color: #f8f9fa; }
# # # # #         QGroupBox#ConfigCard::title {
# # # # #             subcontrol-origin: margin;
# # # # #             subcontrol-position: top left;
# # # # #             left: 15px;
# # # # #             padding: 0 8px;
# # # # #             color: #007acc;
# # # # #             font-weight: bold;
# # # # #         }
# # # # #         QLabel#cardMetadata { color: #495057; font-size: 9pt; font-weight: 500; }
# # # # #         QLabel#cardPath { color: #6c757d; font-style: italic; font-size: 8pt; }

# # # # #         /* Editor Specifics */
# # # # #         QLabel { color: #212529; }
# # # # #         QDockWidget::title { 
# # # # #             text-align: left; 
# # # # #             background: #ffffff; 
# # # # #             padding: 8px 12px; 
# # # # #             border-top-left-radius: 8px;
# # # # #             border-top-right-radius: 8px;
# # # # #             font-weight: bold; 
# # # # #             color: #007acc; 
# # # # #             border-bottom: 1px solid #e9ecef;
# # # # #         }
# # # # #         QDockWidget { border: 1px solid #dee2e6; border-radius: 12px; background-color: #ffffff; }
# # # # #         QGroupBox { 
# # # # #             border: 1px solid #dee2e6; 
# # # # #             border-radius: 10px; 
# # # # #             margin-top: 20px; 
# # # # #             font-weight: bold; 
# # # # #             color: #007acc; 
# # # # #             background-color: #ffffff;
# # # # #             padding-top: 10px;
# # # # #         }
# # # # #         QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 10px; left: 15px; background-color: #ffffff; color: #007acc; }
        
# # # # #         QPushButton { 
# # # # #             background-color: #ffffff; 
# # # # #             color: #212529; 
# # # # #             border: 1px solid #dee2e6; 
# # # # #             padding: 10px 18px; 
# # # # #             border-radius: 8px; 
# # # # #             font-weight: 600; 
# # # # #         }
# # # # #         QPushButton:hover { background-color: #f1f3f5; border-color: #adb5bd; }
# # # # #         QPushButton#btnPrimary { background-color: #007acc; border: none; color: #ffffff; }
# # # # #         QPushButton#btnPrimary:hover { background-color: #1a8ad4; }
# # # # #         QPushButton#btnSuccess { background-color: #2da44e; border: none; color: #ffffff; }
# # # # #         QPushButton#btnSuccess:hover { background-color: #2cbe4e; }
# # # # #         QPushButton#btnDanger { background-color: #cf222e; border: none; color: #ffffff; }
        
# # # # #         QLineEdit, QTextEdit, QComboBox { 
# # # # #             background-color: #ffffff; 
# # # # #             border: 1px solid #dee2e6; 
# # # # #             border-radius: 8px; 
# # # # #             padding: 8px; 
# # # # #             color: #212529; 
# # # # #         }
# # # # #         QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border: 2px solid #007acc; background-color: #ffffff; }
        
# # # # #         QTabWidget::pane { border: 1px solid #dee2e6; border-radius: 10px; background: #ffffff; top: -1px; }
# # # # #         QTabBar::tab { 
# # # # #             background: #f1f3f5; 
# # # # #             border: 1px solid #dee2e6; 
# # # # #             padding: 10px 20px; 
# # # # #             color: #495057; 
# # # # #             border-top-left-radius: 8px; 
# # # # #             border-top-right-radius: 8px;
# # # # #             margin-right: 4px;
# # # # #         }
# # # # #         QTabBar::tab:selected { background: #ffffff; color: #007acc; border-bottom: 3px solid #007acc; font-weight: bold; }
        
# # # # #         /* Table & Data Views */
# # # # #         QTableView, QTableWidget {
# # # # #             background-color: #ffffff;
# # # # #             gridline-color: #e9ecef;
# # # # #             border: 1px solid #dee2e6;
# # # # #             border-radius: 8px;
# # # # #             color: #212529;
# # # # #         }
# # # # #         QHeaderView::section {
# # # # #             background-color: #f1f3f5;
# # # # #             color: #007acc;
# # # # #             padding: 8px;
# # # # #             border: 1px solid #dee2e6;
# # # # #             font-weight: bold;
# # # # #         }
# # # # #         QHeaderView {
# # # # #             background-color: #ffffff;
# # # # #         }
# # # # #         QTableCornerButton::section {
# # # # #             background-color: #f1f3f5;
# # # # #             border: 1px solid #dee2e6;
# # # # #         }
# # # # #         QScrollBar:vertical { border: none; background: #f8f9fa; width: 12px; border-radius: 6px; }
# # # # #         QScrollBar::handle:vertical { background: #dee2e6; min-height: 20px; border-radius: 6px; }
# # # # #         QScrollBar::handle:vertical:hover { background: #ced4da; }
# # # # #         """
# # # # #         self.setStyleSheet(white_qss)
# # # # #         if hasattr(self, 'terminal_output'):
# # # # #             self.terminal_output.setStyleSheet("background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 10px; color: #1a7f37; padding: 10px; font-family: 'Consolas';")
# # # # #             self.terminal_input.setStyleSheet("background-color: #ffffff; border: 2px solid #007acc; border-radius: 8px; color: #212529; padding: 8px;")
        
# # # # #         if hasattr(self, 'dashboard'):
# # # # #             self.dashboard.setStyleSheet(white_qss)
# # # # #             self.dashboard.refresh_configs()



# # # # #     def init_ui(self):
# # # # #         # --- Dashboard ---
# # # # #         self.dashboard = DashboardWidget()
# # # # #         self.dashboard.create_new_requested.connect(lambda: self.show_editor())
# # # # #         self.dashboard.auto_generate_requested.connect(self.auto_generate_pipeline)
# # # # #         self.dashboard.edit_config_requested.connect(lambda p: self.show_editor(p))
# # # # #         self.dashboard.run_config_requested.connect(self.run_config_from_dashboard)
# # # # #         self.stacked_widget.addWidget(self.dashboard)

# # # # #         # --- Menu Bar ---
# # # # #         menubar = self.menuBar()
# # # # #         file_menu = menubar.addMenu('File')

# # # # #         back_action = QAction('🔙 Back to Dashboard', self)
# # # # #         back_action.triggered.connect(lambda: self.show_dashboard())
# # # # #         file_menu.addAction(back_action)
# # # # #         file_menu.addSeparator()

# # # # #         load_conf_action = QAction('Load Pipeline Config', self)
# # # # #         load_conf_action.triggered.connect(lambda: self.load_config())
# # # # #         file_menu.addAction(load_conf_action)

# # # # #         save_conf_action = QAction('Save Pipeline Config', self)
# # # # #         save_conf_action.triggered.connect(lambda: self.save_config())
# # # # #         file_menu.addAction(save_conf_action)

# # # # #         view_menu = menubar.addMenu('View')
# # # # #         self.dock_menu = view_menu.addMenu('Panels')

# # # # #         theme_menu = view_menu.addMenu('Theme')
# # # # #         dark_action = QAction('Dark Mode', self)
# # # # #         dark_action.triggered.connect(lambda: self.apply_dark_theme())
# # # # #         theme_menu.addAction(dark_action)

# # # # #         white_action = QAction('White Mode', self)
# # # # #         white_action.triggered.connect(lambda: self.apply_white_theme())
# # # # #         theme_menu.addAction(white_action)

# # # # #         # --- Editor Central Widget ---
# # # # #         self.editor_central = QWidget()
# # # # #         editor_main_layout = QVBoxLayout(self.editor_central)

# # # # #         # Top Header (Context info)
# # # # #         context_layout = QHBoxLayout()
# # # # #         self.lbl_context = QLabel("Context Available: DFs (0) | Vars (0)")
# # # # #         self.lbl_context.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 11pt;")
# # # # #         context_layout.addWidget(self.lbl_context)

# # # # #         self.combo_view = QComboBox()
# # # # #         self.combo_view.setFixedWidth(280)
# # # # #         self.combo_view.setPlaceholderText("Select a DataFrame to View...")
# # # # #         self.combo_view.currentIndexChanged.connect(self.on_view_combo_changed)
# # # # #         context_layout.addWidget(self.combo_view)
# # # # #         editor_main_layout.addLayout(context_layout)

# # # # #         # Splitter to allow resizing without jumping
# # # # #         self.central_splitter = QSplitter(Qt.Vertical)
        
# # # # #         # Tabs (Data View)
# # # # #         self.tabs = QTabWidget()
# # # # #         self.tabs.setUsesScrollButtons(True) 
# # # # #         self.tabs.currentChanged.connect(self.on_tab_changed)
# # # # #         self.central_splitter.addWidget(self.tabs)

# # # # #         editor_main_layout.addWidget(self.central_splitter)

# # # # #         self.stacked_widget.addWidget(self.editor_central)

# # # # #         # --- Dock 1: Pipeline Controls (Left) ---
# # # # #         self.dock_pipeline = QDockWidget("Pipeline & Steps", self)
# # # # #         self.dock_pipeline.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

# # # # #         pipeline_widget = QWidget()
# # # # #         left_panel = QVBoxLayout(pipeline_widget)

# # # # #         process_layout = QHBoxLayout()
# # # # #         self.combo_processes = QComboBox()
# # # # #         self.combo_processes.addItem("Main_Process")
# # # # #         self.combo_processes.currentTextChanged.connect(self.switch_process)
# # # # #         process_layout.addWidget(self.combo_processes)

# # # # #         btn_add_process = QPushButton("➕")
# # # # #         btn_add_process.setFixedWidth(35)
# # # # #         btn_add_process.clicked.connect(self.add_process)
# # # # #         process_layout.addWidget(btn_add_process)

# # # # #         btn_del_process = QPushButton("🗑️")
# # # # #         btn_del_process.setFixedWidth(35)
# # # # #         btn_del_process.clicked.connect(self.delete_process)
# # # # #         process_layout.addWidget(btn_del_process)

# # # # #         left_panel.addLayout(process_layout)

# # # # #         btn_load = QPushButton("📥 Load Source Data")
# # # # #         btn_load.setObjectName("btnPrimary")
# # # # #         btn_load.clicked.connect(self.load_data)
# # # # #         left_panel.addWidget(btn_load)

# # # # #         btn_load_existing = QPushButton("📄 Load Another Sheet")
# # # # #         btn_load_existing.setObjectName("btnPrimary")
# # # # #         btn_load_existing.clicked.connect(self.load_existing_file_data)
# # # # #         left_panel.addWidget(btn_load_existing)

# # # # #         self.list_steps = QListWidget()
# # # # #         self.list_steps.itemClicked.connect(self.load_step_into_editor)
# # # # #         left_panel.addWidget(self.list_steps)

# # # # #         btn_restore = QPushButton("▶️ Run Pipeline")
# # # # #         btn_restore.setObjectName("btnPurple")
# # # # #         btn_restore.clicked.connect(self.run_full_restore)
# # # # #         left_panel.addWidget(btn_restore)

# # # # #         btn_export_config = QPushButton("⚙️ Export Config")
# # # # #         btn_export_config.setObjectName("btnGray")
# # # # #         btn_export_config.clicked.connect(self.configure_export)
# # # # #         left_panel.addWidget(btn_export_config)

# # # # #         self.dock_pipeline.setWidget(pipeline_widget)
# # # # #         self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_pipeline)
# # # # #         self.dock_menu.addAction(self.dock_pipeline.toggleViewAction())

# # # # #         # --- Dock 2: Python Action Sandbox (Bottom/Right) ---
# # # # #         self.dock_sandbox = QDockWidget("Logic Editor & Sandbox", self)

# # # # #         sandbox_group = QGroupBox()
# # # # #         sandbox_layout = QVBoxLayout(sandbox_group)

# # # # #         self.combo_action = QComboBox()
# # # # #         self.combo_action.addItems([
# # # # #             "Execute Raw Python/Pandas", 
# # # # #             "Evaluate Excel Formula (Native Math)",
# # # # #             "Run External .py Script (Entire File)"
# # # # #         ])
# # # # #         self.combo_action.currentIndexChanged.connect(self.toggle_inputs)
# # # # #         sandbox_layout.addWidget(self.combo_action)

# # # # #         code_font = QFont("Consolas", 11)
# # # # #         self.txt_python = QTextEdit()
# # # # #         self.txt_python.setFont(code_font)
# # # # #         self.txt_python.setPlaceholderText("Write Python/Pandas logic here...")
# # # # #         self.txt_python.setMinimumSize(0, 0) # Allow shrinking
# # # # #         sandbox_layout.addWidget(self.txt_python)

# # # # #         # Excel Formula Inputs
# # # # #         self.widget_excel_formula = QWidget()
# # # # #         excel_layout = QVBoxLayout(self.widget_excel_formula)
# # # # #         excel_layout.setContentsMargins(0, 0, 0, 0)

# # # # #         self.txt_excel_formula = QTextEdit()
# # # # #         self.txt_excel_formula.setFont(code_font)
# # # # #         self.txt_excel_formula.setPlaceholderText("Enter Excel Formula (e.g., =SUM(Sheet1!A:A))")
# # # # #         self.txt_excel_formula.setMaximumHeight(150)
# # # # #         self.txt_excel_formula.setMinimumSize(0, 0)
# # # # #         excel_layout.addWidget(self.txt_excel_formula)

# # # # #         self.txt_excel_target = QLineEdit()
# # # # #         self.txt_excel_target.setPlaceholderText("Target DataFrame Alias (e.g., Master)")
# # # # #         excel_layout.addWidget(self.txt_excel_target)

# # # # #         self.txt_excel_column = QLineEdit()
# # # # #         self.txt_excel_column.setPlaceholderText("Target Column (Optional - e.g., Price)")
# # # # #         excel_layout.addWidget(self.txt_excel_column)

# # # # #         self.widget_excel_formula.hide()
# # # # #         sandbox_layout.addWidget(self.widget_excel_formula)

# # # # #         self.widget_script_path = QWidget()
# # # # #         script_path_layout = QHBoxLayout(self.widget_script_path)
# # # # #         script_path_layout.setContentsMargins(0, 0, 0, 0)
# # # # #         self.txt_script_path = QLineEdit()
# # # # #         self.btn_browse_script = QPushButton("📁")
# # # # #         self.btn_browse_script.clicked.connect(self.browse_script)
# # # # #         script_path_layout.addWidget(self.txt_script_path)
# # # # #         script_path_layout.addWidget(self.btn_browse_script)
# # # # #         self.widget_script_path.hide()
# # # # #         sandbox_layout.addWidget(self.widget_script_path)

# # # # #         btn_layout = QHBoxLayout()
# # # # #         btn_test = QPushButton("🧪 Test")
# # # # #         btn_test.clicked.connect(self.test_step)
# # # # #         btn_layout.addWidget(btn_test)

# # # # #         btn_record = QPushButton("✅ Record")
# # # # #         btn_record.setObjectName("btnSuccess")
# # # # #         btn_record.clicked.connect(self.record_step)
# # # # #         btn_layout.addWidget(btn_record)

# # # # #         btn_update = QPushButton("🔄 Update")
# # # # #         btn_update.setObjectName("btnWarning")
# # # # #         btn_update.clicked.connect(self.update_selected_step)
# # # # #         btn_layout.addWidget(btn_update)

# # # # #         btn_del_step = QPushButton("🗑️ Delete")
# # # # #         btn_del_step.setObjectName("btnDanger")
# # # # #         btn_del_step.clicked.connect(self.delete_step)
# # # # #         btn_layout.addWidget(btn_del_step)

# # # # #         sandbox_layout.addLayout(btn_layout)
# # # # #         self.dock_sandbox.setWidget(sandbox_group)
# # # # #         self.addDockWidget(Qt.RightDockWidgetArea, self.dock_sandbox)
# # # # #         self.dock_menu.addAction(self.dock_sandbox.toggleViewAction())

# # # # #         # --- Dock 3: Terminal (Bottom) ---
# # # # #         self.dock_terminal = QDockWidget("Interactive Terminal REPL", self)
# # # # #         term_widget = QWidget()
# # # # #         term_layout = QVBoxLayout(term_widget)

# # # # #         self.terminal_output = QTextEdit()
# # # # #         self.terminal_output.setFont(code_font)
# # # # #         self.terminal_output.setReadOnly(True)
# # # # #         self.terminal_output.setMinimumSize(0, 0) # Allow shrinking

# # # # #         self.terminal_input = TerminalInput()
# # # # #         self.terminal_input.setFont(code_font)
# # # # #         self.terminal_input.setPlaceholderText(">>> Type Python command and press Enter (Use Arrows for History)")
# # # # #         self.terminal_input.returnPressed.connect(self.execute_terminal_command)

# # # # #         term_layout.addWidget(self.terminal_output)
# # # # #         term_layout.addWidget(self.terminal_input)
# # # # #         self.dock_terminal.setWidget(term_widget)
# # # # #         self.dock_terminal.setMinimumSize(0, 0)
# # # # #         self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_terminal)
# # # # #         self.dock_menu.addAction(self.dock_terminal.toggleViewAction())

# # # # #         self.update_tabs()

# # # # #     def auto_generate_pipeline(self):
# # # # #         if analyze_workbook is None:
# # # # #             QMessageBox.critical(self, "Error", "xlwings is required for Auto-Generation. Please run 'pip install xlwings'.")
# # # # #             return

# # # # #         file_path, _ = QFileDialog.getOpenFileName(self, "Select Excel to Reverse-Engineer", "", "Excel Files (*.xlsx *.xlsm)")
# # # # #         if not file_path: return

# # # # #         # Show a "please wait" message because COM automation can be slow
# # # # #         self.analysis_msg = QMessageBox(self)
# # # # #         self.analysis_msg.setWindowTitle("Working...")
# # # # #         self.analysis_msg.setText("🔍 Analyzing workbook structure and formulas...\nPlease wait, this may take a moment.")
# # # # #         self.analysis_msg.setStandardButtons(QMessageBox.NoButton)
# # # # #         self.analysis_msg.show()

# # # # #         self.analysis_worker = ExcelAnalysisWorker(file_path)
# # # # #         self.analysis_worker.result_ready.connect(self.on_analysis_success)
# # # # #         self.analysis_worker.error_occurred.connect(self.on_analysis_error)
# # # # #         self.analysis_worker.start()

# # # # #     def on_analysis_success(self, config):
# # # # #         if hasattr(self, 'analysis_msg'):
# # # # #             self.analysis_msg.done(0)
# # # # #             self.analysis_msg.close()
        
# # # # #         QApplication.processEvents()
        
# # # # #         # Save the new config automatically
# # # # #         config_dir = "Config"
# # # # #         if not os.path.exists(config_dir): os.makedirs(config_dir)

# # # # #         save_path = os.path.join(config_dir, f"{config['pipeline_name']}.json")
# # # # #         with open(save_path, 'w') as f:
# # # # #             json.dump(config, f, indent=4)

# # # # #         QMessageBox.information(self, "Success", f"Pipeline successfully generated from Excel!\n\nSaved to: {save_path}\n\nAny unsupported features (like Pivot Tables) have been marked as TODO steps for you to fix.")
# # # # #         self.show_editor(save_path)

# # # # #     def on_analysis_error(self, err_msg):
# # # # #         if hasattr(self, 'analysis_msg'):
# # # # #             self.analysis_msg.done(0)
# # # # #             self.analysis_msg.close()
        
# # # # #         QApplication.processEvents()
# # # # #         QMessageBox.critical(self, "Reverse Engineering Error", f"Failed to analyze workbook:\n{err_msg}")

# # # # #     def on_view_combo_changed(self, idx):
# # # # #         if idx >= 0 and idx < self.tabs.count():
# # # # #             self.tabs.blockSignals(True)
# # # # #             self.tabs.setCurrentIndex(idx)
# # # # #             self.tabs.blockSignals(False)

# # # # #     def on_tab_changed(self, idx):
# # # # #         if idx >= 0 and idx < self.combo_view.count():
# # # # #             self.combo_view.blockSignals(True)
# # # # #             self.combo_view.setCurrentIndex(idx)
# # # # #             self.combo_view.blockSignals(False)

# # # # #     def configure_export(self):
# # # # #         pipeline_dfs = set()
# # # # #         for proc in self.processes.values():
# # # # #             for step in proc:
# # # # #                 if step["action"] == "load_file":
# # # # #                     pipeline_dfs.add(step["params"].get("alias"))
        
# # # # #         all_possible = sorted(list(set(self.global_dfs.keys()) | pipeline_dfs | set(self.export_dfs)))
        
# # # # #         dlg = ExportConfigDialog(all_possible, self.export_dfs, self)
# # # # #         if dlg.exec_() == QDialog.Accepted:
# # # # #             self.export_dfs = dlg.get_selected()
# # # # #             QMessageBox.information(self, "Saved", f"Export configuration updated.\n\n{len(self.export_dfs)} DataFrames will be written to Excel in headless mode.")

# # # # #     def browse_script(self):
# # # # #         file_path, _ = QFileDialog.getOpenFileName(self, "Select Python Script", "", "Python Files (*.py);;All Files (*)")
# # # # #         if file_path:
# # # # #             # Task 2: Copy to Custom_Scripts
# # # # #             custom_dir = "Custom_Scripts"
# # # # #             if not os.path.exists(custom_dir):
# # # # #                 os.makedirs(custom_dir)
            
# # # # #             dest_path = os.path.join(custom_dir, os.path.basename(file_path))
            
# # # # #             # Check if source and dest are different
# # # # #             if os.path.abspath(file_path) != os.path.abspath(dest_path):
# # # # #                 try:
# # # # #                     shutil.copy2(file_path, dest_path)
# # # # #                     if hasattr(self, 'terminal_output'):
# # # # #                         self.terminal_output.append(f"\n>>> Copied external script to local project: {dest_path}")
# # # # #                 except Exception as e:
# # # # #                     QMessageBox.warning(self, "Copy Error", f"Could not copy script to Custom_Scripts:\n{e}")
            
# # # # #             self.txt_script_path.setText(dest_path)

# # # # #     def execute_terminal_command(self):
# # # # #         cmd = self.terminal_input.text()
# # # # #         if not cmd.strip(): return
        
# # # # #         self.terminal_input.add_to_history(cmd)
# # # # #         self.terminal_output.append(f"\n>>> {cmd}")
# # # # #         self.terminal_input.clear()
        
# # # # #         env = {**self.preview_dfs, **self.preview_vars, 'pd': pd, 'np': np, 'os': os, 'prompt_file': prompt_file}
# # # # #         output = io.StringIO()
# # # # #         ui_needs_update = False
        
# # # # #         with contextlib.redirect_stdout(output):
# # # # #             try:
# # # # #                 res = eval(cmd, {}, env)
# # # # #                 if res is not None:
# # # # #                     print(res)
# # # # #             except SyntaxError:
# # # # #                 try:
# # # # #                     exec(cmd, env, env)
# # # # #                     ui_needs_update = True
# # # # #                 except Exception as e:
# # # # #                     print(f"Error: {e}")
# # # # #             except Exception as e:
# # # # #                 print(f"Error: {e}")
                
# # # # #         result_text = output.getvalue().strip()
# # # # #         if result_text:
# # # # #             self.terminal_output.append(result_text)
            
# # # # #         scrollbar = self.terminal_output.verticalScrollBar()
# # # # #         scrollbar.setValue(scrollbar.maximum())
        
# # # # #         if ui_needs_update:
# # # # #             self.preview_dfs = {k: v for k, v in env.items() if isinstance(v, pd.DataFrame)}
# # # # #             self.preview_vars = {k: v for k, v in env.items() if not isinstance(v, pd.DataFrame) and not callable(v) and not k.startswith('_') and str(type(v).__module__) == 'builtins'}
# # # # #             self.update_tabs()

# # # # #     def add_process(self):
# # # # #         name, ok = QInputDialog.getText(self, "New Process", "Enter name for new Pipeline/Process:")
# # # # #         if ok and name.strip() and name not in self.processes:
# # # # #             self.processes[name.strip()] = []
# # # # #             self.combo_processes.addItem(name.strip())
# # # # #             self.combo_processes.setCurrentText(name.strip())

# # # # #     def delete_process(self):
# # # # #         if len(self.processes) <= 1:
# # # # #             QMessageBox.warning(self, "Cannot Delete", "You must have at least one active process.")
# # # # #             return
            
# # # # #         reply = QMessageBox.question(self, 'Delete Process', f"Are you sure you want to delete '{self.current_process}' and all its steps?",
# # # # #                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
# # # # #         if reply == QMessageBox.Yes:
# # # # #             del self.processes[self.current_process]
# # # # #             idx = self.combo_processes.currentIndex()
# # # # #             self.combo_processes.removeItem(idx)

# # # # #     def switch_process(self, process_name):
# # # # #         if not process_name: return
# # # # #         self.current_process = process_name
# # # # #         self.refresh_step_list()

# # # # #     def refresh_step_list(self):
# # # # #         self.list_steps.clear()
# # # # #         if self.current_process in self.processes:
# # # # #             for step in self.processes[self.current_process]:
# # # # #                 prompt_flag = " [Prompt at Runtime]" if step.get('params', {}).get('prompt_at_runtime') else ""
# # # # #                 self.list_steps.addItem(f"[{step['step_id']}] {step['action']}{prompt_flag}")

# # # # #     def toggle_inputs(self):
# # # # #         action = self.combo_action.currentText()
# # # # #         self.txt_python.setVisible(action == "Execute Raw Python/Pandas")
# # # # #         self.widget_excel_formula.setVisible("Excel Formula" in action)
# # # # #         self.widget_script_path.setVisible("External" in action)

# # # # #     def load_data(self):
# # # # #         file_path, _ = QFileDialog.getOpenFileName(self, "Select Excel/CSV", "", "Data Files (*.xlsx *.csv)")
# # # # #         if not file_path: return

# # # # #         sheet_name = 0
# # # # #         if file_path.endswith('.xlsx'):
# # # # #             try:
# # # # #                 xl = pd.ExcelFile(file_path)
# # # # #                 sheet_name, ok = QInputDialog.getItem(self, "Select Sheet", "Select sheet:", xl.sheet_names, 0, False)
# # # # #                 if not ok: return
# # # # #             except Exception as e:
# # # # #                 QMessageBox.critical(self, "Error", str(e))
# # # # #                 return

# # # # #         alias, ok = QInputDialog.getText(self, "DataFrame Alias", "Variable name (e.g. df1):")
# # # # #         if not ok or not alias.strip(): return
# # # # #         alias = alias.strip()

# # # # #         reply = QMessageBox.question(self, 'Dynamic Input',
# # # # #                                      f"When this pipeline runs automatically in the future, should it STOP and prompt the user to select the file for '{alias}'?",
# # # # #                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
# # # # #         prompt_at_runtime = (reply == QMessageBox.Yes)

# # # # #         try:
# # # # #             df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path, sheet_name=sheet_name)
            
# # # # #             self.global_dfs[alias] = df
# # # # #             self.preview_dfs = self.global_dfs.copy()
# # # # #             self.update_tabs()
            
# # # # #             step = {
# # # # #                 "step_id": len(self.processes[self.current_process]) + 1,
# # # # #                 "action": "load_file",
# # # # #                 "params": {"filepath": file_path, "sheet": sheet_name, "alias": alias, "prompt_at_runtime": prompt_at_runtime}
# # # # #             }
# # # # #             self.processes[self.current_process].append(step)
# # # # #             self.refresh_step_list()
            
# # # # #         except Exception as e:
# # # # #             QMessageBox.critical(self, "Error", str(e))

# # # # #     def load_existing_file_data(self):
# # # # #         active_files = set()
# # # # #         for proc in self.processes.values():
# # # # #             for step in proc:
# # # # #                 if step.get("action") == "load_file":
# # # # #                     fp = step.get("params", {}).get("filepath")
# # # # #                     if fp and fp.endswith(('.xlsx', '.xlsm')):
# # # # #                         active_files.add(fp)
        
# # # # #         if not active_files:
# # # # #             QMessageBox.information(self, "No Active Files", "No Excel files are currently loaded.")
# # # # #             return
            
# # # # #         file_path, ok = QInputDialog.getItem(self, "Select Existing File", "Choose an Excel file:", list(active_files), 0, False)
# # # # #         if not ok: return
        
# # # # #         try:
# # # # #             xl = pd.ExcelFile(file_path)
# # # # #             sheet_name, ok = QInputDialog.getItem(self, "Select Sheet", f"Select sheet:", xl.sheet_names, 0, False)
# # # # #             if not ok: return
# # # # #         except Exception as e:
# # # # #             QMessageBox.critical(self, "Error", f"Could not read file: {e}")
# # # # #             return
            
# # # # #         alias, ok = QInputDialog.getText(self, "DataFrame Alias", "Variable name:")
# # # # #         if not ok or not alias.strip(): return
# # # # #         alias = alias.strip()

# # # # #         reply = QMessageBox.question(self, 'Dynamic Input',
# # # # #                                      f"Prompt user to select file for '{alias}'?",
# # # # #                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
# # # # #         prompt_at_runtime = (reply == QMessageBox.Yes)

# # # # #         try:
# # # # #             df = pd.read_excel(file_path, sheet_name=sheet_name)
# # # # #             self.global_dfs[alias] = df
# # # # #             self.preview_dfs = self.global_dfs.copy()
# # # # #             self.update_tabs()
            
# # # # #             step = {
# # # # #                 "step_id": len(self.processes[self.current_process]) + 1,
# # # # #                 "action": "load_file",
# # # # #                 "params": {"filepath": file_path, "sheet": sheet_name, "alias": alias, "prompt_at_runtime": prompt_at_runtime}
# # # # #             }
# # # # #             self.processes[self.current_process].append(step)
# # # # #             self.refresh_step_list()
# # # # #         except Exception as e:
# # # # #             QMessageBox.critical(self, "Error", str(e))

# # # # #     def update_tabs(self):
# # # # #         self.tabs.clear()
# # # # #         self.combo_view.blockSignals(True)
# # # # #         self.combo_view.clear()
        
# # # # #         var_table = QTableWidget(len(self.preview_vars), 3)
# # # # #         var_table.setHorizontalHeaderLabels(["Variable Name", "Type", "Value"])
# # # # #         var_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
# # # # #         var_table.verticalHeader().setVisible(False)
        
# # # # #         row = 0
# # # # #         for k, v in self.preview_vars.items():
# # # # #             var_table.setItem(row, 0, QTableWidgetItem(str(k)))
# # # # #             var_table.setItem(row, 1, QTableWidgetItem(type(v).__name__))
# # # # #             var_table.setItem(row, 2, QTableWidgetItem(str(v)[:100]))
# # # # #             row += 1
            
# # # # #         self.tabs.addTab(var_table, "📦 Variables Explorer")
# # # # #         self.combo_view.addItem("📦 Variables Explorer")

# # # # #         for alias, df in self.preview_dfs.items():
# # # # #             table = QTableView()
# # # # #             table.setModel(PandasModel(df))
# # # # #             table.verticalHeader().setVisible(False)
# # # # #             table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
# # # # #             table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
# # # # #             table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
# # # # #             table.horizontalHeader().setDefaultSectionSize(120)
            
# # # # #             self.tabs.addTab(table, f"📊 DF: {alias}")
# # # # #             self.combo_view.addItem(f"📊 DF: {alias}")
            
# # # # #         self.combo_view.blockSignals(False)
# # # # #         self.lbl_context.setText(f"Context: DFs ({len(self.preview_dfs)}) | Vars ({len(self.preview_vars)})")

# # # # #     def get_editor_step_data(self):
# # # # #         action_type = self.combo_action.currentText()
# # # # #         step = {"action": ""}
# # # # #         if action_type == "Execute Raw Python/Pandas":
# # # # #             step["action"] = "execute_python_logic"
# # # # #             step["params"] = {"code_block": self.txt_python.toPlainText()}
# # # # #         elif action_type == "Evaluate Excel Formula (Native Math)":
# # # # #             step["action"] = "evaluate_excel_formula"
# # # # #             step["params"] = {
# # # # #                 "formula": self.txt_excel_formula.toPlainText(),
# # # # #                 "target_alias": self.txt_excel_target.text(),
# # # # #                 "target_col": self.txt_excel_column.text() if self.txt_excel_column.text().strip() else None
# # # # #             }
# # # # #         elif action_type == "Run External .py Script (Entire File)":
# # # # #             step["action"] = "run_python_file"
# # # # #             step["params"] = {"script_path": self.txt_script_path.text()}
# # # # #         return step

# # # # #     def test_step(self):
# # # # #         step = self.get_editor_step_data()
# # # # #         if not step["params"].get("code_block") and step["action"] == "execute_python_logic": return
        
# # # # #         self.pending_step = step
# # # # #         self.worker = StepPreviewWorker(self.global_dfs, self.global_vars, step)
# # # # #         self.worker.result_ready.connect(self.on_test_success)
# # # # #         self.worker.error_occurred.connect(self.on_test_error)
# # # # #         self.worker.start()

# # # # #     def on_test_success(self, new_dfs, new_vars):
# # # # #         self.preview_dfs = new_dfs
# # # # #         self.preview_vars = new_vars
# # # # #         self.update_tabs()
# # # # #         QMessageBox.information(self, "Test Passed", "Code executed!")

# # # # #     def on_test_error(self, err_msg):
# # # # #         QMessageBox.critical(self, "Logic Error", f"Failed to execute:\n\n{err_msg}")

# # # # #     def record_step(self):
# # # # #         if not self.pending_step: return
# # # # #         self.global_dfs = self.preview_dfs.copy()
# # # # #         self.global_vars = self.preview_vars.copy()
# # # # #         self.pending_step["step_id"] = len(self.processes[self.current_process]) + 1
# # # # #         self.processes[self.current_process].append(self.pending_step)
# # # # #         self.refresh_step_list()
# # # # #         self.pending_step = None

# # # # #     def load_step_into_editor(self, item):
# # # # #         row_idx = self.list_steps.row(item)
# # # # #         step = self.processes[self.current_process][row_idx]
        
# # # # #         if step["action"] == "execute_python_logic":
# # # # #             self.combo_action.setCurrentText("Execute Raw Python/Pandas")
# # # # #             self.txt_python.setPlainText(step["params"].get("code_block", ""))
# # # # #         elif step["action"] == "evaluate_excel_formula":
# # # # #             self.combo_action.setCurrentText("Evaluate Excel Formula (Native Math)")
# # # # #             self.txt_excel_formula.setPlainText(step["params"].get("formula", ""))
# # # # #             self.txt_excel_target.setText(step["params"].get("target_alias", ""))
# # # # #             self.txt_excel_column.setText(step["params"].get("target_col", ""))
# # # # #         elif step["action"] == "run_python_file":
# # # # #             self.combo_action.setCurrentText("Run External .py Script (Entire File)")
# # # # #             self.txt_script_path.setText(step["params"].get("script_path", ""))

# # # # #     def update_selected_step(self):
# # # # #         current_item = self.list_steps.currentItem()
# # # # #         if not current_item: return
# # # # #         row_idx = self.list_steps.row(current_item)
# # # # #         original_step = self.processes[self.current_process][row_idx]
        
# # # # #         if original_step["action"] == "load_file":
# # # # #             active_files = set()
# # # # #             for proc in self.processes.values():
# # # # #                 for s in proc:
# # # # #                     if s.get("action") == "load_file":
# # # # #                         fp = s.get("params", {}).get("filepath")
# # # # #                         if fp: active_files.add(fp)
# # # # #             dialog = EditLoadDialog(original_step.get("params", {}), list(active_files), self)
# # # # #             if dialog.exec_() == QDialog.Accepted:
# # # # #                 original_step["params"] = dialog.get_params()
# # # # #                 self.processes[self.current_process][row_idx] = original_step
# # # # #                 self.refresh_step_list()
# # # # #             return
            
# # # # #         new_step_data = self.get_editor_step_data()
# # # # #         new_step_data["step_id"] = original_step["step_id"]
# # # # #         self.processes[self.current_process][row_idx] = new_step_data
# # # # #         self.refresh_step_list()

# # # # #     def delete_step(self):
# # # # #         current_item = self.list_steps.currentItem()
# # # # #         if not current_item: return
# # # # #         row_idx = self.list_steps.row(current_item)
# # # # #         if QMessageBox.question(self, 'Delete', "Delete this step?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
# # # # #             del self.processes[self.current_process][row_idx]
# # # # #             for i, step in enumerate(self.processes[self.current_process]):
# # # # #                 step["step_id"] = i + 1
# # # # #             self.refresh_step_list()

# # # # #     def run_full_restore(self, export_path=None):
# # # # #         if not any(self.processes.values()): return
# # # # #         self.last_export_path = export_path
# # # # #         self.terminal_output.append("\n>>> Restoring Pipeline Data...")
# # # # #         self.restore_worker = PipelineRestoreWorker(self.processes)
# # # # #         self.restore_worker.progress_update.connect(self.terminal_output.append)
# # # # #         self.restore_worker.result_ready.connect(self.on_restore_success)
# # # # #         self.restore_worker.error_occurred.connect(self.on_restore_error)
# # # # #         self.restore_worker.start()

# # # # #     def on_restore_success(self, dfs, vars):
# # # # #         self.global_dfs, self.global_vars = dfs.copy(), vars.copy()
# # # # #         self.preview_dfs, self.preview_vars = dfs.copy(), vars.copy()
# # # # #         self.update_tabs()
# # # # #         self.terminal_output.append(">>> Success!")
        
# # # # #         if hasattr(self, 'last_export_path') and self.last_export_path:
# # # # #             self.terminal_output.append(f">>> Exporting results to: {self.last_export_path}")
# # # # #             try:
# # # # #                 output_file = os.path.join(self.last_export_path, 'Final_Pipeline_Output.xlsx')
# # # # #                 with pd.ExcelWriter(output_file) as writer:
# # # # #                     exported_count = 0
# # # # #                     for alias, df in dfs.items():
# # # # #                         if not self.export_dfs or alias in self.export_dfs:
# # # # #                             df.to_excel(writer, sheet_name=str(alias)[:31], index=False)
# # # # #                             exported_count += 1
# # # # #                 self.terminal_output.append(f">>> Export Complete: {exported_count} DataFrames saved.")
# # # # #             except Exception as e:
# # # # #                 self.terminal_output.append(f">>> Export Error: {e}")
# # # # #             self.last_export_path = None

# # # # #     def on_restore_error(self, err):
# # # # #         self.terminal_output.append(f">>> Error: {err}")

# # # # #     def load_config_from_path(self, file_path):
# # # # #         try:
# # # # #             with open(file_path, 'r') as f:
# # # # #                 config = json.load(f)
# # # # #             self.processes = config["processes"]
# # # # #             self.export_dfs = config.get("export_dfs", [])
# # # # #             self.current_config_path = file_path
            
# # # # #             self.combo_processes.blockSignals(True)
# # # # #             self.combo_processes.clear()
# # # # #             for n in self.processes.keys():
# # # # #                 self.combo_processes.addItem(n)
# # # # #             self.current_process = list(self.processes.keys())[0]
# # # # #             self.combo_processes.setCurrentText(self.current_process)
# # # # #             self.combo_processes.blockSignals(False)
            
# # # # #             self.refresh_step_list()
# # # # #             self.update_tabs()
# # # # #         except Exception as e:
# # # # #             QMessageBox.critical(self, "Error", f"Could not load config:\n{e}")

# # # # #     def load_config(self):
# # # # #         file_path, _ = QFileDialog.getOpenFileName(self, "Load Config", "Config", "JSON Files (*.json)")
# # # # #         if file_path:
# # # # #             self.load_config_from_path(file_path)
# # # # #             if QMessageBox.question(self, 'Restore', "Run pipeline now?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
# # # # #                 self.run_full_restore()

# # # # #     def save_config(self):
# # # # #         default_name = self.current_config_path or "Config/Master_Config.json"
# # # # #         file_path, _ = QFileDialog.getSaveFileName(self, "Save Pipeline", default_name, "JSON Files (*.json)")
# # # # #         if file_path:
# # # # #             config = {
# # # # #                 "pipeline_name": os.path.splitext(os.path.basename(file_path))[0], 
# # # # #                 "export_dfs": self.export_dfs, 
# # # # #                 "processes": self.processes
# # # # #             }
# # # # #             with open(file_path, 'w') as f:
# # # # #                 json.dump(config, f, indent=4)
# # # # #             self.current_config_path = file_path
# # # # #             self.setWindowTitle(f"Pipeline Editor - {os.path.basename(file_path)}")
# # # # #             QMessageBox.information(self, "Saved", f"Saved to {file_path}.")

# # # # # if __name__ == "__main__":
# # # # #     app = QApplication(sys.argv)
# # # # #     window = ScorecardUI()
# # # # #     window.show()
# # # # #     sys.exit(app.exec_())



# # # # # ==============================================================================
# # # # # FILE LOCATION: Dynamic_Scorecard_System/scorecard_ui.py
# # # # # ==============================================================================

# # # # import sys
# # # # import json
# # # # import traceback
# # # # import os
import threading
from concurrent.futures import ThreadPoolExecutor
# # # # import io
# # # # import contextlib
# # # # import shutil
# # # # import pandas as pd
# # # # import numpy as np

# # # # # Force the working directory to be where the EXE is located (or script if running raw)
# # # # if getattr(sys, 'frozen', False):
# # # #     application_path = os.path.dirname(sys.executable)
# # # # else:
# # # #     application_path = os.path.dirname(os.path.abspath(__file__))

# # # # os.chdir(application_path)

# # # # from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
# # # #                              QHBoxLayout, QPushButton, QLabel, QFileDialog, 
# # # #                              QTableView, QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem,
# # # #                              QComboBox, QTextEdit, QLineEdit, QMessageBox, QGroupBox, 
# # # #                              QInputDialog, QTabWidget, QHeaderView, QSplitter, QAction,
# # # #                              QDialog, QFormLayout, QCheckBox, QDialogButtonBox, QAbstractItemView,
# # # #                              QDockWidget, QStackedWidget, QScrollArea, QFrame, QGridLayout)
# # # # from PyQt5.QtCore import QAbstractTableModel, Qt, QThread, pyqtSignal, QEvent
# # # # from PyQt5.QtGui import QFont

# # # # # Make sure these are accessible in your environment
# # # # try:
# # # #     from dynamic_engine import DynamicPipelineEngine, prompt_file
# # # # except ImportError:
# # # #     # Dummy classes to allow UI to run if engine isn't present
# # # #     class DynamicPipelineEngine: pass
# # # #     prompt_file = None

# # # # try:
# # # #     from excel_analyzer import analyze_workbook
# # # # except ImportError:
# # # #     analyze_workbook = None

# # # # class TerminalInput(QLineEdit):
# # # #     """Enhanced QLineEdit with command history (Up/Down arrows)"""
# # # #     def __init__(self, *args, **kwargs):
# # # #         super().__init__(*args, **kwargs)
# # # #         self.history = []
# # # #         self.history_index = -1
# # # #         self.temp_cmd = ""

# # # #     def keyPressEvent(self, event):
# # # #         if event.key() == Qt.Key_Up:
# # # #             if not self.history:
# # # #                 return
# # # #             if self.history_index == -1:
# # # #                 self.temp_cmd = self.text()
            
# # # #             if self.history_index < len(self.history) - 1:
# # # #                 self.history_index += 1
# # # #                 self.setText(self.history[self.history_index])
        
# # # #         elif event.key() == Qt.Key_Down:
# # # #             if self.history_index > -1:
# # # #                 self.history_index -= 1
# # # #                 if self.history_index == -1:
# # # #                     self.setText(self.temp_cmd)
# # # #                 else:
# # # #                     self.setText(self.history[self.history_index])
        
# # # #         else:
# # # #             super().keyPressEvent(event)
# # # #             if event.key() != Qt.Key_Return and event.key() != Qt.Key_Enter:
# # # #                 self.history_index = -1

# # # #     def add_to_history(self, cmd):
# # # #         if cmd.strip():
# # # #             # Remove existing occurrence to move it to the front
# # # #             if cmd in self.history:
# # # #                 self.history.remove(cmd)
# # # #             self.history.insert(0, cmd)
# # # #         self.history_index = -1
# # # #         self.temp_cmd = ""

# # # # class PandasModel(QAbstractTableModel):
# # # #     def __init__(self, data):
# # # #         super().__init__()
# # # #         self._data = data

# # # #     def rowCount(self, parent=None): return self._data.shape[0]
# # # #     def columnCount(self, parent=None): return self._data.shape[1]
# # # #     def data(self, index, role=Qt.DisplayRole):
# # # #         if index.isValid() and role == Qt.DisplayRole:
# # # #             val = self._data.iloc[index.row(), index.column()]
# # # #             return str(val) if not pd.isna(val) else ""
# # # #         return None
# # # #     def headerData(self, col, orientation, role):
# # # #         if orientation == Qt.Horizontal and role == Qt.DisplayRole:
# # # #             return str(self._data.columns[col])
# # # #         return None

# # # # class StepPreviewWorker(QThread):
# # # #     result_ready = pyqtSignal(dict, dict)
# # # #     error_occurred = pyqtSignal(str)

# # # #     def __init__(self, dfs_dict, vars_dict, step):
# # # #         super().__init__()
# # # #         self.dfs_dict = {k: v.copy() for k, v in dfs_dict.items()}
# # # #         self.vars_dict = {k: v for k, v in vars_dict.items()}
# # # #         self.step = step
# # # #         self.engine = DynamicPipelineEngine()

# # # #     def run(self):
# # # #         try:
# # # #             new_dfs, new_vars = self.engine._apply_step(self.dfs_dict, self.vars_dict, self.step)
# # # #             self.result_ready.emit(new_dfs, new_vars)
# # # #         except Exception as e:
# # # #             self.error_occurred.emit(traceback.format_exc())

# # # # class PipelineRestoreWorker(QThread):
# # # #     progress_update = pyqtSignal(str)
# # # #     result_ready = pyqtSignal(dict, dict)
# # # #     error_occurred = pyqtSignal(str)

# # # #     def __init__(self, processes):
# # # #         super().__init__()
# # # #         self.processes = processes
# # # #         self.engine = DynamicPipelineEngine()

# # # #     def run(self):
# # # #         dfs_dict = {}
# # # #         vars_dict = {}
# # # #         try:
# # # #             for proc_name, steps in self.processes.items():
# # # #                 self.progress_update.emit(f"\n--- Running Process: {proc_name} ---")
# # # #                 for step in steps:
# # # #                     self.progress_update.emit(f">>> Executing [{step['step_id']}] {step['action']}...")
                    
# # # #                     original_prompt = step.get('params', {}).get('prompt_at_runtime', False)
# # # #                     if 'params' in step:
# # # #                         step['params']['prompt_at_runtime'] = False
                        
# # # #                     dfs_dict, vars_dict = self.engine._apply_step(dfs_dict, vars_dict, step)
                    
# # # #                     if 'params' in step:
# # # #                         step['params']['prompt_at_runtime'] = original_prompt

# # # #             self.result_ready.emit(dfs_dict, vars_dict)
# # # #         except Exception as e:
# # # #             self.error_occurred.emit(traceback.format_exc())

# # # # class ExcelAnalysisWorker(QThread):
# # # #     result_ready = pyqtSignal(dict)
# # # #     error_occurred = pyqtSignal(str)

# # # #     def __init__(self, file_path):
# # # #         super().__init__()
# # # #         self.file_path = file_path

# # # #     def run(self):
# # # #         try:
# # # #             config = analyze_workbook(self.file_path)
# # # #             self.result_ready.emit(config)
# # # #         except Exception as e:
# # # #             self.error_occurred.emit(str(e))

# # # # class ExportConfigDialog(QDialog):
# # # #     """Custom Dialog for selecting which DataFrames to export to Excel"""
# # # #     def __init__(self, all_dfs, selected_dfs, parent=None):
# # # #         super().__init__(parent)
# # # #         self.setWindowTitle("Configure Headless Export")
# # # #         self.resize(450, 500) # Sets a default size allowing space for lists
        
# # # #         layout = QVBoxLayout(self)
        
# # # #         if not all_dfs:
# # # #             layout.addWidget(QLabel("No DataFrames currently available.\nRun the pipeline or load data first."))
# # # #         else:
# # # #             header_lbl = QLabel("Select which DataFrames to export to Excel\nduring automated Headless execution:")
# # # #             header_lbl.setStyleSheet("margin-bottom: 5px;")
# # # #             layout.addWidget(header_lbl)
            
# # # #             # Action Buttons for Quick Selection
# # # #             btn_layout = QHBoxLayout()
# # # #             btn_select_all = QPushButton("☑ Select All")
# # # #             btn_select_all.clicked.connect(self.select_all)
# # # #             btn_deselect_all = QPushButton("☐ Deselect All")
# # # #             btn_deselect_all.clicked.connect(self.deselect_all)
            
# # # #             btn_layout.addWidget(btn_select_all)
# # # #             btn_layout.addWidget(btn_deselect_all)
# # # #             layout.addLayout(btn_layout)
            
# # # #             # Scrollable List Widget with Checkboxes
# # # #             self.list_widget = QListWidget()
# # # #             self.list_widget.setSelectionMode(QAbstractItemView.NoSelection) # Prevent highlighting, rely purely on checkboxes
            
# # # #             for df_name in all_dfs:
# # # #                 item = QListWidgetItem(df_name)
# # # #                 item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                
# # # #                 # If selected_dfs is empty but we have dfs, default to checked (fallback)
# # # #                 if df_name in selected_dfs or (not selected_dfs and df_name in all_dfs):
# # # #                     item.setCheckState(Qt.Checked)
# # # #                 else:
# # # #                     item.setCheckState(Qt.Unchecked)
                    
# # # #                 self.list_widget.addItem(item)
                
# # # #             layout.addWidget(self.list_widget)
            
# # # #         self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
# # # #         self.buttons.accepted.connect(self.accept)
# # # #         self.buttons.rejected.connect(self.reject)
# # # #         layout.addWidget(self.buttons)

# # # #     def select_all(self):
# # # #         if hasattr(self, 'list_widget'):
# # # #             for i in range(self.list_widget.count()):
# # # #                 self.list_widget.item(i).setCheckState(Qt.Checked)
            
# # # #     def deselect_all(self):
# # # #         if hasattr(self, 'list_widget'):
# # # #             for i in range(self.list_widget.count()):
# # # #                 self.list_widget.item(i).setCheckState(Qt.Unchecked)

# # # #     def get_selected(self):
# # # #         if not hasattr(self, 'list_widget'):
# # # #             return []
        
# # # #         selected = []
# # # #         for i in range(self.list_widget.count()):
# # # #             item = self.list_widget.item(i)
# # # #             if item.checkState() == Qt.Checked:
# # # #                 selected.append(item.text())
# # # #         return selected

# # # # class EditLoadDialog(QDialog):
# # # #     """Custom Dialog for editing an existing 'load_file' step"""
# # # #     def __init__(self, step_params, active_files=None, parent=None):
# # # #         super().__init__(parent)
# # # #         self.active_files = active_files or []
# # # #         self.setWindowTitle("Edit Load File Step")
# # # #         self.setMinimumWidth(550)
        
# # # #         layout = QFormLayout(self)
        
# # # #         self.filepath_input = QLineEdit(step_params.get("filepath", ""))
        
# # # #         # File Path Buttons
# # # #         btn_layout = QHBoxLayout()
# # # #         btn_layout.setContentsMargins(0, 0, 0, 0)
        
# # # #         browse_btn = QPushButton("📁 Browse New")
# # # #         browse_btn.clicked.connect(self.browse)
# # # #         btn_layout.addWidget(browse_btn)
        
# # # #         if self.active_files:
# # # #             active_btn = QPushButton("📄 Select Active File")
# # # #             active_btn.clicked.connect(self.select_active)
# # # #             btn_layout.addWidget(active_btn)
            
# # # #         fp_layout = QVBoxLayout()
# # # #         fp_layout.setContentsMargins(0, 0, 0, 0)
# # # #         fp_layout.addWidget(self.filepath_input)
# # # #         fp_layout.addLayout(btn_layout)
        
# # # #         layout.addRow("File Path:", fp_layout)
        
# # # #         # Sheet Selection Layout
# # # #         self.sheet_input = QLineEdit(str(step_params.get("sheet", 0)))
# # # #         self.sheet_input.setPlaceholderText("0 for first sheet, or 'Sheet1'")
        
# # # #         sheet_layout = QHBoxLayout()
# # # #         sheet_layout.setContentsMargins(0, 0, 0, 0)
# # # #         sheet_layout.addWidget(self.sheet_input)
        
# # # #         inspect_btn = QPushButton("🔍 Select Sheet")
# # # #         inspect_btn.clicked.connect(self.list_sheets)
# # # #         sheet_layout.addWidget(inspect_btn)
        
# # # #         layout.addRow("Sheet Name/Index:", sheet_layout)
        
# # # #         self.alias_input = QLineEdit(step_params.get("alias", ""))
# # # #         layout.addRow("DataFrame Alias:", self.alias_input)
        
# # # #         self.header_input = QLineEdit(str(step_params.get("header", 0)))
# # # #         self.header_input.setPlaceholderText("0 for first row (default)")
# # # #         layout.addRow("Header Row (Index):", self.header_input)
        
# # # #         self.prompt_cb = QCheckBox("Prompt user to select this file at runtime (Filepath becomes a placeholder)")
# # # #         self.prompt_cb.setChecked(step_params.get("prompt_at_runtime", False))
# # # #         layout.addRow("", self.prompt_cb)
        
# # # #         self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
# # # #         self.buttons.accepted.connect(self.accept)
# # # #         self.buttons.rejected.connect(self.reject)
# # # #         layout.addRow(self.buttons)

# # # #     def browse(self):
# # # #         fp, _ = QFileDialog.getOpenFileName(self, "Select Excel/CSV", "", "Data Files (*.xlsx *.csv)")
# # # #         if fp:
# # # #             self.filepath_input.setText(fp)
            
# # # #     def select_active(self):
# # # #         if not self.active_files: return
# # # #         fp, ok = QInputDialog.getItem(self, "Select Active File", "Choose an existing file from the pipeline:", self.active_files, 0, False)
# # # #         if ok and fp:
# # # #             self.filepath_input.setText(fp)

# # # #     def list_sheets(self):
# # # #         fp = self.filepath_input.text().strip()
# # # #         if not fp or not os.path.exists(fp):
# # # #             QMessageBox.warning(self, "File Not Found", "Cannot read sheets. Please ensure the file path is correct and accessible on your machine.")
# # # #             return
# # # #         if not fp.endswith(('.xlsx', '.xlsm')):
# # # #             QMessageBox.information(self, "Not an Excel File", "Only Excel files have multiple sheets to select from.")
# # # #             return
            
# # # #         try:
# # # #             xl = pd.ExcelFile(fp)
# # # #             sheet, ok = QInputDialog.getItem(self, "Select Sheet", f"Available Sheets in {os.path.basename(fp)}:", xl.sheet_names, 0, False)
# # # #             if ok and sheet:
# # # #                 self.sheet_input.setText(sheet)
# # # #         except Exception as e:
# # # #             QMessageBox.critical(self, "Error", f"Could not read sheets:\n{e}")

# # # #     def get_params(self):
# # # #         sheet_val = self.sheet_input.text()
# # # #         if sheet_val.isdigit():
# # # #             sheet_val = int(sheet_val)
            
# # # #         header_val = 0
# # # #         if self.header_input.text().isdigit():
# # # #             header_val = int(self.header_input.text())
            
# # # #         fp = self.filepath_input.text().strip()
# # # #         if not fp and self.prompt_cb.isChecked():
# # # #             fp = "RUNTIME_PROMPT_ONLY.xlsx"
            
# # # #         return {
# # # #             "filepath": fp,
# # # #             "sheet": sheet_val,
# # # #             "header": header_val,
# # # #             "alias": self.alias_input.text(),
# # # #             "prompt_at_runtime": self.prompt_cb.isChecked()
# # # #         }

# # # # class ConfigCard(QGroupBox):
# # # #     """A visually appealing card representing a pipeline configuration"""
# # # #     edit_requested = pyqtSignal(str)
# # # #     run_requested = pyqtSignal(str)
# # # #     delete_requested = pyqtSignal(str)

# # # #     def __init__(self, file_path, config_data):
# # # #         title = config_data.get("pipeline_name", os.path.basename(file_path))
# # # #         super().__init__(title)
# # # #         self.file_path = file_path
# # # #         self.setObjectName("ConfigCard")
        
# # # #         layout = QVBoxLayout(self)
        
# # # #         # Metadata
# # # #         proc_count = len(config_data.get("processes", {}))
# # # #         step_count = sum(len(steps) for steps in config_data.get("processes", {}).values())
        
# # # #         self.info_lbl = QLabel(f"Processes: {proc_count} | Total Steps: {step_count}")
# # # #         self.info_lbl.setObjectName("cardMetadata")
# # # #         layout.addWidget(self.info_lbl)
        
# # # #         self.path_lbl = QLabel(os.path.basename(file_path))
# # # #         self.path_lbl.setObjectName("cardPath")
# # # #         layout.addWidget(self.path_lbl)
        
# # # #         layout.addStretch()
        
# # # #         # Action Buttons
# # # #         btn_layout = QHBoxLayout()
        
# # # #         self.btn_run = QPushButton("▶ Run")
# # # #         self.btn_run.setObjectName("btnSuccess")
# # # #         self.btn_run.clicked.connect(lambda: self.run_requested.emit(self.file_path))
        
# # # #         self.btn_edit = QPushButton("✏ Edit")
# # # #         self.btn_edit.setObjectName("btnPrimary")
# # # #         self.btn_edit.clicked.connect(lambda: self.edit_requested.emit(self.file_path))
        
# # # #         self.btn_del = QPushButton("🗑")
# # # #         self.btn_del.setObjectName("btnDanger")
# # # #         self.btn_del.setFixedWidth(40)
# # # #         self.btn_del.clicked.connect(lambda: self.delete_requested.emit(self.file_path))
        
# # # #         btn_layout.addWidget(self.btn_run)
# # # #         btn_layout.addWidget(self.btn_edit)
# # # #         btn_layout.addWidget(self.btn_del)
        
# # # #         layout.addLayout(btn_layout)

# # # # class DashboardWidget(QWidget):
# # # #     """The landing screen for the application"""
# # # #     create_new_requested = pyqtSignal()
# # # #     auto_generate_requested = pyqtSignal()
# # # #     edit_config_requested = pyqtSignal(str)
# # # #     run_config_requested = pyqtSignal(str)

# # # #     def __init__(self, parent=None):
# # # #         super().__init__(parent)
# # # #         self.init_ui()

# # # #     def init_ui(self):
# # # #         main_layout = QVBoxLayout(self)
# # # #         main_layout.setContentsMargins(40, 40, 40, 40)
# # # #         main_layout.setSpacing(20)
        
# # # #         # Header
# # # #         header_layout = QHBoxLayout()
# # # #         self.title_lbl = QLabel("Dynamic Scorecard System")
# # # #         self.title_lbl.setObjectName("mainTitle")
# # # #         header_layout.addWidget(self.title_lbl)
        
# # # #         header_layout.addStretch()
        
# # # #         self.btn_new = QPushButton("➕ Create New Configuration")
# # # #         self.btn_new.setObjectName("btnPrimary")
# # # #         self.btn_new.setMinimumHeight(50)
# # # #         self.btn_new.clicked.connect(self.create_new_requested.emit)
# # # #         header_layout.addWidget(self.btn_new)
        
# # # #         self.btn_auto = QPushButton("🪄 Auto-Generate from Excel")
# # # #         self.btn_auto.setObjectName("btnSuccess")
# # # #         self.btn_auto.setMinimumHeight(50)
# # # #         self.btn_auto.clicked.connect(self.auto_generate_requested.emit)
# # # #         header_layout.addWidget(self.btn_auto)
        
# # # #         self.btn_import_config = QPushButton("📥 Import Config")
# # # #         self.btn_import_config.setMinimumHeight(50)
# # # #         self.btn_import_config.clicked.connect(self.import_config)
# # # #         header_layout.addWidget(self.btn_import_config)
        
# # # #         self.btn_refresh = QPushButton("🔄 Refresh")
# # # #         self.btn_refresh.setMinimumHeight(50)
# # # #         self.btn_refresh.setFixedWidth(120)
# # # #         self.btn_refresh.clicked.connect(self.refresh_configs)
# # # #         header_layout.addWidget(self.btn_refresh)
        
# # # #         main_layout.addLayout(header_layout)
        
# # # #         # Divider
# # # #         self.divider = QFrame()
# # # #         self.divider.setObjectName("mainDivider")
# # # #         self.divider.setFrameShape(QFrame.HLine)
# # # #         self.divider.setFrameShadow(QFrame.Sunken)
# # # #         main_layout.addWidget(self.divider)
        
# # # #         # Scroll Area for Configs
# # # #         self.scroll = QScrollArea()
# # # #         self.scroll.setObjectName("dashboardScroll")
# # # #         self.scroll.setWidgetResizable(True)
        
# # # #         self.container = QWidget()
# # # #         self.container.setObjectName("dashboardContainer")
# # # #         self.flow_layout = QGridLayout(self.container) # Using grid for card layout
# # # #         self.flow_layout.setSpacing(20)
        
# # # #         self.scroll.setWidget(self.container)
# # # #         main_layout.addWidget(self.scroll)
        
# # # #         self.refresh_configs()

# # # #     def import_config(self):
# # # #         file_path, _ = QFileDialog.getOpenFileName(self, "Select Configuration to Import", "", "JSON Files (*.json)")
# # # #         if file_path:
# # # #             config_dir = "Config"
# # # #             if not os.path.exists(config_dir):
# # # #                 os.makedirs(config_dir)
# # # #             dest_path = os.path.join(config_dir, os.path.basename(file_path))
# # # #             if os.path.abspath(file_path) != os.path.abspath(dest_path):
# # # #                 try:
# # # #                     shutil.copy2(file_path, dest_path)
# # # #                     QMessageBox.information(self, "Success", f"Config imported into application:\n{dest_path}")
# # # #                     self.refresh_configs()
# # # #                 except Exception as e:
# # # #                     QMessageBox.critical(self, "Error", f"Could not import config:\n{e}")

# # # #     def refresh_configs(self):
# # # #         # Clear existing
# # # #         for i in reversed(range(self.flow_layout.count())): 
# # # #             self.flow_layout.itemAt(i).widget().setParent(None)
            
# # # #         config_dir = "Config"
# # # #         if not os.path.exists(config_dir):
# # # #             os.makedirs(config_dir)
            
# # # #         configs = [f for f in os.listdir(config_dir) if f.endswith(".json")]
        
# # # #         if not configs:
# # # #             empty_lbl = QLabel("No configurations found. Create your first pipeline to get started!")
# # # #             empty_lbl.setAlignment(Qt.AlignCenter)
# # # #             empty_lbl.setObjectName("emptyMsg")
# # # #             self.flow_layout.addWidget(empty_lbl, 0, 0)
# # # #             return

# # # #         col_limit = 3
# # # #         for idx, filename in enumerate(configs):
# # # #             path = os.path.join(config_dir, filename)
# # # #             try:
# # # #                 with open(path, 'r') as f:
# # # #                     data = json.load(f)
                
# # # #                 card = ConfigCard(path, data)
# # # #                 card.edit_requested.connect(self.edit_config_requested.emit)
# # # #                 card.run_requested.connect(self.run_config_requested.emit)
# # # #                 card.delete_requested.connect(self.delete_config)
                
# # # #                 self.flow_layout.addWidget(card, idx // col_limit, idx % col_limit)
# # # #             except Exception as e:
# # # #                 print(f"Error loading {filename}: {e}")

# # # #     def delete_config(self, path):
# # # #         reply = QMessageBox.question(self, 'Delete Configuration', 
# # # #                                      f"Are you sure you want to delete '{os.path.basename(path)}'?\nThis cannot be undone.",
# # # #                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
# # # #         if reply == QMessageBox.Yes:
# # # #             try:
# # # #                 os.remove(path)
# # # #                 self.refresh_configs()
# # # #             except Exception as e:
# # # #                 QMessageBox.critical(self, "Error", f"Could not delete file: {e}")

# # # # class ScorecardUI(QMainWindow):
# # # #     def __init__(self):
# # # #         super().__init__()
# # # #         self.setWindowTitle("Dynamic Scorecard System - Dashboard")
# # # #         self.resize(1600, 1000)
        
# # # #         self.processes = {"Main_Process": []} 
# # # #         self.current_process = "Main_Process"
# # # #         self.export_dfs = [] 
# # # #         self.current_config_path = None
        
# # # #         self.global_dfs = {}
# # # #         self.global_vars = {}
# # # #         self.preview_dfs = {} 
# # # #         self.preview_vars = {}
# # # #         self.pending_step = None 
        
# # # #         # State Management
# # # #         self.stacked_widget = QStackedWidget()
# # # #         self.setCentralWidget(self.stacked_widget)
        
# # # #         self.init_ui()
# # # #         self.apply_dark_theme()
        
# # # #         # Start at Dashboard
# # # #         self.show_dashboard()

# # # #     def show_dashboard(self):
# # # #         self.dashboard.refresh_configs()
# # # #         self.stacked_widget.setCurrentIndex(0)
# # # #         self.setWindowTitle("Dynamic Scorecard System - Dashboard")
        
# # # #         # Hide Editor Docks
# # # #         self.dock_pipeline.hide()
# # # #         self.dock_sandbox.hide()
# # # #         self.dock_terminal.hide()
        
# # # #     def show_editor(self, config_path=None):
# # # #         self.stacked_widget.setCurrentIndex(1)
# # # #         self.dock_pipeline.show()
# # # #         self.dock_sandbox.show()
# # # #         self.dock_terminal.show()
        
# # # #         if config_path:
# # # #             self.load_config_from_path(config_path)
# # # #             self.setWindowTitle(f"Pipeline Editor - {os.path.basename(config_path)}")
# # # #         else:
# # # #             self.new_config()
# # # #             self.setWindowTitle("Pipeline Editor - New Configuration")

# # # #     def new_config(self):
# # # #         self.processes = {"Main_Process": []}
# # # #         self.current_process = "Main_Process"
# # # #         self.export_dfs = []
# # # #         self.current_config_path = None
# # # #         self.global_dfs = {}
# # # #         self.global_vars = {}
# # # #         self.preview_dfs = {}
# # # #         self.preview_vars = {}
        
# # # #         self.combo_processes.blockSignals(True)
# # # #         self.combo_processes.clear()
# # # #         self.combo_processes.addItem("Main_Process")
# # # #         self.combo_processes.blockSignals(False)
        
# # # #         self.refresh_step_list()
# # # #         self.update_tabs()

# # # #     def run_config_from_dashboard(self, path):
# # # #         export_dir = QFileDialog.getExistingDirectory(self, "Select Export Folder for Final Data")
# # # #         if not export_dir: return # User cancelled
# # # #         self.show_editor(path)
# # # #         self.run_full_restore(export_dir)

# # # #     def apply_dark_theme(self):
# # # #         dark_qss = """
# # # #         QMainWindow, QWidget { 
# # # #             background-color: #1e1e1e; 
# # # #             color: #d4d4d4; 
# # # #             font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; 
# # # #             font-size: 10pt; 
# # # #         }
        
# # # #         /* Dashboard Specifics */
# # # #         QLabel#mainTitle { font-size: 26pt; font-weight: bold; color: #ffffff; padding-bottom: 5px; }
# # # #         QLabel#emptyMsg { color: #888888; font-size: 14pt; margin-top: 50px; }
# # # #         QFrame#mainDivider { background-color: #333333; height: 1px; border: none; }
# # # #         QScrollArea#dashboardScroll { background-color: transparent; border: none; }
# # # #         QWidget#dashboardContainer { background-color: transparent; }

# # # #         /* Config Card Specifics */
# # # #         QGroupBox#ConfigCard {
# # # #             background-color: #2d2d30;
# # # #             border: 2px solid #3e3e42;
# # # #             border-radius: 12px;
# # # #             margin-top: 20px;
# # # #             padding-top: 15px;
# # # #             font-size: 11pt;
# # # #         }
# # # #         QGroupBox#ConfigCard:hover { border: 2px solid #007acc; background-color: #333337; }
# # # #         QGroupBox#ConfigCard::title {
# # # #             subcontrol-origin: margin;
# # # #             subcontrol-position: top left;
# # # #             left: 15px;
# # # #             padding: 0 8px;
# # # #             color: #007acc;
# # # #             font-weight: bold;
# # # #         }
# # # #         QLabel#cardMetadata { color: #a0a0a0; font-size: 9pt; font-weight: 500; }
# # # #         QLabel#cardPath { color: #666666; font-style: italic; font-size: 8pt; }

# # # #         /* Editor Specifics */
# # # #         QDockWidget::title { 
# # # #             text-align: left; 
# # # #             background: #252526; 
# # # #             padding: 8px 12px; 
# # # #             border-top-left-radius: 8px;
# # # #             border-top-right-radius: 8px;
# # # #             font-weight: bold; 
# # # #             color: #007acc; 
# # # #         }
# # # #         QDockWidget { border: 1px solid #333333; border-radius: 12px; }
# # # #         QGroupBox { 
# # # #             border: 1px solid #333333; 
# # # #             border-radius: 10px; 
# # # #             margin-top: 20px; 
# # # #             font-weight: bold; 
# # # #             color: #007acc; 
# # # #             padding-top: 10px;
# # # #         }
# # # #         QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 10px; left: 15px; }
        
# # # #         QPushButton { 
# # # #             background-color: #333333; 
# # # #             color: #ffffff; 
# # # #             border: 1px solid #444444; 
# # # #             padding: 10px 18px; 
# # # #             border-radius: 8px; 
# # # #             font-weight: 600; 
# # # #         }
# # # #         QPushButton:hover { background-color: #404040; border-color: #007acc; }
# # # #         QPushButton#btnPrimary { background-color: #007acc; border: none; }
# # # #         QPushButton#btnPrimary:hover { background-color: #1a8ad4; }
# # # #         QPushButton#btnSuccess { background-color: #2da44e; border: none; }
# # # #         QPushButton#btnSuccess:hover { background-color: #2cbe4e; }
# # # #         QPushButton#btnDanger { background-color: #cf222e; border: none; }
        
# # # #         QLineEdit, QTextEdit, QComboBox { 
# # # #             background-color: #252526; 
# # # #             border: 1px solid #3c3c3c; 
# # # #             border-radius: 8px; 
# # # #             padding: 8px; 
# # # #             color: #d4d4d4; 
# # # #         }
# # # #         QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border: 2px solid #007acc; background-color: #2d2d30; }
        
# # # #         QTabWidget::pane { border: 1px solid #333333; border-radius: 10px; background: #1e1e1e; top: -1px; }
# # # #         QTabBar::tab { 
# # # #             background: #2d2d30; 
# # # #             border: 1px solid #333333; 
# # # #             padding: 10px 20px; 
# # # #             color: #808080; 
# # # #             border-top-left-radius: 8px; 
# # # #             border-top-right-radius: 8px;
# # # #             margin-right: 4px;
# # # #         }
# # # #         QTabBar::tab:selected { background: #1e1e1e; color: #ffffff; border-bottom: 3px solid #007acc; font-weight: bold; }

# # # #         /* Table & Data Views */
# # # #         QTableView, QTableWidget {
# # # #             background-color: #1e1e1e;
# # # #             gridline-color: #333333;
# # # #             border: 1px solid #333333;
# # # #             border-radius: 8px;
# # # #             color: #d4d4d4;
# # # #         }
# # # #         QHeaderView::section {
# # # #             background-color: #252526;
# # # #             color: #007acc;
# # # #             padding: 8px;
# # # #             border: 1px solid #333333;
# # # #             font-weight: bold;
# # # #         }
# # # #         QHeaderView {
# # # #             background-color: #1e1e1e;
# # # #         }
# # # #         QTableCornerButton::section {
# # # #             background-color: #252526;
# # # #             border: 1px solid #333333;
# # # #         }
# # # #         QScrollBar:vertical { border: none; background: #1e1e1e; width: 12px; border-radius: 6px; }
# # # #         QScrollBar::handle:vertical { background: #3e3e42; min-height: 20px; border-radius: 6px; }
# # # #         QScrollBar::handle:vertical:hover { background: #4e4e52; }
# # # #         """
# # # #         self.setStyleSheet(dark_qss)
# # # #         if hasattr(self, 'terminal_output'):
# # # #             self.terminal_output.setStyleSheet("background-color: #0a0a0a; border-radius: 10px; color: #4CAF50; padding: 10px; font-family: 'Consolas';")
# # # #             self.terminal_input.setStyleSheet("background-color: #0a0a0a; border: 1px solid #007acc; border-radius: 8px; color: #FFFFFF; padding: 8px;")
        
# # # #         if hasattr(self, 'dashboard'):
# # # #             self.dashboard.setStyleSheet(dark_qss)

# # # #     def apply_white_theme(self):
# # # #         white_qss = """
# # # #         QMainWindow, QWidget { 
# # # #             background-color: #f8f9fa; 
# # # #             color: #212529; 
# # # #             font-family: 'Segoe UI', system-ui, sans-serif; 
# # # #             font-size: 10pt; 
# # # #         }
        
# # # #         /* Dashboard Specifics */
# # # #         QLabel#mainTitle { font-size: 26pt; font-weight: bold; color: #1a1a1a; padding-bottom: 5px; }
# # # #         QLabel#emptyMsg { color: #6c757d; font-size: 14pt; margin-top: 50px; }
# # # #         QFrame#mainDivider { background-color: #dee2e6; height: 1px; border: none; }
# # # #         QScrollArea#dashboardScroll { background-color: transparent; border: none; }
# # # #         QWidget#dashboardContainer { background-color: transparent; }

# # # #         /* Config Card Specifics */
# # # #         QGroupBox#ConfigCard {
# # # #             background-color: #ffffff;
# # # #             border: 1px solid #dee2e6;
# # # #             border-radius: 12px;
# # # #             margin-top: 20px;
# # # #             padding-top: 15px;
# # # #             font-size: 11pt;
# # # #         }
# # # #         QGroupBox#ConfigCard:hover { border: 1px solid #007acc; background-color: #f8f9fa; }
# # # #         QGroupBox#ConfigCard::title {
# # # #             subcontrol-origin: margin;
# # # #             subcontrol-position: top left;
# # # #             left: 15px;
# # # #             padding: 0 8px;
# # # #             color: #007acc;
# # # #             font-weight: bold;
# # # #         }
# # # #         QLabel#cardMetadata { color: #495057; font-size: 9pt; font-weight: 500; }
# # # #         QLabel#cardPath { color: #6c757d; font-style: italic; font-size: 8pt; }

# # # #         /* Editor Specifics */
# # # #         QLabel { color: #212529; }
# # # #         QDockWidget::title { 
# # # #             text-align: left; 
# # # #             background: #ffffff; 
# # # #             padding: 8px 12px; 
# # # #             border-top-left-radius: 8px;
# # # #             border-top-right-radius: 8px;
# # # #             font-weight: bold; 
# # # #             color: #007acc; 
# # # #             border-bottom: 1px solid #e9ecef;
# # # #         }
# # # #         QDockWidget { border: 1px solid #dee2e6; border-radius: 12px; background-color: #ffffff; }
# # # #         QGroupBox { 
# # # #             border: 1px solid #dee2e6; 
# # # #             border-radius: 10px; 
# # # #             margin-top: 20px; 
# # # #             font-weight: bold; 
# # # #             color: #007acc; 
# # # #             background-color: #ffffff;
# # # #             padding-top: 10px;
# # # #         }
# # # #         QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 10px; left: 15px; background-color: #ffffff; color: #007acc; }
        
# # # #         QPushButton { 
# # # #             background-color: #ffffff; 
# # # #             color: #212529; 
# # # #             border: 1px solid #dee2e6; 
# # # #             padding: 10px 18px; 
# # # #             border-radius: 8px; 
# # # #             font-weight: 600; 
# # # #         }
# # # #         QPushButton:hover { background-color: #f1f3f5; border-color: #adb5bd; }
# # # #         QPushButton#btnPrimary { background-color: #007acc; border: none; color: #ffffff; }
# # # #         QPushButton#btnPrimary:hover { background-color: #1a8ad4; }
# # # #         QPushButton#btnSuccess { background-color: #2da44e; border: none; color: #ffffff; }
# # # #         QPushButton#btnSuccess:hover { background-color: #2cbe4e; }
# # # #         QPushButton#btnDanger { background-color: #cf222e; border: none; color: #ffffff; }
        
# # # #         QLineEdit, QTextEdit, QComboBox { 
# # # #             background-color: #ffffff; 
# # # #             border: 1px solid #dee2e6; 
# # # #             border-radius: 8px; 
# # # #             padding: 8px; 
# # # #             color: #212529; 
# # # #         }
# # # #         QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border: 2px solid #007acc; background-color: #ffffff; }
        
# # # #         QTabWidget::pane { border: 1px solid #dee2e6; border-radius: 10px; background: #ffffff; top: -1px; }
# # # #         QTabBar::tab { 
# # # #             background: #f1f3f5; 
# # # #             border: 1px solid #dee2e6; 
# # # #             padding: 10px 20px; 
# # # #             color: #495057; 
# # # #             border-top-left-radius: 8px; 
# # # #             border-top-right-radius: 8px;
# # # #             margin-right: 4px;
# # # #         }
# # # #         QTabBar::tab:selected { background: #ffffff; color: #007acc; border-bottom: 3px solid #007acc; font-weight: bold; }
        
# # # #         /* Table & Data Views */
# # # #         QTableView, QTableWidget {
# # # #             background-color: #ffffff;
# # # #             gridline-color: #e9ecef;
# # # #             border: 1px solid #dee2e6;
# # # #             border-radius: 8px;
# # # #             color: #212529;
# # # #         }
# # # #         QHeaderView::section {
# # # #             background-color: #f1f3f5;
# # # #             color: #007acc;
# # # #             padding: 8px;
# # # #             border: 1px solid #dee2e6;
# # # #             font-weight: bold;
# # # #         }
# # # #         QHeaderView {
# # # #             background-color: #ffffff;
# # # #         }
# # # #         QTableCornerButton::section {
# # # #             background-color: #f1f3f5;
# # # #             border: 1px solid #dee2e6;
# # # #         }
# # # #         QScrollBar:vertical { border: none; background: #f8f9fa; width: 12px; border-radius: 6px; }
# # # #         QScrollBar::handle:vertical { background: #dee2e6; min-height: 20px; border-radius: 6px; }
# # # #         QScrollBar::handle:vertical:hover { background: #ced4da; }
# # # #         """
# # # #         self.setStyleSheet(white_qss)
# # # #         if hasattr(self, 'terminal_output'):
# # # #             self.terminal_output.setStyleSheet("background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 10px; color: #1a7f37; padding: 10px; font-family: 'Consolas';")
# # # #             self.terminal_input.setStyleSheet("background-color: #ffffff; border: 2px solid #007acc; border-radius: 8px; color: #212529; padding: 8px;")
        
# # # #         if hasattr(self, 'dashboard'):
# # # #             self.dashboard.setStyleSheet(white_qss)
# # # #             self.dashboard.refresh_configs()

# # # #     def init_ui(self):
# # # #         # --- Dashboard ---
# # # #         self.dashboard = DashboardWidget()
# # # #         self.dashboard.create_new_requested.connect(lambda: self.show_editor())
# # # #         self.dashboard.auto_generate_requested.connect(self.auto_generate_pipeline)
# # # #         self.dashboard.edit_config_requested.connect(lambda p: self.show_editor(p))
# # # #         self.dashboard.run_config_requested.connect(self.run_config_from_dashboard)
# # # #         self.stacked_widget.addWidget(self.dashboard)

# # # #         # --- Menu Bar ---
# # # #         menubar = self.menuBar()
# # # #         file_menu = menubar.addMenu('File')

# # # #         back_action = QAction('🔙 Back to Dashboard', self)
# # # #         back_action.triggered.connect(lambda: self.show_dashboard())
# # # #         file_menu.addAction(back_action)
# # # #         file_menu.addSeparator()

# # # #         load_conf_action = QAction('Load Pipeline Config', self)
# # # #         load_conf_action.triggered.connect(lambda: self.load_config())
# # # #         file_menu.addAction(load_conf_action)

# # # #         save_conf_action = QAction('Save Pipeline Config', self)
# # # #         save_conf_action.triggered.connect(lambda: self.save_config())
# # # #         file_menu.addAction(save_conf_action)

# # # #         view_menu = menubar.addMenu('View')
# # # #         self.dock_menu = view_menu.addMenu('Panels')

# # # #         theme_menu = view_menu.addMenu('Theme')
# # # #         dark_action = QAction('Dark Mode', self)
# # # #         dark_action.triggered.connect(lambda: self.apply_dark_theme())
# # # #         theme_menu.addAction(dark_action)

# # # #         white_action = QAction('White Mode', self)
# # # #         white_action.triggered.connect(lambda: self.apply_white_theme())
# # # #         theme_menu.addAction(white_action)

# # # #         # --- Editor Central Widget ---
# # # #         self.editor_central = QWidget()
# # # #         editor_main_layout = QVBoxLayout(self.editor_central)

# # # #         # Top Header (Context info)
# # # #         context_layout = QHBoxLayout()
# # # #         self.lbl_context = QLabel("Context Available: DFs (0) | Vars (0)")
# # # #         self.lbl_context.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 11pt;")
# # # #         context_layout.addWidget(self.lbl_context)

# # # #         self.combo_view = QComboBox()
# # # #         self.combo_view.setFixedWidth(280)
# # # #         self.combo_view.setPlaceholderText("Select a DataFrame to View...")
# # # #         self.combo_view.currentIndexChanged.connect(self.on_view_combo_changed)
# # # #         context_layout.addWidget(self.combo_view)
# # # #         editor_main_layout.addLayout(context_layout)

# # # #         # Splitter to allow resizing without jumping
# # # #         self.central_splitter = QSplitter(Qt.Vertical)
        
# # # #         # Tabs (Data View)
# # # #         self.tabs = QTabWidget()
# # # #         self.tabs.setUsesScrollButtons(True) 
# # # #         self.tabs.currentChanged.connect(self.on_tab_changed)
# # # #         self.central_splitter.addWidget(self.tabs)

# # # #         editor_main_layout.addWidget(self.central_splitter)

# # # #         self.stacked_widget.addWidget(self.editor_central)

# # # #         # --- Dock 1: Pipeline Controls (Left) ---
# # # #         self.dock_pipeline = QDockWidget("Pipeline & Steps", self)
# # # #         self.dock_pipeline.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

# # # #         pipeline_widget = QWidget()
# # # #         left_panel = QVBoxLayout(pipeline_widget)

# # # #         process_layout = QHBoxLayout()
# # # #         self.combo_processes = QComboBox()
# # # #         self.combo_processes.addItem("Main_Process")
# # # #         self.combo_processes.currentTextChanged.connect(self.switch_process)
# # # #         process_layout.addWidget(self.combo_processes)

# # # #         btn_add_process = QPushButton("➕")
# # # #         btn_add_process.setFixedWidth(35)
# # # #         btn_add_process.clicked.connect(self.add_process)
# # # #         process_layout.addWidget(btn_add_process)

# # # #         btn_del_process = QPushButton("🗑️")
# # # #         btn_del_process.setFixedWidth(35)
# # # #         btn_del_process.clicked.connect(self.delete_process)
# # # #         process_layout.addWidget(btn_del_process)

# # # #         left_panel.addLayout(process_layout)

# # # #         btn_load = QPushButton("📥 Load Source Data")
# # # #         btn_load.setObjectName("btnPrimary")
# # # #         btn_load.clicked.connect(self.load_data)
# # # #         left_panel.addWidget(btn_load)

# # # #         btn_load_existing = QPushButton("📄 Load Another Sheet")
# # # #         btn_load_existing.setObjectName("btnPrimary")
# # # #         btn_load_existing.clicked.connect(self.load_existing_file_data)
# # # #         left_panel.addWidget(btn_load_existing)

# # # #         self.list_steps = QListWidget()
# # # #         self.list_steps.itemClicked.connect(self.load_step_into_editor)
# # # #         left_panel.addWidget(self.list_steps)

# # # #         btn_restore = QPushButton("▶️ Run Pipeline")
# # # #         btn_restore.setObjectName("btnPurple")
# # # #         btn_restore.clicked.connect(self.run_full_restore)
# # # #         left_panel.addWidget(btn_restore)

# # # #         btn_export_config = QPushButton("⚙️ Export Config")
# # # #         btn_export_config.setObjectName("btnGray")
# # # #         btn_export_config.clicked.connect(self.configure_export)
# # # #         left_panel.addWidget(btn_export_config)

# # # #         self.dock_pipeline.setWidget(pipeline_widget)
# # # #         self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_pipeline)
# # # #         self.dock_menu.addAction(self.dock_pipeline.toggleViewAction())

# # # #         # --- Dock 2: Python Action Sandbox (Bottom/Right) ---
# # # #         self.dock_sandbox = QDockWidget("Logic Editor & Sandbox", self)

# # # #         sandbox_group = QGroupBox()
# # # #         sandbox_layout = QVBoxLayout(sandbox_group)

# # # #         self.combo_action = QComboBox()
# # # #         self.combo_action.addItems([
# # # #             "Execute Raw Python/Pandas", 
# # # #             "Evaluate Excel Formula (Native Math)",
# # # #             "Run External .py Script (Entire File)"
# # # #         ])
# # # #         self.combo_action.currentIndexChanged.connect(self.toggle_inputs)
# # # #         sandbox_layout.addWidget(self.combo_action)

# # # #         code_font = QFont("Consolas", 11)
# # # #         self.txt_python = QTextEdit()
# # # #         self.txt_python.setFont(code_font)
# # # #         self.txt_python.setPlaceholderText("Write Python/Pandas logic here...")
# # # #         self.txt_python.setMinimumSize(0, 0) # Allow shrinking
# # # #         sandbox_layout.addWidget(self.txt_python)

# # # #         # Excel Formula Inputs
# # # #         self.widget_excel_formula = QWidget()
# # # #         excel_layout = QVBoxLayout(self.widget_excel_formula)
# # # #         excel_layout.setContentsMargins(0, 0, 0, 0)

# # # #         self.txt_excel_formula = QTextEdit()
# # # #         self.txt_excel_formula.setFont(code_font)
# # # #         self.txt_excel_formula.setPlaceholderText("Enter Excel Formula (e.g., =SUM(Sheet1!A:A))")
# # # #         self.txt_excel_formula.setMaximumHeight(150)
# # # #         self.txt_excel_formula.setMinimumSize(0, 0)
# # # #         excel_layout.addWidget(self.txt_excel_formula)

# # # #         self.txt_excel_target = QLineEdit()
# # # #         self.txt_excel_target.setPlaceholderText("Target DataFrame Alias (e.g., Master)")
# # # #         excel_layout.addWidget(self.txt_excel_target)

# # # #         self.txt_excel_column = QLineEdit()
# # # #         self.txt_excel_column.setPlaceholderText("Target Column (Optional - e.g., Price)")
# # # #         excel_layout.addWidget(self.txt_excel_column)

# # # #         self.widget_excel_formula.hide()
# # # #         sandbox_layout.addWidget(self.widget_excel_formula)

# # # #         self.widget_script_path = QWidget()
# # # #         script_path_layout = QHBoxLayout(self.widget_script_path)
# # # #         script_path_layout.setContentsMargins(0, 0, 0, 0)
# # # #         self.txt_script_path = QLineEdit()
# # # #         self.btn_browse_script = QPushButton("📁")
# # # #         self.btn_browse_script.clicked.connect(self.browse_script)
# # # #         script_path_layout.addWidget(self.txt_script_path)
# # # #         script_path_layout.addWidget(self.btn_browse_script)
# # # #         self.widget_script_path.hide()
# # # #         sandbox_layout.addWidget(self.widget_script_path)

# # # #         btn_layout = QHBoxLayout()
# # # #         btn_test = QPushButton("🧪 Test")
# # # #         btn_test.clicked.connect(self.test_step)
# # # #         btn_layout.addWidget(btn_test)

# # # #         btn_record = QPushButton("✅ Record")
# # # #         btn_record.setObjectName("btnSuccess")
# # # #         btn_record.clicked.connect(self.record_step)
# # # #         btn_layout.addWidget(btn_record)

# # # #         btn_update = QPushButton("🔄 Update")
# # # #         btn_update.setObjectName("btnWarning")
# # # #         btn_update.clicked.connect(self.update_selected_step)
# # # #         btn_layout.addWidget(btn_update)

# # # #         btn_del_step = QPushButton("🗑️ Delete")
# # # #         btn_del_step.setObjectName("btnDanger")
# # # #         btn_del_step.clicked.connect(self.delete_step)
# # # #         btn_layout.addWidget(btn_del_step)

# # # #         sandbox_layout.addLayout(btn_layout)
# # # #         self.dock_sandbox.setWidget(sandbox_group)
# # # #         self.addDockWidget(Qt.RightDockWidgetArea, self.dock_sandbox)
# # # #         self.dock_menu.addAction(self.dock_sandbox.toggleViewAction())

# # # #         # --- Dock 3: Terminal (Bottom) ---
# # # #         self.dock_terminal = QDockWidget("Interactive Terminal REPL", self)
# # # #         term_widget = QWidget()
# # # #         term_layout = QVBoxLayout(term_widget)

# # # #         self.terminal_output = QTextEdit()
# # # #         self.terminal_output.setFont(code_font)
# # # #         self.terminal_output.setReadOnly(True)
# # # #         self.terminal_output.setMinimumSize(0, 0) # Allow shrinking

# # # #         self.terminal_input = TerminalInput()
# # # #         self.terminal_input.setFont(code_font)
# # # #         self.terminal_input.setPlaceholderText(">>> Type Python command and press Enter (Use Arrows for History)")
# # # #         self.terminal_input.returnPressed.connect(self.execute_terminal_command)

# # # #         term_layout.addWidget(self.terminal_output)
# # # #         term_layout.addWidget(self.terminal_input)
# # # #         self.dock_terminal.setWidget(term_widget)
# # # #         self.dock_terminal.setMinimumSize(0, 0)
# # # #         self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_terminal)
# # # #         self.dock_menu.addAction(self.dock_terminal.toggleViewAction())

# # # #         self.update_tabs()

# # # #     def auto_generate_pipeline(self):
# # # #         if analyze_workbook is None:
# # # #             QMessageBox.critical(self, "Error", "xlwings is required for Auto-Generation. Please run 'pip install xlwings'.")
# # # #             return

# # # #         file_path, _ = QFileDialog.getOpenFileName(self, "Select Excel to Reverse-Engineer", "", "Excel Files (*.xlsx *.xlsm)")
# # # #         if not file_path: return

# # # #         # Show a "please wait" message because COM automation can be slow
# # # #         self.analysis_msg = QMessageBox(self)
# # # #         self.analysis_msg.setWindowTitle("Working...")
# # # #         self.analysis_msg.setText("🔍 Analyzing workbook structure and formulas...\nPlease wait, this may take a moment.")
# # # #         self.analysis_msg.setStandardButtons(QMessageBox.NoButton)
# # # #         self.analysis_msg.show()

# # # #         self.analysis_worker = ExcelAnalysisWorker(file_path)
# # # #         self.analysis_worker.result_ready.connect(self.on_analysis_success)
# # # #         self.analysis_worker.error_occurred.connect(self.on_analysis_error)
# # # #         self.analysis_worker.start()

# # # #     def on_analysis_success(self, config):
# # # #         if hasattr(self, 'analysis_msg'):
# # # #             self.analysis_msg.done(0)
# # # #             self.analysis_msg.close()
        
# # # #         QApplication.processEvents()
        
# # # #         # Save the new config automatically
# # # #         config_dir = "Config"
# # # #         if not os.path.exists(config_dir): os.makedirs(config_dir)

# # # #         save_path = os.path.join(config_dir, f"{config['pipeline_name']}.json")
# # # #         with open(save_path, 'w') as f:
# # # #             json.dump(config, f, indent=4)

# # # #         QMessageBox.information(self, "Success", f"Pipeline successfully generated from Excel!\n\nSaved to: {save_path}\n\nAny unsupported features (like Pivot Tables) have been marked as TODO steps for you to fix.")
# # # #         self.show_editor(save_path)

# # # #     def on_analysis_error(self, err_msg):
# # # #         if hasattr(self, 'analysis_msg'):
# # # #             self.analysis_msg.done(0)
# # # #             self.analysis_msg.close()
        
# # # #         QApplication.processEvents()
# # # #         QMessageBox.critical(self, "Reverse Engineering Error", f"Failed to analyze workbook:\n{err_msg}")

# # # #     def on_view_combo_changed(self, idx):
# # # #         if idx >= 0 and idx < self.tabs.count():
# # # #             self.tabs.blockSignals(True)
# # # #             self.tabs.setCurrentIndex(idx)
# # # #             self.tabs.blockSignals(False)

# # # #     def on_tab_changed(self, idx):
# # # #         if idx >= 0 and idx < self.combo_view.count():
# # # #             self.combo_view.blockSignals(True)
# # # #             self.combo_view.setCurrentIndex(idx)
# # # #             self.combo_view.blockSignals(False)

# # # #     def configure_export(self):
# # # #         pipeline_dfs = set()
# # # #         for proc in self.processes.values():
# # # #             for step in proc:
# # # #                 if step["action"] == "load_file":
# # # #                     pipeline_dfs.add(step["params"].get("alias"))
        
# # # #         all_possible = sorted(list(set(self.global_dfs.keys()) | pipeline_dfs | set(self.export_dfs)))
        
# # # #         dlg = ExportConfigDialog(all_possible, self.export_dfs, self)
# # # #         if dlg.exec_() == QDialog.Accepted:
# # # #             self.export_dfs = dlg.get_selected()
# # # #             QMessageBox.information(self, "Saved", f"Export configuration updated.\n\n{len(self.export_dfs)} DataFrames will be written to Excel in headless mode.")

# # # #     def browse_script(self):
# # # #         file_path, _ = QFileDialog.getOpenFileName(self, "Select Python Script", "", "Python Files (*.py);;All Files (*)")
# # # #         if file_path:
# # # #             # Task 2: Copy to Custom_Scripts
# # # #             custom_dir = "Custom_Scripts"
# # # #             if not os.path.exists(custom_dir):
# # # #                 os.makedirs(custom_dir)
            
# # # #             dest_path = os.path.join(custom_dir, os.path.basename(file_path))
            
# # # #             # Check if source and dest are different
# # # #             if os.path.abspath(file_path) != os.path.abspath(dest_path):
# # # #                 try:
# # # #                     shutil.copy2(file_path, dest_path)
# # # #                     if hasattr(self, 'terminal_output'):
# # # #                         self.terminal_output.append(f"\n>>> Copied external script to local project: {dest_path}")
# # # #                 except Exception as e:
# # # #                     QMessageBox.warning(self, "Copy Error", f"Could not copy script to Custom_Scripts:\n{e}")
            
# # # #             self.txt_script_path.setText(dest_path)

# # # #     def execute_terminal_command(self):
# # # #         cmd = self.terminal_input.text()
# # # #         if not cmd.strip(): return
        
# # # #         self.terminal_input.add_to_history(cmd)
# # # #         self.terminal_output.append(f"\n>>> {cmd}")
# # # #         self.terminal_input.clear()
        
# # # #         env = {**self.preview_dfs, **self.preview_vars, 'pd': pd, 'np': np, 'os': os, 'prompt_file': prompt_file}
# # # #         output = io.StringIO()
# # # #         ui_needs_update = False
        
# # # #         with contextlib.redirect_stdout(output):
# # # #             try:
# # # #                 res = eval(cmd, {}, env)
# # # #                 if res is not None:
# # # #                     print(res)
# # # #             except SyntaxError:
# # # #                 try:
# # # #                     exec(cmd, env, env)
# # # #                     ui_needs_update = True
# # # #                 except Exception as e:
# # # #                     print(f"Error: {e}")
# # # #             except Exception as e:
# # # #                 print(f"Error: {e}")
                
# # # #         result_text = output.getvalue().strip()
# # # #         if result_text:
# # # #             self.terminal_output.append(result_text)
            
# # # #         scrollbar = self.terminal_output.verticalScrollBar()
# # # #         scrollbar.setValue(scrollbar.maximum())
        
# # # #         if ui_needs_update:
# # # #             self.preview_dfs = {k: v for k, v in env.items() if isinstance(v, pd.DataFrame)}
# # # #             self.preview_vars = {k: v for k, v in env.items() if not isinstance(v, pd.DataFrame) and not callable(v) and not k.startswith('_') and str(type(v).__module__) == 'builtins'}
# # # #             self.update_tabs()

# # # #     def add_process(self):
# # # #         name, ok = QInputDialog.getText(self, "New Process", "Enter name for new Pipeline/Process:")
# # # #         if ok and name.strip() and name not in self.processes:
# # # #             self.processes[name.strip()] = []
# # # #             self.combo_processes.addItem(name.strip())
# # # #             self.combo_processes.setCurrentText(name.strip())

# # # #     def delete_process(self):
# # # #         if len(self.processes) <= 1:
# # # #             QMessageBox.warning(self, "Cannot Delete", "You must have at least one active process.")
# # # #             return
            
# # # #         reply = QMessageBox.question(self, 'Delete Process', f"Are you sure you want to delete '{self.current_process}' and all its steps?",
# # # #                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
# # # #         if reply == QMessageBox.Yes:
# # # #             del self.processes[self.current_process]
# # # #             idx = self.combo_processes.currentIndex()
# # # #             self.combo_processes.removeItem(idx)

# # # #     def switch_process(self, process_name):
# # # #         if not process_name: return
# # # #         self.current_process = process_name
# # # #         self.refresh_step_list()

# # # #     def refresh_step_list(self):
# # # #         self.list_steps.clear()
# # # #         if self.current_process in self.processes:
# # # #             for step in self.processes[self.current_process]:
# # # #                 prompt_flag = " [Prompt at Runtime]" if step.get('params', {}).get('prompt_at_runtime') else ""
# # # #                 self.list_steps.addItem(f"[{step['step_id']}] {step['action']}{prompt_flag}")

# # # #     def toggle_inputs(self):
# # # #         action = self.combo_action.currentText()
# # # #         self.txt_python.setVisible(action == "Execute Raw Python/Pandas")
# # # #         self.widget_excel_formula.setVisible("Excel Formula" in action)
# # # #         self.widget_script_path.setVisible("External" in action)

# # # #     def load_data(self):
# # # #         file_path, _ = QFileDialog.getOpenFileName(self, "Select Excel/CSV", "", "Data Files (*.xlsx *.csv)")
# # # #         if not file_path: return

# # # #         sheet_name = 0
# # # #         if file_path.endswith('.xlsx'):
# # # #             try:
# # # #                 xl = pd.ExcelFile(file_path)
# # # #                 sheet_name, ok = QInputDialog.getItem(self, "Select Sheet", "Select sheet:", xl.sheet_names, 0, False)
# # # #                 if not ok: return
# # # #             except Exception as e:
# # # #                 QMessageBox.critical(self, "Error", str(e))
# # # #                 return

# # # #         alias, ok = QInputDialog.getText(self, "DataFrame Alias", "Variable name (e.g. df1):")
# # # #         if not ok or not alias.strip(): return
# # # #         alias = alias.strip()

# # # #         reply = QMessageBox.question(self, 'Dynamic Input',
# # # #                                      f"When this pipeline runs automatically in the future, should it STOP and prompt the user to select the file for '{alias}'?",
# # # #                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
# # # #         prompt_at_runtime = (reply == QMessageBox.Yes)

# # # #         try:
# # # #             df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path, sheet_name=sheet_name)
            
# # # #             self.global_dfs[alias] = df
# # # #             self.preview_dfs = self.global_dfs.copy()
# # # #             self.update_tabs()
            
# # # #             step = {
# # # #                 "step_id": len(self.processes[self.current_process]) + 1,
# # # #                 "action": "load_file",
# # # #                 "params": {"filepath": file_path, "sheet": sheet_name, "alias": alias, "prompt_at_runtime": prompt_at_runtime}
# # # #             }
# # # #             self.processes[self.current_process].append(step)
# # # #             self.refresh_step_list()
            
# # # #         except Exception as e:
# # # #             QMessageBox.critical(self, "Error", str(e))

# # # #     def load_existing_file_data(self):
# # # #         active_files = set()
# # # #         for proc in self.processes.values():
# # # #             for step in proc:
# # # #                 if step.get("action") == "load_file":
# # # #                     fp = step.get("params", {}).get("filepath")
# # # #                     if fp and fp.endswith(('.xlsx', '.xlsm')):
# # # #                         active_files.add(fp)
        
# # # #         if not active_files:
# # # #             QMessageBox.information(self, "No Active Files", "No Excel files are currently loaded.")
# # # #             return
            
# # # #         file_path, ok = QInputDialog.getItem(self, "Select Existing File", "Choose an Excel file:", list(active_files), 0, False)
# # # #         if not ok: return
        
# # # #         try:
# # # #             xl = pd.ExcelFile(file_path)
# # # #             sheet_name, ok = QInputDialog.getItem(self, "Select Sheet", f"Select sheet:", xl.sheet_names, 0, False)
# # # #             if not ok: return
# # # #         except Exception as e:
# # # #             QMessageBox.critical(self, "Error", f"Could not read file: {e}")
# # # #             return
            
# # # #         alias, ok = QInputDialog.getText(self, "DataFrame Alias", "Variable name:")
# # # #         if not ok or not alias.strip(): return
# # # #         alias = alias.strip()

# # # #         reply = QMessageBox.question(self, 'Dynamic Input',
# # # #                                      f"Prompt user to select file for '{alias}'?",
# # # #                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
# # # #         prompt_at_runtime = (reply == QMessageBox.Yes)

# # # #         try:
# # # #             df = pd.read_excel(file_path, sheet_name=sheet_name)
# # # #             self.global_dfs[alias] = df
# # # #             self.preview_dfs = self.global_dfs.copy()
# # # #             self.update_tabs()
            
# # # #             step = {
# # # #                 "step_id": len(self.processes[self.current_process]) + 1,
# # # #                 "action": "load_file",
# # # #                 "params": {"filepath": file_path, "sheet": sheet_name, "alias": alias, "prompt_at_runtime": prompt_at_runtime}
# # # #             }
# # # #             self.processes[self.current_process].append(step)
# # # #             self.refresh_step_list()
# # # #         except Exception as e:
# # # #             QMessageBox.critical(self, "Error", str(e))

# # # #     def update_tabs(self):
# # # #         self.tabs.clear()
# # # #         self.combo_view.blockSignals(True)
# # # #         self.combo_view.clear()
        
# # # #         var_table = QTableWidget(len(self.preview_vars), 3)
# # # #         var_table.setHorizontalHeaderLabels(["Variable Name", "Type", "Value"])
# # # #         var_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
# # # #         var_table.verticalHeader().setVisible(False)
        
# # # #         row = 0
# # # #         for k, v in self.preview_vars.items():
# # # #             var_table.setItem(row, 0, QTableWidgetItem(str(k)))
# # # #             var_table.setItem(row, 1, QTableWidgetItem(type(v).__name__))
# # # #             var_table.setItem(row, 2, QTableWidgetItem(str(v)[:100]))
# # # #             row += 1
            
# # # #         self.tabs.addTab(var_table, "📦 Variables Explorer")
# # # #         self.combo_view.addItem("📦 Variables Explorer")

# # # #         for alias, df in self.preview_dfs.items():
# # # #             table = QTableView()
# # # #             table.setModel(PandasModel(df))
# # # #             table.verticalHeader().setVisible(False)
# # # #             table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
# # # #             table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
# # # #             table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
# # # #             table.horizontalHeader().setDefaultSectionSize(120)
            
# # # #             self.tabs.addTab(table, f"📊 DF: {alias}")
# # # #             self.combo_view.addItem(f"📊 DF: {alias}")
            
# # # #         self.combo_view.blockSignals(False)
# # # #         self.lbl_context.setText(f"Context: DFs ({len(self.preview_dfs)}) | Vars ({len(self.preview_vars)})")

# # # #     def get_editor_step_data(self):
# # # #         action_type = self.combo_action.currentText()
# # # #         step = {"action": ""}
# # # #         if action_type == "Execute Raw Python/Pandas":
# # # #             step["action"] = "execute_python_logic"
# # # #             step["params"] = {"code_block": self.txt_python.toPlainText()}
# # # #         elif action_type == "Evaluate Excel Formula (Native Math)":
# # # #             step["action"] = "evaluate_excel_formula"
# # # #             step["params"] = {
# # # #                 "formula": self.txt_excel_formula.toPlainText(),
# # # #                 "target_alias": self.txt_excel_target.text(),
# # # #                 "target_col": self.txt_excel_column.text() if self.txt_excel_column.text().strip() else None
# # # #             }
# # # #         elif action_type == "Run External .py Script (Entire File)":
# # # #             step["action"] = "run_python_file"
# # # #             step["params"] = {"script_path": self.txt_script_path.text()}
# # # #         return step

# # # #     def test_step(self):
# # # #         step = self.get_editor_step_data()
# # # #         if not step["params"].get("code_block") and step["action"] == "execute_python_logic": return
        
# # # #         self.pending_step = step
# # # #         self.worker = StepPreviewWorker(self.global_dfs, self.global_vars, step)
# # # #         self.worker.result_ready.connect(self.on_test_success)
# # # #         self.worker.error_occurred.connect(self.on_test_error)
# # # #         self.worker.start()

# # # #     def on_test_success(self, new_dfs, new_vars):
# # # #         self.preview_dfs = new_dfs
# # # #         self.preview_vars = new_vars
# # # #         self.update_tabs()
# # # #         QMessageBox.information(self, "Test Passed", "Code executed!")

# # # #     def on_test_error(self, err_msg):
# # # #         QMessageBox.critical(self, "Logic Error", f"Failed to execute:\n\n{err_msg}")

# # # #     # FIX: Allows you to instantly record what is in the editor without having to run "Test" first
# # # #     def record_step(self):
# # # #         step = self.get_editor_step_data()
        
# # # #         # Validation
# # # #         if step["action"] == "execute_python_logic" and not step["params"].get("code_block", "").strip():
# # # #             QMessageBox.warning(self, "Warning", "Code block is empty!")
# # # #             return
# # # #         elif step["action"] == "run_python_file" and not step["params"].get("script_path", "").strip():
# # # #             QMessageBox.warning(self, "Warning", "Script path is empty!")
# # # #             return
            
# # # #         step["step_id"] = len(self.processes[self.current_process]) + 1
# # # #         self.processes[self.current_process].append(step)
        
# # # #         # If tested recently, commit state
# # # #         if self.pending_step:
# # # #             self.global_dfs = self.preview_dfs.copy()
# # # #             self.global_vars = self.preview_vars.copy()
# # # #             self.pending_step = None
            
# # # #         self.refresh_step_list()
# # # #         QMessageBox.information(self, "Recorded", f"Step '{step['action']}' successfully recorded.")

# # # #     def load_step_into_editor(self, item):
# # # #         row_idx = self.list_steps.row(item)
# # # #         step = self.processes[self.current_process][row_idx]
        
# # # #         if step["action"] == "execute_python_logic":
# # # #             self.combo_action.setCurrentText("Execute Raw Python/Pandas")
# # # #             self.txt_python.setPlainText(step["params"].get("code_block", ""))
# # # #         elif step["action"] == "evaluate_excel_formula":
# # # #             self.combo_action.setCurrentText("Evaluate Excel Formula (Native Math)")
# # # #             self.txt_excel_formula.setPlainText(step["params"].get("formula", ""))
# # # #             self.txt_excel_target.setText(step["params"].get("target_alias", ""))
# # # #             self.txt_excel_column.setText(step["params"].get("target_col", ""))
# # # #         elif step["action"] == "run_python_file":
# # # #             self.combo_action.setCurrentText("Run External .py Script (Entire File)")
# # # #             self.txt_script_path.setText(step["params"].get("script_path", ""))

# # # #     # FIX: Allows you to grab the live editor content and seamlessly overwrite the selected list item
# # # #     def update_selected_step(self):
# # # #         current_item = self.list_steps.currentItem()
# # # #         if not current_item:
# # # #             QMessageBox.warning(self, "Warning", "Please select a step from the list to update.")
# # # #             return
            
# # # #         row_idx = self.list_steps.row(current_item)
# # # #         original_step = self.processes[self.current_process][row_idx]
        
# # # #         if original_step["action"] == "load_file":
# # # #             active_files = set()
# # # #             for proc in self.processes.values():
# # # #                 for s in proc:
# # # #                     if s.get("action") == "load_file":
# # # #                         fp = s.get("params", {}).get("filepath")
# # # #                         if fp: active_files.add(fp)
# # # #             dialog = EditLoadDialog(original_step.get("params", {}), list(active_files), self)
# # # #             if dialog.exec_() == QDialog.Accepted:
# # # #                 original_step["params"] = dialog.get_params()
# # # #                 self.processes[self.current_process][row_idx] = original_step
# # # #                 self.refresh_step_list()
# # # #             return
            
# # # #         new_step_data = self.get_editor_step_data()
        
# # # #         # Validation
# # # #         if new_step_data["action"] == "execute_python_logic" and not new_step_data["params"].get("code_block", "").strip():
# # # #             QMessageBox.warning(self, "Warning", "Code block is empty!")
# # # #             return
            
# # # #         new_step_data["step_id"] = original_step["step_id"]
# # # #         self.processes[self.current_process][row_idx] = new_step_data
# # # #         self.refresh_step_list()
        
# # # #         QMessageBox.information(self, "Success", "Step updated successfully. (Note: Run the pipeline to refresh the visual state)")

# # # #     def delete_step(self):
# # # #         current_item = self.list_steps.currentItem()
# # # #         if not current_item: return
# # # #         row_idx = self.list_steps.row(current_item)
# # # #         if QMessageBox.question(self, 'Delete', "Delete this step?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
# # # #             del self.processes[self.current_process][row_idx]
# # # #             for i, step in enumerate(self.processes[self.current_process]):
# # # #                 step["step_id"] = i + 1
# # # #             self.refresh_step_list()

# # # #     def run_full_restore(self, export_path=None):
# # # #         if not any(self.processes.values()): return
# # # #         self.last_export_path = export_path
# # # #         self.terminal_output.append("\n>>> Restoring Pipeline Data...")
# # # #         self.restore_worker = PipelineRestoreWorker(self.processes)
# # # #         self.restore_worker.progress_update.connect(self.terminal_output.append)
# # # #         self.restore_worker.result_ready.connect(self.on_restore_success)
# # # #         self.restore_worker.error_occurred.connect(self.on_restore_error)
# # # #         self.restore_worker.start()

# # # #     def on_restore_success(self, dfs, vars):
# # # #         self.global_dfs, self.global_vars = dfs.copy(), vars.copy()
# # # #         self.preview_dfs, self.preview_vars = dfs.copy(), vars.copy()
# # # #         self.update_tabs()
# # # #         self.terminal_output.append(">>> Success!")
        
# # # #         if hasattr(self, 'last_export_path') and self.last_export_path:
# # # #             self.terminal_output.append(f">>> Exporting results to: {self.last_export_path}")
# # # #             try:
# # # #                 output_file = os.path.join(self.last_export_path, 'Final_Pipeline_Output.xlsx')
# # # #                 with pd.ExcelWriter(output_file) as writer:
# # # #                     exported_count = 0
# # # #                     for alias, df in dfs.items():
# # # #                         if not self.export_dfs or alias in self.export_dfs:
# # # #                             df.to_excel(writer, sheet_name=str(alias)[:31], index=False)
# # # #                             exported_count += 1
# # # #                 self.terminal_output.append(f">>> Export Complete: {exported_count} DataFrames saved.")
# # # #             except Exception as e:
# # # #                 self.terminal_output.append(f">>> Export Error: {e}")
# # # #             self.last_export_path = None

# # # #     def on_restore_error(self, err):
# # # #         self.terminal_output.append(f">>> Error: {err}")

# # # #     def load_config_from_path(self, file_path):
# # # #         try:
# # # #             with open(file_path, 'r') as f:
# # # #                 config = json.load(f)
# # # #             self.processes = config["processes"]
# # # #             self.export_dfs = config.get("export_dfs", [])
# # # #             self.current_config_path = file_path
            
# # # #             self.combo_processes.blockSignals(True)
# # # #             self.combo_processes.clear()
# # # #             for n in self.processes.keys():
# # # #                 self.combo_processes.addItem(n)
# # # #             self.current_process = list(self.processes.keys())[0]
# # # #             self.combo_processes.setCurrentText(self.current_process)
# # # #             self.combo_processes.blockSignals(False)
            
# # # #             self.refresh_step_list()
# # # #             self.update_tabs()
# # # #         except Exception as e:
# # # #             QMessageBox.critical(self, "Error", f"Could not load config:\n{e}")

# # # #     def load_config(self):
# # # #         file_path, _ = QFileDialog.getOpenFileName(self, "Load Config", "Config", "JSON Files (*.json)")
# # # #         if file_path:
# # # #             self.load_config_from_path(file_path)
# # # #             if QMessageBox.question(self, 'Restore', "Run pipeline now?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
# # # #                 self.run_full_restore()

# # # #     def save_config(self):
# # # #         default_name = self.current_config_path or "Config/Master_Config.json"
# # # #         file_path, _ = QFileDialog.getSaveFileName(self, "Save Pipeline", default_name, "JSON Files (*.json)")
# # # #         if file_path:
# # # #             config = {
# # # #                 "pipeline_name": os.path.splitext(os.path.basename(file_path))[0], 
# # # #                 "export_dfs": self.export_dfs, 
# # # #                 "processes": self.processes
# # # #             }
# # # #             with open(file_path, 'w') as f:
# # # #                 json.dump(config, f, indent=4)
# # # #             self.current_config_path = file_path
# # # #             self.setWindowTitle(f"Pipeline Editor - {os.path.basename(file_path)}")
# # # #             QMessageBox.information(self, "Saved", f"Saved to {file_path}.")

# # # # if __name__ == "__main__":
# # # #     app = QApplication(sys.argv)
# # # #     window = ScorecardUI()
# # # #     window.show()
# # # #     sys.exit(app.exec_())




# # # # ==============================================================================
# # # # FILE LOCATION: Dynamic_Scorecard_System/scorecard_ui.py
# # # # ==============================================================================

# # # import sys
# # # import json
# # # import traceback
# # # import os
import threading
from concurrent.futures import ThreadPoolExecutor
# # # import io
# # # import contextlib
# # # import shutil
# # # import pandas as pd
# # # import numpy as np

# # # # Force the working directory to be where the EXE is located (or script if running raw)
# # # if getattr(sys, 'frozen', False):
# # #     application_path = os.path.dirname(sys.executable)
# # # else:
# # #     application_path = os.path.dirname(os.path.abspath(__file__))

# # # os.chdir(application_path)

# # # from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
# # #                              QHBoxLayout, QPushButton, QLabel, QFileDialog, 
# # #                              QTableView, QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem,
# # #                              QComboBox, QTextEdit, QLineEdit, QMessageBox, QGroupBox, 
# # #                              QInputDialog, QTabWidget, QHeaderView, QSplitter, QAction,
# # #                              QDialog, QFormLayout, QCheckBox, QDialogButtonBox, QAbstractItemView,
# # #                              QDockWidget, QStackedWidget, QScrollArea, QFrame, QGridLayout)
# # # from PyQt5.QtCore import QAbstractTableModel, Qt, QThread, pyqtSignal, QEvent, QTimer
# # # from PyQt5.QtGui import QFont

# # # # Make sure these are accessible in your environment
# # # try:
# # #     from dynamic_engine import DynamicPipelineEngine, prompt_file
# # # except ImportError:
# # #     # Dummy classes to allow UI to run if engine isn't present
# # #     class DynamicPipelineEngine: pass
# # #     prompt_file = None

# # # try:
# # #     from excel_analyzer import analyze_workbook
# # # except ImportError:
# # #     analyze_workbook = None

# # # class TerminalInput(QLineEdit):
# # #     """Enhanced QLineEdit with command history (Up/Down arrows)"""
# # #     def __init__(self, *args, **kwargs):
# # #         super().__init__(*args, **kwargs)
# # #         self.history = []
# # #         self.history_index = -1
# # #         self.temp_cmd = ""

# # #     def keyPressEvent(self, event):
# # #         if event.key() == Qt.Key_Up:
# # #             if not self.history:
# # #                 return
# # #             if self.history_index == -1:
# # #                 self.temp_cmd = self.text()
            
# # #             if self.history_index < len(self.history) - 1:
# # #                 self.history_index += 1
# # #                 self.setText(self.history[self.history_index])
        
# # #         elif event.key() == Qt.Key_Down:
# # #             if self.history_index > -1:
# # #                 self.history_index -= 1
# # #                 if self.history_index == -1:
# # #                     self.setText(self.temp_cmd)
# # #                 else:
# # #                     self.setText(self.history[self.history_index])
        
# # #         else:
# # #             super().keyPressEvent(event)
# # #             if event.key() != Qt.Key_Return and event.key() != Qt.Key_Enter:
# # #                 self.history_index = -1

# # #     def add_to_history(self, cmd):
# # #         if cmd.strip():
# # #             # Remove existing occurrence to move it to the front
# # #             if cmd in self.history:
# # #                 self.history.remove(cmd)
# # #             self.history.insert(0, cmd)
# # #         self.history_index = -1
# # #         self.temp_cmd = ""

# # # class PandasModel(QAbstractTableModel):
# # #     def __init__(self, data):
# # #         super().__init__()
# # #         self._data = data

# # #     def rowCount(self, parent=None): return self._data.shape[0]
# # #     def columnCount(self, parent=None): return self._data.shape[1]
# # #     def data(self, index, role=Qt.DisplayRole):
# # #         if index.isValid() and role == Qt.DisplayRole:
# # #             val = self._data.iloc[index.row(), index.column()]
# # #             return str(val) if not pd.isna(val) else ""
# # #         return None
# # #     def headerData(self, col, orientation, role):
# # #         if orientation == Qt.Horizontal and role == Qt.DisplayRole:
# # #             return str(self._data.columns[col])
# # #         return None

# # # class StepPreviewWorker(QThread):
# # #     result_ready = pyqtSignal(dict, dict)
# # #     error_occurred = pyqtSignal(str)

# # #     def __init__(self, dfs_dict, vars_dict, step):
# # #         super().__init__()
# # #         self.dfs_dict = {k: v.copy() for k, v in dfs_dict.items()}
# # #         self.vars_dict = {k: v for k, v in vars_dict.items()}
# # #         self.step = step
# # #         self.engine = DynamicPipelineEngine()

# # #     def run(self):
# # #         try:
# # #             new_dfs, new_vars = self.engine._apply_step(self.dfs_dict, self.vars_dict, self.step)
# # #             self.result_ready.emit(new_dfs, new_vars)
# # #         except Exception as e:
# # #             self.error_occurred.emit(traceback.format_exc())

# # # class PipelineRestoreWorker(QThread):
# # #     progress_update = pyqtSignal(str)
# # #     result_ready = pyqtSignal(dict, dict)
# # #     error_occurred = pyqtSignal(str)

# # #     def __init__(self, processes):
# # #         super().__init__()
# # #         self.processes = processes
# # #         self.engine = DynamicPipelineEngine()

# # #     def run(self):
# # #         dfs_dict = {}
# # #         vars_dict = {}
# # #         try:
# # #             for proc_name, steps in self.processes.items():
# # #                 self.progress_update.emit(f"\n--- Running Process: {proc_name} ---")
# # #                 for step in steps:
# # #                     self.progress_update.emit(f">>> Executing [{step['step_id']}] {step['action']}...")
                    
# # #                     original_prompt = step.get('params', {}).get('prompt_at_runtime', False)
# # #                     if 'params' in step:
# # #                         step['params']['prompt_at_runtime'] = False
                        
# # #                     dfs_dict, vars_dict = self.engine._apply_step(dfs_dict, vars_dict, step)
                    
# # #                     if 'params' in step:
# # #                         step['params']['prompt_at_runtime'] = original_prompt

# # #             self.result_ready.emit(dfs_dict, vars_dict)
# # #         except Exception as e:
# # #             self.error_occurred.emit(traceback.format_exc())

# # # class ExcelAnalysisWorker(QThread):
# # #     result_ready = pyqtSignal(dict)
# # #     error_occurred = pyqtSignal(str)

# # #     def __init__(self, file_path):
# # #         super().__init__()
# # #         self.file_path = file_path

# # #     def run(self):
# # #         try:
# # #             config = analyze_workbook(self.file_path)
# # #             self.result_ready.emit(config)
# # #         except Exception as e:
# # #             self.error_occurred.emit(str(e))

# # # class ExportConfigDialog(QDialog):
# # #     """Custom Dialog for selecting which DataFrames to export to Excel"""
# # #     def __init__(self, all_dfs, selected_dfs, parent=None):
# # #         super().__init__(parent)
# # #         self.setWindowTitle("Configure Headless Export")
# # #         self.resize(450, 500) # Sets a default size allowing space for lists
        
# # #         layout = QVBoxLayout(self)
        
# # #         if not all_dfs:
# # #             layout.addWidget(QLabel("No DataFrames currently available.\nRun the pipeline or load data first."))
# # #         else:
# # #             header_lbl = QLabel("Select which DataFrames to export to Excel\nduring automated Headless execution:")
# # #             header_lbl.setStyleSheet("margin-bottom: 5px;")
# # #             layout.addWidget(header_lbl)
            
# # #             # Action Buttons for Quick Selection
# # #             btn_layout = QHBoxLayout()
# # #             btn_select_all = QPushButton("☑ Select All")
# # #             btn_select_all.clicked.connect(self.select_all)
# # #             btn_deselect_all = QPushButton("☐ Deselect All")
# # #             btn_deselect_all.clicked.connect(self.deselect_all)
            
# # #             btn_layout.addWidget(btn_select_all)
# # #             btn_layout.addWidget(btn_deselect_all)
# # #             layout.addLayout(btn_layout)
            
# # #             # Scrollable List Widget with Checkboxes
# # #             self.list_widget = QListWidget()
# # #             self.list_widget.setSelectionMode(QAbstractItemView.NoSelection) # Prevent highlighting, rely purely on checkboxes
            
# # #             for df_name in all_dfs:
# # #                 item = QListWidgetItem(df_name)
# # #                 item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                
# # #                 # If selected_dfs is empty but we have dfs, default to checked (fallback)
# # #                 if df_name in selected_dfs or (not selected_dfs and df_name in all_dfs):
# # #                     item.setCheckState(Qt.Checked)
# # #                 else:
# # #                     item.setCheckState(Qt.Unchecked)
                    
# # #                 self.list_widget.addItem(item)
                
# # #             layout.addWidget(self.list_widget)
            
# # #         self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
# # #         self.buttons.accepted.connect(self.accept)
# # #         self.buttons.rejected.connect(self.reject)
# # #         layout.addWidget(self.buttons)

# # #     def select_all(self):
# # #         if hasattr(self, 'list_widget'):
# # #             for i in range(self.list_widget.count()):
# # #                 self.list_widget.item(i).setCheckState(Qt.Checked)
            
# # #     def deselect_all(self):
# # #         if hasattr(self, 'list_widget'):
# # #             for i in range(self.list_widget.count()):
# # #                 self.list_widget.item(i).setCheckState(Qt.Unchecked)

# # #     def get_selected(self):
# # #         if not hasattr(self, 'list_widget'):
# # #             return []
        
# # #         selected = []
# # #         for i in range(self.list_widget.count()):
# # #             item = self.list_widget.item(i)
# # #             if item.checkState() == Qt.Checked:
# # #                 selected.append(item.text())
# # #         return selected

# # # class EditLoadDialog(QDialog):
# # #     """Custom Dialog for editing an existing 'load_file' step"""
# # #     def __init__(self, step_params, active_files=None, parent=None):
# # #         super().__init__(parent)
# # #         self.active_files = active_files or []
# # #         self.setWindowTitle("Edit Load File Step")
# # #         self.setMinimumWidth(550)
        
# # #         layout = QFormLayout(self)
        
# # #         self.filepath_input = QLineEdit(step_params.get("filepath", ""))
        
# # #         # File Path Buttons
# # #         btn_layout = QHBoxLayout()
# # #         btn_layout.setContentsMargins(0, 0, 0, 0)
        
# # #         browse_btn = QPushButton("📁 Browse New")
# # #         browse_btn.clicked.connect(self.browse)
# # #         btn_layout.addWidget(browse_btn)
        
# # #         if self.active_files:
# # #             active_btn = QPushButton("📄 Select Active File")
# # #             active_btn.clicked.connect(self.select_active)
# # #             btn_layout.addWidget(active_btn)
            
# # #         fp_layout = QVBoxLayout()
# # #         fp_layout.setContentsMargins(0, 0, 0, 0)
# # #         fp_layout.addWidget(self.filepath_input)
# # #         fp_layout.addLayout(btn_layout)
        
# # #         layout.addRow("File Path:", fp_layout)
        
# # #         # Sheet Selection Layout
# # #         self.sheet_input = QLineEdit(str(step_params.get("sheet", 0)))
# # #         self.sheet_input.setPlaceholderText("0 for first sheet, or 'Sheet1'")
        
# # #         sheet_layout = QHBoxLayout()
# # #         sheet_layout.setContentsMargins(0, 0, 0, 0)
# # #         sheet_layout.addWidget(self.sheet_input)
        
# # #         inspect_btn = QPushButton("🔍 Select Sheet")
# # #         inspect_btn.clicked.connect(self.list_sheets)
# # #         sheet_layout.addWidget(inspect_btn)
        
# # #         layout.addRow("Sheet Name/Index:", sheet_layout)
        
# # #         self.alias_input = QLineEdit(step_params.get("alias", ""))
# # #         layout.addRow("DataFrame Alias:", self.alias_input)
        
# # #         self.header_input = QLineEdit(str(step_params.get("header", 0)))
# # #         self.header_input.setPlaceholderText("0 for first row (default)")
# # #         layout.addRow("Header Row (Index):", self.header_input)
        
# # #         self.prompt_cb = QCheckBox("Prompt user to select this file at runtime (Filepath becomes a placeholder)")
# # #         self.prompt_cb.setChecked(step_params.get("prompt_at_runtime", False))
# # #         layout.addRow("", self.prompt_cb)
        
# # #         self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
# # #         self.buttons.accepted.connect(self.accept)
# # #         self.buttons.rejected.connect(self.reject)
# # #         layout.addRow(self.buttons)

# # #     def browse(self):
# # #         fp, _ = QFileDialog.getOpenFileName(self, "Select Excel/CSV", "", "Data Files (*.xlsx *.csv)")
# # #         if fp:
# # #             self.filepath_input.setText(fp)
            
# # #     def select_active(self):
# # #         if not self.active_files: return
# # #         fp, ok = QInputDialog.getItem(self, "Select Active File", "Choose an existing file from the pipeline:", self.active_files, 0, False)
# # #         if ok and fp:
# # #             self.filepath_input.setText(fp)

# # #     def list_sheets(self):
# # #         fp = self.filepath_input.text().strip()
# # #         if not fp or not os.path.exists(fp):
# # #             QMessageBox.warning(self, "File Not Found", "Cannot read sheets. Please ensure the file path is correct and accessible on your machine.")
# # #             return
# # #         if not fp.endswith(('.xlsx', '.xlsm')):
# # #             QMessageBox.information(self, "Not an Excel File", "Only Excel files have multiple sheets to select from.")
# # #             return
            
# # #         try:
# # #             xl = pd.ExcelFile(fp)
# # #             sheet, ok = QInputDialog.getItem(self, "Select Sheet", f"Available Sheets in {os.path.basename(fp)}:", xl.sheet_names, 0, False)
# # #             if ok and sheet:
# # #                 self.sheet_input.setText(sheet)
# # #         except Exception as e:
# # #             QMessageBox.critical(self, "Error", f"Could not read sheets:\n{e}")

# # #     def get_params(self):
# # #         sheet_val = self.sheet_input.text()
# # #         if sheet_val.isdigit():
# # #             sheet_val = int(sheet_val)
            
# # #         header_val = 0
# # #         if self.header_input.text().isdigit():
# # #             header_val = int(self.header_input.text())
            
# # #         fp = self.filepath_input.text().strip()
# # #         if not fp and self.prompt_cb.isChecked():
# # #             fp = "RUNTIME_PROMPT_ONLY.xlsx"
            
# # #         return {
# # #             "filepath": fp,
# # #             "sheet": sheet_val,
# # #             "header": header_val,
# # #             "alias": self.alias_input.text(),
# # #             "prompt_at_runtime": self.prompt_cb.isChecked()
# # #         }

# # # class ConfigCard(QGroupBox):
# # #     """A visually appealing card representing a pipeline configuration"""
# # #     edit_requested = pyqtSignal(str)
# # #     run_requested = pyqtSignal(str)
# # #     delete_requested = pyqtSignal(str)

# # #     def __init__(self, file_path, config_data):
# # #         title = config_data.get("pipeline_name", os.path.basename(file_path))
# # #         super().__init__(title)
# # #         self.file_path = file_path
# # #         self.setObjectName("ConfigCard")
        
# # #         layout = QVBoxLayout(self)
        
# # #         # Metadata
# # #         proc_count = len(config_data.get("processes", {}))
# # #         step_count = sum(len(steps) for steps in config_data.get("processes", {}).values())
        
# # #         self.info_lbl = QLabel(f"Processes: {proc_count} | Total Steps: {step_count}")
# # #         self.info_lbl.setObjectName("cardMetadata")
# # #         layout.addWidget(self.info_lbl)
        
# # #         self.path_lbl = QLabel(os.path.basename(file_path))
# # #         self.path_lbl.setObjectName("cardPath")
# # #         layout.addWidget(self.path_lbl)
        
# # #         layout.addStretch()
        
# # #         # Action Buttons
# # #         btn_layout = QHBoxLayout()
        
# # #         self.btn_run = QPushButton("▶ Run")
# # #         self.btn_run.setObjectName("btnSuccess")
# # #         self.btn_run.clicked.connect(lambda: self.run_requested.emit(self.file_path))
        
# # #         self.btn_edit = QPushButton("✏ Edit")
# # #         self.btn_edit.setObjectName("btnPrimary")
# # #         self.btn_edit.clicked.connect(lambda: self.edit_requested.emit(self.file_path))
        
# # #         self.btn_del = QPushButton("🗑")
# # #         self.btn_del.setObjectName("btnDanger")
# # #         self.btn_del.setFixedWidth(40)
# # #         self.btn_del.clicked.connect(lambda: self.delete_requested.emit(self.file_path))
        
# # #         btn_layout.addWidget(self.btn_run)
# # #         btn_layout.addWidget(self.btn_edit)
# # #         btn_layout.addWidget(self.btn_del)
        
# # #         layout.addLayout(btn_layout)

# # # class DashboardWidget(QWidget):
# # #     """The landing screen for the application"""
# # #     create_new_requested = pyqtSignal()
# # #     auto_generate_requested = pyqtSignal()
# # #     edit_config_requested = pyqtSignal(str)
# # #     run_config_requested = pyqtSignal(str)

# # #     def __init__(self, parent=None):
# # #         super().__init__(parent)
# # #         self.init_ui()

# # #     def init_ui(self):
# # #         main_layout = QVBoxLayout(self)
# # #         main_layout.setContentsMargins(40, 40, 40, 40)
# # #         main_layout.setSpacing(20)
        
# # #         # Header
# # #         header_layout = QHBoxLayout()
# # #         self.title_lbl = QLabel("Dynamic Scorecard System")
# # #         self.title_lbl.setObjectName("mainTitle")
# # #         header_layout.addWidget(self.title_lbl)
        
# # #         header_layout.addStretch()
        
# # #         self.btn_new = QPushButton("➕ Create New Configuration")
# # #         self.btn_new.setObjectName("btnPrimary")
# # #         self.btn_new.setMinimumHeight(50)
# # #         self.btn_new.clicked.connect(self.create_new_requested.emit)
# # #         header_layout.addWidget(self.btn_new)
        
# # #         self.btn_auto = QPushButton("🪄 Auto-Generate from Excel")
# # #         self.btn_auto.setObjectName("btnSuccess")
# # #         self.btn_auto.setMinimumHeight(50)
# # #         self.btn_auto.clicked.connect(self.auto_generate_requested.emit)
# # #         header_layout.addWidget(self.btn_auto)
        
# # #         self.btn_import_config = QPushButton("📥 Import Config")
# # #         self.btn_import_config.setMinimumHeight(50)
# # #         self.btn_import_config.clicked.connect(self.import_config)
# # #         header_layout.addWidget(self.btn_import_config)
        
# # #         self.btn_refresh = QPushButton("🔄 Refresh")
# # #         self.btn_refresh.setMinimumHeight(50)
# # #         self.btn_refresh.setFixedWidth(120)
# # #         self.btn_refresh.clicked.connect(self.refresh_configs)
# # #         header_layout.addWidget(self.btn_refresh)
        
# # #         main_layout.addLayout(header_layout)
        
# # #         # Divider
# # #         self.divider = QFrame()
# # #         self.divider.setObjectName("mainDivider")
# # #         self.divider.setFrameShape(QFrame.HLine)
# # #         self.divider.setFrameShadow(QFrame.Sunken)
# # #         main_layout.addWidget(self.divider)
        
# # #         # Scroll Area for Configs
# # #         self.scroll = QScrollArea()
# # #         self.scroll.setObjectName("dashboardScroll")
# # #         self.scroll.setWidgetResizable(True)
        
# # #         self.container = QWidget()
# # #         self.container.setObjectName("dashboardContainer")
# # #         self.flow_layout = QGridLayout(self.container) # Using grid for card layout
# # #         self.flow_layout.setSpacing(20)
        
# # #         self.scroll.setWidget(self.container)
# # #         main_layout.addWidget(self.scroll)
        
# # #         self.refresh_configs()

# # #     def import_config(self):
# # #         file_path, _ = QFileDialog.getOpenFileName(self, "Select Configuration to Import", "", "JSON Files (*.json)")
# # #         if file_path:
# # #             config_dir = "Config"
# # #             if not os.path.exists(config_dir):
# # #                 os.makedirs(config_dir)
# # #             dest_path = os.path.join(config_dir, os.path.basename(file_path))
# # #             if os.path.abspath(file_path) != os.path.abspath(dest_path):
# # #                 try:
# # #                     shutil.copy2(file_path, dest_path)
# # #                     QMessageBox.information(self, "Success", f"Config imported into application:\n{dest_path}")
# # #                     self.refresh_configs()
# # #                 except Exception as e:
# # #                     QMessageBox.critical(self, "Error", f"Could not import config:\n{e}")

# # #     def refresh_configs(self):
# # #         # Clear existing
# # #         for i in reversed(range(self.flow_layout.count())): 
# # #             self.flow_layout.itemAt(i).widget().setParent(None)
            
# # #         config_dir = "Config"
# # #         if not os.path.exists(config_dir):
# # #             os.makedirs(config_dir)
            
# # #         configs = [f for f in os.listdir(config_dir) if f.endswith(".json")]
        
# # #         if not configs:
# # #             empty_lbl = QLabel("No configurations found. Create your first pipeline to get started!")
# # #             empty_lbl.setAlignment(Qt.AlignCenter)
# # #             empty_lbl.setObjectName("emptyMsg")
# # #             self.flow_layout.addWidget(empty_lbl, 0, 0)
# # #             return

# # #         col_limit = 3
# # #         for idx, filename in enumerate(configs):
# # #             path = os.path.join(config_dir, filename)
# # #             try:
# # #                 with open(path, 'r') as f:
# # #                     data = json.load(f)
                
# # #                 card = ConfigCard(path, data)
# # #                 card.edit_requested.connect(self.edit_config_requested.emit)
# # #                 card.run_requested.connect(self.run_config_requested.emit)
# # #                 card.delete_requested.connect(self.delete_config)
                
# # #                 self.flow_layout.addWidget(card, idx // col_limit, idx % col_limit)
# # #             except Exception as e:
# # #                 print(f"Error loading {filename}: {e}")

# # #     def delete_config(self, path):
# # #         reply = QMessageBox.question(self, 'Delete Configuration', 
# # #                                      f"Are you sure you want to delete '{os.path.basename(path)}'?\nThis cannot be undone.",
# # #                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
# # #         if reply == QMessageBox.Yes:
# # #             try:
# # #                 os.remove(path)
# # #                 self.refresh_configs()
# # #             except Exception as e:
# # #                 QMessageBox.critical(self, "Error", f"Could not delete file: {e}")

# # # class ScorecardUI(QMainWindow):
# # #     def __init__(self):
# # #         super().__init__()
# # #         self.setWindowTitle("Dynamic Scorecard System - Dashboard")
# # #         self.resize(1600, 1000)
        
# # #         self.processes = {"Main_Process": []} 
# # #         self.current_process = "Main_Process"
# # #         self.export_dfs = [] 
# # #         self.current_config_path = None
        
# # #         self.global_dfs = {}
# # #         self.global_vars = {}
# # #         self.preview_dfs = {} 
# # #         self.preview_vars = {}
# # #         self.pending_step = None 
        
# # #         # State Management
# # #         self.stacked_widget = QStackedWidget()
# # #         self.setCentralWidget(self.stacked_widget)
        
# # #         self.init_ui()
# # #         self.apply_dark_theme()
        
# # #         # Start at Dashboard
# # #         self.show_dashboard()

# # #     def show_dashboard(self):
# # #         self.dashboard.refresh_configs()
# # #         self.stacked_widget.setCurrentIndex(0)
# # #         self.setWindowTitle("Dynamic Scorecard System - Dashboard")
        
# # #         # Hide Editor Docks
# # #         self.dock_pipeline.hide()
# # #         self.dock_sandbox.hide()
# # #         self.dock_terminal.hide()
        
# # #     def show_editor(self, config_path=None):
# # #         self.stacked_widget.setCurrentIndex(1)
# # #         self.dock_pipeline.show()
# # #         self.dock_sandbox.show()
# # #         self.dock_terminal.show()
        
# # #         if config_path:
# # #             self.load_config_from_path(config_path)
# # #             self.setWindowTitle(f"Pipeline Editor - {os.path.basename(config_path)}")
# # #         else:
# # #             self.new_config()
# # #             self.setWindowTitle("Pipeline Editor - New Configuration")

# # #     def new_config(self):
# # #         self.processes = {"Main_Process": []}
# # #         self.current_process = "Main_Process"
# # #         self.export_dfs = []
# # #         self.current_config_path = None
# # #         self.global_dfs = {}
# # #         self.global_vars = {}
# # #         self.preview_dfs = {}
# # #         self.preview_vars = {}
        
# # #         self.combo_processes.blockSignals(True)
# # #         self.combo_processes.clear()
# # #         self.combo_processes.addItem("Main_Process")
# # #         self.combo_processes.blockSignals(False)
        
# # #         self.refresh_step_list()
# # #         self.update_tabs()

# # #     def run_config_from_dashboard(self, path):
# # #         export_dir = QFileDialog.getExistingDirectory(self, "Select Export Folder for Final Data")
# # #         if not export_dir: return # User cancelled
# # #         self.show_editor(path)
# # #         self.run_full_restore(export_dir)

# # #     def apply_dark_theme(self):
# # #         dark_qss = """
# # #         QMainWindow, QWidget { 
# # #             background-color: #1e1e1e; 
# # #             color: #d4d4d4; 
# # #             font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; 
# # #             font-size: 10pt; 
# # #         }
        
# # #         /* Dashboard Specifics */
# # #         QLabel#mainTitle { font-size: 26pt; font-weight: bold; color: #ffffff; padding-bottom: 5px; }
# # #         QLabel#emptyMsg { color: #888888; font-size: 14pt; margin-top: 50px; }
# # #         QFrame#mainDivider { background-color: #333333; height: 1px; border: none; }
# # #         QScrollArea#dashboardScroll { background-color: transparent; border: none; }
# # #         QWidget#dashboardContainer { background-color: transparent; }

# # #         /* Config Card Specifics */
# # #         QGroupBox#ConfigCard {
# # #             background-color: #2d2d30;
# # #             border: 2px solid #3e3e42;
# # #             border-radius: 12px;
# # #             margin-top: 20px;
# # #             padding-top: 15px;
# # #             font-size: 11pt;
# # #         }
# # #         QGroupBox#ConfigCard:hover { border: 2px solid #007acc; background-color: #333337; }
# # #         QGroupBox#ConfigCard::title {
# # #             subcontrol-origin: margin;
# # #             subcontrol-position: top left;
# # #             left: 15px;
# # #             padding: 0 8px;
# # #             color: #007acc;
# # #             font-weight: bold;
# # #         }
# # #         QLabel#cardMetadata { color: #a0a0a0; font-size: 9pt; font-weight: 500; }
# # #         QLabel#cardPath { color: #666666; font-style: italic; font-size: 8pt; }

# # #         /* Editor Specifics */
# # #         QDockWidget::title { 
# # #             text-align: left; 
# # #             background: #252526; 
# # #             padding: 8px 12px; 
# # #             border-top-left-radius: 8px;
# # #             border-top-right-radius: 8px;
# # #             font-weight: bold; 
# # #             color: #007acc; 
# # #         }
# # #         QDockWidget { border: 1px solid #333333; border-radius: 12px; }
# # #         QGroupBox { 
# # #             border: 1px solid #333333; 
# # #             border-radius: 10px; 
# # #             margin-top: 20px; 
# # #             font-weight: bold; 
# # #             color: #007acc; 
# # #             padding-top: 10px;
# # #         }
# # #         QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 10px; left: 15px; }
        
# # #         QPushButton { 
# # #             background-color: #333333; 
# # #             color: #ffffff; 
# # #             border: 1px solid #444444; 
# # #             padding: 10px 18px; 
# # #             border-radius: 8px; 
# # #             font-weight: 600; 
# # #         }
# # #         QPushButton:hover { background-color: #404040; border-color: #007acc; }
# # #         QPushButton#btnPrimary { background-color: #007acc; border: none; }
# # #         QPushButton#btnPrimary:hover { background-color: #1a8ad4; }
# # #         QPushButton#btnSuccess { background-color: #2da44e; border: none; }
# # #         QPushButton#btnSuccess:hover { background-color: #2cbe4e; }
# # #         QPushButton#btnDanger { background-color: #cf222e; border: none; }
        
# # #         QLineEdit, QTextEdit, QComboBox { 
# # #             background-color: #252526; 
# # #             border: 1px solid #3c3c3c; 
# # #             border-radius: 8px; 
# # #             padding: 8px; 
# # #             color: #d4d4d4; 
# # #         }
# # #         QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border: 2px solid #007acc; background-color: #2d2d30; }
        
# # #         QTabWidget::pane { border: 1px solid #333333; border-radius: 10px; background: #1e1e1e; top: -1px; }
# # #         QTabBar::tab { 
# # #             background: #2d2d30; 
# # #             border: 1px solid #333333; 
# # #             padding: 10px 20px; 
# # #             color: #808080; 
# # #             border-top-left-radius: 8px; 
# # #             border-top-right-radius: 8px;
# # #             margin-right: 4px;
# # #         }
# # #         QTabBar::tab:selected { background: #1e1e1e; color: #ffffff; border-bottom: 3px solid #007acc; font-weight: bold; }

# # #         /* Table & Data Views */
# # #         QTableView, QTableWidget {
# # #             background-color: #1e1e1e;
# # #             gridline-color: #333333;
# # #             border: 1px solid #333333;
# # #             border-radius: 8px;
# # #             color: #d4d4d4;
# # #         }
# # #         QHeaderView::section {
# # #             background-color: #252526;
# # #             color: #007acc;
# # #             padding: 8px;
# # #             border: 1px solid #333333;
# # #             font-weight: bold;
# # #         }
# # #         QHeaderView {
# # #             background-color: #1e1e1e;
# # #         }
# # #         QTableCornerButton::section {
# # #             background-color: #252526;
# # #             border: 1px solid #333333;
# # #         }
# # #         QScrollBar:vertical { border: none; background: #1e1e1e; width: 12px; border-radius: 6px; }
# # #         QScrollBar::handle:vertical { background: #3e3e42; min-height: 20px; border-radius: 6px; }
# # #         QScrollBar::handle:vertical:hover { background: #4e4e52; }
# # #         """
# # #         self.setStyleSheet(dark_qss)
# # #         if hasattr(self, 'terminal_output'):
# # #             self.terminal_output.setStyleSheet("background-color: #0a0a0a; border-radius: 10px; color: #4CAF50; padding: 10px; font-family: 'Consolas';")
# # #             self.terminal_input.setStyleSheet("background-color: #0a0a0a; border: 1px solid #007acc; border-radius: 8px; color: #FFFFFF; padding: 8px;")
        
# # #         if hasattr(self, 'dashboard'):
# # #             self.dashboard.setStyleSheet(dark_qss)

# # #     def apply_white_theme(self):
# # #         white_qss = """
# # #         QMainWindow, QWidget { 
# # #             background-color: #f8f9fa; 
# # #             color: #212529; 
# # #             font-family: 'Segoe UI', system-ui, sans-serif; 
# # #             font-size: 10pt; 
# # #         }
        
# # #         /* Dashboard Specifics */
# # #         QLabel#mainTitle { font-size: 26pt; font-weight: bold; color: #1a1a1a; padding-bottom: 5px; }
# # #         QLabel#emptyMsg { color: #6c757d; font-size: 14pt; margin-top: 50px; }
# # #         QFrame#mainDivider { background-color: #dee2e6; height: 1px; border: none; }
# # #         QScrollArea#dashboardScroll { background-color: transparent; border: none; }
# # #         QWidget#dashboardContainer { background-color: transparent; }

# # #         /* Config Card Specifics */
# # #         QGroupBox#ConfigCard {
# # #             background-color: #ffffff;
# # #             border: 1px solid #dee2e6;
# # #             border-radius: 12px;
# # #             margin-top: 20px;
# # #             padding-top: 15px;
# # #             font-size: 11pt;
# # #         }
# # #         QGroupBox#ConfigCard:hover { border: 1px solid #007acc; background-color: #f8f9fa; }
# # #         QGroupBox#ConfigCard::title {
# # #             subcontrol-origin: margin;
# # #             subcontrol-position: top left;
# # #             left: 15px;
# # #             padding: 0 8px;
# # #             color: #007acc;
# # #             font-weight: bold;
# # #         }
# # #         QLabel#cardMetadata { color: #495057; font-size: 9pt; font-weight: 500; }
# # #         QLabel#cardPath { color: #6c757d; font-style: italic; font-size: 8pt; }

# # #         /* Editor Specifics */
# # #         QLabel { color: #212529; }
# # #         QDockWidget::title { 
# # #             text-align: left; 
# # #             background: #ffffff; 
# # #             padding: 8px 12px; 
# # #             border-top-left-radius: 8px;
# # #             border-top-right-radius: 8px;
# # #             font-weight: bold; 
# # #             color: #007acc; 
# # #             border-bottom: 1px solid #e9ecef;
# # #         }
# # #         QDockWidget { border: 1px solid #dee2e6; border-radius: 12px; background-color: #ffffff; }
# # #         QGroupBox { 
# # #             border: 1px solid #dee2e6; 
# # #             border-radius: 10px; 
# # #             margin-top: 20px; 
# # #             font-weight: bold; 
# # #             color: #007acc; 
# # #             background-color: #ffffff;
# # #             padding-top: 10px;
# # #         }
# # #         QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 10px; left: 15px; background-color: #ffffff; color: #007acc; }
        
# # #         QPushButton { 
# # #             background-color: #ffffff; 
# # #             color: #212529; 
# # #             border: 1px solid #dee2e6; 
# # #             padding: 10px 18px; 
# # #             border-radius: 8px; 
# # #             font-weight: 600; 
# # #         }
# # #         QPushButton:hover { background-color: #f1f3f5; border-color: #adb5bd; }
# # #         QPushButton#btnPrimary { background-color: #007acc; border: none; color: #ffffff; }
# # #         QPushButton#btnPrimary:hover { background-color: #1a8ad4; }
# # #         QPushButton#btnSuccess { background-color: #2da44e; border: none; color: #ffffff; }
# # #         QPushButton#btnSuccess:hover { background-color: #2cbe4e; }
# # #         QPushButton#btnDanger { background-color: #cf222e; border: none; color: #ffffff; }
        
# # #         QLineEdit, QTextEdit, QComboBox { 
# # #             background-color: #ffffff; 
# # #             border: 1px solid #dee2e6; 
# # #             border-radius: 8px; 
# # #             padding: 8px; 
# # #             color: #212529; 
# # #         }
# # #         QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border: 2px solid #007acc; background-color: #ffffff; }
        
# # #         QTabWidget::pane { border: 1px solid #dee2e6; border-radius: 10px; background: #ffffff; top: -1px; }
# # #         QTabBar::tab { 
# # #             background: #f1f3f5; 
# # #             border: 1px solid #dee2e6; 
# # #             padding: 10px 20px; 
# # #             color: #495057; 
# # #             border-top-left-radius: 8px; 
# # #             border-top-right-radius: 8px;
# # #             margin-right: 4px;
# # #         }
# # #         QTabBar::tab:selected { background: #ffffff; color: #007acc; border-bottom: 3px solid #007acc; font-weight: bold; }
        
# # #         /* Table & Data Views */
# # #         QTableView, QTableWidget {
# # #             background-color: #ffffff;
# # #             gridline-color: #e9ecef;
# # #             border: 1px solid #dee2e6;
# # #             border-radius: 8px;
# # #             color: #212529;
# # #         }
# # #         QHeaderView::section {
# # #             background-color: #f1f3f5;
# # #             color: #007acc;
# # #             padding: 8px;
# # #             border: 1px solid #dee2e6;
# # #             font-weight: bold;
# # #         }
# # #         QHeaderView {
# # #             background-color: #ffffff;
# # #         }
# # #         QTableCornerButton::section {
# # #             background-color: #f1f3f5;
# # #             border: 1px solid #dee2e6;
# # #         }
# # #         QScrollBar:vertical { border: none; background: #f8f9fa; width: 12px; border-radius: 6px; }
# # #         QScrollBar::handle:vertical { background: #dee2e6; min-height: 20px; border-radius: 6px; }
# # #         QScrollBar::handle:vertical:hover { background: #ced4da; }
# # #         """
# # #         self.setStyleSheet(white_qss)
# # #         if hasattr(self, 'terminal_output'):
# # #             self.terminal_output.setStyleSheet("background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 10px; color: #1a7f37; padding: 10px; font-family: 'Consolas';")
# # #             self.terminal_input.setStyleSheet("background-color: #ffffff; border: 2px solid #007acc; border-radius: 8px; color: #212529; padding: 8px;")
        
# # #         if hasattr(self, 'dashboard'):
# # #             self.dashboard.setStyleSheet(white_qss)
# # #             self.dashboard.refresh_configs()

# # #     def init_ui(self):
# # #         # --- Dashboard ---
# # #         self.dashboard = DashboardWidget()
# # #         self.dashboard.create_new_requested.connect(lambda: self.show_editor())
# # #         self.dashboard.auto_generate_requested.connect(self.auto_generate_pipeline)
# # #         self.dashboard.edit_config_requested.connect(lambda p: self.show_editor(p))
# # #         self.dashboard.run_config_requested.connect(self.run_config_from_dashboard)
# # #         self.stacked_widget.addWidget(self.dashboard)

# # #         # --- Menu Bar ---
# # #         menubar = self.menuBar()
# # #         file_menu = menubar.addMenu('File')

# # #         back_action = QAction('🔙 Back to Dashboard', self)
# # #         back_action.triggered.connect(lambda: self.show_dashboard())
# # #         file_menu.addAction(back_action)
# # #         file_menu.addSeparator()

# # #         load_conf_action = QAction('Load Pipeline Config', self)
# # #         load_conf_action.triggered.connect(lambda: self.load_config())
# # #         file_menu.addAction(load_conf_action)

# # #         save_conf_action = QAction('Save Pipeline Config', self)
# # #         save_conf_action.triggered.connect(lambda: self.save_config())
# # #         file_menu.addAction(save_conf_action)

# # #         view_menu = menubar.addMenu('View')
# # #         self.dock_menu = view_menu.addMenu('Panels')

# # #         theme_menu = view_menu.addMenu('Theme')
# # #         dark_action = QAction('Dark Mode', self)
# # #         dark_action.triggered.connect(lambda: self.apply_dark_theme())
# # #         theme_menu.addAction(dark_action)

# # #         white_action = QAction('White Mode', self)
# # #         white_action.triggered.connect(lambda: self.apply_white_theme())
# # #         theme_menu.addAction(white_action)

# # #         # --- Editor Central Widget ---
# # #         self.editor_central = QWidget()
# # #         editor_main_layout = QVBoxLayout(self.editor_central)

# # #         # Top Header (Context info)
# # #         context_layout = QHBoxLayout()
# # #         self.lbl_context = QLabel("Context Available: DFs (0) | Vars (0)")
# # #         self.lbl_context.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 11pt;")
# # #         context_layout.addWidget(self.lbl_context)

# # #         self.combo_view = QComboBox()
# # #         self.combo_view.setFixedWidth(280)
# # #         self.combo_view.setPlaceholderText("Select a DataFrame to View...")
# # #         self.combo_view.currentIndexChanged.connect(self.on_view_combo_changed)
# # #         context_layout.addWidget(self.combo_view)
# # #         editor_main_layout.addLayout(context_layout)

# # #         # Splitter to allow resizing without jumping
# # #         self.central_splitter = QSplitter(Qt.Vertical)
        
# # #         # Tabs (Data View)
# # #         self.tabs = QTabWidget()
# # #         self.tabs.setUsesScrollButtons(True) 
# # #         self.tabs.currentChanged.connect(self.on_tab_changed)
# # #         self.central_splitter.addWidget(self.tabs)

# # #         editor_main_layout.addWidget(self.central_splitter)

# # #         self.stacked_widget.addWidget(self.editor_central)

# # #         # --- Dock 1: Pipeline Controls (Left) ---
# # #         self.dock_pipeline = QDockWidget("Pipeline & Steps", self)
# # #         self.dock_pipeline.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

# # #         pipeline_widget = QWidget()
# # #         left_panel = QVBoxLayout(pipeline_widget)

# # #         process_layout = QHBoxLayout()
# # #         self.combo_processes = QComboBox()
# # #         self.combo_processes.addItem("Main_Process")
# # #         self.combo_processes.currentTextChanged.connect(self.switch_process)
# # #         process_layout.addWidget(self.combo_processes)

# # #         btn_add_process = QPushButton("➕")
# # #         btn_add_process.setFixedWidth(35)
# # #         btn_add_process.clicked.connect(self.add_process)
# # #         process_layout.addWidget(btn_add_process)

# # #         btn_del_process = QPushButton("🗑️")
# # #         btn_del_process.setFixedWidth(35)
# # #         btn_del_process.clicked.connect(self.delete_process)
# # #         process_layout.addWidget(btn_del_process)

# # #         left_panel.addLayout(process_layout)

# # #         btn_load = QPushButton("📥 Load Source Data")
# # #         btn_load.setObjectName("btnPrimary")
# # #         btn_load.clicked.connect(self.load_data)
# # #         left_panel.addWidget(btn_load)

# # #         btn_load_existing = QPushButton("📄 Load Another Sheet")
# # #         btn_load_existing.setObjectName("btnPrimary")
# # #         btn_load_existing.clicked.connect(self.load_existing_file_data)
# # #         left_panel.addWidget(btn_load_existing)

# # #         self.list_steps = QListWidget()
# # #         self.list_steps.itemClicked.connect(self.load_step_into_editor)
# # #         left_panel.addWidget(self.list_steps)

# # #         btn_restore = QPushButton("▶️ Run Pipeline")
# # #         btn_restore.setObjectName("btnPurple")
# # #         btn_restore.clicked.connect(self.run_full_restore)
# # #         left_panel.addWidget(btn_restore)

# # #         btn_export_config = QPushButton("⚙️ Export Config")
# # #         btn_export_config.setObjectName("btnGray")
# # #         btn_export_config.clicked.connect(self.configure_export)
# # #         left_panel.addWidget(btn_export_config)

# # #         self.dock_pipeline.setWidget(pipeline_widget)
# # #         self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_pipeline)
# # #         self.dock_menu.addAction(self.dock_pipeline.toggleViewAction())

# # #         # --- Dock 2: Python Action Sandbox (Bottom/Right) ---
# # #         self.dock_sandbox = QDockWidget("Logic Editor & Sandbox", self)

# # #         sandbox_group = QGroupBox()
# # #         sandbox_layout = QVBoxLayout(sandbox_group)

# # #         self.combo_action = QComboBox()
# # #         self.combo_action.addItems([
# # #             "Execute Raw Python/Pandas", 
# # #             "Evaluate Excel Formula (Native Math)",
# # #             "Run External .py Script (Entire File)"
# # #         ])
# # #         self.combo_action.currentIndexChanged.connect(self.toggle_inputs)
# # #         sandbox_layout.addWidget(self.combo_action)

# # #         code_font = QFont("Consolas", 11)
# # #         self.txt_python = QTextEdit()
# # #         self.txt_python.setFont(code_font)
# # #         self.txt_python.setPlaceholderText("Write Python/Pandas logic here...")
# # #         self.txt_python.setMinimumSize(0, 0) # Allow shrinking
# # #         sandbox_layout.addWidget(self.txt_python)

# # #         # Excel Formula Inputs
# # #         self.widget_excel_formula = QWidget()
# # #         excel_layout = QVBoxLayout(self.widget_excel_formula)
# # #         excel_layout.setContentsMargins(0, 0, 0, 0)

# # #         self.txt_excel_formula = QTextEdit()
# # #         self.txt_excel_formula.setFont(code_font)
# # #         self.txt_excel_formula.setPlaceholderText("Enter Excel Formula (e.g., =SUM(Sheet1!A:A))")
# # #         self.txt_excel_formula.setMaximumHeight(150)
# # #         self.txt_excel_formula.setMinimumSize(0, 0)
# # #         excel_layout.addWidget(self.txt_excel_formula)

# # #         self.txt_excel_target = QLineEdit()
# # #         self.txt_excel_target.setPlaceholderText("Target DataFrame Alias (e.g., Master)")
# # #         excel_layout.addWidget(self.txt_excel_target)

# # #         self.txt_excel_column = QLineEdit()
# # #         self.txt_excel_column.setPlaceholderText("Target Column (Optional - e.g., Price)")
# # #         excel_layout.addWidget(self.txt_excel_column)

# # #         self.widget_excel_formula.hide()
# # #         sandbox_layout.addWidget(self.widget_excel_formula)

# # #         self.widget_script_path = QWidget()
# # #         script_path_layout = QHBoxLayout(self.widget_script_path)
# # #         script_path_layout.setContentsMargins(0, 0, 0, 0)
# # #         self.txt_script_path = QLineEdit()
# # #         self.btn_browse_script = QPushButton("📁")
# # #         self.btn_browse_script.clicked.connect(self.browse_script)
# # #         script_path_layout.addWidget(self.txt_script_path)
# # #         script_path_layout.addWidget(self.btn_browse_script)
# # #         self.widget_script_path.hide()
# # #         sandbox_layout.addWidget(self.widget_script_path)

# # #         btn_layout = QHBoxLayout()
# # #         btn_test = QPushButton("🧪 Test")
# # #         btn_test.clicked.connect(self.test_step)
# # #         btn_layout.addWidget(btn_test)

# # #         btn_record = QPushButton("✅ Record")
# # #         btn_record.setObjectName("btnSuccess")
# # #         btn_record.clicked.connect(self.record_step)
# # #         btn_layout.addWidget(btn_record)

# # #         btn_update = QPushButton("🔄 Update")
# # #         btn_update.setObjectName("btnWarning")
# # #         btn_update.clicked.connect(self.update_selected_step)
# # #         btn_layout.addWidget(btn_update)

# # #         btn_del_step = QPushButton("🗑️ Delete")
# # #         btn_del_step.setObjectName("btnDanger")
# # #         btn_del_step.clicked.connect(self.delete_step)
# # #         btn_layout.addWidget(btn_del_step)

# # #         sandbox_layout.addLayout(btn_layout)
# # #         self.dock_sandbox.setWidget(sandbox_group)
# # #         self.addDockWidget(Qt.RightDockWidgetArea, self.dock_sandbox)
# # #         self.dock_menu.addAction(self.dock_sandbox.toggleViewAction())

# # #         # --- Dock 3: Terminal (Bottom) ---
# # #         self.dock_terminal = QDockWidget("Interactive Terminal REPL", self)
# # #         term_widget = QWidget()
# # #         term_layout = QVBoxLayout(term_widget)

# # #         self.terminal_output = QTextEdit()
# # #         self.terminal_output.setFont(code_font)
# # #         self.terminal_output.setReadOnly(True)
# # #         self.terminal_output.setMinimumSize(0, 0) # Allow shrinking

# # #         self.terminal_input = TerminalInput()
# # #         self.terminal_input.setFont(code_font)
# # #         self.terminal_input.setPlaceholderText(">>> Type Python command and press Enter (Use Arrows for History)")
# # #         self.terminal_input.returnPressed.connect(self.execute_terminal_command)

# # #         term_layout.addWidget(self.terminal_output)
# # #         term_layout.addWidget(self.terminal_input)
# # #         self.dock_terminal.setWidget(term_widget)
# # #         self.dock_terminal.setMinimumSize(0, 0)
# # #         self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_terminal)
# # #         self.dock_menu.addAction(self.dock_terminal.toggleViewAction())

# # #         self.update_tabs()

# # #     def auto_generate_pipeline(self):
# # #         if analyze_workbook is None:
# # #             QMessageBox.critical(self, "Error", "xlwings is required for Auto-Generation. Please run 'pip install xlwings'.")
# # #             return

# # #         file_path, _ = QFileDialog.getOpenFileName(self, "Select Excel to Reverse-Engineer", "", "Excel Files (*.xlsx *.xlsm)")
# # #         if not file_path: return

# # #         # Show a "please wait" message because COM automation can be slow
# # #         self.analysis_msg = QMessageBox(self)
# # #         self.analysis_msg.setWindowTitle("Working...")
# # #         self.analysis_msg.setText("🔍 Analyzing workbook structure and formulas...\nPlease wait, this may take a moment.")
# # #         self.analysis_msg.setStandardButtons(QMessageBox.NoButton)
# # #         self.analysis_msg.show()

# # #         self.analysis_worker = ExcelAnalysisWorker(file_path)
# # #         self.analysis_worker.result_ready.connect(self.on_analysis_success)
# # #         self.analysis_worker.error_occurred.connect(self.on_analysis_error)
# # #         self.analysis_worker.start()

# # #     def on_analysis_success(self, config):
# # #         if hasattr(self, 'analysis_msg'):
# # #             self.analysis_msg.done(0)
# # #             self.analysis_msg.close()
        
# # #         QApplication.processEvents()
        
# # #         # Save the new config automatically
# # #         config_dir = "Config"
# # #         if not os.path.exists(config_dir): os.makedirs(config_dir)

# # #         save_path = os.path.join(config_dir, f"{config['pipeline_name']}.json")
# # #         with open(save_path, 'w') as f:
# # #             json.dump(config, f, indent=4)

# # #         QMessageBox.information(self, "Success", f"Pipeline successfully generated from Excel!\n\nSaved to: {save_path}\n\nAny unsupported features (like Pivot Tables) have been marked as TODO steps for you to fix.")
# # #         self.show_editor(save_path)

# # #     def on_analysis_error(self, err_msg):
# # #         if hasattr(self, 'analysis_msg'):
# # #             self.analysis_msg.done(0)
# # #             self.analysis_msg.close()
        
# # #         QApplication.processEvents()
# # #         QMessageBox.critical(self, "Reverse Engineering Error", f"Failed to analyze workbook:\n{err_msg}")

# # #     def on_view_combo_changed(self, idx):
# # #         if idx >= 0 and idx < self.tabs.count():
# # #             self.tabs.blockSignals(True)
# # #             self.tabs.setCurrentIndex(idx)
# # #             self.tabs.blockSignals(False)

# # #     def on_tab_changed(self, idx):
# # #         if idx >= 0 and idx < self.combo_view.count():
# # #             self.combo_view.blockSignals(True)
# # #             self.combo_view.setCurrentIndex(idx)
# # #             self.combo_view.blockSignals(False)

# # #     def configure_export(self):
# # #         pipeline_dfs = set()
# # #         for proc in self.processes.values():
# # #             for step in proc:
# # #                 if step["action"] == "load_file":
# # #                     pipeline_dfs.add(step["params"].get("alias"))
        
# # #         all_possible = sorted(list(set(self.global_dfs.keys()) | pipeline_dfs | set(self.export_dfs)))
        
# # #         dlg = ExportConfigDialog(all_possible, self.export_dfs, self)
# # #         if dlg.exec_() == QDialog.Accepted:
# # #             self.export_dfs = dlg.get_selected()
# # #             QMessageBox.information(self, "Saved", f"Export configuration updated.\n\n{len(self.export_dfs)} DataFrames will be written to Excel in headless mode.")

# # #     def browse_script(self):
# # #         file_path, _ = QFileDialog.getOpenFileName(self, "Select Python Script", "", "Python Files (*.py);;All Files (*)")
# # #         if file_path:
# # #             # Task 2: Copy to Custom_Scripts
# # #             custom_dir = "Custom_Scripts"
# # #             if not os.path.exists(custom_dir):
# # #                 os.makedirs(custom_dir)
            
# # #             dest_path = os.path.join(custom_dir, os.path.basename(file_path))
            
# # #             # Check if source and dest are different
# # #             if os.path.abspath(file_path) != os.path.abspath(dest_path):
# # #                 try:
# # #                     shutil.copy2(file_path, dest_path)
# # #                     if hasattr(self, 'terminal_output'):
# # #                         self.terminal_output.append(f"\n>>> Copied external script to local project: {dest_path}")
# # #                 except Exception as e:
# # #                     QMessageBox.warning(self, "Copy Error", f"Could not copy script to Custom_Scripts:\n{e}")
            
# # #             self.txt_script_path.setText(dest_path)

# # #     def execute_terminal_command(self):
# # #         cmd = self.terminal_input.text()
# # #         if not cmd.strip(): return
        
# # #         self.terminal_input.add_to_history(cmd)
# # #         self.terminal_output.append(f"\n>>> {cmd}")
# # #         self.terminal_input.clear()
        
# # #         env = {**self.preview_dfs, **self.preview_vars, 'pd': pd, 'np': np, 'os': os, 'prompt_file': prompt_file}
# # #         output = io.StringIO()
# # #         ui_needs_update = False
        
# # #         with contextlib.redirect_stdout(output):
# # #             try:
# # #                 res = eval(cmd, {}, env)
# # #                 if res is not None:
# # #                     print(res)
# # #             except SyntaxError:
# # #                 try:
# # #                     exec(cmd, env, env)
# # #                     ui_needs_update = True
# # #                 except Exception as e:
# # #                     print(f"Error: {e}")
# # #             except Exception as e:
# # #                 print(f"Error: {e}")
                
# # #         result_text = output.getvalue().strip()
# # #         if result_text:
# # #             self.terminal_output.append(result_text)
            
# # #         scrollbar = self.terminal_output.verticalScrollBar()
# # #         scrollbar.setValue(scrollbar.maximum())
        
# # #         if ui_needs_update:
# # #             self.preview_dfs = {k: v for k, v in env.items() if isinstance(v, pd.DataFrame)}
# # #             self.preview_vars = {k: v for k, v in env.items() if not isinstance(v, pd.DataFrame) and not callable(v) and not k.startswith('_') and str(type(v).__module__) == 'builtins'}
# # #             self.update_tabs()

# # #     def add_process(self):
# # #         name, ok = QInputDialog.getText(self, "New Process", "Enter name for new Pipeline/Process:")
# # #         if ok and name.strip() and name not in self.processes:
# # #             self.processes[name.strip()] = []
# # #             self.combo_processes.addItem(name.strip())
# # #             self.combo_processes.setCurrentText(name.strip())

# # #     def delete_process(self):
# # #         if len(self.processes) <= 1:
# # #             QMessageBox.warning(self, "Cannot Delete", "You must have at least one active process.")
# # #             return
            
# # #         reply = QMessageBox.question(self, 'Delete Process', f"Are you sure you want to delete '{self.current_process}' and all its steps?",
# # #                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
# # #         if reply == QMessageBox.Yes:
# # #             del self.processes[self.current_process]
# # #             idx = self.combo_processes.currentIndex()
# # #             self.combo_processes.removeItem(idx)

# # #     def switch_process(self, process_name):
# # #         if not process_name: return
# # #         self.current_process = process_name
# # #         self.refresh_step_list()

# # #     def refresh_step_list(self):
# # #         self.list_steps.clear()
# # #         if self.current_process in self.processes:
# # #             for step in self.processes[self.current_process]:
# # #                 prompt_flag = " [Prompt at Runtime]" if step.get('params', {}).get('prompt_at_runtime') else ""
# # #                 self.list_steps.addItem(f"[{step['step_id']}] {step['action']}{prompt_flag}")

# # #     def toggle_inputs(self):
# # #         action = self.combo_action.currentText()
# # #         self.txt_python.setVisible(action == "Execute Raw Python/Pandas")
# # #         self.widget_excel_formula.setVisible("Excel Formula" in action)
# # #         self.widget_script_path.setVisible("External" in action)

# # #     def load_data(self):
# # #         file_path, _ = QFileDialog.getOpenFileName(self, "Select Excel/CSV", "", "Data Files (*.xlsx *.csv)")
# # #         if not file_path: return

# # #         sheet_name = 0
# # #         if file_path.endswith('.xlsx'):
# # #             try:
# # #                 xl = pd.ExcelFile(file_path)
# # #                 sheet_name, ok = QInputDialog.getItem(self, "Select Sheet", "Select sheet:", xl.sheet_names, 0, False)
# # #                 if not ok: return
# # #             except Exception as e:
# # #                 QMessageBox.critical(self, "Error", str(e))
# # #                 return

# # #         alias, ok = QInputDialog.getText(self, "DataFrame Alias", "Variable name (e.g. df1):")
# # #         if not ok or not alias.strip(): return
# # #         alias = alias.strip()

# # #         reply = QMessageBox.question(self, 'Dynamic Input',
# # #                                      f"When this pipeline runs automatically in the future, should it STOP and prompt the user to select the file for '{alias}'?",
# # #                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
# # #         prompt_at_runtime = (reply == QMessageBox.Yes)

# # #         try:
# # #             df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path, sheet_name=sheet_name)
            
# # #             self.global_dfs[alias] = df
# # #             self.preview_dfs = self.global_dfs.copy()
# # #             self.update_tabs()
            
# # #             step = {
# # #                 "step_id": len(self.processes[self.current_process]) + 1,
# # #                 "action": "load_file",
# # #                 "params": {"filepath": file_path, "sheet": sheet_name, "alias": alias, "prompt_at_runtime": prompt_at_runtime}
# # #             }
# # #             self.processes[self.current_process].append(step)
# # #             self.refresh_step_list()
            
# # #         except Exception as e:
# # #             QMessageBox.critical(self, "Error", str(e))

# # #     def load_existing_file_data(self):
# # #         active_files = set()
# # #         for proc in self.processes.values():
# # #             for step in proc:
# # #                 if step.get("action") == "load_file":
# # #                     fp = step.get("params", {}).get("filepath")
# # #                     if fp and fp.endswith(('.xlsx', '.xlsm')):
# # #                         active_files.add(fp)
        
# # #         if not active_files:
# # #             QMessageBox.information(self, "No Active Files", "No Excel files are currently loaded.")
# # #             return
            
# # #         file_path, ok = QInputDialog.getItem(self, "Select Existing File", "Choose an Excel file:", list(active_files), 0, False)
# # #         if not ok: return
        
# # #         try:
# # #             xl = pd.ExcelFile(file_path)
# # #             sheet_name, ok = QInputDialog.getItem(self, "Select Sheet", f"Select sheet:", xl.sheet_names, 0, False)
# # #             if not ok: return
# # #         except Exception as e:
# # #             QMessageBox.critical(self, "Error", f"Could not read file: {e}")
# # #             return
            
# # #         alias, ok = QInputDialog.getText(self, "DataFrame Alias", "Variable name:")
# # #         if not ok or not alias.strip(): return
# # #         alias = alias.strip()

# # #         reply = QMessageBox.question(self, 'Dynamic Input',
# # #                                      f"Prompt user to select file for '{alias}'?",
# # #                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
# # #         prompt_at_runtime = (reply == QMessageBox.Yes)

# # #         try:
# # #             df = pd.read_excel(file_path, sheet_name=sheet_name)
# # #             self.global_dfs[alias] = df
# # #             self.preview_dfs = self.global_dfs.copy()
# # #             self.update_tabs()
            
# # #             step = {
# # #                 "step_id": len(self.processes[self.current_process]) + 1,
# # #                 "action": "load_file",
# # #                 "params": {"filepath": file_path, "sheet": sheet_name, "alias": alias, "prompt_at_runtime": prompt_at_runtime}
# # #             }
# # #             self.processes[self.current_process].append(step)
# # #             self.refresh_step_list()
# # #         except Exception as e:
# # #             QMessageBox.critical(self, "Error", str(e))

# # #     def copy_df_name(self, name, btn):
# # #         """Copies the DataFrame alias to clipboard and temporarily updates the button UI"""
# # #         QApplication.clipboard().setText(name)
# # #         original_text = btn.text()
# # #         btn.setText("✅ Copied!")
# # #         btn.setStyleSheet("background-color: #2da44e; color: white; border: none;") # Success green color
        
# # #         # Reset button state after 1.5 seconds
# # #         QTimer.singleShot(1500, lambda: self.reset_copy_btn(btn, original_text))

# # #     def reset_copy_btn(self, btn, text):
# # #         """Resets the copy button back to its standard state safely"""
# # #         try:
# # #             btn.setText(text)
# # #             btn.setStyleSheet("") # Revert to the application's standard stylesheet
# # #         except RuntimeError:
# # #             pass # Button might have been destroyed if the user navigated/refreshed tabs quickly

# # #     def update_tabs(self):
# # #         self.tabs.clear()
# # #         self.combo_view.blockSignals(True)
# # #         self.combo_view.clear()
        
# # #         var_table = QTableWidget(len(self.preview_vars), 3)
# # #         var_table.setHorizontalHeaderLabels(["Variable Name", "Type", "Value"])
# # #         var_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
# # #         var_table.verticalHeader().setVisible(False)
        
# # #         row = 0
# # #         for k, v in self.preview_vars.items():
# # #             var_table.setItem(row, 0, QTableWidgetItem(str(k)))
# # #             var_table.setItem(row, 1, QTableWidgetItem(type(v).__name__))
# # #             var_table.setItem(row, 2, QTableWidgetItem(str(v)[:100]))
# # #             row += 1
            
# # #         self.tabs.addTab(var_table, "📦 Variables Explorer")
# # #         self.combo_view.addItem("📦 Variables Explorer")

# # #         for alias, df in self.preview_dfs.items():
# # #             # Create a container widget for the tab's specific layout
# # #             tab_widget = QWidget()
# # #             tab_layout = QVBoxLayout(tab_widget)
# # #             tab_layout.setContentsMargins(5, 5, 5, 5)

# # #             # --- Start Custom Feature: Tab Actions Header ---
# # #             top_bar = QHBoxLayout()
# # #             lbl_alias = QLabel(f"Viewing DataFrame: <b>{alias}</b>")
# # #             lbl_alias.setStyleSheet("font-size: 11pt;")
            
# # #             btn_copy = QPushButton("📋 Copy Name")
# # #             btn_copy.setFixedWidth(120)
# # #             btn_copy.setObjectName("btnPrimary")
# # #             # Connect using default argument in lambda to lock in this specific loop's 'alias' and 'btn_copy'
# # #             btn_copy.clicked.connect(lambda checked=False, n=alias, b=btn_copy: self.copy_df_name(n, b))
            
# # #             top_bar.addWidget(lbl_alias)
# # #             top_bar.addStretch()
# # #             top_bar.addWidget(btn_copy)
            
# # #             tab_layout.addLayout(top_bar)
# # #             # --- End Custom Feature ---

# # #             table = QTableView()
# # #             table.setModel(PandasModel(df))
# # #             table.verticalHeader().setVisible(False)
# # #             table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
# # #             table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
# # #             table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
# # #             table.horizontalHeader().setDefaultSectionSize(120)
            
# # #             tab_layout.addWidget(table)
            
# # #             # Add the entire container instead of just the table
# # #             self.tabs.addTab(tab_widget, f"📊 DF: {alias}")
# # #             self.combo_view.addItem(f"📊 DF: {alias}")
            
# # #         self.combo_view.blockSignals(False)
# # #         self.lbl_context.setText(f"Context: DFs ({len(self.preview_dfs)}) | Vars ({len(self.preview_vars)})")

# # #     def get_editor_step_data(self):
# # #         action_type = self.combo_action.currentText()
# # #         step = {"action": ""}
# # #         if action_type == "Execute Raw Python/Pandas":
# # #             step["action"] = "execute_python_logic"
# # #             step["params"] = {"code_block": self.txt_python.toPlainText()}
# # #         elif action_type == "Evaluate Excel Formula (Native Math)":
# # #             step["action"] = "evaluate_excel_formula"
# # #             step["params"] = {
# # #                 "formula": self.txt_excel_formula.toPlainText(),
# # #                 "target_alias": self.txt_excel_target.text(),
# # #                 "target_col": self.txt_excel_column.text() if self.txt_excel_column.text().strip() else None
# # #             }
# # #         elif action_type == "Run External .py Script (Entire File)":
# # #             step["action"] = "run_python_file"
# # #             step["params"] = {"script_path": self.txt_script_path.text()}
# # #         return step

# # #     def test_step(self):
# # #         step = self.get_editor_step_data()
# # #         if not step["params"].get("code_block") and step["action"] == "execute_python_logic": return
        
# # #         self.pending_step = step
# # #         self.worker = StepPreviewWorker(self.global_dfs, self.global_vars, step)
# # #         self.worker.result_ready.connect(self.on_test_success)
# # #         self.worker.error_occurred.connect(self.on_test_error)
# # #         self.worker.start()

# # #     def on_test_success(self, new_dfs, new_vars):
# # #         self.preview_dfs = new_dfs
# # #         self.preview_vars = new_vars
# # #         self.update_tabs()
# # #         QMessageBox.information(self, "Test Passed", "Code executed!")

# # #     def on_test_error(self, err_msg):
# # #         QMessageBox.critical(self, "Logic Error", f"Failed to execute:\n\n{err_msg}")

# # #     # FIX: Allows you to instantly record what is in the editor without having to run "Test" first
# # #     def record_step(self):
# # #         step = self.get_editor_step_data()
        
# # #         # Validation
# # #         if step["action"] == "execute_python_logic" and not step["params"].get("code_block", "").strip():
# # #             QMessageBox.warning(self, "Warning", "Code block is empty!")
# # #             return
# # #         elif step["action"] == "run_python_file" and not step["params"].get("script_path", "").strip():
# # #             QMessageBox.warning(self, "Warning", "Script path is empty!")
# # #             return
            
# # #         step["step_id"] = len(self.processes[self.current_process]) + 1
# # #         self.processes[self.current_process].append(step)
        
# # #         # If tested recently, commit state
# # #         if self.pending_step:
# # #             self.global_dfs = self.preview_dfs.copy()
# # #             self.global_vars = self.preview_vars.copy()
# # #             self.pending_step = None
            
# # #         self.refresh_step_list()
# # #         QMessageBox.information(self, "Recorded", f"Step '{step['action']}' successfully recorded.")

# # #     def load_step_into_editor(self, item):
# # #         row_idx = self.list_steps.row(item)
# # #         step = self.processes[self.current_process][row_idx]
        
# # #         if step["action"] == "execute_python_logic":
# # #             self.combo_action.setCurrentText("Execute Raw Python/Pandas")
# # #             self.txt_python.setPlainText(step["params"].get("code_block", ""))
# # #         elif step["action"] == "evaluate_excel_formula":
# # #             self.combo_action.setCurrentText("Evaluate Excel Formula (Native Math)")
# # #             self.txt_excel_formula.setPlainText(step["params"].get("formula", ""))
# # #             self.txt_excel_target.setText(step["params"].get("target_alias", ""))
# # #             self.txt_excel_column.setText(step["params"].get("target_col", ""))
# # #         elif step["action"] == "run_python_file":
# # #             self.combo_action.setCurrentText("Run External .py Script (Entire File)")
# # #             self.txt_script_path.setText(step["params"].get("script_path", ""))

# # #     # FIX: Allows you to grab the live editor content and seamlessly overwrite the selected list item
# # #     def update_selected_step(self):
# # #         current_item = self.list_steps.currentItem()
# # #         if not current_item:
# # #             QMessageBox.warning(self, "Warning", "Please select a step from the list to update.")
# # #             return
            
# # #         row_idx = self.list_steps.row(current_item)
# # #         original_step = self.processes[self.current_process][row_idx]
        
# # #         if original_step["action"] == "load_file":
# # #             active_files = set()
# # #             for proc in self.processes.values():
# # #                 for s in proc:
# # #                     if s.get("action") == "load_file":
# # #                         fp = s.get("params", {}).get("filepath")
# # #                         if fp: active_files.add(fp)
# # #             dialog = EditLoadDialog(original_step.get("params", {}), list(active_files), self)
# # #             if dialog.exec_() == QDialog.Accepted:
# # #                 original_step["params"] = dialog.get_params()
# # #                 self.processes[self.current_process][row_idx] = original_step
# # #                 self.refresh_step_list()
# # #             return
            
# # #         new_step_data = self.get_editor_step_data()
        
# # #         # Validation
# # #         if new_step_data["action"] == "execute_python_logic" and not new_step_data["params"].get("code_block", "").strip():
# # #             QMessageBox.warning(self, "Warning", "Code block is empty!")
# # #             return
            
# # #         new_step_data["step_id"] = original_step["step_id"]
# # #         self.processes[self.current_process][row_idx] = new_step_data
# # #         self.refresh_step_list()
        
# # #         QMessageBox.information(self, "Success", "Step updated successfully. (Note: Run the pipeline to refresh the visual state)")

# # #     def delete_step(self):
# # #         current_item = self.list_steps.currentItem()
# # #         if not current_item: return
# # #         row_idx = self.list_steps.row(current_item)
# # #         if QMessageBox.question(self, 'Delete', "Delete this step?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
# # #             del self.processes[self.current_process][row_idx]
# # #             for i, step in enumerate(self.processes[self.current_process]):
# # #                 step["step_id"] = i + 1
# # #             self.refresh_step_list()

# # #     def run_full_restore(self, export_path=None):
# # #         if not any(self.processes.values()): return
# # #         self.last_export_path = export_path
# # #         self.terminal_output.append("\n>>> Restoring Pipeline Data...")
# # #         self.restore_worker = PipelineRestoreWorker(self.processes)
# # #         self.restore_worker.progress_update.connect(self.terminal_output.append)
# # #         self.restore_worker.result_ready.connect(self.on_restore_success)
# # #         self.restore_worker.error_occurred.connect(self.on_restore_error)
# # #         self.restore_worker.start()

# # #     def on_restore_success(self, dfs, vars):
# # #         self.global_dfs, self.global_vars = dfs.copy(), vars.copy()
# # #         self.preview_dfs, self.preview_vars = dfs.copy(), vars.copy()
# # #         self.update_tabs()
# # #         self.terminal_output.append(">>> Success!")
        
# # #         if hasattr(self, 'last_export_path') and self.last_export_path:
# # #             self.terminal_output.append(f">>> Exporting results to: {self.last_export_path}")
# # #             try:
# # #                 output_file = os.path.join(self.last_export_path, 'Final_Pipeline_Output.xlsx')
# # #                 with pd.ExcelWriter(output_file) as writer:
# # #                     exported_count = 0
# # #                     for alias, df in dfs.items():
# # #                         if not self.export_dfs or alias in self.export_dfs:
# # #                             df.to_excel(writer, sheet_name=str(alias)[:31], index=False)
# # #                             exported_count += 1
# # #                 self.terminal_output.append(f">>> Export Complete: {exported_count} DataFrames saved.")
# # #             except Exception as e:
# # #                 self.terminal_output.append(f">>> Export Error: {e}")
# # #             self.last_export_path = None

# # #     def on_restore_error(self, err):
# # #         self.terminal_output.append(f">>> Error: {err}")

# # #     def load_config_from_path(self, file_path):
# # #         try:
# # #             with open(file_path, 'r') as f:
# # #                 config = json.load(f)
# # #             self.processes = config["processes"]
# # #             self.export_dfs = config.get("export_dfs", [])
# # #             self.current_config_path = file_path
            
# # #             self.combo_processes.blockSignals(True)
# # #             self.combo_processes.clear()
# # #             for n in self.processes.keys():
# # #                 self.combo_processes.addItem(n)
# # #             self.current_process = list(self.processes.keys())[0]
# # #             self.combo_processes.setCurrentText(self.current_process)
# # #             self.combo_processes.blockSignals(False)
            
# # #             self.refresh_step_list()
# # #             self.update_tabs()
# # #         except Exception as e:
# # #             QMessageBox.critical(self, "Error", f"Could not load config:\n{e}")

# # #     def load_config(self):
# # #         file_path, _ = QFileDialog.getOpenFileName(self, "Load Config", "Config", "JSON Files (*.json)")
# # #         if file_path:
# # #             self.load_config_from_path(file_path)
# # #             if QMessageBox.question(self, 'Restore', "Run pipeline now?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
# # #                 self.run_full_restore()

# # #     def save_config(self):
# # #         default_name = self.current_config_path or "Config/Master_Config.json"
# # #         file_path, _ = QFileDialog.getSaveFileName(self, "Save Pipeline", default_name, "JSON Files (*.json)")
# # #         if file_path:
# # #             config = {
# # #                 "pipeline_name": os.path.splitext(os.path.basename(file_path))[0], 
# # #                 "export_dfs": self.export_dfs, 
# # #                 "processes": self.processes
# # #             }
# # #             with open(file_path, 'w') as f:
# # #                 json.dump(config, f, indent=4)
# # #             self.current_config_path = file_path
# # #             self.setWindowTitle(f"Pipeline Editor - {os.path.basename(file_path)}")
# # #             QMessageBox.information(self, "Saved", f"Saved to {file_path}.")

# # # if __name__ == "__main__":
# # #     app = QApplication(sys.argv)
# # #     window = ScorecardUI()
# # #     window.show()
# # #     sys.exit(app.exec_())



# # # ==============================================================================
# # # FILE LOCATION: Dynamic_Scorecard_System/scorecard_ui.py
# # # ==============================================================================

# # import sys
# # import json
# # import traceback
# # import os
import threading
from concurrent.futures import ThreadPoolExecutor
# # import io
# # import contextlib
# # import shutil
# # import pandas as pd
# # import numpy as np

# # # Force the working directory to be where the EXE is located (or script if running raw)
# # if getattr(sys, 'frozen', False):
# #     application_path = os.path.dirname(sys.executable)
# # else:
# #     application_path = os.path.dirname(os.path.abspath(__file__))

# # os.chdir(application_path)

# # from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
# #                              QHBoxLayout, QPushButton, QLabel, QFileDialog, 
# #                              QTableView, QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem,
# #                              QComboBox, QTextEdit, QLineEdit, QMessageBox, QGroupBox, 
# #                              QInputDialog, QTabWidget, QHeaderView, QSplitter, QAction,
# #                              QDialog, QFormLayout, QCheckBox, QDialogButtonBox, QAbstractItemView,
# #                              QDockWidget, QStackedWidget, QScrollArea, QFrame, QGridLayout)
# # from PyQt5.QtCore import QAbstractTableModel, Qt, QThread, pyqtSignal, QEvent, QTimer
# # from PyQt5.QtGui import QFont

# # # Make sure these are accessible in your environment
# # try:
# #     from dynamic_engine import DynamicPipelineEngine, prompt_file
# # except ImportError:
# #     # Dummy classes to allow UI to run if engine isn't present
# #     class DynamicPipelineEngine: pass
# #     prompt_file = None

# # try:
# #     from excel_analyzer import analyze_workbook
# # except ImportError:
# #     analyze_workbook = None

# # class DraggableListWidget(QListWidget):
# #     """Custom QListWidget that handles drag-and-drop reordering and emits a signal when an item is moved."""
# #     item_moved = pyqtSignal(int, int) # old_index, new_index

# #     def __init__(self, parent=None):
# #         super().__init__(parent)
# #         self.setDragDropMode(QAbstractItemView.InternalMove)

# #     def dropEvent(self, event):
# #         if event.source() == self:
# #             old_index = self.currentRow()
# #             super().dropEvent(event)
# #             new_index = self.currentRow()
# #             if old_index != new_index and old_index >= 0 and new_index >= 0:
# #                 self.item_moved.emit(old_index, new_index)
# #         else:
# #             super().dropEvent(event)

# # class ProcessManagerDialog(QDialog):
# #     """Dialog to manage, rename, reorder, and insert Processes."""
# #     def __init__(self, processes_dict, parent=None):
# #         super().__init__(parent)
# #         self.setWindowTitle("Manage & Reorder Processes")
# #         self.setMinimumWidth(450)
# #         self.setMinimumHeight(400)
        
# #         layout = QVBoxLayout(self)
# #         lbl = QLabel("Drag and drop to reorder. Processes execute from top to bottom.")
# #         lbl.setStyleSheet("color: #007acc; font-weight: bold; margin-bottom: 5px;")
# #         lbl.setWordWrap(True)
# #         layout.addWidget(lbl)
        
# #         self.process_map = {k: k for k in processes_dict.keys()}
        
# #         self.list_widget = QListWidget()
# #         self.list_widget.setDragDropMode(QAbstractItemView.InternalMove)
# #         for proc in processes_dict.keys():
# #             self.list_widget.addItem(proc)
# #         layout.addWidget(self.list_widget)
        
# #         btn_layout = QHBoxLayout()
# #         btn_add = QPushButton("➕ Insert New")
# #         btn_add.clicked.connect(self.add_process)
# #         btn_rename = QPushButton("✏️ Rename")
# #         btn_rename.clicked.connect(self.rename_process)
# #         btn_del = QPushButton("🗑️ Delete")
# #         btn_del.setObjectName("btnDanger")
# #         btn_del.clicked.connect(self.delete_process)
        
# #         btn_layout.addWidget(btn_add)
# #         btn_layout.addWidget(btn_rename)
# #         btn_layout.addWidget(btn_del)
# #         layout.addLayout(btn_layout)
        
# #         self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
# #         self.buttons.accepted.connect(self.accept)
# #         self.buttons.rejected.connect(self.reject)
# #         layout.addWidget(self.buttons)

# #     def add_process(self):
# #         name, ok = QInputDialog.getText(self, "New Process", "Enter new process name:")
# #         if ok and name.strip():
# #             name = name.strip()
# #             if name in [self.list_widget.item(i).text() for i in range(self.list_widget.count())]:
# #                 QMessageBox.warning(self, "Error", "Process name already exists.")
# #                 return
            
# #             self.process_map[name] = None # None indicates a brand new process
            
# #             # Insert directly below the selected item (allows inserting in the middle!)
# #             curr_row = self.list_widget.currentRow()
# #             if curr_row >= 0:
# #                 self.list_widget.insertItem(curr_row + 1, name)
# #                 self.list_widget.setCurrentRow(curr_row + 1)
# #             else:
# #                 self.list_widget.addItem(name)
# #                 self.list_widget.setCurrentRow(self.list_widget.count() - 1)
                
# #     def rename_process(self):
# #         item = self.list_widget.currentItem()
# #         if not item: return
# #         old_name = item.text()
# #         new_name, ok = QInputDialog.getText(self, "Rename", "New process name:", QLineEdit.Normal, old_name)
# #         if ok and new_name.strip() and new_name.strip() != old_name:
# #             new_name = new_name.strip()
# #             if new_name in [self.list_widget.item(i).text() for i in range(self.list_widget.count())]:
# #                 QMessageBox.warning(self, "Error", "Process name already exists.")
# #                 return
            
# #             # Maintain mapping back to the original dictionary key
# #             original_mapped_name = self.process_map.pop(old_name)
# #             self.process_map[new_name] = original_mapped_name
# #             item.setText(new_name)

# #     def delete_process(self):
# #         item = self.list_widget.currentItem()
# #         if not item: return
# #         if self.list_widget.count() <= 1:
# #             QMessageBox.warning(self, "Error", "You must have at least one active process.")
# #             return
# #         if QMessageBox.question(self, "Delete", f"Delete process '{item.text()}' and all its steps?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
# #             self.process_map.pop(item.text(), None)
# #             self.list_widget.takeItem(self.list_widget.row(item))
            
# #     def get_process_mapping(self):
# #         """Returns the ordered list of tuples: (new_process_name, old_mapped_name_or_None)"""
# #         result = []
# #         for i in range(self.list_widget.count()):
# #             name = self.list_widget.item(i).text()
# #             result.append((name, self.process_map.get(name)))
# #         return result

# # class TerminalInput(QLineEdit):
# #     """Enhanced QLineEdit with command history (Up/Down arrows)"""
# #     def __init__(self, *args, **kwargs):
# #         super().__init__(*args, **kwargs)
# #         self.history = []
# #         self.history_index = -1
# #         self.temp_cmd = ""

# #     def keyPressEvent(self, event):
# #         if event.key() == Qt.Key_Up:
# #             if not self.history:
# #                 return
# #             if self.history_index == -1:
# #                 self.temp_cmd = self.text()
            
# #             if self.history_index < len(self.history) - 1:
# #                 self.history_index += 1
# #                 self.setText(self.history[self.history_index])
        
# #         elif event.key() == Qt.Key_Down:
# #             if self.history_index > -1:
# #                 self.history_index -= 1
# #                 if self.history_index == -1:
# #                     self.setText(self.temp_cmd)
# #                 else:
# #                     self.setText(self.history[self.history_index])
        
# #         else:
# #             super().keyPressEvent(event)
# #             if event.key() != Qt.Key_Return and event.key() != Qt.Key_Enter:
# #                 self.history_index = -1

# #     def add_to_history(self, cmd):
# #         if cmd.strip():
# #             # Remove existing occurrence to move it to the front
# #             if cmd in self.history:
# #                 self.history.remove(cmd)
# #             self.history.insert(0, cmd)
# #         self.history_index = -1
# #         self.temp_cmd = ""

# # class PandasModel(QAbstractTableModel):
# #     def __init__(self, data):
# #         super().__init__()
# #         self._data = data

# #     def rowCount(self, parent=None): return self._data.shape[0]
# #     def columnCount(self, parent=None): return self._data.shape[1]
# #     def data(self, index, role=Qt.DisplayRole):
# #         if index.isValid() and role == Qt.DisplayRole:
# #             val = self._data.iloc[index.row(), index.column()]
# #             return str(val) if not pd.isna(val) else ""
# #         return None
# #     def headerData(self, col, orientation, role):
# #         if orientation == Qt.Horizontal and role == Qt.DisplayRole:
# #             return str(self._data.columns[col])
# #         return None

# # class StepPreviewWorker(QThread):
# #     result_ready = pyqtSignal(dict, dict)
# #     error_occurred = pyqtSignal(str)

# #     def __init__(self, dfs_dict, vars_dict, step):
# #         super().__init__()
# #         self.dfs_dict = {k: v.copy() for k, v in dfs_dict.items()}
# #         self.vars_dict = {k: v for k, v in vars_dict.items()}
# #         self.step = step
# #         self.engine = DynamicPipelineEngine()

# #     def run(self):
# #         try:
# #             new_dfs, new_vars = self.engine._apply_step(self.dfs_dict, self.vars_dict, self.step)
# #             self.result_ready.emit(new_dfs, new_vars)
# #         except Exception as e:
# #             self.error_occurred.emit(traceback.format_exc())

# # class PipelineRestoreWorker(QThread):
# #     progress_update = pyqtSignal(str)
# #     result_ready = pyqtSignal(dict, dict)
# #     error_occurred = pyqtSignal(str)

# #     def __init__(self, processes):
# #         super().__init__()
# #         self.processes = processes
# #         self.engine = DynamicPipelineEngine()

# #     def run(self):
# #         dfs_dict = {}
# #         vars_dict = {}
# #         try:
# #             for proc_name, steps in self.processes.items():
# #                 self.progress_update.emit(f"\n--- Running Process: {proc_name} ---")
# #                 for step in steps:
# #                     self.progress_update.emit(f">>> Executing [{step['step_id']}] {step['action']}...")
                    
# #                     original_prompt = step.get('params', {}).get('prompt_at_runtime', False)
# #                     if 'params' in step:
# #                         step['params']['prompt_at_runtime'] = False
                        
# #                     dfs_dict, vars_dict = self.engine._apply_step(dfs_dict, vars_dict, step)
                    
# #                     if 'params' in step:
# #                         step['params']['prompt_at_runtime'] = original_prompt

# #             self.result_ready.emit(dfs_dict, vars_dict)
# #         except Exception as e:
# #             self.error_occurred.emit(traceback.format_exc())

# # class ExcelAnalysisWorker(QThread):
# #     result_ready = pyqtSignal(dict)
# #     error_occurred = pyqtSignal(str)

# #     def __init__(self, file_path):
# #         super().__init__()
# #         self.file_path = file_path

# #     def run(self):
# #         try:
# #             config = analyze_workbook(self.file_path)
# #             self.result_ready.emit(config)
# #         except Exception as e:
# #             self.error_occurred.emit(str(e))

# # class ExportConfigDialog(QDialog):
# #     """Custom Dialog for selecting which DataFrames to export to Excel"""
# #     def __init__(self, all_dfs, selected_dfs, parent=None):
# #         super().__init__(parent)
# #         self.setWindowTitle("Configure Headless Export")
# #         self.resize(450, 500) # Sets a default size allowing space for lists
        
# #         layout = QVBoxLayout(self)
        
# #         if not all_dfs:
# #             layout.addWidget(QLabel("No DataFrames currently available.\nRun the pipeline or load data first."))
# #         else:
# #             header_lbl = QLabel("Select which DataFrames to export to Excel\nduring automated Headless execution:")
# #             header_lbl.setStyleSheet("margin-bottom: 5px;")
# #             layout.addWidget(header_lbl)
            
# #             # Action Buttons for Quick Selection
# #             btn_layout = QHBoxLayout()
# #             btn_select_all = QPushButton("☑ Select All")
# #             btn_select_all.clicked.connect(self.select_all)
# #             btn_deselect_all = QPushButton("☐ Deselect All")
# #             btn_deselect_all.clicked.connect(self.deselect_all)
            
# #             btn_layout.addWidget(btn_select_all)
# #             btn_layout.addWidget(btn_deselect_all)
# #             layout.addLayout(btn_layout)
            
# #             # Scrollable List Widget with Checkboxes
# #             self.list_widget = QListWidget()
# #             self.list_widget.setSelectionMode(QAbstractItemView.NoSelection) # Prevent highlighting, rely purely on checkboxes
            
# #             for df_name in all_dfs:
# #                 item = QListWidgetItem(df_name)
# #                 item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                
# #                 # If selected_dfs is empty but we have dfs, default to checked (fallback)
# #                 if df_name in selected_dfs or (not selected_dfs and df_name in all_dfs):
# #                     item.setCheckState(Qt.Checked)
# #                 else:
# #                     item.setCheckState(Qt.Unchecked)
                    
# #                 self.list_widget.addItem(item)
                
# #             layout.addWidget(self.list_widget)
            
# #         self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
# #         self.buttons.accepted.connect(self.accept)
# #         self.buttons.rejected.connect(self.reject)
# #         layout.addWidget(self.buttons)

# #     def select_all(self):
# #         if hasattr(self, 'list_widget'):
# #             for i in range(self.list_widget.count()):
# #                 self.list_widget.item(i).setCheckState(Qt.Checked)
            
# #     def deselect_all(self):
# #         if hasattr(self, 'list_widget'):
# #             for i in range(self.list_widget.count()):
# #                 self.list_widget.item(i).setCheckState(Qt.Unchecked)

# #     def get_selected(self):
# #         if not hasattr(self, 'list_widget'):
# #             return []
        
# #         selected = []
# #         for i in range(self.list_widget.count()):
# #             item = self.list_widget.item(i)
# #             if item.checkState() == Qt.Checked:
# #                 selected.append(item.text())
# #         return selected

# # class EditLoadDialog(QDialog):
# #     """Custom Dialog for editing an existing 'load_file' step"""
# #     def __init__(self, step_params, active_files=None, parent=None):
# #         super().__init__(parent)
# #         self.active_files = active_files or []
# #         self.setWindowTitle("Edit Load File Step")
# #         self.setMinimumWidth(550)
        
# #         layout = QFormLayout(self)
        
# #         self.filepath_input = QLineEdit(step_params.get("filepath", ""))
        
# #         # File Path Buttons
# #         btn_layout = QHBoxLayout()
# #         btn_layout.setContentsMargins(0, 0, 0, 0)
        
# #         browse_btn = QPushButton("📁 Browse New")
# #         browse_btn.clicked.connect(self.browse)
# #         btn_layout.addWidget(browse_btn)
        
# #         if self.active_files:
# #             active_btn = QPushButton("📄 Select Active File")
# #             active_btn.clicked.connect(self.select_active)
# #             btn_layout.addWidget(active_btn)
            
# #         fp_layout = QVBoxLayout()
# #         fp_layout.setContentsMargins(0, 0, 0, 0)
# #         fp_layout.addWidget(self.filepath_input)
# #         fp_layout.addLayout(btn_layout)
        
# #         layout.addRow("File Path:", fp_layout)
        
# #         # Sheet Selection Layout
# #         self.sheet_input = QLineEdit(str(step_params.get("sheet", 0)))
# #         self.sheet_input.setPlaceholderText("0 for first sheet, or 'Sheet1'")
        
# #         sheet_layout = QHBoxLayout()
# #         sheet_layout.setContentsMargins(0, 0, 0, 0)
# #         sheet_layout.addWidget(self.sheet_input)
        
# #         inspect_btn = QPushButton("🔍 Select Sheet")
# #         inspect_btn.clicked.connect(self.list_sheets)
# #         sheet_layout.addWidget(inspect_btn)
        
# #         layout.addRow("Sheet Name/Index:", sheet_layout)
        
# #         self.alias_input = QLineEdit(step_params.get("alias", ""))
# #         layout.addRow("DataFrame Alias:", self.alias_input)
        
# #         self.header_input = QLineEdit(str(step_params.get("header", 0)))
# #         self.header_input.setPlaceholderText("0 for first row (default)")
# #         layout.addRow("Header Row (Index):", self.header_input)
        
# #         self.prompt_cb = QCheckBox("Prompt user to select this file at runtime (Filepath becomes a placeholder)")
# #         self.prompt_cb.setChecked(step_params.get("prompt_at_runtime", False))
# #         layout.addRow("", self.prompt_cb)
        
# #         self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
# #         self.buttons.accepted.connect(self.accept)
# #         self.buttons.rejected.connect(self.reject)
# #         layout.addRow(self.buttons)

# #     def browse(self):
# #         fp, _ = QFileDialog.getOpenFileName(self, "Select Excel/CSV", "", "Data Files (*.xlsx *.csv)")
# #         if fp:
# #             self.filepath_input.setText(fp)
            
# #     def select_active(self):
# #         if not self.active_files: return
# #         fp, ok = QInputDialog.getItem(self, "Select Active File", "Choose an existing file from the pipeline:", self.active_files, 0, False)
# #         if ok and fp:
# #             self.filepath_input.setText(fp)

# #     def list_sheets(self):
# #         fp = self.filepath_input.text().strip()
# #         if not fp or not os.path.exists(fp):
# #             QMessageBox.warning(self, "File Not Found", "Cannot read sheets. Please ensure the file path is correct and accessible on your machine.")
# #             return
# #         if not fp.endswith(('.xlsx', '.xlsm')):
# #             QMessageBox.information(self, "Not an Excel File", "Only Excel files have multiple sheets to select from.")
# #             return
            
# #         try:
# #             xl = pd.ExcelFile(fp)
# #             sheet, ok = QInputDialog.getItem(self, "Select Sheet", f"Available Sheets in {os.path.basename(fp)}:", xl.sheet_names, 0, False)
# #             if ok and sheet:
# #                 self.sheet_input.setText(sheet)
# #         except Exception as e:
# #             QMessageBox.critical(self, "Error", f"Could not read sheets:\n{e}")

# #     def get_params(self):
# #         sheet_val = self.sheet_input.text()
# #         if sheet_val.isdigit():
# #             sheet_val = int(sheet_val)
            
# #         header_val = 0
# #         if self.header_input.text().isdigit():
# #             header_val = int(self.header_input.text())
            
# #         fp = self.filepath_input.text().strip()
# #         if not fp and self.prompt_cb.isChecked():
# #             fp = "RUNTIME_PROMPT_ONLY.xlsx"
            
# #         return {
# #             "filepath": fp,
# #             "sheet": sheet_val,
# #             "header": header_val,
# #             "alias": self.alias_input.text(),
# #             "prompt_at_runtime": self.prompt_cb.isChecked()
# #         }

# # class ConfigCard(QGroupBox):
# #     """A visually appealing card representing a pipeline configuration"""
# #     edit_requested = pyqtSignal(str)
# #     run_requested = pyqtSignal(str)
# #     delete_requested = pyqtSignal(str)

# #     def __init__(self, file_path, config_data):
# #         title = config_data.get("pipeline_name", os.path.basename(file_path))
# #         super().__init__(title)
# #         self.file_path = file_path
# #         self.setObjectName("ConfigCard")
        
# #         layout = QVBoxLayout(self)
        
# #         # Metadata
# #         proc_count = len(config_data.get("processes", {}))
# #         step_count = sum(len(steps) for steps in config_data.get("processes", {}).values())
        
# #         self.info_lbl = QLabel(f"Processes: {proc_count} | Total Steps: {step_count}")
# #         self.info_lbl.setObjectName("cardMetadata")
# #         layout.addWidget(self.info_lbl)
        
# #         self.path_lbl = QLabel(os.path.basename(file_path))
# #         self.path_lbl.setObjectName("cardPath")
# #         layout.addWidget(self.path_lbl)
        
# #         layout.addStretch()
        
# #         # Action Buttons
# #         btn_layout = QHBoxLayout()
        
# #         self.btn_run = QPushButton("▶ Run")
# #         self.btn_run.setObjectName("btnSuccess")
# #         self.btn_run.clicked.connect(lambda: self.run_requested.emit(self.file_path))
        
# #         self.btn_edit = QPushButton("✏ Edit")
# #         self.btn_edit.setObjectName("btnPrimary")
# #         self.btn_edit.clicked.connect(lambda: self.edit_requested.emit(self.file_path))
        
# #         self.btn_del = QPushButton("🗑")
# #         self.btn_del.setObjectName("btnDanger")
# #         self.btn_del.setFixedWidth(40)
# #         self.btn_del.clicked.connect(lambda: self.delete_requested.emit(self.file_path))
        
# #         btn_layout.addWidget(self.btn_run)
# #         btn_layout.addWidget(self.btn_edit)
# #         btn_layout.addWidget(self.btn_del)
        
# #         layout.addLayout(btn_layout)

# # class DashboardWidget(QWidget):
# #     """The landing screen for the application"""
# #     create_new_requested = pyqtSignal()
# #     auto_generate_requested = pyqtSignal()
# #     edit_config_requested = pyqtSignal(str)
# #     run_config_requested = pyqtSignal(str)

# #     def __init__(self, parent=None):
# #         super().__init__(parent)
# #         self.init_ui()

# #     def init_ui(self):
# #         main_layout = QVBoxLayout(self)
# #         main_layout.setContentsMargins(40, 40, 40, 40)
# #         main_layout.setSpacing(20)
        
# #         # Header
# #         header_layout = QHBoxLayout()
# #         self.title_lbl = QLabel("Dynamic Scorecard System")
# #         self.title_lbl.setObjectName("mainTitle")
# #         header_layout.addWidget(self.title_lbl)
        
# #         header_layout.addStretch()
        
# #         self.btn_new = QPushButton("➕ Create New Configuration")
# #         self.btn_new.setObjectName("btnPrimary")
# #         self.btn_new.setMinimumHeight(50)
# #         self.btn_new.clicked.connect(self.create_new_requested.emit)
# #         header_layout.addWidget(self.btn_new)
        
# #         self.btn_auto = QPushButton("🪄 Auto-Generate from Excel")
# #         self.btn_auto.setObjectName("btnSuccess")
# #         self.btn_auto.setMinimumHeight(50)
# #         self.btn_auto.clicked.connect(self.auto_generate_requested.emit)
# #         header_layout.addWidget(self.btn_auto)
        
# #         self.btn_import_config = QPushButton("📥 Import Config")
# #         self.btn_import_config.setMinimumHeight(50)
# #         self.btn_import_config.clicked.connect(self.import_config)
# #         header_layout.addWidget(self.btn_import_config)
        
# #         self.btn_refresh = QPushButton("🔄 Refresh")
# #         self.btn_refresh.setMinimumHeight(50)
# #         self.btn_refresh.setFixedWidth(120)
# #         self.btn_refresh.clicked.connect(self.refresh_configs)
# #         header_layout.addWidget(self.btn_refresh)
        
# #         main_layout.addLayout(header_layout)
        
# #         # Divider
# #         self.divider = QFrame()
# #         self.divider.setObjectName("mainDivider")
# #         self.divider.setFrameShape(QFrame.HLine)
# #         self.divider.setFrameShadow(QFrame.Sunken)
# #         main_layout.addWidget(self.divider)
        
# #         # Scroll Area for Configs
# #         self.scroll = QScrollArea()
# #         self.scroll.setObjectName("dashboardScroll")
# #         self.scroll.setWidgetResizable(True)
        
# #         self.container = QWidget()
# #         self.container.setObjectName("dashboardContainer")
# #         self.flow_layout = QGridLayout(self.container) # Using grid for card layout
# #         self.flow_layout.setSpacing(20)
        
# #         self.scroll.setWidget(self.container)
# #         main_layout.addWidget(self.scroll)
        
# #         self.refresh_configs()

# #     def import_config(self):
# #         file_path, _ = QFileDialog.getOpenFileName(self, "Select Configuration to Import", "", "JSON Files (*.json)")
# #         if file_path:
# #             config_dir = "Config"
# #             if not os.path.exists(config_dir):
# #                 os.makedirs(config_dir)
# #             dest_path = os.path.join(config_dir, os.path.basename(file_path))
# #             if os.path.abspath(file_path) != os.path.abspath(dest_path):
# #                 try:
# #                     shutil.copy2(file_path, dest_path)
# #                     QMessageBox.information(self, "Success", f"Config imported into application:\n{dest_path}")
# #                     self.refresh_configs()
# #                 except Exception as e:
# #                     QMessageBox.critical(self, "Error", f"Could not import config:\n{e}")

# #     def refresh_configs(self):
# #         # Clear existing
# #         for i in reversed(range(self.flow_layout.count())): 
# #             self.flow_layout.itemAt(i).widget().setParent(None)
            
# #         config_dir = "Config"
# #         if not os.path.exists(config_dir):
# #             os.makedirs(config_dir)
            
# #         configs = [f for f in os.listdir(config_dir) if f.endswith(".json")]
        
# #         if not configs:
# #             empty_lbl = QLabel("No configurations found. Create your first pipeline to get started!")
# #             empty_lbl.setAlignment(Qt.AlignCenter)
# #             empty_lbl.setObjectName("emptyMsg")
# #             self.flow_layout.addWidget(empty_lbl, 0, 0)
# #             return

# #         col_limit = 3
# #         for idx, filename in enumerate(configs):
# #             path = os.path.join(config_dir, filename)
# #             try:
# #                 with open(path, 'r') as f:
# #                     data = json.load(f)
                
# #                 card = ConfigCard(path, data)
# #                 card.edit_requested.connect(self.edit_config_requested.emit)
# #                 card.run_requested.connect(self.run_config_requested.emit)
# #                 card.delete_requested.connect(self.delete_config)
                
# #                 self.flow_layout.addWidget(card, idx // col_limit, idx % col_limit)
# #             except Exception as e:
# #                 print(f"Error loading {filename}: {e}")

# #     def delete_config(self, path):
# #         reply = QMessageBox.question(self, 'Delete Configuration', 
# #                                      f"Are you sure you want to delete '{os.path.basename(path)}'?\nThis cannot be undone.",
# #                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
# #         if reply == QMessageBox.Yes:
# #             try:
# #                 os.remove(path)
# #                 self.refresh_configs()
# #             except Exception as e:
# #                 QMessageBox.critical(self, "Error", f"Could not delete file: {e}")

# # class ScorecardUI(QMainWindow):
# #     def __init__(self):
# #         super().__init__()
# #         self.setWindowTitle("Dynamic Scorecard System - Dashboard")
# #         self.resize(1600, 1000)
        
# #         self.processes = {"Main_Process": []} 
# #         self.current_process = "Main_Process"
# #         self.export_dfs = [] 
# #         self.current_config_path = None
        
# #         self.global_dfs = {}
# #         self.global_vars = {}
# #         self.preview_dfs = {} 
# #         self.preview_vars = {}
# #         self.pending_step = None 
        
# #         # State Management
# #         self.stacked_widget = QStackedWidget()
# #         self.setCentralWidget(self.stacked_widget)
        
# #         self.init_ui()
# #         self.apply_dark_theme()
        
# #         # Start at Dashboard
# #         self.show_dashboard()

# #     def show_dashboard(self):
# #         self.dashboard.refresh_configs()
# #         self.stacked_widget.setCurrentIndex(0)
# #         self.setWindowTitle("Dynamic Scorecard System - Dashboard")
        
# #         # Hide Editor Docks
# #         self.dock_pipeline.hide()
# #         self.dock_sandbox.hide()
# #         self.dock_terminal.hide()
        
# #     def show_editor(self, config_path=None):
# #         self.stacked_widget.setCurrentIndex(1)
# #         self.dock_pipeline.show()
# #         self.dock_sandbox.show()
# #         self.dock_terminal.show()
        
# #         if config_path:
# #             self.load_config_from_path(config_path)
# #             self.setWindowTitle(f"Pipeline Editor - {os.path.basename(config_path)}")
# #         else:
# #             self.new_config()
# #             self.setWindowTitle("Pipeline Editor - New Configuration")

# #     def new_config(self):
# #         self.processes = {"Main_Process": []}
# #         self.current_process = "Main_Process"
# #         self.export_dfs = []
# #         self.current_config_path = None
# #         self.global_dfs = {}
# #         self.global_vars = {}
# #         self.preview_dfs = {}
# #         self.preview_vars = {}
        
# #         self.combo_processes.blockSignals(True)
# #         self.combo_processes.clear()
# #         self.combo_processes.addItem("Main_Process")
# #         self.combo_processes.blockSignals(False)
        
# #         self.refresh_step_list()
# #         self.update_tabs()

# #     def run_config_from_dashboard(self, path):
# #         export_dir = QFileDialog.getExistingDirectory(self, "Select Export Folder for Final Data")
# #         if not export_dir: return # User cancelled
# #         self.show_editor(path)
# #         self.run_full_restore(export_dir)

# #     def apply_dark_theme(self):
# #         dark_qss = """
# #         QMainWindow, QWidget { 
# #             background-color: #1e1e1e; 
# #             color: #d4d4d4; 
# #             font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; 
# #             font-size: 10pt; 
# #         }
        
# #         /* Dashboard Specifics */
# #         QLabel#mainTitle { font-size: 26pt; font-weight: bold; color: #ffffff; padding-bottom: 5px; }
# #         QLabel#emptyMsg { color: #888888; font-size: 14pt; margin-top: 50px; }
# #         QFrame#mainDivider { background-color: #333333; height: 1px; border: none; }
# #         QScrollArea#dashboardScroll { background-color: transparent; border: none; }
# #         QWidget#dashboardContainer { background-color: transparent; }

# #         /* Config Card Specifics */
# #         QGroupBox#ConfigCard {
# #             background-color: #2d2d30;
# #             border: 2px solid #3e3e42;
# #             border-radius: 12px;
# #             margin-top: 20px;
# #             padding-top: 15px;
# #             font-size: 11pt;
# #         }
# #         QGroupBox#ConfigCard:hover { border: 2px solid #007acc; background-color: #333337; }
# #         QGroupBox#ConfigCard::title {
# #             subcontrol-origin: margin;
# #             subcontrol-position: top left;
# #             left: 15px;
# #             padding: 0 8px;
# #             color: #007acc;
# #             font-weight: bold;
# #         }
# #         QLabel#cardMetadata { color: #a0a0a0; font-size: 9pt; font-weight: 500; }
# #         QLabel#cardPath { color: #666666; font-style: italic; font-size: 8pt; }

# #         /* Editor Specifics */
# #         QDockWidget::title { 
# #             text-align: left; 
# #             background: #252526; 
# #             padding: 8px 12px; 
# #             border-top-left-radius: 8px;
# #             border-top-right-radius: 8px;
# #             font-weight: bold; 
# #             color: #007acc; 
# #         }
# #         QDockWidget { border: 1px solid #333333; border-radius: 12px; }
# #         QGroupBox { 
# #             border: 1px solid #333333; 
# #             border-radius: 10px; 
# #             margin-top: 20px; 
# #             font-weight: bold; 
# #             color: #007acc; 
# #             padding-top: 10px;
# #         }
# #         QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 10px; left: 15px; }
        
# #         QPushButton { 
# #             background-color: #333333; 
# #             color: #ffffff; 
# #             border: 1px solid #444444; 
# #             padding: 10px 18px; 
# #             border-radius: 8px; 
# #             font-weight: 600; 
# #         }
# #         QPushButton:hover { background-color: #404040; border-color: #007acc; }
# #         QPushButton#btnPrimary { background-color: #007acc; border: none; }
# #         QPushButton#btnPrimary:hover { background-color: #1a8ad4; }
# #         QPushButton#btnSuccess { background-color: #2da44e; border: none; }
# #         QPushButton#btnSuccess:hover { background-color: #2cbe4e; }
# #         QPushButton#btnDanger { background-color: #cf222e; border: none; }
        
# #         QLineEdit, QTextEdit, QComboBox { 
# #             background-color: #252526; 
# #             border: 1px solid #3c3c3c; 
# #             border-radius: 8px; 
# #             padding: 8px; 
# #             color: #d4d4d4; 
# #         }
# #         QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border: 2px solid #007acc; background-color: #2d2d30; }
        
# #         QTabWidget::pane { border: 1px solid #333333; border-radius: 10px; background: #1e1e1e; top: -1px; }
# #         QTabBar::tab { 
# #             background: #2d2d30; 
# #             border: 1px solid #333333; 
# #             padding: 10px 20px; 
# #             color: #808080; 
# #             border-top-left-radius: 8px; 
# #             border-top-right-radius: 8px;
# #             margin-right: 4px;
# #         }
# #         QTabBar::tab:selected { background: #1e1e1e; color: #ffffff; border-bottom: 3px solid #007acc; font-weight: bold; }

# #         /* Table & Data Views */
# #         QTableView, QTableWidget {
# #             background-color: #1e1e1e;
# #             gridline-color: #333333;
# #             border: 1px solid #333333;
# #             border-radius: 8px;
# #             color: #d4d4d4;
# #         }
# #         QHeaderView::section {
# #             background-color: #252526;
# #             color: #007acc;
# #             padding: 8px;
# #             border: 1px solid #333333;
# #             font-weight: bold;
# #         }
# #         QHeaderView {
# #             background-color: #1e1e1e;
# #         }
# #         QTableCornerButton::section {
# #             background-color: #252526;
# #             border: 1px solid #333333;
# #         }
# #         QScrollBar:vertical { border: none; background: #1e1e1e; width: 12px; border-radius: 6px; }
# #         QScrollBar::handle:vertical { background: #3e3e42; min-height: 20px; border-radius: 6px; }
# #         QScrollBar::handle:vertical:hover { background: #4e4e52; }
# #         """
# #         self.setStyleSheet(dark_qss)
# #         if hasattr(self, 'terminal_output'):
# #             self.terminal_output.setStyleSheet("background-color: #0a0a0a; border-radius: 10px; color: #4CAF50; padding: 10px; font-family: 'Consolas';")
# #             self.terminal_input.setStyleSheet("background-color: #0a0a0a; border: 1px solid #007acc; border-radius: 8px; color: #FFFFFF; padding: 8px;")
        
# #         if hasattr(self, 'dashboard'):
# #             self.dashboard.setStyleSheet(dark_qss)

# #     def apply_white_theme(self):
# #         white_qss = """
# #         QMainWindow, QWidget { 
# #             background-color: #f8f9fa; 
# #             color: #212529; 
# #             font-family: 'Segoe UI', system-ui, sans-serif; 
# #             font-size: 10pt; 
# #         }
        
# #         /* Dashboard Specifics */
# #         QLabel#mainTitle { font-size: 26pt; font-weight: bold; color: #1a1a1a; padding-bottom: 5px; }
# #         QLabel#emptyMsg { color: #6c757d; font-size: 14pt; margin-top: 50px; }
# #         QFrame#mainDivider { background-color: #dee2e6; height: 1px; border: none; }
# #         QScrollArea#dashboardScroll { background-color: transparent; border: none; }
# #         QWidget#dashboardContainer { background-color: transparent; }

# #         /* Config Card Specifics */
# #         QGroupBox#ConfigCard {
# #             background-color: #ffffff;
# #             border: 1px solid #dee2e6;
# #             border-radius: 12px;
# #             margin-top: 20px;
# #             padding-top: 15px;
# #             font-size: 11pt;
# #         }
# #         QGroupBox#ConfigCard:hover { border: 1px solid #007acc; background-color: #f8f9fa; }
# #         QGroupBox#ConfigCard::title {
# #             subcontrol-origin: margin;
# #             subcontrol-position: top left;
# #             left: 15px;
# #             padding: 0 8px;
# #             color: #007acc;
# #             font-weight: bold;
# #         }
# #         QLabel#cardMetadata { color: #495057; font-size: 9pt; font-weight: 500; }
# #         QLabel#cardPath { color: #6c757d; font-style: italic; font-size: 8pt; }

# #         /* Editor Specifics */
# #         QLabel { color: #212529; }
# #         QDockWidget::title { 
# #             text-align: left; 
# #             background: #ffffff; 
# #             padding: 8px 12px; 
# #             border-top-left-radius: 8px;
# #             border-top-right-radius: 8px;
# #             font-weight: bold; 
# #             color: #007acc; 
# #             border-bottom: 1px solid #e9ecef;
# #         }
# #         QDockWidget { border: 1px solid #dee2e6; border-radius: 12px; background-color: #ffffff; }
# #         QGroupBox { 
# #             border: 1px solid #dee2e6; 
# #             border-radius: 10px; 
# #             margin-top: 20px; 
# #             font-weight: bold; 
# #             color: #007acc; 
# #             background-color: #ffffff;
# #             padding-top: 10px;
# #         }
# #         QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 10px; left: 15px; background-color: #ffffff; color: #007acc; }
        
# #         QPushButton { 
# #             background-color: #ffffff; 
# #             color: #212529; 
# #             border: 1px solid #dee2e6; 
# #             padding: 10px 18px; 
# #             border-radius: 8px; 
# #             font-weight: 600; 
# #         }
# #         QPushButton:hover { background-color: #f1f3f5; border-color: #adb5bd; }
# #         QPushButton#btnPrimary { background-color: #007acc; border: none; color: #ffffff; }
# #         QPushButton#btnPrimary:hover { background-color: #1a8ad4; }
# #         QPushButton#btnSuccess { background-color: #2da44e; border: none; color: #ffffff; }
# #         QPushButton#btnSuccess:hover { background-color: #2cbe4e; }
# #         QPushButton#btnDanger { background-color: #cf222e; border: none; color: #ffffff; }
        
# #         QLineEdit, QTextEdit, QComboBox { 
# #             background-color: #ffffff; 
# #             border: 1px solid #dee2e6; 
# #             border-radius: 8px; 
# #             padding: 8px; 
# #             color: #212529; 
# #         }
# #         QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border: 2px solid #007acc; background-color: #ffffff; }
        
# #         QTabWidget::pane { border: 1px solid #dee2e6; border-radius: 10px; background: #ffffff; top: -1px; }
# #         QTabBar::tab { 
# #             background: #f1f3f5; 
# #             border: 1px solid #dee2e6; 
# #             padding: 10px 20px; 
# #             color: #495057; 
# #             border-top-left-radius: 8px; 
# #             border-top-right-radius: 8px;
# #             margin-right: 4px;
# #         }
# #         QTabBar::tab:selected { background: #ffffff; color: #007acc; border-bottom: 3px solid #007acc; font-weight: bold; }
        
# #         /* Table & Data Views */
# #         QTableView, QTableWidget {
# #             background-color: #ffffff;
# #             gridline-color: #e9ecef;
# #             border: 1px solid #dee2e6;
# #             border-radius: 8px;
# #             color: #212529;
# #         }
# #         QHeaderView::section {
# #             background-color: #f1f3f5;
# #             color: #007acc;
# #             padding: 8px;
# #             border: 1px solid #dee2e6;
# #             font-weight: bold;
# #         }
# #         QHeaderView {
# #             background-color: #ffffff;
# #         }
# #         QTableCornerButton::section {
# #             background-color: #f1f3f5;
# #             border: 1px solid #dee2e6;
# #         }
# #         QScrollBar:vertical { border: none; background: #f8f9fa; width: 12px; border-radius: 6px; }
# #         QScrollBar::handle:vertical { background: #dee2e6; min-height: 20px; border-radius: 6px; }
# #         QScrollBar::handle:vertical:hover { background: #ced4da; }
# #         """
# #         self.setStyleSheet(white_qss)
# #         if hasattr(self, 'terminal_output'):
# #             self.terminal_output.setStyleSheet("background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 10px; color: #1a7f37; padding: 10px; font-family: 'Consolas';")
# #             self.terminal_input.setStyleSheet("background-color: #ffffff; border: 2px solid #007acc; border-radius: 8px; color: #212529; padding: 8px;")
        
# #         if hasattr(self, 'dashboard'):
# #             self.dashboard.setStyleSheet(white_qss)
# #             self.dashboard.refresh_configs()

# #     def init_ui(self):
# #         # --- Dashboard ---
# #         self.dashboard = DashboardWidget()
# #         self.dashboard.create_new_requested.connect(lambda: self.show_editor())
# #         self.dashboard.auto_generate_requested.connect(self.auto_generate_pipeline)
# #         self.dashboard.edit_config_requested.connect(lambda p: self.show_editor(p))
# #         self.dashboard.run_config_requested.connect(self.run_config_from_dashboard)
# #         self.stacked_widget.addWidget(self.dashboard)

# #         # --- Menu Bar ---
# #         menubar = self.menuBar()
# #         file_menu = menubar.addMenu('File')

# #         back_action = QAction('🔙 Back to Dashboard', self)
# #         back_action.triggered.connect(lambda: self.show_dashboard())
# #         file_menu.addAction(back_action)
# #         file_menu.addSeparator()

# #         load_conf_action = QAction('Load Pipeline Config', self)
# #         load_conf_action.triggered.connect(lambda: self.load_config())
# #         file_menu.addAction(load_conf_action)

# #         save_conf_action = QAction('Save Pipeline Config', self)
# #         save_conf_action.triggered.connect(lambda: self.save_config())
# #         file_menu.addAction(save_conf_action)

# #         view_menu = menubar.addMenu('View')
# #         self.dock_menu = view_menu.addMenu('Panels')

# #         theme_menu = view_menu.addMenu('Theme')
# #         dark_action = QAction('Dark Mode', self)
# #         dark_action.triggered.connect(lambda: self.apply_dark_theme())
# #         theme_menu.addAction(dark_action)

# #         white_action = QAction('White Mode', self)
# #         white_action.triggered.connect(lambda: self.apply_white_theme())
# #         theme_menu.addAction(white_action)

# #         # --- Editor Central Widget ---
# #         self.editor_central = QWidget()
# #         editor_main_layout = QVBoxLayout(self.editor_central)

# #         # Top Header (Context info)
# #         context_layout = QHBoxLayout()
# #         self.lbl_context = QLabel("Context Available: DFs (0) | Vars (0)")
# #         self.lbl_context.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 11pt;")
# #         context_layout.addWidget(self.lbl_context)

# #         self.combo_view = QComboBox()
# #         self.combo_view.setFixedWidth(280)
# #         self.combo_view.setPlaceholderText("Select a DataFrame to View...")
# #         self.combo_view.currentIndexChanged.connect(self.on_view_combo_changed)
# #         context_layout.addWidget(self.combo_view)
# #         editor_main_layout.addLayout(context_layout)

# #         # Splitter to allow resizing without jumping
# #         self.central_splitter = QSplitter(Qt.Vertical)
        
# #         # Tabs (Data View)
# #         self.tabs = QTabWidget()
# #         self.tabs.setUsesScrollButtons(True) 
# #         self.tabs.currentChanged.connect(self.on_tab_changed)
# #         self.central_splitter.addWidget(self.tabs)

# #         editor_main_layout.addWidget(self.central_splitter)

# #         self.stacked_widget.addWidget(self.editor_central)

# #         # --- Dock 1: Pipeline Controls (Left) ---
# #         self.dock_pipeline = QDockWidget("Pipeline & Steps", self)
# #         self.dock_pipeline.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

# #         pipeline_widget = QWidget()
# #         left_panel = QVBoxLayout(pipeline_widget)

# #         # ** Process Management UI Update **
# #         process_layout = QHBoxLayout()
# #         self.combo_processes = QComboBox()
# #         self.combo_processes.addItem("Main_Process")
# #         self.combo_processes.currentTextChanged.connect(self.switch_process)
# #         process_layout.addWidget(self.combo_processes)

# #         btn_manage_proc = QPushButton("⚙️ Manage")
# #         btn_manage_proc.clicked.connect(self.manage_processes)
# #         process_layout.addWidget(btn_manage_proc)

# #         left_panel.addLayout(process_layout)

# #         btn_load = QPushButton("📥 Load Source Data")
# #         btn_load.setObjectName("btnPrimary")
# #         btn_load.clicked.connect(self.load_data)
# #         left_panel.addWidget(btn_load)

# #         btn_load_existing = QPushButton("📄 Load Another Sheet")
# #         btn_load_existing.setObjectName("btnPrimary")
# #         btn_load_existing.clicked.connect(self.load_existing_file_data)
# #         left_panel.addWidget(btn_load_existing)

# #         # ** Drag and Drop Step List Implementation **
# #         self.list_steps = DraggableListWidget()
# #         self.list_steps.itemClicked.connect(self.load_step_into_editor)
# #         self.list_steps.item_moved.connect(self.on_step_moved) # Reorder Hook
# #         left_panel.addWidget(self.list_steps)

# #         btn_restore = QPushButton("▶️ Run Pipeline")
# #         btn_restore.setObjectName("btnPurple")
# #         btn_restore.clicked.connect(self.run_full_restore)
# #         left_panel.addWidget(btn_restore)

# #         btn_export_config = QPushButton("⚙️ Export Config")
# #         btn_export_config.setObjectName("btnGray")
# #         btn_export_config.clicked.connect(self.configure_export)
# #         left_panel.addWidget(btn_export_config)

# #         self.dock_pipeline.setWidget(pipeline_widget)
# #         self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_pipeline)
# #         self.dock_menu.addAction(self.dock_pipeline.toggleViewAction())

# #         # --- Dock 2: Python Action Sandbox (Bottom/Right) ---
# #         self.dock_sandbox = QDockWidget("Logic Editor & Sandbox", self)

# #         sandbox_group = QGroupBox()
# #         sandbox_layout = QVBoxLayout(sandbox_group)

# #         self.combo_action = QComboBox()
# #         self.combo_action.addItems([
# #             "Execute Raw Python/Pandas", 
# #             "Evaluate Excel Formula (Native Math)",
# #             "Run External .py Script (Entire File)"
# #         ])
# #         self.combo_action.currentIndexChanged.connect(self.toggle_inputs)
# #         sandbox_layout.addWidget(self.combo_action)

# #         code_font = QFont("Consolas", 11)
# #         self.txt_python = QTextEdit()
# #         self.txt_python.setFont(code_font)
# #         self.txt_python.setPlaceholderText("Write Python/Pandas logic here...")
# #         self.txt_python.setMinimumSize(0, 0) # Allow shrinking
# #         sandbox_layout.addWidget(self.txt_python)

# #         # Excel Formula Inputs
# #         self.widget_excel_formula = QWidget()
# #         excel_layout = QVBoxLayout(self.widget_excel_formula)
# #         excel_layout.setContentsMargins(0, 0, 0, 0)

# #         self.txt_excel_formula = QTextEdit()
# #         self.txt_excel_formula.setFont(code_font)
# #         self.txt_excel_formula.setPlaceholderText("Enter Excel Formula (e.g., =SUM(Sheet1!A:A))")
# #         self.txt_excel_formula.setMaximumHeight(150)
# #         self.txt_excel_formula.setMinimumSize(0, 0)
# #         excel_layout.addWidget(self.txt_excel_formula)

# #         self.txt_excel_target = QLineEdit()
# #         self.txt_excel_target.setPlaceholderText("Target DataFrame Alias (e.g., Master)")
# #         excel_layout.addWidget(self.txt_excel_target)

# #         self.txt_excel_column = QLineEdit()
# #         self.txt_excel_column.setPlaceholderText("Target Column (Optional - e.g., Price)")
# #         excel_layout.addWidget(self.txt_excel_column)

# #         self.widget_excel_formula.hide()
# #         sandbox_layout.addWidget(self.widget_excel_formula)

# #         self.widget_script_path = QWidget()
# #         script_path_layout = QHBoxLayout(self.widget_script_path)
# #         script_path_layout.setContentsMargins(0, 0, 0, 0)
# #         self.txt_script_path = QLineEdit()
# #         self.btn_browse_script = QPushButton("📁")
# #         self.btn_browse_script.clicked.connect(self.browse_script)
# #         script_path_layout.addWidget(self.txt_script_path)
# #         script_path_layout.addWidget(self.btn_browse_script)
# #         self.widget_script_path.hide()
# #         sandbox_layout.addWidget(self.widget_script_path)

# #         btn_layout = QHBoxLayout()
# #         btn_test = QPushButton("🧪 Test")
# #         btn_test.clicked.connect(self.test_step)
# #         btn_layout.addWidget(btn_test)

# #         btn_record = QPushButton("✅ Record")
# #         btn_record.setObjectName("btnSuccess")
# #         btn_record.clicked.connect(self.record_step)
# #         btn_layout.addWidget(btn_record)

# #         btn_update = QPushButton("🔄 Update")
# #         btn_update.setObjectName("btnWarning")
# #         btn_update.clicked.connect(self.update_selected_step)
# #         btn_layout.addWidget(btn_update)

# #         btn_del_step = QPushButton("🗑️ Delete")
# #         btn_del_step.setObjectName("btnDanger")
# #         btn_del_step.clicked.connect(self.delete_step)
# #         btn_layout.addWidget(btn_del_step)

# #         sandbox_layout.addLayout(btn_layout)
# #         self.dock_sandbox.setWidget(sandbox_group)
# #         self.addDockWidget(Qt.RightDockWidgetArea, self.dock_sandbox)
# #         self.dock_menu.addAction(self.dock_sandbox.toggleViewAction())

# #         # --- Dock 3: Terminal (Bottom) ---
# #         self.dock_terminal = QDockWidget("Interactive Terminal REPL", self)
# #         term_widget = QWidget()
# #         term_layout = QVBoxLayout(term_widget)

# #         self.terminal_output = QTextEdit()
# #         self.terminal_output.setFont(code_font)
# #         self.terminal_output.setReadOnly(True)
# #         self.terminal_output.setMinimumSize(0, 0) # Allow shrinking

# #         self.terminal_input = TerminalInput()
# #         self.terminal_input.setFont(code_font)
# #         self.terminal_input.setPlaceholderText(">>> Type Python command and press Enter (Use Arrows for History)")
# #         self.terminal_input.returnPressed.connect(self.execute_terminal_command)

# #         term_layout.addWidget(self.terminal_output)
# #         term_layout.addWidget(self.terminal_input)
# #         self.dock_terminal.setWidget(term_widget)
# #         self.dock_terminal.setMinimumSize(0, 0)
# #         self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_terminal)
# #         self.dock_menu.addAction(self.dock_terminal.toggleViewAction())

# #         self.update_tabs()

# #     def auto_generate_pipeline(self):
# #         if analyze_workbook is None:
# #             QMessageBox.critical(self, "Error", "xlwings is required for Auto-Generation. Please run 'pip install xlwings'.")
# #             return

# #         file_path, _ = QFileDialog.getOpenFileName(self, "Select Excel to Reverse-Engineer", "", "Excel Files (*.xlsx *.xlsm)")
# #         if not file_path: return

# #         # Show a "please wait" message because COM automation can be slow
# #         self.analysis_msg = QMessageBox(self)
# #         self.analysis_msg.setWindowTitle("Working...")
# #         self.analysis_msg.setText("🔍 Analyzing workbook structure and formulas...\nPlease wait, this may take a moment.")
# #         self.analysis_msg.setStandardButtons(QMessageBox.NoButton)
# #         self.analysis_msg.show()

# #         self.analysis_worker = ExcelAnalysisWorker(file_path)
# #         self.analysis_worker.result_ready.connect(self.on_analysis_success)
# #         self.analysis_worker.error_occurred.connect(self.on_analysis_error)
# #         self.analysis_worker.start()

# #     def on_analysis_success(self, config):
# #         if hasattr(self, 'analysis_msg'):
# #             self.analysis_msg.done(0)
# #             self.analysis_msg.close()
        
# #         QApplication.processEvents()
        
# #         # Save the new config automatically
# #         config_dir = "Config"
# #         if not os.path.exists(config_dir): os.makedirs(config_dir)

# #         save_path = os.path.join(config_dir, f"{config['pipeline_name']}.json")
# #         with open(save_path, 'w') as f:
# #             json.dump(config, f, indent=4)

# #         QMessageBox.information(self, "Success", f"Pipeline successfully generated from Excel!\n\nSaved to: {save_path}\n\nAny unsupported features (like Pivot Tables) have been marked as TODO steps for you to fix.")
# #         self.show_editor(save_path)

# #     def on_analysis_error(self, err_msg):
# #         if hasattr(self, 'analysis_msg'):
# #             self.analysis_msg.done(0)
# #             self.analysis_msg.close()
        
# #         QApplication.processEvents()
# #         QMessageBox.critical(self, "Reverse Engineering Error", f"Failed to analyze workbook:\n{err_msg}")

# #     def on_view_combo_changed(self, idx):
# #         if idx >= 0 and idx < self.tabs.count():
# #             self.tabs.blockSignals(True)
# #             self.tabs.setCurrentIndex(idx)
# #             self.tabs.blockSignals(False)

# #     def on_tab_changed(self, idx):
# #         if idx >= 0 and idx < self.combo_view.count():
# #             self.combo_view.blockSignals(True)
# #             self.combo_view.setCurrentIndex(idx)
# #             self.combo_view.blockSignals(False)

# #     def configure_export(self):
# #         pipeline_dfs = set()
# #         for proc in self.processes.values():
# #             for step in proc:
# #                 if step["action"] == "load_file":
# #                     pipeline_dfs.add(step["params"].get("alias"))
        
# #         all_possible = sorted(list(set(self.global_dfs.keys()) | pipeline_dfs | set(self.export_dfs)))
        
# #         dlg = ExportConfigDialog(all_possible, self.export_dfs, self)
# #         if dlg.exec_() == QDialog.Accepted:
# #             self.export_dfs = dlg.get_selected()
# #             QMessageBox.information(self, "Saved", f"Export configuration updated.\n\n{len(self.export_dfs)} DataFrames will be written to Excel in headless mode.")

# #     def browse_script(self):
# #         file_path, _ = QFileDialog.getOpenFileName(self, "Select Python Script", "", "Python Files (*.py);;All Files (*)")
# #         if file_path:
# #             # Task 2: Copy to Custom_Scripts
# #             custom_dir = "Custom_Scripts"
# #             if not os.path.exists(custom_dir):
# #                 os.makedirs(custom_dir)
            
# #             dest_path = os.path.join(custom_dir, os.path.basename(file_path))
            
# #             # Check if source and dest are different
# #             if os.path.abspath(file_path) != os.path.abspath(dest_path):
# #                 try:
# #                     shutil.copy2(file_path, dest_path)
# #                     if hasattr(self, 'terminal_output'):
# #                         self.terminal_output.append(f"\n>>> Copied external script to local project: {dest_path}")
# #                 except Exception as e:
# #                     QMessageBox.warning(self, "Copy Error", f"Could not copy script to Custom_Scripts:\n{e}")
            
# #             self.txt_script_path.setText(dest_path)

# #     def execute_terminal_command(self):
# #         cmd = self.terminal_input.text()
# #         if not cmd.strip(): return
        
# #         self.terminal_input.add_to_history(cmd)
# #         self.terminal_output.append(f"\n>>> {cmd}")
# #         self.terminal_input.clear()
        
# #         env = {**self.preview_dfs, **self.preview_vars, 'pd': pd, 'np': np, 'os': os, 'prompt_file': prompt_file}
# #         output = io.StringIO()
# #         ui_needs_update = False
        
# #         with contextlib.redirect_stdout(output):
# #             try:
# #                 res = eval(cmd, {}, env)
# #                 if res is not None:
# #                     print(res)
# #             except SyntaxError:
# #                 try:
# #                     exec(cmd, env, env)
# #                     ui_needs_update = True
# #                 except Exception as e:
# #                     print(f"Error: {e}")
# #             except Exception as e:
# #                 print(f"Error: {e}")
                
# #         result_text = output.getvalue().strip()
# #         if result_text:
# #             self.terminal_output.append(result_text)
            
# #         scrollbar = self.terminal_output.verticalScrollBar()
# #         scrollbar.setValue(scrollbar.maximum())
        
# #         if ui_needs_update:
# #             self.preview_dfs = {k: v for k, v in env.items() if isinstance(v, pd.DataFrame)}
# #             self.preview_vars = {k: v for k, v in env.items() if not isinstance(v, pd.DataFrame) and not callable(v) and not k.startswith('_') and str(type(v).__module__) == 'builtins'}
# #             self.update_tabs()

# #     # ** New Process Manager Hook **
# #     def manage_processes(self):
# #         dialog = ProcessManagerDialog(self.processes, self)
# #         if dialog.exec_() == QDialog.Accepted:
# #             mapping = dialog.get_process_mapping()
# #             new_processes = {}
# #             for new_name, old_name in mapping:
# #                 if old_name is not None and old_name in self.processes:
# #                     new_processes[new_name] = self.processes[old_name] # Keep existing steps
# #                 else:
# #                     new_processes[new_name] = [] # Brand new process created by user
                    
# #             self.processes = new_processes
            
# #             if self.current_process not in self.processes:
# #                 self.current_process = list(self.processes.keys())[0] if self.processes else ""
                
# #             self.combo_processes.blockSignals(True)
# #             self.combo_processes.clear()
# #             self.combo_processes.addItems(list(self.processes.keys()))
# #             self.combo_processes.setCurrentText(self.current_process)
# #             self.combo_processes.blockSignals(False)
            
# #             self.refresh_step_list()

# #     def switch_process(self, process_name):
# #         if not process_name: return
# #         self.current_process = process_name
# #         self.refresh_step_list()

# #     def refresh_step_list(self):
# #         self.list_steps.clear()
# #         if self.current_process in self.processes:
# #             for step in self.processes[self.current_process]:
# #                 prompt_flag = " [Prompt at Runtime]" if step.get('params', {}).get('prompt_at_runtime') else ""
# #                 self.list_steps.addItem(f"[{step['step_id']}] {step['action']}{prompt_flag}")

# #     def toggle_inputs(self):
# #         action = self.combo_action.currentText()
# #         self.txt_python.setVisible(action == "Execute Raw Python/Pandas")
# #         self.widget_excel_formula.setVisible("Excel Formula" in action)
# #         self.widget_script_path.setVisible("External" in action)

# #     def load_data(self):
# #         file_path, _ = QFileDialog.getOpenFileName(self, "Select Excel/CSV", "", "Data Files (*.xlsx *.csv)")
# #         if not file_path: return

# #         sheet_name = 0
# #         if file_path.endswith('.xlsx'):
# #             try:
# #                 xl = pd.ExcelFile(file_path)
# #                 sheet_name, ok = QInputDialog.getItem(self, "Select Sheet", "Select sheet:", xl.sheet_names, 0, False)
# #                 if not ok: return
# #             except Exception as e:
# #                 QMessageBox.critical(self, "Error", str(e))
# #                 return

# #         alias, ok = QInputDialog.getText(self, "DataFrame Alias", "Variable name (e.g. df1):")
# #         if not ok or not alias.strip(): return
# #         alias = alias.strip()

# #         reply = QMessageBox.question(self, 'Dynamic Input',
# #                                      f"When this pipeline runs automatically in the future, should it STOP and prompt the user to select the file for '{alias}'?",
# #                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
# #         prompt_at_runtime = (reply == QMessageBox.Yes)

# #         try:
# #             df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path, sheet_name=sheet_name)
            
# #             self.global_dfs[alias] = df
# #             self.preview_dfs = self.global_dfs.copy()
# #             self.update_tabs()
            
# #             step = {
# #                 "step_id": len(self.processes[self.current_process]) + 1,
# #                 "action": "load_file",
# #                 "params": {"filepath": file_path, "sheet": sheet_name, "alias": alias, "prompt_at_runtime": prompt_at_runtime}
# #             }
# #             self.processes[self.current_process].append(step)
# #             self.refresh_step_list()
            
# #         except Exception as e:
# #             QMessageBox.critical(self, "Error", str(e))

# #     def load_existing_file_data(self):
# #         active_files = set()
# #         for proc in self.processes.values():
# #             for step in proc:
# #                 if step.get("action") == "load_file":
# #                     fp = step.get("params", {}).get("filepath")
# #                     if fp and fp.endswith(('.xlsx', '.xlsm')):
# #                         active_files.add(fp)
        
# #         if not active_files:
# #             QMessageBox.information(self, "No Active Files", "No Excel files are currently loaded.")
# #             return
            
# #         file_path, ok = QInputDialog.getItem(self, "Select Existing File", "Choose an Excel file:", list(active_files), 0, False)
# #         if not ok: return
        
# #         try:
# #             xl = pd.ExcelFile(file_path)
# #             sheet_name, ok = QInputDialog.getItem(self, "Select Sheet", f"Select sheet:", xl.sheet_names, 0, False)
# #             if not ok: return
# #         except Exception as e:
# #             QMessageBox.critical(self, "Error", f"Could not read file: {e}")
# #             return
            
# #         alias, ok = QInputDialog.getText(self, "DataFrame Alias", "Variable name:")
# #         if not ok or not alias.strip(): return
# #         alias = alias.strip()

# #         reply = QMessageBox.question(self, 'Dynamic Input',
# #                                      f"Prompt user to select file for '{alias}'?",
# #                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
# #         prompt_at_runtime = (reply == QMessageBox.Yes)

# #         try:
# #             df = pd.read_excel(file_path, sheet_name=sheet_name)
# #             self.global_dfs[alias] = df
# #             self.preview_dfs = self.global_dfs.copy()
# #             self.update_tabs()
            
# #             step = {
# #                 "step_id": len(self.processes[self.current_process]) + 1,
# #                 "action": "load_file",
# #                 "params": {"filepath": file_path, "sheet": sheet_name, "alias": alias, "prompt_at_runtime": prompt_at_runtime}
# #             }
# #             self.processes[self.current_process].append(step)
# #             self.refresh_step_list()
# #         except Exception as e:
# #             QMessageBox.critical(self, "Error", str(e))

# #     def copy_df_name(self, name, btn):
# #         """Copies the DataFrame alias to clipboard and temporarily updates the button UI"""
# #         QApplication.clipboard().setText(name)
# #         original_text = btn.text()
# #         btn.setText("✅ Copied!")
# #         btn.setStyleSheet("background-color: #2da44e; color: white; border: none;") # Success green color
        
# #         # Reset button state after 1.5 seconds
# #         QTimer.singleShot(1500, lambda: self.reset_copy_btn(btn, original_text))

# #     def reset_copy_btn(self, btn, text):
# #         """Resets the copy button back to its standard state safely"""
# #         try:
# #             btn.setText(text)
# #             btn.setStyleSheet("") # Revert to the application's standard stylesheet
# #         except RuntimeError:
# #             pass # Button might have been destroyed if the user navigated/refreshed tabs quickly

# #     def update_tabs(self):
# #         self.tabs.clear()
# #         self.combo_view.blockSignals(True)
# #         self.combo_view.clear()
        
# #         var_table = QTableWidget(len(self.preview_vars), 3)
# #         var_table.setHorizontalHeaderLabels(["Variable Name", "Type", "Value"])
# #         var_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
# #         var_table.verticalHeader().setVisible(False)
        
# #         row = 0
# #         for k, v in self.preview_vars.items():
# #             var_table.setItem(row, 0, QTableWidgetItem(str(k)))
# #             var_table.setItem(row, 1, QTableWidgetItem(type(v).__name__))
# #             var_table.setItem(row, 2, QTableWidgetItem(str(v)[:100]))
# #             row += 1
            
# #         self.tabs.addTab(var_table, "📦 Variables Explorer")
# #         self.combo_view.addItem("📦 Variables Explorer")

# #         for alias, df in self.preview_dfs.items():
# #             # Create a container widget for the tab's specific layout
# #             tab_widget = QWidget()
# #             tab_layout = QVBoxLayout(tab_widget)
# #             tab_layout.setContentsMargins(5, 5, 5, 5)

# #             # --- Start Custom Feature: Tab Actions Header ---
# #             top_bar = QHBoxLayout()
# #             lbl_alias = QLabel(f"Viewing DataFrame: <b>{alias}</b>")
# #             lbl_alias.setStyleSheet("font-size: 11pt;")
            
# #             btn_copy = QPushButton("📋 Copy Name")
# #             btn_copy.setFixedWidth(120)
# #             btn_copy.setObjectName("btnPrimary")
# #             # Connect using default argument in lambda to lock in this specific loop's 'alias' and 'btn_copy'
# #             btn_copy.clicked.connect(lambda checked=False, n=alias, b=btn_copy: self.copy_df_name(n, b))
            
# #             top_bar.addWidget(lbl_alias)
# #             top_bar.addStretch()
# #             top_bar.addWidget(btn_copy)
            
# #             tab_layout.addLayout(top_bar)
# #             # --- End Custom Feature ---

# #             table = QTableView()
# #             table.setModel(PandasModel(df))
# #             table.verticalHeader().setVisible(False)
# #             table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
# #             table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
# #             table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
# #             table.horizontalHeader().setDefaultSectionSize(120)
            
# #             tab_layout.addWidget(table)
            
# #             # Add the entire container instead of just the table
# #             self.tabs.addTab(tab_widget, f"📊 DF: {alias}")
# #             self.combo_view.addItem(f"📊 DF: {alias}")
            
# #         self.combo_view.blockSignals(False)
# #         self.lbl_context.setText(f"Context: DFs ({len(self.preview_dfs)}) | Vars ({len(self.preview_vars)})")

# #     def get_editor_step_data(self):
# #         action_type = self.combo_action.currentText()
# #         step = {"action": ""}
# #         if action_type == "Execute Raw Python/Pandas":
# #             step["action"] = "execute_python_logic"
# #             step["params"] = {"code_block": self.txt_python.toPlainText()}
# #         elif action_type == "Evaluate Excel Formula (Native Math)":
# #             step["action"] = "evaluate_excel_formula"
# #             step["params"] = {
# #                 "formula": self.txt_excel_formula.toPlainText(),
# #                 "target_alias": self.txt_excel_target.text(),
# #                 "target_col": self.txt_excel_column.text() if self.txt_excel_column.text().strip() else None
# #             }
# #         elif action_type == "Run External .py Script (Entire File)":
# #             step["action"] = "run_python_file"
# #             step["params"] = {"script_path": self.txt_script_path.text()}
# #         return step

# #     def test_step(self):
# #         step = self.get_editor_step_data()
# #         if not step["params"].get("code_block") and step["action"] == "execute_python_logic": return
        
# #         self.pending_step = step
# #         self.worker = StepPreviewWorker(self.global_dfs, self.global_vars, step)
# #         self.worker.result_ready.connect(self.on_test_success)
# #         self.worker.error_occurred.connect(self.on_test_error)
# #         self.worker.start()

# #     def on_test_success(self, new_dfs, new_vars):
# #         self.preview_dfs = new_dfs
# #         self.preview_vars = new_vars
# #         self.update_tabs()
# #         QMessageBox.information(self, "Test Passed", "Code executed!")

# #     def on_test_error(self, err_msg):
# #         QMessageBox.critical(self, "Logic Error", f"Failed to execute:\n\n{err_msg}")

# #     # FIX: Allows you to instantly record what is in the editor without having to run "Test" first
# #     def record_step(self):
# #         step = self.get_editor_step_data()
        
# #         # Validation
# #         if step["action"] == "execute_python_logic" and not step["params"].get("code_block", "").strip():
# #             QMessageBox.warning(self, "Warning", "Code block is empty!")
# #             return
# #         elif step["action"] == "run_python_file" and not step["params"].get("script_path", "").strip():
# #             QMessageBox.warning(self, "Warning", "Script path is empty!")
# #             return
            
# #         step["step_id"] = len(self.processes[self.current_process]) + 1
# #         self.processes[self.current_process].append(step)
        
# #         # If tested recently, commit state
# #         if self.pending_step:
# #             self.global_dfs = self.preview_dfs.copy()
# #             self.global_vars = self.preview_vars.copy()
# #             self.pending_step = None
            
# #         self.refresh_step_list()
# #         QMessageBox.information(self, "Recorded", f"Step '{step['action']}' successfully recorded.")

# #     def load_step_into_editor(self, item):
# #         row_idx = self.list_steps.row(item)
# #         step = self.processes[self.current_process][row_idx]
        
# #         if step["action"] == "execute_python_logic":
# #             self.combo_action.setCurrentText("Execute Raw Python/Pandas")
# #             self.txt_python.setPlainText(step["params"].get("code_block", ""))
# #         elif step["action"] == "evaluate_excel_formula":
# #             self.combo_action.setCurrentText("Evaluate Excel Formula (Native Math)")
# #             self.txt_excel_formula.setPlainText(step["params"].get("formula", ""))
# #             self.txt_excel_target.setText(step["params"].get("target_alias", ""))
# #             self.txt_excel_column.setText(step["params"].get("target_col", ""))
# #         elif step["action"] == "run_python_file":
# #             self.combo_action.setCurrentText("Run External .py Script (Entire File)")
# #             self.txt_script_path.setText(step["params"].get("script_path", ""))

# #     # ** Hook for Reordering Steps in List **
# #     def on_step_moved(self, old_index, new_index):
# #         if not (0 <= old_index < len(self.processes[self.current_process])) or not (0 <= new_index < len(self.processes[self.current_process])):
# #             return
            
# #         step_list = self.processes[self.current_process]
        
# #         # Pop the step out and put it in its new location
# #         step = step_list.pop(old_index)
# #         step_list.insert(new_index, step)
        
# #         # Sequentially re-assign step_ids so they remain perfect [1, 2, 3...]
# #         for i, s in enumerate(step_list):
# #             s["step_id"] = i + 1
            
# #         self.refresh_step_list()
# #         self.list_steps.setCurrentRow(new_index) # Keep the moved item selected

# #     # FIX: Allows you to grab the live editor content and seamlessly overwrite the selected list item
# #     def update_selected_step(self):
# #         current_item = self.list_steps.currentItem()
# #         if not current_item:
# #             QMessageBox.warning(self, "Warning", "Please select a step from the list to update.")
# #             return
            
# #         row_idx = self.list_steps.row(current_item)
# #         original_step = self.processes[self.current_process][row_idx]
        
# #         if original_step["action"] == "load_file":
# #             active_files = set()
# #             for proc in self.processes.values():
# #                 for s in proc:
# #                     if s.get("action") == "load_file":
# #                         fp = s.get("params", {}).get("filepath")
# #                         if fp: active_files.add(fp)
# #             dialog = EditLoadDialog(original_step.get("params", {}), list(active_files), self)
# #             if dialog.exec_() == QDialog.Accepted:
# #                 original_step["params"] = dialog.get_params()
# #                 self.processes[self.current_process][row_idx] = original_step
# #                 self.refresh_step_list()
# #             return
            
# #         new_step_data = self.get_editor_step_data()
        
# #         # Validation
# #         if new_step_data["action"] == "execute_python_logic" and not new_step_data["params"].get("code_block", "").strip():
# #             QMessageBox.warning(self, "Warning", "Code block is empty!")
# #             return
            
# #         new_step_data["step_id"] = original_step["step_id"]
# #         self.processes[self.current_process][row_idx] = new_step_data
# #         self.refresh_step_list()
        
# #         QMessageBox.information(self, "Success", "Step updated successfully. (Note: Run the pipeline to refresh the visual state)")

# #     def delete_step(self):
# #         current_item = self.list_steps.currentItem()
# #         if not current_item: return
# #         row_idx = self.list_steps.row(current_item)
# #         if QMessageBox.question(self, 'Delete', "Delete this step?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
# #             del self.processes[self.current_process][row_idx]
# #             for i, step in enumerate(self.processes[self.current_process]):
# #                 step["step_id"] = i + 1
# #             self.refresh_step_list()

# #     def run_full_restore(self, export_path=None):
# #         if not any(self.processes.values()): return
# #         self.last_export_path = export_path
# #         self.terminal_output.append("\n>>> Restoring Pipeline Data...")
# #         self.restore_worker = PipelineRestoreWorker(self.processes)
# #         self.restore_worker.progress_update.connect(self.terminal_output.append)
# #         self.restore_worker.result_ready.connect(self.on_restore_success)
# #         self.restore_worker.error_occurred.connect(self.on_restore_error)
# #         self.restore_worker.start()

# #     def on_restore_success(self, dfs, vars):
# #         self.global_dfs, self.global_vars = dfs.copy(), vars.copy()
# #         self.preview_dfs, self.preview_vars = dfs.copy(), vars.copy()
# #         self.update_tabs()
# #         self.terminal_output.append(">>> Success!")
        
# #         if hasattr(self, 'last_export_path') and self.last_export_path:
# #             self.terminal_output.append(f">>> Exporting results to: {self.last_export_path}")
# #             try:
# #                 output_file = os.path.join(self.last_export_path, 'Final_Pipeline_Output.xlsx')
# #                 with pd.ExcelWriter(output_file) as writer:
# #                     exported_count = 0
# #                     for alias, df in dfs.items():
# #                         if not self.export_dfs or alias in self.export_dfs:
# #                             df.to_excel(writer, sheet_name=str(alias)[:31], index=False)
# #                             exported_count += 1
# #                 self.terminal_output.append(f">>> Export Complete: {exported_count} DataFrames saved.")
# #             except Exception as e:
# #                 self.terminal_output.append(f">>> Export Error: {e}")
# #             self.last_export_path = None

# #     def on_restore_error(self, err):
# #         self.terminal_output.append(f">>> Error: {err}")

# #     def load_config_from_path(self, file_path):
# #         try:
# #             with open(file_path, 'r') as f:
# #                 config = json.load(f)
# #             self.processes = config["processes"]
# #             self.export_dfs = config.get("export_dfs", [])
# #             self.current_config_path = file_path
            
# #             self.combo_processes.blockSignals(True)
# #             self.combo_processes.clear()
# #             for n in self.processes.keys():
# #                 self.combo_processes.addItem(n)
# #             self.current_process = list(self.processes.keys())[0]
# #             self.combo_processes.setCurrentText(self.current_process)
# #             self.combo_processes.blockSignals(False)
            
# #             self.refresh_step_list()
# #             self.update_tabs()
# #         except Exception as e:
# #             QMessageBox.critical(self, "Error", f"Could not load config:\n{e}")

# #     def load_config(self):
# #         file_path, _ = QFileDialog.getOpenFileName(self, "Load Config", "Config", "JSON Files (*.json)")
# #         if file_path:
# #             self.load_config_from_path(file_path)
# #             if QMessageBox.question(self, 'Restore', "Run pipeline now?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
# #                 self.run_full_restore()

# #     def save_config(self):
# #         default_name = self.current_config_path or "Config/Master_Config.json"
# #         file_path, _ = QFileDialog.getSaveFileName(self, "Save Pipeline", default_name, "JSON Files (*.json)")
# #         if file_path:
# #             config = {
# #                 "pipeline_name": os.path.splitext(os.path.basename(file_path))[0], 
# #                 "export_dfs": self.export_dfs, 
# #                 "processes": self.processes
# #             }
# #             with open(file_path, 'w') as f:
# #                 json.dump(config, f, indent=4)
# #             self.current_config_path = file_path
# #             self.setWindowTitle(f"Pipeline Editor - {os.path.basename(file_path)}")
# #             QMessageBox.information(self, "Saved", f"Saved to {file_path}.")

# # if __name__ == "__main__":
# #     app = QApplication(sys.argv)
# #     window = ScorecardUI()
# #     window.show()
# #     sys.exit(app.exec_())



# # ==============================================================================
# # FILE LOCATION: Dynamic_Scorecard_System/scorecard_ui.py
# # ==============================================================================

# import sys
# import json
# import traceback
# import os
import threading
from concurrent.futures import ThreadPoolExecutor
# import io
# import contextlib
# import shutil
# import pandas as pd
# import numpy as np

# # Force the working directory to be where the EXE is located (or script if running raw)
# if getattr(sys, 'frozen', False):
#     application_path = os.path.dirname(sys.executable)
# else:
#     application_path = os.path.dirname(os.path.abspath(__file__))

# os.chdir(application_path)

# from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
#                              QHBoxLayout, QPushButton, QLabel, QFileDialog, 
#                              QTableView, QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem,
#                              QComboBox, QTextEdit, QLineEdit, QMessageBox, QGroupBox, 
#                              QInputDialog, QTabWidget, QHeaderView, QSplitter, QAction,
#                              QDialog, QFormLayout, QCheckBox, QDialogButtonBox, QAbstractItemView,
#                              QDockWidget, QStackedWidget, QScrollArea, QFrame, QGridLayout,
#                              QToolTip) # <-- Added QToolTip for column copy feedback
# from PyQt5.QtCore import QAbstractTableModel, Qt, QThread, pyqtSignal, QEvent, QTimer
# from PyQt5.QtGui import QFont, QCursor # <-- Added QCursor for tooltip positioning

# # Make sure these are accessible in your environment
# try:
#     from dynamic_engine import DynamicPipelineEngine, prompt_file
# except ImportError:
#     # Dummy classes to allow UI to run if engine isn't present
#     class DynamicPipelineEngine: pass
#     prompt_file = None

# try:
#     from excel_analyzer import analyze_workbook
# except ImportError:
#     analyze_workbook = None

# class DraggableListWidget(QListWidget):
#     """Custom QListWidget that handles drag-and-drop reordering and emits a signal when an item is moved."""
#     item_moved = pyqtSignal(int, int) # old_index, new_index

#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setDragDropMode(QAbstractItemView.InternalMove)

#     def dropEvent(self, event):
#         if event.source() == self:
#             old_index = self.currentRow()
#             super().dropEvent(event)
#             new_index = self.currentRow()
#             if old_index != new_index and old_index >= 0 and new_index >= 0:
#                 self.item_moved.emit(old_index, new_index)
#         else:
#             super().dropEvent(event)

# class ProcessManagerDialog(QDialog):
#     """Dialog to manage, rename, reorder, and insert Processes."""
#     def __init__(self, processes_dict, parent=None):
#         super().__init__(parent)
#         self.setWindowTitle("Manage & Reorder Processes")
#         self.setMinimumWidth(450)
#         self.setMinimumHeight(400)
        
#         layout = QVBoxLayout(self)
#         lbl = QLabel("Drag and drop to reorder. Processes execute from top to bottom.")
#         lbl.setStyleSheet("color: #007acc; font-weight: bold; margin-bottom: 5px;")
#         lbl.setWordWrap(True)
#         layout.addWidget(lbl)
        
#         self.process_map = {k: k for k in processes_dict.keys()}
        
#         self.list_widget = QListWidget()
#         self.list_widget.setDragDropMode(QAbstractItemView.InternalMove)
#         for proc in processes_dict.keys():
#             self.list_widget.addItem(proc)
#         layout.addWidget(self.list_widget)
        
#         btn_layout = QHBoxLayout()
#         btn_add = QPushButton("➕ Insert New")
#         btn_add.clicked.connect(self.add_process)
#         btn_rename = QPushButton("✏️ Rename")
#         btn_rename.clicked.connect(self.rename_process)
#         btn_del = QPushButton("🗑️ Delete")
#         btn_del.setObjectName("btnDanger")
#         btn_del.clicked.connect(self.delete_process)
        
#         btn_layout.addWidget(btn_add)
#         btn_layout.addWidget(btn_rename)
#         btn_layout.addWidget(btn_del)
#         layout.addLayout(btn_layout)
        
#         self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
#         self.buttons.accepted.connect(self.accept)
#         self.buttons.rejected.connect(self.reject)
#         layout.addWidget(self.buttons)

#     def add_process(self):
#         name, ok = QInputDialog.getText(self, "New Process", "Enter new process name:")
#         if ok and name.strip():
#             name = name.strip()
#             if name in [self.list_widget.item(i).text() for i in range(self.list_widget.count())]:
#                 QMessageBox.warning(self, "Error", "Process name already exists.")
#                 return
            
#             self.process_map[name] = None # None indicates a brand new process
            
#             # Insert directly below the selected item (allows inserting in the middle!)
#             curr_row = self.list_widget.currentRow()
#             if curr_row >= 0:
#                 self.list_widget.insertItem(curr_row + 1, name)
#                 self.list_widget.setCurrentRow(curr_row + 1)
#             else:
#                 self.list_widget.addItem(name)
#                 self.list_widget.setCurrentRow(self.list_widget.count() - 1)
                
#     def rename_process(self):
#         item = self.list_widget.currentItem()
#         if not item: return
#         old_name = item.text()
#         new_name, ok = QInputDialog.getText(self, "Rename", "New process name:", QLineEdit.Normal, old_name)
#         if ok and new_name.strip() and new_name.strip() != old_name:
#             new_name = new_name.strip()
#             if new_name in [self.list_widget.item(i).text() for i in range(self.list_widget.count())]:
#                 QMessageBox.warning(self, "Error", "Process name already exists.")
#                 return
            
#             # Maintain mapping back to the original dictionary key
#             original_mapped_name = self.process_map.pop(old_name)
#             self.process_map[new_name] = original_mapped_name
#             item.setText(new_name)

#     def delete_process(self):
#         item = self.list_widget.currentItem()
#         if not item: return
#         if self.list_widget.count() <= 1:
#             QMessageBox.warning(self, "Error", "You must have at least one active process.")
#             return
#         if QMessageBox.question(self, "Delete", f"Delete process '{item.text()}' and all its steps?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
#             self.process_map.pop(item.text(), None)
#             self.list_widget.takeItem(self.list_widget.row(item))
            
#     def get_process_mapping(self):
#         """Returns the ordered list of tuples: (new_process_name, old_mapped_name_or_None)"""
#         result = []
#         for i in range(self.list_widget.count()):
#             name = self.list_widget.item(i).text()
#             result.append((name, self.process_map.get(name)))
#         return result

# class TerminalInput(QLineEdit):
#     """Enhanced QLineEdit with command history (Up/Down arrows)"""
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.history = []
#         self.history_index = -1
#         self.temp_cmd = ""

#     def keyPressEvent(self, event):
#         if event.key() == Qt.Key_Up:
#             if not self.history:
#                 return
#             if self.history_index == -1:
#                 self.temp_cmd = self.text()
            
#             if self.history_index < len(self.history) - 1:
#                 self.history_index += 1
#                 self.setText(self.history[self.history_index])
        
#         elif event.key() == Qt.Key_Down:
#             if self.history_index > -1:
#                 self.history_index -= 1
#                 if self.history_index == -1:
#                     self.setText(self.temp_cmd)
#                 else:
#                     self.setText(self.history[self.history_index])
        
#         else:
#             super().keyPressEvent(event)
#             if event.key() != Qt.Key_Return and event.key() != Qt.Key_Enter:
#                 self.history_index = -1

#     def add_to_history(self, cmd):
#         if cmd.strip():
#             # Remove existing occurrence to move it to the front
#             if cmd in self.history:
#                 self.history.remove(cmd)
#             self.history.insert(0, cmd)
#         self.history_index = -1
#         self.temp_cmd = ""

# class PandasModel(QAbstractTableModel):
#     def __init__(self, data):
#         super().__init__()
#         self._data = data

#     def rowCount(self, parent=None): return self._data.shape[0]
#     def columnCount(self, parent=None): return self._data.shape[1]
#     def data(self, index, role=Qt.DisplayRole):
#         if index.isValid() and role == Qt.DisplayRole:
#             val = self._data.iloc[index.row(), index.column()]
#             return str(val) if not pd.isna(val) else ""
#         return None
#     def headerData(self, col, orientation, role):
#         if orientation == Qt.Horizontal and role == Qt.DisplayRole:
#             return str(self._data.columns[col])
#         return None

# class StepPreviewWorker(QThread):
#     result_ready = pyqtSignal(dict, dict)
#     error_occurred = pyqtSignal(str)

#     def __init__(self, dfs_dict, vars_dict, step):
#         super().__init__()
#         self.dfs_dict = {k: v.copy() for k, v in dfs_dict.items()}
#         self.vars_dict = {k: v for k, v in vars_dict.items()}
#         self.step = step
#         self.engine = DynamicPipelineEngine()

#     def run(self):
#         try:
#             new_dfs, new_vars = self.engine._apply_step(self.dfs_dict, self.vars_dict, self.step)
#             self.result_ready.emit(new_dfs, new_vars)
#         except Exception as e:
#             self.error_occurred.emit(traceback.format_exc())

# class PipelineRestoreWorker(QThread):
#     progress_update = pyqtSignal(str)
#     result_ready = pyqtSignal(dict, dict)
#     error_occurred = pyqtSignal(str)

#     def __init__(self, processes):
#         super().__init__()
#         self.processes = processes
#         self.engine = DynamicPipelineEngine()

#     def run(self):
#         dfs_dict = {}
#         vars_dict = {}
#         try:
#             for proc_name, steps in self.processes.items():
#                 self.progress_update.emit(f"\n--- Running Process: {proc_name} ---")
#                 for step in steps:
#                     self.progress_update.emit(f">>> Executing [{step['step_id']}] {step['action']}...")
                    
#                     original_prompt = step.get('params', {}).get('prompt_at_runtime', False)
#                     if 'params' in step:
#                         step['params']['prompt_at_runtime'] = False
                        
#                     dfs_dict, vars_dict = self.engine._apply_step(dfs_dict, vars_dict, step)
                    
#                     if 'params' in step:
#                         step['params']['prompt_at_runtime'] = original_prompt

#             self.result_ready.emit(dfs_dict, vars_dict)
#         except Exception as e:
#             self.error_occurred.emit(traceback.format_exc())

# class ExcelAnalysisWorker(QThread):
#     result_ready = pyqtSignal(dict)
#     error_occurred = pyqtSignal(str)

#     def __init__(self, file_path):
#         super().__init__()
#         self.file_path = file_path

#     def run(self):
#         try:
#             config = analyze_workbook(self.file_path)
#             self.result_ready.emit(config)
#         except Exception as e:
#             self.error_occurred.emit(str(e))

# class ExportConfigDialog(QDialog):
#     """Custom Dialog for selecting which DataFrames to export to Excel"""
#     def __init__(self, all_dfs, selected_dfs, parent=None):
#         super().__init__(parent)
#         self.setWindowTitle("Configure Headless Export")
#         self.resize(450, 500) # Sets a default size allowing space for lists
        
#         layout = QVBoxLayout(self)
        
#         if not all_dfs:
#             layout.addWidget(QLabel("No DataFrames currently available.\nRun the pipeline or load data first."))
#         else:
#             header_lbl = QLabel("Select which DataFrames to export to Excel\nduring automated Headless execution:")
#             header_lbl.setStyleSheet("margin-bottom: 5px;")
#             layout.addWidget(header_lbl)
            
#             # Action Buttons for Quick Selection
#             btn_layout = QHBoxLayout()
#             btn_select_all = QPushButton("☑ Select All")
#             btn_select_all.clicked.connect(self.select_all)
#             btn_deselect_all = QPushButton("☐ Deselect All")
#             btn_deselect_all.clicked.connect(self.deselect_all)
            
#             btn_layout.addWidget(btn_select_all)
#             btn_layout.addWidget(btn_deselect_all)
#             layout.addLayout(btn_layout)
            
#             # Scrollable List Widget with Checkboxes
#             self.list_widget = QListWidget()
#             self.list_widget.setSelectionMode(QAbstractItemView.NoSelection) # Prevent highlighting, rely purely on checkboxes
            
#             for df_name in all_dfs:
#                 item = QListWidgetItem(df_name)
#                 item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                
#                 # If selected_dfs is empty but we have dfs, default to checked (fallback)
#                 if df_name in selected_dfs or (not selected_dfs and df_name in all_dfs):
#                     item.setCheckState(Qt.Checked)
#                 else:
#                     item.setCheckState(Qt.Unchecked)
                    
#                 self.list_widget.addItem(item)
                
#             layout.addWidget(self.list_widget)
            
#         self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
#         self.buttons.accepted.connect(self.accept)
#         self.buttons.rejected.connect(self.reject)
#         layout.addWidget(self.buttons)

#     def select_all(self):
#         if hasattr(self, 'list_widget'):
#             for i in range(self.list_widget.count()):
#                 self.list_widget.item(i).setCheckState(Qt.Checked)
            
#     def deselect_all(self):
#         if hasattr(self, 'list_widget'):
#             for i in range(self.list_widget.count()):
#                 self.list_widget.item(i).setCheckState(Qt.Unchecked)

#     def get_selected(self):
#         if not hasattr(self, 'list_widget'):
#             return []
        
#         selected = []
#         for i in range(self.list_widget.count()):
#             item = self.list_widget.item(i)
#             if item.checkState() == Qt.Checked:
#                 selected.append(item.text())
#         return selected

# class EditLoadDialog(QDialog):
#     """Custom Dialog for editing an existing 'load_file' step"""
#     def __init__(self, step_params, active_files=None, parent=None):
#         super().__init__(parent)
#         self.active_files = active_files or []
#         self.setWindowTitle("Edit Load File Step")
#         self.setMinimumWidth(550)
        
#         layout = QFormLayout(self)
        
#         self.filepath_input = QLineEdit(step_params.get("filepath", ""))
        
#         # File Path Buttons
#         btn_layout = QHBoxLayout()
#         btn_layout.setContentsMargins(0, 0, 0, 0)
        
#         browse_btn = QPushButton("📁 Browse New")
#         browse_btn.clicked.connect(self.browse)
#         btn_layout.addWidget(browse_btn)
        
#         if self.active_files:
#             active_btn = QPushButton("📄 Select Active File")
#             active_btn.clicked.connect(self.select_active)
#             btn_layout.addWidget(active_btn)
            
#         fp_layout = QVBoxLayout()
#         fp_layout.setContentsMargins(0, 0, 0, 0)
#         fp_layout.addWidget(self.filepath_input)
#         fp_layout.addLayout(btn_layout)
        
#         layout.addRow("File Path:", fp_layout)
        
#         # Sheet Selection Layout
#         self.sheet_input = QLineEdit(str(step_params.get("sheet", 0)))
#         self.sheet_input.setPlaceholderText("0 for first sheet, or 'Sheet1'")
        
#         sheet_layout = QHBoxLayout()
#         sheet_layout.setContentsMargins(0, 0, 0, 0)
#         sheet_layout.addWidget(self.sheet_input)
        
#         inspect_btn = QPushButton("🔍 Select Sheet")
#         inspect_btn.clicked.connect(self.list_sheets)
#         sheet_layout.addWidget(inspect_btn)
        
#         layout.addRow("Sheet Name/Index:", sheet_layout)
        
#         self.alias_input = QLineEdit(step_params.get("alias", ""))
#         layout.addRow("DataFrame Alias:", self.alias_input)
        
#         self.header_input = QLineEdit(str(step_params.get("header", 0)))
#         self.header_input.setPlaceholderText("0 for first row (default)")
#         layout.addRow("Header Row (Index):", self.header_input)
        
#         self.prompt_cb = QCheckBox("Prompt user to select this file at runtime (Filepath becomes a placeholder)")
#         self.prompt_cb.setChecked(step_params.get("prompt_at_runtime", False))
#         layout.addRow("", self.prompt_cb)
        
#         self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
#         self.buttons.accepted.connect(self.accept)
#         self.buttons.rejected.connect(self.reject)
#         layout.addRow(self.buttons)

#     def browse(self):
#         fp, _ = QFileDialog.getOpenFileName(self, "Select Excel/CSV", "", "Data Files (*.xlsx *.csv)")
#         if fp:
#             self.filepath_input.setText(fp)
            
#     def select_active(self):
#         if not self.active_files: return
#         fp, ok = QInputDialog.getItem(self, "Select Active File", "Choose an existing file from the pipeline:", self.active_files, 0, False)
#         if ok and fp:
#             self.filepath_input.setText(fp)

#     def list_sheets(self):
#         fp = self.filepath_input.text().strip()
#         if not fp or not os.path.exists(fp):
#             QMessageBox.warning(self, "File Not Found", "Cannot read sheets. Please ensure the file path is correct and accessible on your machine.")
#             return
#         if not fp.endswith(('.xlsx', '.xlsm')):
#             QMessageBox.information(self, "Not an Excel File", "Only Excel files have multiple sheets to select from.")
#             return
            
#         try:
#             xl = pd.ExcelFile(fp)
#             sheet, ok = QInputDialog.getItem(self, "Select Sheet", f"Available Sheets in {os.path.basename(fp)}:", xl.sheet_names, 0, False)
#             if ok and sheet:
#                 self.sheet_input.setText(sheet)
#         except Exception as e:
#             QMessageBox.critical(self, "Error", f"Could not read sheets:\n{e}")

#     def get_params(self):
#         sheet_val = self.sheet_input.text()
#         if sheet_val.isdigit():
#             sheet_val = int(sheet_val)
            
#         header_val = 0
#         if self.header_input.text().isdigit():
#             header_val = int(self.header_input.text())
            
#         fp = self.filepath_input.text().strip()
#         if not fp and self.prompt_cb.isChecked():
#             fp = "RUNTIME_PROMPT_ONLY.xlsx"
            
#         return {
#             "filepath": fp,
#             "sheet": sheet_val,
#             "header": header_val,
#             "alias": self.alias_input.text(),
#             "prompt_at_runtime": self.prompt_cb.isChecked()
#         }

# class ConfigCard(QGroupBox):
#     """A visually appealing card representing a pipeline configuration"""
#     edit_requested = pyqtSignal(str)
#     run_requested = pyqtSignal(str)
#     delete_requested = pyqtSignal(str)

#     def __init__(self, file_path, config_data):
#         title = config_data.get("pipeline_name", os.path.basename(file_path))
#         super().__init__(title)
#         self.file_path = file_path
#         self.setObjectName("ConfigCard")
        
#         layout = QVBoxLayout(self)
        
#         # Metadata
#         proc_count = len(config_data.get("processes", {}))
#         step_count = sum(len(steps) for steps in config_data.get("processes", {}).values())
        
#         self.info_lbl = QLabel(f"Processes: {proc_count} | Total Steps: {step_count}")
#         self.info_lbl.setObjectName("cardMetadata")
#         layout.addWidget(self.info_lbl)
        
#         self.path_lbl = QLabel(os.path.basename(file_path))
#         self.path_lbl.setObjectName("cardPath")
#         layout.addWidget(self.path_lbl)
        
#         layout.addStretch()
        
#         # Action Buttons
#         btn_layout = QHBoxLayout()
        
#         self.btn_run = QPushButton("▶ Run")
#         self.btn_run.setObjectName("btnSuccess")
#         self.btn_run.clicked.connect(lambda: self.run_requested.emit(self.file_path))
        
#         self.btn_edit = QPushButton("✏ Edit")
#         self.btn_edit.setObjectName("btnPrimary")
#         self.btn_edit.clicked.connect(lambda: self.edit_requested.emit(self.file_path))
        
#         self.btn_del = QPushButton("🗑")
#         self.btn_del.setObjectName("btnDanger")
#         self.btn_del.setFixedWidth(40)
#         self.btn_del.clicked.connect(lambda: self.delete_requested.emit(self.file_path))
        
#         btn_layout.addWidget(self.btn_run)
#         btn_layout.addWidget(self.btn_edit)
#         btn_layout.addWidget(self.btn_del)
        
#         layout.addLayout(btn_layout)

# class DashboardWidget(QWidget):
#     """The landing screen for the application"""
#     create_new_requested = pyqtSignal()
#     auto_generate_requested = pyqtSignal()
#     edit_config_requested = pyqtSignal(str)
#     run_config_requested = pyqtSignal(str)

#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.init_ui()

#     def init_ui(self):
#         main_layout = QVBoxLayout(self)
#         main_layout.setContentsMargins(40, 40, 40, 40)
#         main_layout.setSpacing(20)
        
#         # Header
#         header_layout = QHBoxLayout()
#         self.title_lbl = QLabel("Dynamic Scorecard System")
#         self.title_lbl.setObjectName("mainTitle")
#         header_layout.addWidget(self.title_lbl)
        
#         header_layout.addStretch()
        
#         self.btn_new = QPushButton("➕ Create New Configuration")
#         self.btn_new.setObjectName("btnPrimary")
#         self.btn_new.setMinimumHeight(50)
#         self.btn_new.clicked.connect(self.create_new_requested.emit)
#         header_layout.addWidget(self.btn_new)
        
#         self.btn_auto = QPushButton("🪄 Auto-Generate from Excel")
#         self.btn_auto.setObjectName("btnSuccess")
#         self.btn_auto.setMinimumHeight(50)
#         self.btn_auto.clicked.connect(self.auto_generate_requested.emit)
#         header_layout.addWidget(self.btn_auto)
        
#         self.btn_import_config = QPushButton("📥 Import Config")
#         self.btn_import_config.setMinimumHeight(50)
#         self.btn_import_config.clicked.connect(self.import_config)
#         header_layout.addWidget(self.btn_import_config)
        
#         self.btn_refresh = QPushButton("🔄 Refresh")
#         self.btn_refresh.setMinimumHeight(50)
#         self.btn_refresh.setFixedWidth(120)
#         self.btn_refresh.clicked.connect(self.refresh_configs)
#         header_layout.addWidget(self.btn_refresh)
        
#         main_layout.addLayout(header_layout)
        
#         # Divider
#         self.divider = QFrame()
#         self.divider.setObjectName("mainDivider")
#         self.divider.setFrameShape(QFrame.HLine)
#         self.divider.setFrameShadow(QFrame.Sunken)
#         main_layout.addWidget(self.divider)
        
#         # Scroll Area for Configs
#         self.scroll = QScrollArea()
#         self.scroll.setObjectName("dashboardScroll")
#         self.scroll.setWidgetResizable(True)
        
#         self.container = QWidget()
#         self.container.setObjectName("dashboardContainer")
#         self.flow_layout = QGridLayout(self.container) # Using grid for card layout
#         self.flow_layout.setSpacing(20)
        
#         self.scroll.setWidget(self.container)
#         main_layout.addWidget(self.scroll)
        
#         self.refresh_configs()

#     def import_config(self):
#         file_path, _ = QFileDialog.getOpenFileName(self, "Select Configuration to Import", "", "JSON Files (*.json)")
#         if file_path:
#             config_dir = "Config"
#             if not os.path.exists(config_dir):
#                 os.makedirs(config_dir)
#             dest_path = os.path.join(config_dir, os.path.basename(file_path))
#             if os.path.abspath(file_path) != os.path.abspath(dest_path):
#                 try:
#                     shutil.copy2(file_path, dest_path)
#                     QMessageBox.information(self, "Success", f"Config imported into application:\n{dest_path}")
#                     self.refresh_configs()
#                 except Exception as e:
#                     QMessageBox.critical(self, "Error", f"Could not import config:\n{e}")

#     def refresh_configs(self):
#         # Clear existing
#         for i in reversed(range(self.flow_layout.count())): 
#             self.flow_layout.itemAt(i).widget().setParent(None)
            
#         config_dir = "Config"
#         if not os.path.exists(config_dir):
#             os.makedirs(config_dir)
            
#         configs = [f for f in os.listdir(config_dir) if f.endswith(".json")]
        
#         if not configs:
#             empty_lbl = QLabel("No configurations found. Create your first pipeline to get started!")
#             empty_lbl.setAlignment(Qt.AlignCenter)
#             empty_lbl.setObjectName("emptyMsg")
#             self.flow_layout.addWidget(empty_lbl, 0, 0)
#             return

#         col_limit = 3
#         for idx, filename in enumerate(configs):
#             path = os.path.join(config_dir, filename)
#             try:
#                 with open(path, 'r') as f:
#                     data = json.load(f)
                
#                 card = ConfigCard(path, data)
#                 card.edit_requested.connect(self.edit_config_requested.emit)
#                 card.run_requested.connect(self.run_config_requested.emit)
#                 card.delete_requested.connect(self.delete_config)
                
#                 self.flow_layout.addWidget(card, idx // col_limit, idx % col_limit)
#             except Exception as e:
#                 print(f"Error loading {filename}: {e}")

#     def delete_config(self, path):
#         reply = QMessageBox.question(self, 'Delete Configuration', 
#                                      f"Are you sure you want to delete '{os.path.basename(path)}'?\nThis cannot be undone.",
#                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
#         if reply == QMessageBox.Yes:
#             try:
#                 os.remove(path)
#                 self.refresh_configs()
#             except Exception as e:
#                 QMessageBox.critical(self, "Error", f"Could not delete file: {e}")

# class ScorecardUI(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Dynamic Scorecard System - Dashboard")
#         self.resize(1600, 1000)
        
#         self.processes = {"Main_Process": []} 
#         self.current_process = "Main_Process"
#         self.export_dfs = [] 
#         self.current_config_path = None
        
#         self.global_dfs = {}
#         self.global_vars = {}
#         self.preview_dfs = {} 
#         self.preview_vars = {}
#         self.pending_step = None 
        
#         # State Management
#         self.stacked_widget = QStackedWidget()
#         self.setCentralWidget(self.stacked_widget)
        
#         self.init_ui()
#         self.apply_dark_theme()
        
#         # Start at Dashboard
#         self.show_dashboard()

#     def show_dashboard(self):
#         self.dashboard.refresh_configs()
#         self.stacked_widget.setCurrentIndex(0)
#         self.setWindowTitle("Dynamic Scorecard System - Dashboard")
        
#         # Hide Editor Docks
#         self.dock_pipeline.hide()
#         self.dock_sandbox.hide()
#         self.dock_terminal.hide()
        
#     def show_editor(self, config_path=None):
#         self.stacked_widget.setCurrentIndex(1)
#         self.dock_pipeline.show()
#         self.dock_sandbox.show()
#         self.dock_terminal.show()
        
#         if config_path:
#             self.load_config_from_path(config_path)
#             self.setWindowTitle(f"Pipeline Editor - {os.path.basename(config_path)}")
#         else:
#             self.new_config()
#             self.setWindowTitle("Pipeline Editor - New Configuration")

#     def new_config(self):
#         self.processes = {"Main_Process": []}
#         self.current_process = "Main_Process"
#         self.export_dfs = []
#         self.current_config_path = None
#         self.global_dfs = {}
#         self.global_vars = {}
#         self.preview_dfs = {}
#         self.preview_vars = {}
        
#         self.combo_processes.blockSignals(True)
#         self.combo_processes.clear()
#         self.combo_processes.addItem("Main_Process")
#         self.combo_processes.blockSignals(False)
        
#         self.refresh_step_list()
#         self.update_tabs()

#     def run_config_from_dashboard(self, path):
#         export_dir = QFileDialog.getExistingDirectory(self, "Select Export Folder for Final Data")
#         if not export_dir: return # User cancelled
#         self.show_editor(path)
#         self.run_full_restore(export_dir)

#     def apply_dark_theme(self):
#         dark_qss = """
#         QMainWindow, QWidget { 
#             background-color: #1e1e1e; 
#             color: #d4d4d4; 
#             font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; 
#             font-size: 10pt; 
#         }
        
#         /* Dashboard Specifics */
#         QLabel#mainTitle { font-size: 26pt; font-weight: bold; color: #ffffff; padding-bottom: 5px; }
#         QLabel#emptyMsg { color: #888888; font-size: 14pt; margin-top: 50px; }
#         QFrame#mainDivider { background-color: #333333; height: 1px; border: none; }
#         QScrollArea#dashboardScroll { background-color: transparent; border: none; }
#         QWidget#dashboardContainer { background-color: transparent; }

#         /* Config Card Specifics */
#         QGroupBox#ConfigCard {
#             background-color: #2d2d30;
#             border: 2px solid #3e3e42;
#             border-radius: 12px;
#             margin-top: 20px;
#             padding-top: 15px;
#             font-size: 11pt;
#         }
#         QGroupBox#ConfigCard:hover { border: 2px solid #007acc; background-color: #333337; }
#         QGroupBox#ConfigCard::title {
#             subcontrol-origin: margin;
#             subcontrol-position: top left;
#             left: 15px;
#             padding: 0 8px;
#             color: #007acc;
#             font-weight: bold;
#         }
#         QLabel#cardMetadata { color: #a0a0a0; font-size: 9pt; font-weight: 500; }
#         QLabel#cardPath { color: #666666; font-style: italic; font-size: 8pt; }

#         /* Editor Specifics */
#         QDockWidget::title { 
#             text-align: left; 
#             background: #252526; 
#             padding: 8px 12px; 
#             border-top-left-radius: 8px;
#             border-top-right-radius: 8px;
#             font-weight: bold; 
#             color: #007acc; 
#         }
#         QDockWidget { border: 1px solid #333333; border-radius: 12px; }
#         QGroupBox { 
#             border: 1px solid #333333; 
#             border-radius: 10px; 
#             margin-top: 20px; 
#             font-weight: bold; 
#             color: #007acc; 
#             padding-top: 10px;
#         }
#         QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 10px; left: 15px; }
        
#         QPushButton { 
#             background-color: #333333; 
#             color: #ffffff; 
#             border: 1px solid #444444; 
#             padding: 10px 18px; 
#             border-radius: 8px; 
#             font-weight: 600; 
#         }
#         QPushButton:hover { background-color: #404040; border-color: #007acc; }
#         QPushButton#btnPrimary { background-color: #007acc; border: none; }
#         QPushButton#btnPrimary:hover { background-color: #1a8ad4; }
#         QPushButton#btnSuccess { background-color: #2da44e; border: none; }
#         QPushButton#btnSuccess:hover { background-color: #2cbe4e; }
#         QPushButton#btnDanger { background-color: #cf222e; border: none; }
        
#         QLineEdit, QTextEdit, QComboBox { 
#             background-color: #252526; 
#             border: 1px solid #3c3c3c; 
#             border-radius: 8px; 
#             padding: 8px; 
#             color: #d4d4d4; 
#         }
#         QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border: 2px solid #007acc; background-color: #2d2d30; }
        
#         QTabWidget::pane { border: 1px solid #333333; border-radius: 10px; background: #1e1e1e; top: -1px; }
#         QTabBar::tab { 
#             background: #2d2d30; 
#             border: 1px solid #333333; 
#             padding: 10px 20px; 
#             color: #808080; 
#             border-top-left-radius: 8px; 
#             border-top-right-radius: 8px;
#             margin-right: 4px;
#         }
#         QTabBar::tab:selected { background: #1e1e1e; color: #ffffff; border-bottom: 3px solid #007acc; font-weight: bold; }

#         /* Table & Data Views */
#         QTableView, QTableWidget {
#             background-color: #1e1e1e;
#             gridline-color: #333333;
#             border: 1px solid #333333;
#             border-radius: 8px;
#             color: #d4d4d4;
#         }
#         QHeaderView::section {
#             background-color: #252526;
#             color: #007acc;
#             padding: 8px;
#             border: 1px solid #333333;
#             font-weight: bold;
#         }
#         QHeaderView {
#             background-color: #1e1e1e;
#         }
#         QTableCornerButton::section {
#             background-color: #252526;
#             border: 1px solid #333333;
#         }
#         QScrollBar:vertical { border: none; background: #1e1e1e; width: 12px; border-radius: 6px; }
#         QScrollBar::handle:vertical { background: #3e3e42; min-height: 20px; border-radius: 6px; }
#         QScrollBar::handle:vertical:hover { background: #4e4e52; }
#         """
#         self.setStyleSheet(dark_qss)
#         if hasattr(self, 'terminal_output'):
#             self.terminal_output.setStyleSheet("background-color: #0a0a0a; border-radius: 10px; color: #4CAF50; padding: 10px; font-family: 'Consolas';")
#             self.terminal_input.setStyleSheet("background-color: #0a0a0a; border: 1px solid #007acc; border-radius: 8px; color: #FFFFFF; padding: 8px;")
        
#         if hasattr(self, 'dashboard'):
#             self.dashboard.setStyleSheet(dark_qss)

#     def apply_white_theme(self):
#         white_qss = """
#         QMainWindow, QWidget { 
#             background-color: #f8f9fa; 
#             color: #212529; 
#             font-family: 'Segoe UI', system-ui, sans-serif; 
#             font-size: 10pt; 
#         }
        
#         /* Dashboard Specifics */
#         QLabel#mainTitle { font-size: 26pt; font-weight: bold; color: #1a1a1a; padding-bottom: 5px; }
#         QLabel#emptyMsg { color: #6c757d; font-size: 14pt; margin-top: 50px; }
#         QFrame#mainDivider { background-color: #dee2e6; height: 1px; border: none; }
#         QScrollArea#dashboardScroll { background-color: transparent; border: none; }
#         QWidget#dashboardContainer { background-color: transparent; }

#         /* Config Card Specifics */
#         QGroupBox#ConfigCard {
#             background-color: #ffffff;
#             border: 1px solid #dee2e6;
#             border-radius: 12px;
#             margin-top: 20px;
#             padding-top: 15px;
#             font-size: 11pt;
#         }
#         QGroupBox#ConfigCard:hover { border: 1px solid #007acc; background-color: #f8f9fa; }
#         QGroupBox#ConfigCard::title {
#             subcontrol-origin: margin;
#             subcontrol-position: top left;
#             left: 15px;
#             padding: 0 8px;
#             color: #007acc;
#             font-weight: bold;
#         }
#         QLabel#cardMetadata { color: #495057; font-size: 9pt; font-weight: 500; }
#         QLabel#cardPath { color: #6c757d; font-style: italic; font-size: 8pt; }

#         /* Editor Specifics */
#         QLabel { color: #212529; }
#         QDockWidget::title { 
#             text-align: left; 
#             background: #ffffff; 
#             padding: 8px 12px; 
#             border-top-left-radius: 8px;
#             border-top-right-radius: 8px;
#             font-weight: bold; 
#             color: #007acc; 
#             border-bottom: 1px solid #e9ecef;
#         }
#         QDockWidget { border: 1px solid #dee2e6; border-radius: 12px; background-color: #ffffff; }
#         QGroupBox { 
#             border: 1px solid #dee2e6; 
#             border-radius: 10px; 
#             margin-top: 20px; 
#             font-weight: bold; 
#             color: #007acc; 
#             background-color: #ffffff;
#             padding-top: 10px;
#         }
#         QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 10px; left: 15px; background-color: #ffffff; color: #007acc; }
        
#         QPushButton { 
#             background-color: #ffffff; 
#             color: #212529; 
#             border: 1px solid #dee2e6; 
#             padding: 10px 18px; 
#             border-radius: 8px; 
#             font-weight: 600; 
#         }
#         QPushButton:hover { background-color: #f1f3f5; border-color: #adb5bd; }
#         QPushButton#btnPrimary { background-color: #007acc; border: none; color: #ffffff; }
#         QPushButton#btnPrimary:hover { background-color: #1a8ad4; }
#         QPushButton#btnSuccess { background-color: #2da44e; border: none; color: #ffffff; }
#         QPushButton#btnSuccess:hover { background-color: #2cbe4e; }
#         QPushButton#btnDanger { background-color: #cf222e; border: none; color: #ffffff; }
        
#         QLineEdit, QTextEdit, QComboBox { 
#             background-color: #ffffff; 
#             border: 1px solid #dee2e6; 
#             border-radius: 8px; 
#             padding: 8px; 
#             color: #212529; 
#         }
#         QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border: 2px solid #007acc; background-color: #ffffff; }
        
#         QTabWidget::pane { border: 1px solid #dee2e6; border-radius: 10px; background: #ffffff; top: -1px; }
#         QTabBar::tab { 
#             background: #f1f3f5; 
#             border: 1px solid #dee2e6; 
#             padding: 10px 20px; 
#             color: #495057; 
#             border-top-left-radius: 8px; 
#             border-top-right-radius: 8px;
#             margin-right: 4px;
#         }
#         QTabBar::tab:selected { background: #ffffff; color: #007acc; border-bottom: 3px solid #007acc; font-weight: bold; }
        
#         /* Table & Data Views */
#         QTableView, QTableWidget {
#             background-color: #ffffff;
#             gridline-color: #e9ecef;
#             border: 1px solid #dee2e6;
#             border-radius: 8px;
#             color: #212529;
#         }
#         QHeaderView::section {
#             background-color: #f1f3f5;
#             color: #007acc;
#             padding: 8px;
#             border: 1px solid #dee2e6;
#             font-weight: bold;
#         }
#         QHeaderView {
#             background-color: #ffffff;
#         }
#         QTableCornerButton::section {
#             background-color: #f1f3f5;
#             border: 1px solid #dee2e6;
#         }
#         QScrollBar:vertical { border: none; background: #f8f9fa; width: 12px; border-radius: 6px; }
#         QScrollBar::handle:vertical { background: #dee2e6; min-height: 20px; border-radius: 6px; }
#         QScrollBar::handle:vertical:hover { background: #ced4da; }
#         """
#         self.setStyleSheet(white_qss)
#         if hasattr(self, 'terminal_output'):
#             self.terminal_output.setStyleSheet("background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 10px; color: #1a7f37; padding: 10px; font-family: 'Consolas';")
#             self.terminal_input.setStyleSheet("background-color: #ffffff; border: 2px solid #007acc; border-radius: 8px; color: #212529; padding: 8px;")
        
#         if hasattr(self, 'dashboard'):
#             self.dashboard.setStyleSheet(white_qss)
#             self.dashboard.refresh_configs()

#     def init_ui(self):
#         # --- Dashboard ---
#         self.dashboard = DashboardWidget()
#         self.dashboard.create_new_requested.connect(lambda: self.show_editor())
#         self.dashboard.auto_generate_requested.connect(self.auto_generate_pipeline)
#         self.dashboard.edit_config_requested.connect(lambda p: self.show_editor(p))
#         self.dashboard.run_config_requested.connect(self.run_config_from_dashboard)
#         self.stacked_widget.addWidget(self.dashboard)

#         # --- Menu Bar ---
#         menubar = self.menuBar()
#         file_menu = menubar.addMenu('File')

#         back_action = QAction('🔙 Back to Dashboard', self)
#         back_action.triggered.connect(lambda: self.show_dashboard())
#         file_menu.addAction(back_action)
#         file_menu.addSeparator()

#         load_conf_action = QAction('Load Pipeline Config', self)
#         load_conf_action.triggered.connect(lambda: self.load_config())
#         file_menu.addAction(load_conf_action)

#         save_conf_action = QAction('Save Pipeline Config', self)
#         save_conf_action.triggered.connect(lambda: self.save_config())
#         file_menu.addAction(save_conf_action)

#         view_menu = menubar.addMenu('View')
#         self.dock_menu = view_menu.addMenu('Panels')

#         theme_menu = view_menu.addMenu('Theme')
#         dark_action = QAction('Dark Mode', self)
#         dark_action.triggered.connect(lambda: self.apply_dark_theme())
#         theme_menu.addAction(dark_action)

#         white_action = QAction('White Mode', self)
#         white_action.triggered.connect(lambda: self.apply_white_theme())
#         theme_menu.addAction(white_action)

#         # --- Editor Central Widget ---
#         self.editor_central = QWidget()
#         editor_main_layout = QVBoxLayout(self.editor_central)

#         # Top Header (Context info)
#         context_layout = QHBoxLayout()
#         self.lbl_context = QLabel("Context Available: DFs (0) | Vars (0)")
#         self.lbl_context.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 11pt;")
#         context_layout.addWidget(self.lbl_context)

#         self.combo_view = QComboBox()
#         self.combo_view.setFixedWidth(280)
#         self.combo_view.setPlaceholderText("Select a DataFrame to View...")
#         self.combo_view.currentIndexChanged.connect(self.on_view_combo_changed)
#         context_layout.addWidget(self.combo_view)
#         editor_main_layout.addLayout(context_layout)

#         # Splitter to allow resizing without jumping
#         self.central_splitter = QSplitter(Qt.Vertical)
        
#         # Tabs (Data View)
#         self.tabs = QTabWidget()
#         self.tabs.setUsesScrollButtons(True) 
#         self.tabs.currentChanged.connect(self.on_tab_changed)
#         self.central_splitter.addWidget(self.tabs)

#         editor_main_layout.addWidget(self.central_splitter)

#         self.stacked_widget.addWidget(self.editor_central)

#         # --- Dock 1: Pipeline Controls (Left) ---
#         self.dock_pipeline = QDockWidget("Pipeline & Steps", self)
#         self.dock_pipeline.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

#         pipeline_widget = QWidget()
#         left_panel = QVBoxLayout(pipeline_widget)

#         # ** Process Management UI Update **
#         process_layout = QHBoxLayout()
#         self.combo_processes = QComboBox()
#         self.combo_processes.addItem("Main_Process")
#         self.combo_processes.currentTextChanged.connect(self.switch_process)
#         process_layout.addWidget(self.combo_processes)

#         btn_manage_proc = QPushButton("⚙️ Manage")
#         btn_manage_proc.clicked.connect(self.manage_processes)
#         process_layout.addWidget(btn_manage_proc)

#         left_panel.addLayout(process_layout)

#         btn_load = QPushButton("📥 Load Source Data")
#         btn_load.setObjectName("btnPrimary")
#         btn_load.clicked.connect(self.load_data)
#         left_panel.addWidget(btn_load)

#         btn_load_existing = QPushButton("📄 Load Another Sheet")
#         btn_load_existing.setObjectName("btnPrimary")
#         btn_load_existing.clicked.connect(self.load_existing_file_data)
#         left_panel.addWidget(btn_load_existing)

#         # ** Drag and Drop Step List Implementation **
#         self.list_steps = DraggableListWidget()
#         self.list_steps.itemClicked.connect(self.load_step_into_editor)
#         self.list_steps.item_moved.connect(self.on_step_moved) # Reorder Hook
#         left_panel.addWidget(self.list_steps)

#         btn_restore = QPushButton("▶️ Run Pipeline")
#         btn_restore.setObjectName("btnPurple")
#         btn_restore.clicked.connect(self.run_full_restore)
#         left_panel.addWidget(btn_restore)

#         btn_export_config = QPushButton("⚙️ Export Config")
#         btn_export_config.setObjectName("btnGray")
#         btn_export_config.clicked.connect(self.configure_export)
#         left_panel.addWidget(btn_export_config)

#         self.dock_pipeline.setWidget(pipeline_widget)
#         self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_pipeline)
#         self.dock_menu.addAction(self.dock_pipeline.toggleViewAction())

#         # --- Dock 2: Python Action Sandbox (Bottom/Right) ---
#         self.dock_sandbox = QDockWidget("Logic Editor & Sandbox", self)

#         sandbox_group = QGroupBox()
#         sandbox_layout = QVBoxLayout(sandbox_group)

#         self.combo_action = QComboBox()
#         self.combo_action.addItems([
#             "Execute Raw Python/Pandas", 
#             "Evaluate Excel Formula (Native Math)",
#             "Run External .py Script (Entire File)"
#         ])
#         self.combo_action.currentIndexChanged.connect(self.toggle_inputs)
#         sandbox_layout.addWidget(self.combo_action)

#         code_font = QFont("Consolas", 11)
#         self.txt_python = QTextEdit()
#         self.txt_python.setFont(code_font)
#         self.txt_python.setPlaceholderText("Write Python/Pandas logic here...")
#         self.txt_python.setMinimumSize(0, 0) # Allow shrinking
#         sandbox_layout.addWidget(self.txt_python)

#         # Excel Formula Inputs
#         self.widget_excel_formula = QWidget()
#         excel_layout = QVBoxLayout(self.widget_excel_formula)
#         excel_layout.setContentsMargins(0, 0, 0, 0)

#         self.txt_excel_formula = QTextEdit()
#         self.txt_excel_formula.setFont(code_font)
#         self.txt_excel_formula.setPlaceholderText("Enter Excel Formula (e.g., =SUM(Sheet1!A:A))")
#         self.txt_excel_formula.setMaximumHeight(150)
#         self.txt_excel_formula.setMinimumSize(0, 0)
#         excel_layout.addWidget(self.txt_excel_formula)

#         self.txt_excel_target = QLineEdit()
#         self.txt_excel_target.setPlaceholderText("Target DataFrame Alias (e.g., Master)")
#         excel_layout.addWidget(self.txt_excel_target)

#         self.txt_excel_column = QLineEdit()
#         self.txt_excel_column.setPlaceholderText("Target Column (Optional - e.g., Price)")
#         excel_layout.addWidget(self.txt_excel_column)

#         self.widget_excel_formula.hide()
#         sandbox_layout.addWidget(self.widget_excel_formula)

#         self.widget_script_path = QWidget()
#         script_path_layout = QHBoxLayout(self.widget_script_path)
#         script_path_layout.setContentsMargins(0, 0, 0, 0)
#         self.txt_script_path = QLineEdit()
#         self.btn_browse_script = QPushButton("📁")
#         self.btn_browse_script.clicked.connect(self.browse_script)
#         script_path_layout.addWidget(self.txt_script_path)
#         script_path_layout.addWidget(self.btn_browse_script)
#         self.widget_script_path.hide()
#         sandbox_layout.addWidget(self.widget_script_path)

#         btn_layout = QHBoxLayout()
#         btn_test = QPushButton("🧪 Test")
#         btn_test.clicked.connect(self.test_step)
#         btn_layout.addWidget(btn_test)

#         btn_record = QPushButton("✅ Record")
#         btn_record.setObjectName("btnSuccess")
#         btn_record.clicked.connect(self.record_step)
#         btn_layout.addWidget(btn_record)

#         btn_update = QPushButton("🔄 Update")
#         btn_update.setObjectName("btnWarning")
#         btn_update.clicked.connect(self.update_selected_step)
#         btn_layout.addWidget(btn_update)

#         btn_del_step = QPushButton("🗑️ Delete")
#         btn_del_step.setObjectName("btnDanger")
#         btn_del_step.clicked.connect(self.delete_step)
#         btn_layout.addWidget(btn_del_step)

#         sandbox_layout.addLayout(btn_layout)
#         self.dock_sandbox.setWidget(sandbox_group)
#         self.addDockWidget(Qt.RightDockWidgetArea, self.dock_sandbox)
#         self.dock_menu.addAction(self.dock_sandbox.toggleViewAction())

#         # --- Dock 3: Terminal (Bottom) ---
#         self.dock_terminal = QDockWidget("Interactive Terminal REPL", self)
#         term_widget = QWidget()
#         term_layout = QVBoxLayout(term_widget)

#         self.terminal_output = QTextEdit()
#         self.terminal_output.setFont(code_font)
#         self.terminal_output.setReadOnly(True)
#         self.terminal_output.setMinimumSize(0, 0) # Allow shrinking

#         self.terminal_input = TerminalInput()
#         self.terminal_input.setFont(code_font)
#         self.terminal_input.setPlaceholderText(">>> Type Python command and press Enter (Use Arrows for History)")
#         self.terminal_input.returnPressed.connect(self.execute_terminal_command)

#         term_layout.addWidget(self.terminal_output)
#         term_layout.addWidget(self.terminal_input)
#         self.dock_terminal.setWidget(term_widget)
#         self.dock_terminal.setMinimumSize(0, 0)
#         self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_terminal)
#         self.dock_menu.addAction(self.dock_terminal.toggleViewAction())

#         self.update_tabs()

#     def auto_generate_pipeline(self):
#         if analyze_workbook is None:
#             QMessageBox.critical(self, "Error", "xlwings is required for Auto-Generation. Please run 'pip install xlwings'.")
#             return

#         file_path, _ = QFileDialog.getOpenFileName(self, "Select Excel to Reverse-Engineer", "", "Excel Files (*.xlsx *.xlsm)")
#         if not file_path: return

#         # Show a "please wait" message because COM automation can be slow
#         self.analysis_msg = QMessageBox(self)
#         self.analysis_msg.setWindowTitle("Working...")
#         self.analysis_msg.setText("🔍 Analyzing workbook structure and formulas...\nPlease wait, this may take a moment.")
#         self.analysis_msg.setStandardButtons(QMessageBox.NoButton)
#         self.analysis_msg.show()

#         self.analysis_worker = ExcelAnalysisWorker(file_path)
#         self.analysis_worker.result_ready.connect(self.on_analysis_success)
#         self.analysis_worker.error_occurred.connect(self.on_analysis_error)
#         self.analysis_worker.start()

#     def on_analysis_success(self, config):
#         if hasattr(self, 'analysis_msg'):
#             self.analysis_msg.done(0)
#             self.analysis_msg.close()
        
#         QApplication.processEvents()
        
#         # Save the new config automatically
#         config_dir = "Config"
#         if not os.path.exists(config_dir): os.makedirs(config_dir)

#         save_path = os.path.join(config_dir, f"{config['pipeline_name']}.json")
#         with open(save_path, 'w') as f:
#             json.dump(config, f, indent=4)

#         QMessageBox.information(self, "Success", f"Pipeline successfully generated from Excel!\n\nSaved to: {save_path}\n\nAny unsupported features (like Pivot Tables) have been marked as TODO steps for you to fix.")
#         self.show_editor(save_path)

#     def on_analysis_error(self, err_msg):
#         if hasattr(self, 'analysis_msg'):
#             self.analysis_msg.done(0)
#             self.analysis_msg.close()
        
#         QApplication.processEvents()
#         QMessageBox.critical(self, "Reverse Engineering Error", f"Failed to analyze workbook:\n{err_msg}")

#     def on_view_combo_changed(self, idx):
#         if idx >= 0 and idx < self.tabs.count():
#             self.tabs.blockSignals(True)
#             self.tabs.setCurrentIndex(idx)
#             self.tabs.blockSignals(False)

#     def on_tab_changed(self, idx):
#         if idx >= 0 and idx < self.combo_view.count():
#             self.combo_view.blockSignals(True)
#             self.combo_view.setCurrentIndex(idx)
#             self.combo_view.blockSignals(False)

#     def configure_export(self):
#         pipeline_dfs = set()
#         for proc in self.processes.values():
#             for step in proc:
#                 if step["action"] == "load_file":
#                     pipeline_dfs.add(step["params"].get("alias"))
        
#         all_possible = sorted(list(set(self.global_dfs.keys()) | pipeline_dfs | set(self.export_dfs)))
        
#         dlg = ExportConfigDialog(all_possible, self.export_dfs, self)
#         if dlg.exec_() == QDialog.Accepted:
#             self.export_dfs = dlg.get_selected()
#             QMessageBox.information(self, "Saved", f"Export configuration updated.\n\n{len(self.export_dfs)} DataFrames will be written to Excel in headless mode.")

#     def browse_script(self):
#         file_path, _ = QFileDialog.getOpenFileName(self, "Select Python Script", "", "Python Files (*.py);;All Files (*)")
#         if file_path:
#             # Task 2: Copy to Custom_Scripts
#             custom_dir = "Custom_Scripts"
#             if not os.path.exists(custom_dir):
#                 os.makedirs(custom_dir)
            
#             dest_path = os.path.join(custom_dir, os.path.basename(file_path))
            
#             # Check if source and dest are different
#             if os.path.abspath(file_path) != os.path.abspath(dest_path):
#                 try:
#                     shutil.copy2(file_path, dest_path)
#                     if hasattr(self, 'terminal_output'):
#                         self.terminal_output.append(f"\n>>> Copied external script to local project: {dest_path}")
#                 except Exception as e:
#                     QMessageBox.warning(self, "Copy Error", f"Could not copy script to Custom_Scripts:\n{e}")
            
#             self.txt_script_path.setText(dest_path)

#     def execute_terminal_command(self):
#         cmd = self.terminal_input.text()
#         if not cmd.strip(): return
        
#         self.terminal_input.add_to_history(cmd)
#         self.terminal_output.append(f"\n>>> {cmd}")
#         self.terminal_input.clear()
        
#         env = {**self.preview_dfs, **self.preview_vars, 'pd': pd, 'np': np, 'os': os, 'prompt_file': prompt_file}
#         output = io.StringIO()
#         ui_needs_update = False
        
#         with contextlib.redirect_stdout(output):
#             try:
#                 res = eval(cmd, {}, env)
#                 if res is not None:
#                     print(res)
#             except SyntaxError:
#                 try:
#                     exec(cmd, env, env)
#                     ui_needs_update = True
#                 except Exception as e:
#                     print(f"Error: {e}")
#             except Exception as e:
#                 print(f"Error: {e}")
                
#         result_text = output.getvalue().strip()
#         if result_text:
#             self.terminal_output.append(result_text)
            
#         scrollbar = self.terminal_output.verticalScrollBar()
#         scrollbar.setValue(scrollbar.maximum())
        
#         if ui_needs_update:
#             self.preview_dfs = {k: v for k, v in env.items() if isinstance(v, pd.DataFrame)}
#             self.preview_vars = {k: v for k, v in env.items() if not isinstance(v, pd.DataFrame) and not callable(v) and not k.startswith('_') and str(type(v).__module__) == 'builtins'}
#             self.update_tabs()

#     # ** New Process Manager Hook **
#     def manage_processes(self):
#         dialog = ProcessManagerDialog(self.processes, self)
#         if dialog.exec_() == QDialog.Accepted:
#             mapping = dialog.get_process_mapping()
#             new_processes = {}
#             for new_name, old_name in mapping:
#                 if old_name is not None and old_name in self.processes:
#                     new_processes[new_name] = self.processes[old_name] # Keep existing steps
#                 else:
#                     new_processes[new_name] = [] # Brand new process created by user
                    
#             self.processes = new_processes
            
#             if self.current_process not in self.processes:
#                 self.current_process = list(self.processes.keys())[0] if self.processes else ""
                
#             self.combo_processes.blockSignals(True)
#             self.combo_processes.clear()
#             self.combo_processes.addItems(list(self.processes.keys()))
#             self.combo_processes.setCurrentText(self.current_process)
#             self.combo_processes.blockSignals(False)
            
#             self.refresh_step_list()

#     def switch_process(self, process_name):
#         if not process_name: return
#         self.current_process = process_name
#         self.refresh_step_list()

#     def refresh_step_list(self):
#         self.list_steps.clear()
#         if self.current_process in self.processes:
#             for step in self.processes[self.current_process]:
#                 prompt_flag = " [Prompt at Runtime]" if step.get('params', {}).get('prompt_at_runtime') else ""
#                 self.list_steps.addItem(f"[{step['step_id']}] {step['action']}{prompt_flag}")

#     def toggle_inputs(self):
#         action = self.combo_action.currentText()
#         self.txt_python.setVisible(action == "Execute Raw Python/Pandas")
#         self.widget_excel_formula.setVisible("Excel Formula" in action)
#         self.widget_script_path.setVisible("External" in action)

#     def load_data(self):
#         file_path, _ = QFileDialog.getOpenFileName(self, "Select Excel/CSV", "", "Data Files (*.xlsx *.csv)")
#         if not file_path: return

#         sheet_name = 0
#         if file_path.endswith('.xlsx'):
#             try:
#                 xl = pd.ExcelFile(file_path)
#                 sheet_name, ok = QInputDialog.getItem(self, "Select Sheet", "Select sheet:", xl.sheet_names, 0, False)
#                 if not ok: return
#             except Exception as e:
#                 QMessageBox.critical(self, "Error", str(e))
#                 return

#         alias, ok = QInputDialog.getText(self, "DataFrame Alias", "Variable name (e.g. df1):")
#         if not ok or not alias.strip(): return
#         alias = alias.strip()

#         reply = QMessageBox.question(self, 'Dynamic Input',
#                                      f"When this pipeline runs automatically in the future, should it STOP and prompt the user to select the file for '{alias}'?",
#                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
#         prompt_at_runtime = (reply == QMessageBox.Yes)

#         try:
#             df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path, sheet_name=sheet_name)
            
#             self.global_dfs[alias] = df
#             self.preview_dfs = self.global_dfs.copy()
#             self.update_tabs()
            
#             step = {
#                 "step_id": len(self.processes[self.current_process]) + 1,
#                 "action": "load_file",
#                 "params": {"filepath": file_path, "sheet": sheet_name, "alias": alias, "prompt_at_runtime": prompt_at_runtime}
#             }
#             self.processes[self.current_process].append(step)
#             self.refresh_step_list()
            
#         except Exception as e:
#             QMessageBox.critical(self, "Error", str(e))

#     def load_existing_file_data(self):
#         active_files = set()
#         for proc in self.processes.values():
#             for step in proc:
#                 if step.get("action") == "load_file":
#                     fp = step.get("params", {}).get("filepath")
#                     if fp and fp.endswith(('.xlsx', '.xlsm')):
#                         active_files.add(fp)
        
#         if not active_files:
#             QMessageBox.information(self, "No Active Files", "No Excel files are currently loaded.")
#             return
            
#         file_path, ok = QInputDialog.getItem(self, "Select Existing File", "Choose an Excel file:", list(active_files), 0, False)
#         if not ok: return
        
#         try:
#             xl = pd.ExcelFile(file_path)
#             sheet_name, ok = QInputDialog.getItem(self, "Select Sheet", f"Select sheet:", xl.sheet_names, 0, False)
#             if not ok: return
#         except Exception as e:
#             QMessageBox.critical(self, "Error", f"Could not read file: {e}")
#             return
            
#         alias, ok = QInputDialog.getText(self, "DataFrame Alias", "Variable name:")
#         if not ok or not alias.strip(): return
#         alias = alias.strip()

#         reply = QMessageBox.question(self, 'Dynamic Input',
#                                      f"Prompt user to select file for '{alias}'?",
#                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
#         prompt_at_runtime = (reply == QMessageBox.Yes)

#         try:
#             df = pd.read_excel(file_path, sheet_name=sheet_name)
#             self.global_dfs[alias] = df
#             self.preview_dfs = self.global_dfs.copy()
#             self.update_tabs()
            
#             step = {
#                 "step_id": len(self.processes[self.current_process]) + 1,
#                 "action": "load_file",
#                 "params": {"filepath": file_path, "sheet": sheet_name, "alias": alias, "prompt_at_runtime": prompt_at_runtime}
#             }
#             self.processes[self.current_process].append(step)
#             self.refresh_step_list()
#         except Exception as e:
#             QMessageBox.critical(self, "Error", str(e))

#     def copy_df_name(self, name, btn):
#         """Copies the DataFrame alias to clipboard and temporarily updates the button UI"""
#         QApplication.clipboard().setText(name)
#         original_text = btn.text()
#         btn.setText("✅ Copied!")
#         btn.setStyleSheet("background-color: #2da44e; color: white; border: none;") # Success green color
        
#         # Reset button state after 1.5 seconds
#         QTimer.singleShot(1500, lambda: self.reset_copy_btn(btn, original_text))

#     def reset_copy_btn(self, btn, text):
#         """Resets the copy button back to its standard state safely"""
#         try:
#             btn.setText(text)
#             btn.setStyleSheet("") # Revert to the application's standard stylesheet
#         except RuntimeError:
#             pass # Button might have been destroyed if the user navigated/refreshed tabs quickly

#     def copy_column_name(self, index, df_columns):
#         """Copies the clicked column name to the clipboard and shows a tooltip."""
#         if 0 <= index < len(df_columns):
#             col_name = str(df_columns[index])
#             QApplication.clipboard().setText(col_name)
            
#             # Show a floating tooltip right at the mouse cursor
#             QToolTip.showText(QCursor.pos(), f"✅ Copied Column: '{col_name}'")

#     def update_tabs(self):
#         self.tabs.clear()
#         self.combo_view.blockSignals(True)
#         self.combo_view.clear()
        
#         var_table = QTableWidget(len(self.preview_vars), 3)
#         var_table.setHorizontalHeaderLabels(["Variable Name", "Type", "Value"])
#         var_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
#         var_table.verticalHeader().setVisible(False)
        
#         row = 0
#         for k, v in self.preview_vars.items():
#             var_table.setItem(row, 0, QTableWidgetItem(str(k)))
#             var_table.setItem(row, 1, QTableWidgetItem(type(v).__name__))
#             var_table.setItem(row, 2, QTableWidgetItem(str(v)[:100]))
#             row += 1
            
#         self.tabs.addTab(var_table, "📦 Variables Explorer")
#         self.combo_view.addItem("📦 Variables Explorer")

#         for alias, df in self.preview_dfs.items():
#             # Create a container widget for the tab's specific layout
#             tab_widget = QWidget()
#             tab_layout = QVBoxLayout(tab_widget)
#             tab_layout.setContentsMargins(5, 5, 5, 5)

#             # --- Start Custom Feature: Tab Actions Header ---
#             top_bar = QHBoxLayout()
#             lbl_alias = QLabel(f"Viewing DataFrame: <b>{alias}</b>")
#             lbl_alias.setStyleSheet("font-size: 11pt;")
            
#             btn_copy = QPushButton("📋 Copy Name")
#             btn_copy.setFixedWidth(120)
#             btn_copy.setObjectName("btnPrimary")
#             # Connect using default argument in lambda to lock in this specific loop's 'alias' and 'btn_copy'
#             btn_copy.clicked.connect(lambda checked=False, n=alias, b=btn_copy: self.copy_df_name(n, b))
            
#             top_bar.addWidget(lbl_alias)
#             top_bar.addStretch()
#             top_bar.addWidget(btn_copy)
            
#             tab_layout.addLayout(top_bar)
#             # --- End Custom Feature ---

#             table = QTableView()
#             table.setModel(PandasModel(df))
#             table.verticalHeader().setVisible(False)
#             table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
#             table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
#             table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
#             table.horizontalHeader().setDefaultSectionSize(120)
            
#             # --- Start Custom Feature: Clickable Headers to Copy Column Name ---
#             table.horizontalHeader().setSectionsClickable(True)
#             table.horizontalHeader().setToolTip("Click a column header to quickly copy its name")
            
#             # Bind the logical index and the specific dataframe columns
#             table.horizontalHeader().sectionClicked.connect(
#                 lambda logicalIndex, cols=df.columns: self.copy_column_name(logicalIndex, cols)
#             )
#             # --- End Custom Feature ---

#             tab_layout.addWidget(table)
            
#             # Add the entire container instead of just the table
#             self.tabs.addTab(tab_widget, f"📊 DF: {alias}")
#             self.combo_view.addItem(f"📊 DF: {alias}")
            
#         self.combo_view.blockSignals(False)
#         self.lbl_context.setText(f"Context: DFs ({len(self.preview_dfs)}) | Vars ({len(self.preview_vars)})")

#     def get_editor_step_data(self):
#         action_type = self.combo_action.currentText()
#         step = {"action": ""}
#         if action_type == "Execute Raw Python/Pandas":
#             step["action"] = "execute_python_logic"
#             step["params"] = {"code_block": self.txt_python.toPlainText()}
#         elif action_type == "Evaluate Excel Formula (Native Math)":
#             step["action"] = "evaluate_excel_formula"
#             step["params"] = {
#                 "formula": self.txt_excel_formula.toPlainText(),
#                 "target_alias": self.txt_excel_target.text(),
#                 "target_col": self.txt_excel_column.text() if self.txt_excel_column.text().strip() else None
#             }
#         elif action_type == "Run External .py Script (Entire File)":
#             step["action"] = "run_python_file"
#             step["params"] = {"script_path": self.txt_script_path.text()}
#         return step

#     def test_step(self):
#         step = self.get_editor_step_data()
#         if not step["params"].get("code_block") and step["action"] == "execute_python_logic": return
        
#         self.pending_step = step
#         self.worker = StepPreviewWorker(self.global_dfs, self.global_vars, step)
#         self.worker.result_ready.connect(self.on_test_success)
#         self.worker.error_occurred.connect(self.on_test_error)
#         self.worker.start()

#     def on_test_success(self, new_dfs, new_vars):
#         self.preview_dfs = new_dfs
#         self.preview_vars = new_vars
#         self.update_tabs()
#         QMessageBox.information(self, "Test Passed", "Code executed!")

#     def on_test_error(self, err_msg):
#         QMessageBox.critical(self, "Logic Error", f"Failed to execute:\n\n{err_msg}")

#     # FIX: Allows you to instantly record what is in the editor without having to run "Test" first
#     def record_step(self):
#         step = self.get_editor_step_data()
        
#         # Validation
#         if step["action"] == "execute_python_logic" and not step["params"].get("code_block", "").strip():
#             QMessageBox.warning(self, "Warning", "Code block is empty!")
#             return
#         elif step["action"] == "run_python_file" and not step["params"].get("script_path", "").strip():
#             QMessageBox.warning(self, "Warning", "Script path is empty!")
#             return
            
#         step["step_id"] = len(self.processes[self.current_process]) + 1
#         self.processes[self.current_process].append(step)
        
#         # If tested recently, commit state
#         if self.pending_step:
#             self.global_dfs = self.preview_dfs.copy()
#             self.global_vars = self.preview_vars.copy()
#             self.pending_step = None
            
#         self.refresh_step_list()
#         QMessageBox.information(self, "Recorded", f"Step '{step['action']}' successfully recorded.")

#     def load_step_into_editor(self, item):
#         row_idx = self.list_steps.row(item)
#         step = self.processes[self.current_process][row_idx]
        
#         if step["action"] == "execute_python_logic":
#             self.combo_action.setCurrentText("Execute Raw Python/Pandas")
#             self.txt_python.setPlainText(step["params"].get("code_block", ""))
#         elif step["action"] == "evaluate_excel_formula":
#             self.combo_action.setCurrentText("Evaluate Excel Formula (Native Math)")
#             self.txt_excel_formula.setPlainText(step["params"].get("formula", ""))
#             self.txt_excel_target.setText(step["params"].get("target_alias", ""))
#             self.txt_excel_column.setText(step["params"].get("target_col", ""))
#         elif step["action"] == "run_python_file":
#             self.combo_action.setCurrentText("Run External .py Script (Entire File)")
#             self.txt_script_path.setText(step["params"].get("script_path", ""))

#     # ** Hook for Reordering Steps in List **
#     def on_step_moved(self, old_index, new_index):
#         if not (0 <= old_index < len(self.processes[self.current_process])) or not (0 <= new_index < len(self.processes[self.current_process])):
#             return
            
#         step_list = self.processes[self.current_process]
        
#         # Pop the step out and put it in its new location
#         step = step_list.pop(old_index)
#         step_list.insert(new_index, step)
        
#         # Sequentially re-assign step_ids so they remain perfect [1, 2, 3...]
#         for i, s in enumerate(step_list):
#             s["step_id"] = i + 1
            
#         self.refresh_step_list()
#         self.list_steps.setCurrentRow(new_index) # Keep the moved item selected

#     # FIX: Allows you to grab the live editor content and seamlessly overwrite the selected list item
#     def update_selected_step(self):
#         current_item = self.list_steps.currentItem()
#         if not current_item:
#             QMessageBox.warning(self, "Warning", "Please select a step from the list to update.")
#             return
            
#         row_idx = self.list_steps.row(current_item)
#         original_step = self.processes[self.current_process][row_idx]
        
#         if original_step["action"] == "load_file":
#             active_files = set()
#             for proc in self.processes.values():
#                 for s in proc:
#                     if s.get("action") == "load_file":
#                         fp = s.get("params", {}).get("filepath")
#                         if fp: active_files.add(fp)
#             dialog = EditLoadDialog(original_step.get("params", {}), list(active_files), self)
#             if dialog.exec_() == QDialog.Accepted:
#                 original_step["params"] = dialog.get_params()
#                 self.processes[self.current_process][row_idx] = original_step
#                 self.refresh_step_list()
#             return
            
#         new_step_data = self.get_editor_step_data()
        
#         # Validation
#         if new_step_data["action"] == "execute_python_logic" and not new_step_data["params"].get("code_block", "").strip():
#             QMessageBox.warning(self, "Warning", "Code block is empty!")
#             return
            
#         new_step_data["step_id"] = original_step["step_id"]
#         self.processes[self.current_process][row_idx] = new_step_data
#         self.refresh_step_list()
        
#         QMessageBox.information(self, "Success", "Step updated successfully. (Note: Run the pipeline to refresh the visual state)")

#     def delete_step(self):
#         current_item = self.list_steps.currentItem()
#         if not current_item: return
#         row_idx = self.list_steps.row(current_item)
#         if QMessageBox.question(self, 'Delete', "Delete this step?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
#             del self.processes[self.current_process][row_idx]
#             for i, step in enumerate(self.processes[self.current_process]):
#                 step["step_id"] = i + 1
#             self.refresh_step_list()

#     def run_full_restore(self, export_path=None):
#         if not any(self.processes.values()): return
#         self.last_export_path = export_path
#         self.terminal_output.append("\n>>> Restoring Pipeline Data...")
#         self.restore_worker = PipelineRestoreWorker(self.processes)
#         self.restore_worker.progress_update.connect(self.terminal_output.append)
#         self.restore_worker.result_ready.connect(self.on_restore_success)
#         self.restore_worker.error_occurred.connect(self.on_restore_error)
#         self.restore_worker.start()

#     def on_restore_success(self, dfs, vars):
#         self.global_dfs, self.global_vars = dfs.copy(), vars.copy()
#         self.preview_dfs, self.preview_vars = dfs.copy(), vars.copy()
#         self.update_tabs()
#         self.terminal_output.append(">>> Success!")
        
#         if hasattr(self, 'last_export_path') and self.last_export_path:
#             self.terminal_output.append(f">>> Exporting results to: {self.last_export_path}")
#             try:
#                 output_file = os.path.join(self.last_export_path, 'Final_Pipeline_Output.xlsx')
#                 with pd.ExcelWriter(output_file) as writer:
#                     exported_count = 0
#                     for alias, df in dfs.items():
#                         if not self.export_dfs or alias in self.export_dfs:
#                             df.to_excel(writer, sheet_name=str(alias)[:31], index=False)
#                             exported_count += 1
#                 self.terminal_output.append(f">>> Export Complete: {exported_count} DataFrames saved.")
#             except Exception as e:
#                 self.terminal_output.append(f">>> Export Error: {e}")
#             self.last_export_path = None

#     def on_restore_error(self, err):
#         self.terminal_output.append(f">>> Error: {err}")

#     def load_config_from_path(self, file_path):
#         try:
#             with open(file_path, 'r') as f:
#                 config = json.load(f)
#             self.processes = config["processes"]
#             self.export_dfs = config.get("export_dfs", [])
#             self.current_config_path = file_path
            
#             self.combo_processes.blockSignals(True)
#             self.combo_processes.clear()
#             for n in self.processes.keys():
#                 self.combo_processes.addItem(n)
#             self.current_process = list(self.processes.keys())[0]
#             self.combo_processes.setCurrentText(self.current_process)
#             self.combo_processes.blockSignals(False)
            
#             self.refresh_step_list()
#             self.update_tabs()
#         except Exception as e:
#             QMessageBox.critical(self, "Error", f"Could not load config:\n{e}")

#     def load_config(self):
#         file_path, _ = QFileDialog.getOpenFileName(self, "Load Config", "Config", "JSON Files (*.json)")
#         if file_path:
#             self.load_config_from_path(file_path)
#             if QMessageBox.question(self, 'Restore', "Run pipeline now?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
#                 self.run_full_restore()

#     def save_config(self):
#         default_name = self.current_config_path or "Config/Master_Config.json"
#         file_path, _ = QFileDialog.getSaveFileName(self, "Save Pipeline", default_name, "JSON Files (*.json)")
#         if file_path:
#             config = {
#                 "pipeline_name": os.path.splitext(os.path.basename(file_path))[0], 
#                 "export_dfs": self.export_dfs, 
#                 "processes": self.processes
#             }
#             with open(file_path, 'w') as f:
#                 json.dump(config, f, indent=4)
#             self.current_config_path = file_path
#             self.setWindowTitle(f"Pipeline Editor - {os.path.basename(file_path)}")
#             QMessageBox.information(self, "Saved", f"Saved to {file_path}.")

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = ScorecardUI()
#     window.show()
#     sys.exit(app.exec_())





# # # # # ==============================================================================
# # # # # FILE LOCATION: Dynamic_Scorecard_System/scorecard_ui.py
# # # # # ==============================================================================

import sys
import json
import traceback
import os
import threading
from concurrent.futures import ThreadPoolExecutor
import io
import contextlib
import shutil
import pandas as pd
import numpy as np

# Force the working directory to be where the EXE is located (or script if running raw)
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

os.chdir(application_path)

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QTableView, QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem,
                             QComboBox, QTextEdit, QLineEdit, QMessageBox, QGroupBox, 
                             QInputDialog, QTabWidget, QHeaderView, QSplitter, QAction,
                             QDialog, QFormLayout, QCheckBox, QDialogButtonBox, QAbstractItemView,
                             QDockWidget, QStackedWidget, QScrollArea, QFrame, QGridLayout,
                             QToolTip, QSizePolicy, QMenu, QStatusBar)
from PyQt5.QtCore import (QAbstractTableModel, Qt, QThread, pyqtSignal, QEvent, QTimer, 
                          QSortFilterProxyModel, QRect, QPoint)
from PyQt5.QtGui import QFont, QCursor, QKeySequence, QColor, QPainter, QPen

# Make sure these are accessible in your environment
try:
    from dynamic_engine import DynamicPipelineEngine, prompt_file
except ImportError:
    class DynamicPipelineEngine: pass
    prompt_file = None

try:
    from excel_analyzer import analyze_workbook
except ImportError:
    analyze_workbook = None

# ==============================================================================
# ENHANCED FEATURE: Excel-Style Autofilter Popup, Header, and Table
# ==============================================================================
class FilterPopup(QWidget):
    """The Excel-style popup menu with sorting, searching, and checkboxes."""
    def __init__(self, parent, col, unique_vals, active_vals, proxy_model, header_view):
        super().__init__(parent, Qt.Popup) # Acts like a dropdown menu
        self.col = col
        self.unique_vals = unique_vals
        self.active_vals = active_vals
        self.proxy_model = proxy_model
        self.header_view = header_view
        
        self.setFixedWidth(260)
        self.setObjectName("FilterPopup")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Sort Buttons
        btn_sort_asc = QPushButton("↓ Sort A to Z")
        btn_sort_asc.clicked.connect(self.sort_asc)
        layout.addWidget(btn_sort_asc)
        
        btn_sort_desc = QPushButton("↑ Sort Z to A")
        btn_sort_desc.clicked.connect(self.sort_desc)
        layout.addWidget(btn_sort_desc)
        
        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("background-color: gray;")
        layout.addWidget(div)
        
        # Search Box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search...")
        self.search_box.textChanged.connect(self.filter_list)
        layout.addWidget(self.search_box)
        
        # List Widget for Checkboxes
        self.list_widget = QListWidget()
        self.list_widget.setMaximumHeight(200)
        layout.addWidget(self.list_widget)
        
        # Populate List
        self.item_select_all = QListWidgetItem("(Select All)")
        self.item_select_all.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        self.list_widget.addItem(self.item_select_all)
        
        self.items = []
        all_checked_default = (active_vals is None)
        
        for val in unique_vals:
            item = QListWidgetItem(val)
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            is_checked = all_checked_default or (val in active_vals)
            item.setCheckState(Qt.Checked if is_checked else Qt.Unchecked)
            self.list_widget.addItem(item)
            self.items.append(item)
            
        # Determine Select All state
        if all_checked_default or all(i.checkState() == Qt.Checked for i in self.items):
            self.item_select_all.setCheckState(Qt.Checked)
        else:
            self.item_select_all.setCheckState(Qt.Unchecked)
            
        self.list_widget.itemChanged.connect(self.on_item_changed)
        
        # Ok / Cancel
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_ok.setObjectName("btnPrimary")
        btn_ok.clicked.connect(self.apply_filter)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.close)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        self.updating = False

    def sort_asc(self):
        self.proxy_model.sort(self.col, Qt.AscendingOrder)
        self.close()

    def sort_desc(self):
        self.proxy_model.sort(self.col, Qt.DescendingOrder)
        self.close()

    def filter_list(self, text):
        text = text.lower()
        for item in self.items:
            item.setHidden(text not in item.text().lower())

    def on_item_changed(self, item):
        if self.updating: return
        self.updating = True
        if item == self.item_select_all:
            state = item.checkState()
            for i in self.items:
                if not i.isHidden():
                    i.setCheckState(state)
        else:
            if item.checkState() == Qt.Unchecked:
                self.item_select_all.setCheckState(Qt.Unchecked)
            else:
                if all(i.checkState() == Qt.Checked for i in self.items if not i.isHidden()):
                    self.item_select_all.setCheckState(Qt.Checked)
        self.updating = False

    def apply_filter(self):
        selected = set()
        for item in self.items:
            if item.checkState() == Qt.Checked:
                selected.add(item.text())
        
        # If all are checked, remove the filter
        if len(selected) == len(self.unique_vals):
            self.proxy_model.setFilterValues(self.col, None)
            self.header_view.filtered_cols.discard(self.col)
        else:
            self.proxy_model.setFilterValues(self.col, selected)
            self.header_view.filtered_cols.add(self.col)
            
        self.header_view.viewport().update()
        self.close()


class FilterHeaderView(QHeaderView):
    """Custom Header that draws Excel dropdown arrows and catches clicks on them."""
    filter_button_clicked = pyqtSignal(int, int, int) # col, global_x, global_y
    
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.filters_enabled = True 
        self.filtered_cols = set()
        self.setSectionsClickable(True)
        self.setToolTip("Click column name to copy.\nClick ▼ to filter.")

    def paintSection(self, painter, rect, logicalIndex):
        # 1. Paint the default header background and text
        super().paintSection(painter, rect, logicalIndex)
        
        # 3. Overlay our custom arrow if filters are enabled
        if self.filters_enabled:
            painter.save()
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Use a slightly larger button area
            btn_size = 18
            margin = 4
            # rect.x() and rect.y() are the absolute start points of this header section
            x = rect.x() + rect.width() - btn_size - margin
            y = rect.y() + (rect.height() - btn_size) // 2
            
            icon_rect = QRect(x, y, btn_size, btn_size)
            is_active = logicalIndex in self.filtered_cols
            
            # Professional Drawing
            painter.setPen(Qt.NoPen)
            if is_active:
                painter.setBrush(QColor("#007acc")) # Blue if filtered
            else:
                # Use a subtle background for the arrow area
                box_bg = self.palette().windowText().color()
                box_bg.setAlpha(30) 
                painter.setBrush(box_bg)
            painter.drawRoundedRect(icon_rect, 4, 4)
            
            # Draw a manual polygon arrow
            arrow_color = Qt.white if is_active else self.palette().windowText().color()
            painter.setPen(QPen(arrow_color, 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.setBrush(arrow_color)

            center_x = icon_rect.center().x()
            center_y = icon_rect.center().y()

            triangle = [
                QPoint(center_x - 4, center_y - 2),
                QPoint(center_x + 4, center_y - 2),
                QPoint(center_x, center_y + 3)
            ]
            painter.drawPolygon(*triangle)

            painter.restore()
    def mousePressEvent(self, event):
        if self.filters_enabled:
            idx = self.logicalIndexAt(event.pos())
            if idx >= 0:
                section_x = self.sectionViewportPosition(idx)
                width = self.sectionSize(idx)
                
                # If they clicked the rightmost 26 pixels, trigger the filter menu
                if event.pos().x() > section_x + width - 26:
                    global_pos = QCursor.pos() # Safe cursor mapping
                    self.filter_button_clicked.emit(idx, global_pos.x(), global_pos.y())
                    event.accept()
                    return 
                    
        super().mousePressEvent(event)


class MultiFilterProxyModel(QSortFilterProxyModel):
    """Filters data based on exact matched sets, allowing Excel-style Checkbox logic."""
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.value_filters = {} # {col_index: set_of_allowed_strings}

    def setFilterValues(self, column, accepted_values):
        if accepted_values is None:
            self.value_filters.pop(column, None)
        else:
            self.value_filters[column] = set(accepted_values)
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if not self.value_filters:
            return True
        for col, accepted_values in self.value_filters.items():
            idx = self.sourceModel().index(source_row, col, source_parent)
            data = self.sourceModel().data(idx, Qt.DisplayRole)
            if str(data) not in accepted_values:
                return False
        return True

    def lessThan(self, left, right):
        """Allows Excel-style sorting of both numeric and string values properly."""
        left_data = self.sourceModel().data(left, Qt.DisplayRole)
        right_data = self.sourceModel().data(right, Qt.DisplayRole)
        
        try:
            return float(left_data) < float(right_data)
        except (ValueError, TypeError):
            return str(left_data) < str(right_data)


class DataFrameTableView(QTableView):
    """Enhanced Table with Excel Keybinds (Ctrl+Shift+L, Alt+Down)."""
    filter_toggled = pyqtSignal()

    def keyPressEvent(self, event):
        # 1. Advanced Copying
        if event.matches(QKeySequence.Copy):
            self.copy_selection()
            
        # 2. Toggle Autofilter (Ctrl + Shift + L)
        elif event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier) and event.key() == Qt.Key_L:
            self.filter_toggled.emit()
            event.accept()
            
        # 3. Open Autofilter Dropdown (Alt + Down Arrow)
        elif event.modifiers() == Qt.AltModifier and event.key() == Qt.Key_Down:
            idx = self.selectionModel().currentIndex()
            header = self.horizontalHeader()
            if idx.isValid() and isinstance(header, FilterHeaderView) and header.filters_enabled:
                col = idx.column()
                global_pos = QCursor.pos()
                header.filter_button_clicked.emit(col, global_pos.x(), global_pos.y())
                event.accept()
        else:
            super().keyPressEvent(event)

    def copy_selection(self):
        indexes = self.selectionModel().selectedIndexes()
        if not indexes: return

        rows = sorted(list(set([idx.row() for idx in indexes])))
        cols = sorted(list(set([idx.column() for idx in indexes])))

        total_rows = self.model().rowCount()
        is_full_column_selected = (len(rows) == total_rows)

        grid = []
        if is_full_column_selected:
            header_data = [str(self.model().headerData(c, Qt.Horizontal, Qt.DisplayRole)) for c in cols]
            grid.append("\t".join(header_data))
            
        for r in rows:
            row_data = []
            for c in cols:
                idx = self.model().index(r, c)
                row_data.append(str(self.model().data(idx, Qt.DisplayRole)) if idx in indexes else "")
            grid.append("\t".join(row_data))
        
        QApplication.clipboard().setText("\n".join(grid))
        msg = "✅ Copied selection + headers" if is_full_column_selected else "✅ Copied selected cells"
        QToolTip.showText(QCursor.pos(), msg)


# ==============================================================================
# EXISTING COMPONENTS (Models, Dialogs, Threads)
# ==============================================================================
class DraggableListWidget(QListWidget):
    item_moved = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.InternalMove)

    def dropEvent(self, event):
        if event.source() == self:
            old_index = self.currentRow()
            super().dropEvent(event)
            new_index = self.currentRow()
            if old_index != new_index and old_index >= 0 and new_index >= 0:
                self.item_moved.emit(old_index, new_index)
        else:
            super().dropEvent(event)

class ProcessManagerDialog(QDialog):
    def __init__(self, processes_dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage & Reorder Processes")
        self.setMinimumWidth(450)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout(self)
        lbl = QLabel("Drag and drop to reorder. Processes execute from top to bottom.")
        lbl.setStyleSheet("color: #007acc; font-weight: bold; margin-bottom: 5px;")
        lbl.setWordWrap(True)
        layout.addWidget(lbl)
        
        self.process_map = {k: k for k in processes_dict.keys()}
        
        self.list_widget = QListWidget()
        self.list_widget.setDragDropMode(QAbstractItemView.InternalMove)
        for proc in processes_dict.keys():
            self.list_widget.addItem(proc)
        layout.addWidget(self.list_widget)
        
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("➕ Insert New")
        btn_add.clicked.connect(self.add_process)
        btn_rename = QPushButton("✏️ Rename")
        btn_rename.clicked.connect(self.rename_process)
        btn_del = QPushButton("🗑️ Delete")
        btn_del.setObjectName("btnDanger")
        btn_del.clicked.connect(self.delete_process)
        
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_rename)
        btn_layout.addWidget(btn_del)
        layout.addLayout(btn_layout)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def add_process(self):
        name, ok = QInputDialog.getText(self, "New Process", "Enter new process name:")
        if ok and name.strip():
            name = name.strip()
            if name in [self.list_widget.item(i).text() for i in range(self.list_widget.count())]:
                QMessageBox.warning(self, "Error", "Process name already exists.")
                return
            self.process_map[name] = None
            curr_row = self.list_widget.currentRow()
            if curr_row >= 0:
                self.list_widget.insertItem(curr_row + 1, name)
                self.list_widget.setCurrentRow(curr_row + 1)
            else:
                self.list_widget.addItem(name)
                self.list_widget.setCurrentRow(self.list_widget.count() - 1)
                
    def rename_process(self):
        item = self.list_widget.currentItem()
        if not item: return
        old_name = item.text()
        new_name, ok = QInputDialog.getText(self, "Rename", "New process name:", QLineEdit.Normal, old_name)
        if ok and new_name.strip() and new_name.strip() != old_name:
            new_name = new_name.strip()
            if new_name in [self.list_widget.item(i).text() for i in range(self.list_widget.count())]:
                QMessageBox.warning(self, "Error", "Process name already exists.")
                return
            original_mapped_name = self.process_map.pop(old_name)
            self.process_map[new_name] = original_mapped_name
            item.setText(new_name)

    def delete_process(self):
        item = self.list_widget.currentItem()
        if not item: return
        if self.list_widget.count() <= 1:
            QMessageBox.warning(self, "Error", "You must have at least one active process.")
            return
        if QMessageBox.question(self, "Delete", f"Delete process '{item.text()}' and all its steps?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.process_map.pop(item.text(), None)
            self.list_widget.takeItem(self.list_widget.row(item))
            
    def get_process_mapping(self):
        result = []
        for i in range(self.list_widget.count()):
            name = self.list_widget.item(i).text()
            result.append((name, self.process_map.get(name)))
        return result

class TerminalInput(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.history = []
        self.history_index = -1
        self.temp_cmd = ""

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            if not self.history: return
            if self.history_index == -1: self.temp_cmd = self.text()
            if self.history_index < len(self.history) - 1:
                self.history_index += 1
                self.setText(self.history[self.history_index])
        elif event.key() == Qt.Key_Down:
            if self.history_index > -1:
                self.history_index -= 1
                if self.history_index == -1:
                    self.setText(self.temp_cmd)
                else:
                    self.setText(self.history[self.history_index])
        else:
            super().keyPressEvent(event)
            if event.key() != Qt.Key_Return and event.key() != Qt.Key_Enter:
                self.history_index = -1

    def add_to_history(self, cmd):
        if cmd.strip():
            if cmd in self.history: self.history.remove(cmd)
            self.history.insert(0, cmd)
        self.history_index = -1
        self.temp_cmd = ""

class PandasModel(QAbstractTableModel):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self._data = data
        self.is_editable = False # Track lock status

    def rowCount(self, parent=None): return self._data.shape[0]
    def columnCount(self, parent=None): return self._data.shape[1]
    
    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole or role == Qt.EditRole:
                val = self._data.iloc[index.row(), index.column()]
                return str(val) if not pd.isna(val) else ""
        return None
        
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return str(self._data.columns[col])
        return None

    def flags(self, index):
        flags = super().flags(index)
        if self.is_editable:
            flags |= Qt.ItemIsEditable
        return flags

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole and self.is_editable:
            row = index.row()
            col = index.column()
            old_val = str(self._data.iat[row, col])
            
            if value != old_val:
                col_name = self._data.columns[col]
                reply = QMessageBox.question(
                    None, 'Confirm Edit',
                    f"Modify DataFrame data at Row {row}, Column '{col_name}'?\n\nOriginal: '{old_val}'\nNew: '{value}'\n\nNote: This modifies the active DataFrame in memory.",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    try:
                        dtype = self._data.dtypes.iloc[col]
                        if pd.api.types.is_numeric_dtype(dtype):
                            value = pd.to_numeric(value)
                            
                        self._data.iat[row, col] = value
                        self.dataChanged.emit(index, index, [Qt.DisplayRole])
                        return True
                    except Exception as e:
                        QMessageBox.warning(None, "Edit Failed", f"Could not set value:\n{e}")
        return False

class StepPreviewWorker(QThread):
    result_ready = pyqtSignal(dict, dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, dfs_dict, vars_dict, step):
        super().__init__()
        self.dfs_dict = {k: v.copy() for k, v in dfs_dict.items()}
        self.vars_dict = {k: v for k, v in vars_dict.items()}
        self.step = step
        self.engine = DynamicPipelineEngine()

    def run(self):
        try:
            new_dfs, new_vars = self.engine._apply_step(self.dfs_dict, self.vars_dict, self.step)
            self.result_ready.emit(new_dfs, new_vars)
        except Exception as e:
            self.error_occurred.emit(traceback.format_exc())

class PipelineRestoreWorker(QThread):
    progress_update = pyqtSignal(str)
    result_ready = pyqtSignal(dict, dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, processes):
        super().__init__()
        self.processes = processes
        self.engine = DynamicPipelineEngine()
        self.state_lock = threading.Lock()

    def run(self):
        dfs_dict = {}
        vars_dict = {}
        try:
            # PERFORMANCE BOOST: Parallelize independent processes
            # Processes are assumed independent unless they explicitly depend on 
            # DataFrames produced by others. 
            self.progress_update.emit(f">>> Initializing Multi-Threaded Execution Engine...")
            
            def execute_process(proc_name, steps):
                local_dfs = {}
                local_vars = {}
                self.progress_update.emit(f" -> Thread Start: {proc_name}")
                
                for step in steps:
                    # Sync common state before step if needed, 
                    # but for performance we keep them isolated during the proc
                    # and merge at the end.
                    local_dfs, local_vars = self.engine._apply_step(local_dfs, local_vars, step)
                
                with self.state_lock:
                    dfs_dict.update(local_dfs)
                    vars_dict.update(local_vars)
                
                self.progress_update.emit(f" -> Thread Finish: {proc_name}")

            # Use ThreadPoolExecutor to run all processes in parallel
            with ThreadPoolExecutor(max_workers=min(len(self.processes), 8)) as executor:
                futures = []
                for proc_name, steps in self.processes.items():
                    futures.append(executor.submit(execute_process, proc_name, steps))
                
                # Wait for all to complete
                for future in futures:
                    future.result() # Catch errors if any

            self.result_ready.emit(dfs_dict, vars_dict)
        except Exception as e:
            self.error_occurred.emit(traceback.format_exc())

class ExcelAnalysisWorker(QThread):
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            config = analyze_workbook(self.file_path)
            self.result_ready.emit(config)
        except Exception as e:
            self.error_occurred.emit(str(e))

class ExportConfigDialog(QDialog):
    def __init__(self, all_dfs, selected_dfs, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Headless Export")
        self.resize(450, 500) 
        
        layout = QVBoxLayout(self)
        
        if not all_dfs:
            layout.addWidget(QLabel("No DataFrames currently available.\nRun the pipeline or load data first."))
        else:
            header_lbl = QLabel("Select which DataFrames to export to Excel\nduring automated Headless execution:")
            header_lbl.setStyleSheet("margin-bottom: 5px;")
            layout.addWidget(header_lbl)
            
            btn_layout = QHBoxLayout()
            btn_select_all = QPushButton("☑ Select All")
            btn_select_all.clicked.connect(self.select_all)
            btn_deselect_all = QPushButton("☐ Deselect All")
            btn_deselect_all.clicked.connect(self.deselect_all)
            
            btn_layout.addWidget(btn_select_all)
            btn_layout.addWidget(btn_deselect_all)
            layout.addLayout(btn_layout)
            
            self.list_widget = QListWidget()
            self.list_widget.setSelectionMode(QAbstractItemView.NoSelection) 
            
            for df_name in all_dfs:
                item = QListWidgetItem(df_name)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                if df_name in selected_dfs or (not selected_dfs and df_name in all_dfs):
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)
                self.list_widget.addItem(item)
                
            layout.addWidget(self.list_widget)
            
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def select_all(self):
        if hasattr(self, 'list_widget'):
            for i in range(self.list_widget.count()): self.list_widget.item(i).setCheckState(Qt.Checked)
            
    def deselect_all(self):
        if hasattr(self, 'list_widget'):
            for i in range(self.list_widget.count()): self.list_widget.item(i).setCheckState(Qt.Unchecked)

    def get_selected(self):
        if not hasattr(self, 'list_widget'): return []
        selected = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.Checked: selected.append(item.text())
        return selected

class EditLoadDialog(QDialog):
    def __init__(self, step_params, active_files=None, parent=None):
        super().__init__(parent)
        self.active_files = active_files or []
        self.setWindowTitle("Edit Load File Step")
        self.setMinimumWidth(550)
        
        layout = QFormLayout(self)
        
        self.filepath_input = QLineEdit(step_params.get("filepath", ""))
        
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        
        browse_btn = QPushButton("📁 Browse New")
        browse_btn.clicked.connect(self.browse)
        btn_layout.addWidget(browse_btn)
        
        if self.active_files:
            active_btn = QPushButton("📄 Select Active File")
            active_btn.clicked.connect(self.select_active)
            btn_layout.addWidget(active_btn)
            
        fp_layout = QVBoxLayout()
        fp_layout.setContentsMargins(0, 0, 0, 0)
        fp_layout.addWidget(self.filepath_input)
        fp_layout.addLayout(btn_layout)
        
        layout.addRow("File Path:", fp_layout)
        
        self.sheet_input = QLineEdit(str(step_params.get("sheet", 0)))
        self.sheet_input.setPlaceholderText("0 for first sheet, or 'Sheet1'")
        
        sheet_layout = QHBoxLayout()
        sheet_layout.setContentsMargins(0, 0, 0, 0)
        sheet_layout.addWidget(self.sheet_input)
        
        inspect_btn = QPushButton("🔍 Select Sheet")
        inspect_btn.clicked.connect(self.list_sheets)
        sheet_layout.addWidget(inspect_btn)
        
        layout.addRow("Sheet Name/Index:", sheet_layout)
        
        self.alias_input = QLineEdit(step_params.get("alias", ""))
        layout.addRow("DataFrame Alias:", self.alias_input)
        
        self.header_input = QLineEdit(str(step_params.get("header", 0)))
        self.header_input.setPlaceholderText("0 for first row (default)")
        layout.addRow("Header Row (Index):", self.header_input)
        
        self.prompt_cb = QCheckBox("Prompt user to select this file at runtime (Filepath becomes a placeholder)")
        self.prompt_cb.setChecked(step_params.get("prompt_at_runtime", False))
        layout.addRow("", self.prompt_cb)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)

    def browse(self):
        fp, _ = QFileDialog.getOpenFileName(self, "Select Excel/CSV", "", "Data Files (*.xlsx *.csv)")
        if fp: self.filepath_input.setText(fp)
            
    def select_active(self):
        if not self.active_files: return
        fp, ok = QInputDialog.getItem(self, "Select Active File", "Choose an existing file from the pipeline:", self.active_files, 0, False)
        if ok and fp: self.filepath_input.setText(fp)

    def list_sheets(self):
        fp = self.filepath_input.text().strip()
        if not fp or not os.path.exists(fp):
            QMessageBox.warning(self, "File Not Found", "Cannot read sheets. Please ensure the file path is correct and accessible.")
            return
        if not fp.endswith(('.xlsx', '.xlsm')):
            QMessageBox.information(self, "Not an Excel File", "Only Excel files have multiple sheets to select from.")
            return
            
        try:
            xl = pd.ExcelFile(fp)
            sheet, ok = QInputDialog.getItem(self, "Select Sheet", f"Available Sheets in {os.path.basename(fp)}:", xl.sheet_names, 0, False)
            if ok and sheet: self.sheet_input.setText(sheet)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not read sheets:\n{e}")

    def get_params(self):
        sheet_val = self.sheet_input.text()
        if sheet_val.isdigit(): sheet_val = int(sheet_val)
            
        header_val = 0
        if self.header_input.text().isdigit(): header_val = int(self.header_input.text())
            
        fp = self.filepath_input.text().strip()
        if not fp and self.prompt_cb.isChecked(): fp = "RUNTIME_PROMPT_ONLY.xlsx"
            
        return {
            "filepath": fp,
            "sheet": sheet_val,
            "header": header_val,
            "alias": self.alias_input.text(),
            "prompt_at_runtime": self.prompt_cb.isChecked()
        }

class MapColumnsDialog(QDialog):
    def __init__(self, dfs_dict, parent=None):
        super().__init__(parent)
        self.dfs_dict = dfs_dict
        self.setWindowTitle("Map Columns Between DataFrames")
        self.setMinimumWidth(600)
        
        layout = QFormLayout(self)
        
        self.target_combo = QComboBox()
        self.target_combo.addItems(sorted(dfs_dict.keys()))
        self.target_combo.currentTextChanged.connect(self.update_target_keys)
        layout.addRow("Target DataFrame (To Update):", self.target_combo)
        
        self.target_key_combo = QComboBox()
        layout.addRow("Target Match Column:", self.target_key_combo)
        
        self.source_combo = QComboBox()
        self.source_combo.addItems(sorted(dfs_dict.keys()))
        self.source_combo.currentTextChanged.connect(self.update_source_keys_and_cols)
        layout.addRow("Source DataFrame (To Copy From):", self.source_combo)
        
        self.source_key_combo = QComboBox()
        layout.addRow("Source Match Column:", self.source_key_combo)
        
        self.cols_list = QListWidget()
        self.cols_list.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addRow("Columns to Copy:", self.cols_list)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)
        
        self.update_target_keys()
        self.update_source_keys_and_cols()

    def update_target_keys(self):
        self.target_key_combo.clear()
        alias = self.target_combo.currentText()
        if alias in self.dfs_dict:
            self.target_key_combo.addItems(list(self.dfs_dict[alias].columns))

    def update_source_keys_and_cols(self):
        self.source_key_combo.clear()
        self.cols_list.clear()
        alias = self.source_combo.currentText()
        if alias in self.dfs_dict:
            cols = list(self.dfs_dict[alias].columns)
            self.source_key_combo.addItems(cols)
            self.cols_list.addItems(cols)

    def get_data(self):
        selected_items = self.cols_list.selectedItems()
        selected_cols = [item.text() for item in selected_items]
        return {
            "target_df": self.target_combo.currentText(),
            "target_key": self.target_key_combo.currentText(),
            "source_df": self.source_combo.currentText(),
            "source_key": self.source_key_combo.currentText(),
            "columns_to_map": selected_cols,
            "how": "left"
        }

class ConfigCard(QGroupBox):
    edit_requested = pyqtSignal(str)
    run_requested = pyqtSignal(str)
    delete_requested = pyqtSignal(str)

    def __init__(self, file_path, config_data):
        title = config_data.get("pipeline_name", os.path.basename(file_path))
        super().__init__(title)
        self.file_path = file_path
        self.setObjectName("ConfigCard")
        
        layout = QVBoxLayout(self)
        
        proc_count = len(config_data.get("processes", {}))
        step_count = sum(len(steps) for steps in config_data.get("processes", {}).values())
        
        self.info_lbl = QLabel(f"Processes: {proc_count} | Total Steps: {step_count}")
        self.info_lbl.setObjectName("cardMetadata")
        layout.addWidget(self.info_lbl)
        
        self.path_lbl = QLabel(os.path.basename(file_path))
        self.path_lbl.setObjectName("cardPath")
        layout.addWidget(self.path_lbl)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        
        self.btn_run = QPushButton("▶ Run")
        self.btn_run.setObjectName("btnSuccess")
        self.btn_run.clicked.connect(lambda: self.run_requested.emit(self.file_path))
        
        self.btn_edit = QPushButton("✏ Edit")
        self.btn_edit.setObjectName("btnPrimary")
        self.btn_edit.clicked.connect(lambda: self.edit_requested.emit(self.file_path))
        
        self.btn_del = QPushButton("🗑")
        self.btn_del.setObjectName("btnDanger")
        self.btn_del.setFixedWidth(40)
        self.btn_del.clicked.connect(lambda: self.delete_requested.emit(self.file_path))
        
        btn_layout.addWidget(self.btn_run)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_del)
        
        layout.addLayout(btn_layout)

class DashboardWidget(QWidget):
    create_new_requested = pyqtSignal()
    auto_generate_requested = pyqtSignal()
    edit_config_requested = pyqtSignal(str)
    run_config_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        
        header_layout = QHBoxLayout()
        self.title_lbl = QLabel("Dynamic Scorecard System")
        self.title_lbl.setObjectName("mainTitle")
        header_layout.addWidget(self.title_lbl)
        header_layout.addStretch()
        
        self.btn_new = QPushButton("➕ Create New Configuration")
        self.btn_new.setObjectName("btnPrimary")
        self.btn_new.setMinimumHeight(50)
        self.btn_new.clicked.connect(self.create_new_requested.emit)
        header_layout.addWidget(self.btn_new)
        
        self.btn_auto = QPushButton("🪄 Auto-Generate from Excel")
        self.btn_auto.setObjectName("btnSuccess")
        self.btn_auto.setMinimumHeight(50)
        self.btn_auto.clicked.connect(self.auto_generate_requested.emit)
        header_layout.addWidget(self.btn_auto)
        
        self.btn_import_config = QPushButton("📥 Import Config")
        self.btn_import_config.setMinimumHeight(50)
        self.btn_import_config.clicked.connect(self.import_config)
        header_layout.addWidget(self.btn_import_config)
        
        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.setMinimumHeight(50)
        self.btn_refresh.setFixedWidth(120)
        self.btn_refresh.clicked.connect(self.refresh_configs)
        header_layout.addWidget(self.btn_refresh)
        
        main_layout.addLayout(header_layout)
        
        self.divider = QFrame()
        self.divider.setObjectName("mainDivider")
        self.divider.setFrameShape(QFrame.HLine)
        self.divider.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(self.divider)
        
        self.scroll = QScrollArea()
        self.scroll.setObjectName("dashboardScroll")
        self.scroll.setWidgetResizable(True)
        
        self.container = QWidget()
        self.container.setObjectName("dashboardContainer")
        self.flow_layout = QGridLayout(self.container)
        self.flow_layout.setSpacing(20)
        
        self.scroll.setWidget(self.container)
        main_layout.addWidget(self.scroll)
        
        self.refresh_configs()

    def import_config(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Configuration to Import", "", "JSON Files (*.json)")
        if file_path:
            config_dir = "Config"
            if not os.path.exists(config_dir): os.makedirs(config_dir)
            dest_path = os.path.join(config_dir, os.path.basename(file_path))
            if os.path.abspath(file_path) != os.path.abspath(dest_path):
                try:
                    shutil.copy2(file_path, dest_path)
                    QMessageBox.information(self, "Success", f"Config imported:\n{dest_path}")
                    self.refresh_configs()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Could not import config:\n{e}")

    def refresh_configs(self):
        for i in reversed(range(self.flow_layout.count())): 
            self.flow_layout.itemAt(i).widget().setParent(None)
            
        config_dir = "Config"
        if not os.path.exists(config_dir): os.makedirs(config_dir)
            
        configs = [f for f in os.listdir(config_dir) if f.endswith(".json")]
        
        if not configs:
            empty_lbl = QLabel("No configurations found. Create your first pipeline to get started!")
            empty_lbl.setAlignment(Qt.AlignCenter)
            empty_lbl.setObjectName("emptyMsg")
            self.flow_layout.addWidget(empty_lbl, 0, 0)
            return

        col_limit = 3
        for idx, filename in enumerate(configs):
            path = os.path.join(config_dir, filename)
            try:
                with open(path, 'r') as f: data = json.load(f)
                card = ConfigCard(path, data)
                card.edit_requested.connect(self.edit_config_requested.emit)
                card.run_requested.connect(self.run_config_requested.emit)
                card.delete_requested.connect(self.delete_config)
                self.flow_layout.addWidget(card, idx // col_limit, idx % col_limit)
            except Exception as e:
                print(f"Error loading {filename}: {e}")

    def delete_config(self, path):
        reply = QMessageBox.question(self, 'Delete Configuration', 
                                     f"Are you sure you want to delete '{os.path.basename(path)}'?\nThis cannot be undone.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                os.remove(path)
                self.refresh_configs()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete file: {e}")

class ScorecardUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic Scorecard System - Dashboard")
        self.resize(1600, 1000)
        
        self.processes = {"Main_Process": []} 
        self.current_process = "Main_Process"
        self.export_dfs = [] 
        self.current_config_path = None
        
        self.global_dfs = {}
        self.global_vars = {}
        self.preview_dfs = {} 
        self.preview_vars = {}
        self.pending_step = None 
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.init_ui()
        self.apply_dark_theme()
        
        self.show_dashboard()

    def show_dashboard(self):
        self.dashboard.refresh_configs()
        self.stacked_widget.setCurrentIndex(0)
        self.setWindowTitle("Dynamic Scorecard System - Dashboard")
        self.dock_pipeline.hide()
        self.dock_sandbox.hide()
        self.dock_terminal.hide()
        
    def show_editor(self, config_path=None):
        self.stacked_widget.setCurrentIndex(1)
        self.dock_pipeline.show()
        self.dock_sandbox.show()
        self.dock_terminal.show()
        
        if config_path:
            self.load_config_from_path(config_path)
            self.setWindowTitle(f"Pipeline Editor - {os.path.basename(config_path)}")
        else:
            self.new_config()
            self.setWindowTitle("Pipeline Editor - New Configuration")

    def new_config(self):
        self.processes = {"Main_Process": []}
        self.current_process = "Main_Process"
        self.export_dfs = []
        self.current_config_path = None
        self.global_dfs, self.global_vars, self.preview_dfs, self.preview_vars = {}, {}, {}, {}
        
        self.combo_processes.blockSignals(True)
        self.combo_processes.clear()
        self.combo_processes.addItem("Main_Process")
        self.combo_processes.blockSignals(False)
        
        self.refresh_step_list()
        self.update_tabs()

    def run_config_from_dashboard(self, path):
        export_dir = QFileDialog.getExistingDirectory(self, "Select Export Folder for Final Data")
        if not export_dir: return
        self.show_editor(path)
        self.run_full_restore(export_dir)

    def apply_dark_theme(self):
        dark_qss = """
        QMainWindow, QWidget { 
            background-color: #181818; 
            color: #cccccc; 
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; 
            font-size: 9pt; 
        }

        /* IDE Header & Toolbar */
        QToolBar { 
            background-color: #252525; 
            border-bottom: 1px solid #333333; 
            spacing: 5px; 
            padding: 5px;
        }
        QToolButton { 
            background: transparent; 
            border: 1px solid transparent; 
            border-radius: 4px; 
            padding: 4px 8px; 
            color: #e0e0e0;
            font-weight: 500;
        }
        QToolButton:hover { background-color: #3c3c3c; border: 1px solid #454545; }
        QToolButton:pressed { background-color: #505050; }

        /* Status Bar */
        QStatusBar { background-color: #007acc; color: #ffffff; min-height: 22px; }
        QStatusBar::item { border: none; }

        /* Dock System */
        QDockWidget { 
            border: 1px solid #2b2b2b; 
        }
        QDockWidget::title { 
            text-align: left; 
            background: #252525; 
            padding: 6px 10px; 
            font-weight: 600; 
            color: #969696; 
            border-bottom: 1px solid #333333;
        }
        QDockWidget::close-button, QDockWidget::float-button { border: none; background: transparent; }
        QDockWidget::close-button:hover, QDockWidget::float-button:hover { background: #3c3c3c; border-radius: 3px; }

        QGroupBox { 
            border: 1px solid #333333; 
            border-radius: 6px; 
            margin-top: 15px; 
            font-weight: 600; 
            color: #007acc; 
            padding: 10px;
        }
        QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; left: 10px; }

        QPushButton { 
            background-color: #333333; 
            color: #e0e0e0; 
            border: 1px solid #454545; 
            padding: 6px 12px; 
            border-radius: 4px; 
            font-weight: 500; 
        }
        QPushButton:hover { background-color: #3c3c3c; border-color: #007acc; }
        QPushButton#btnPrimary { background-color: #007acc; border: none; color: #ffffff; }
        QPushButton#btnPrimary:hover { background-color: #1a8ad4; }
        QPushButton#btnSuccess { background-color: #2da44e; border: none; color: #ffffff; }
        QPushButton#btnDanger { background-color: #cf222e; border: none; color: #ffffff; }

        QLineEdit, QTextEdit, QComboBox { 
            background-color: #1e1e1e; 
            border: 1px solid #3c3c3c; 
            border-radius: 4px; 
            padding: 6px; 
            color: #cccccc; 
            selection-background-color: #264f78;
        }
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border: 1px solid #007acc; }

        /* Central Tabs */
        QTabWidget::pane { border-top: 1px solid #2b2b2b; background: #1e1e1e; }
        QTabBar::tab { 
            background: #2d2d2d; 
            border: 1px solid #252525; 
            padding: 8px 15px; 
            color: #969696; 
            min-width: 80px;
        }
        QTabBar::tab:selected { background: #1e1e1e; color: #ffffff; border-bottom: 2px solid #007acc; font-weight: 600; }
        QTabBar::tab:hover:!selected { background: #323232; }

        /* Tables & Data */
        QTableView, QTableWidget {
            background-color: #1e1e1e;
            gridline-color: #2b2b2b;
            border: none;
            color: #cccccc;
            selection-background-color: #264f78;
            selection-color: #ffffff;
        }
        QHeaderView::section {
            background-color: #252525;
            color: #969696;
            padding: 6px;
            border: 1px solid #181818;
            border-bottom: 1px solid #2b2b2b;
            font-weight: 500;
        }
        QHeaderView { background-color: #252525; }

        /* Scrollbars (Modern Thin) */
        QScrollBar:vertical { border: none; background: #181818; width: 10px; }
        QScrollBar::handle:vertical { background: #333333; min-height: 20px; border-radius: 5px; margin: 2px; }
        QScrollBar::handle:vertical:hover { background: #454545; }
        QScrollBar:horizontal { border: none; background: #181818; height: 10px; }
        QScrollBar::handle:horizontal { background: #333333; min-width: 20px; border-radius: 5px; margin: 2px; }

        QListWidget { background-color: #1e1e1e; border: 1px solid #2b2b2b; }
        QListWidget::item { padding: 8px; border-radius: 2px; }
        QListWidget::item:selected { background-color: #094771; color: #ffffff; }
        QListWidget::item:hover:!selected { background-color: #2a2d2e; }
        """
        self.setStyleSheet(dark_qss)
        if hasattr(self, 'terminal_output'):
            self.terminal_output.setStyleSheet("background-color: #1e1e1e; border: 1px solid #2b2b2b; color: #00e676; padding: 10px; font-family: 'JetBrains Mono', 'Consolas'; font-size: 10pt;")
            self.terminal_input.setStyleSheet("background-color: #1e1e1e; border: 1px solid #333333; border-top: 1px solid #007acc; color: #ffffff; padding: 8px;")
        if hasattr(self, 'dashboard'): self.dashboard.setStyleSheet(dark_qss)

    def apply_white_theme(self):
        white_qss = """
        QMainWindow, QWidget { 
            background-color: #ffffff; 
            color: #3b3b3b; 
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; 
            font-size: 9pt; 
        }

        /* IDE Header & Toolbar */
        QToolBar { 
            background-color: #f3f3f3; 
            border-bottom: 1px solid #dddddd; 
            spacing: 5px; 
            padding: 5px;
        }
        QToolButton { 
            background: transparent; 
            border: 1px solid transparent; 
            border-radius: 4px; 
            padding: 4px 8px; 
            color: #3b3b3b;
            font-weight: 500;
        }
        QToolButton:hover { background-color: #e5e5e5; border: 1px solid #d0d0d0; }

        /* Status Bar */
        QStatusBar { background-color: #007acc; color: #ffffff; min-height: 22px; }

        /* Dock System */
        QDockWidget { border: 1px solid #dddddd; }
        QDockWidget::title { 
            text-align: left; 
            background: #f3f3f3; 
            padding: 6px 10px; 
            font-weight: 600; 
            color: #616161; 
            border-bottom: 1px solid #dddddd;
        }
        QDockWidget::close-button, QDockWidget::float-button { border: none; background: transparent; }
        QDockWidget::close-button:hover { background: #e81123; border-radius: 2px; }

        QGroupBox { 
            border: 1px solid #dddddd; 
            border-radius: 6px; 
            margin-top: 15px; 
            font-weight: 600; 
            color: #007acc; 
            padding: 10px;
        }
        QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; left: 10px; background-color: #ffffff; }

        QPushButton { 
            background-color: #f3f3f3; 
            color: #3b3b3b; 
            border: 1px solid #dcdcdc; 
            padding: 6px 12px; 
            border-radius: 4px; 
            font-weight: 500; 
        }
        QPushButton:hover { background-color: #e5e5e5; border-color: #007acc; }
        QPushButton#btnPrimary { background-color: #007acc; border: none; color: #ffffff; }
        QPushButton#btnPrimary:hover { background-color: #1a8ad4; }

        QLineEdit, QTextEdit, QComboBox { 
            background-color: #ffffff; 
            border: 1px solid #cecece; 
            border-radius: 4px; 
            padding: 6px; 
            color: #3b3b3b; 
        }
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border: 1px solid #007acc; }

        /* Central Tabs */
        QTabWidget::pane { border-top: 1px solid #dddddd; background: #ffffff; }
        QTabBar::tab { 
            background: #ececec; 
            border: 1px solid #dddddd; 
            padding: 8px 15px; 
            color: #616161; 
            min-width: 80px;
        }
        QTabBar::tab:selected { background: #ffffff; color: #007acc; border-bottom: 2px solid #007acc; font-weight: 600; }

        /* Tables & Data */
        QTableView, QTableWidget {
            background-color: #ffffff;
            gridline-color: #f0f0f0;
            border: none;
            color: #3b3b3b;
            selection-background-color: #add6ff;
            selection-color: #000000;
        }
        QHeaderView::section {
            background-color: #f3f3f3;
            color: #616161;
            padding: 6px;
            border: 1px solid #ffffff;
            border-bottom: 1px solid #dddddd;
            font-weight: 500;
        }

        /* Scrollbars (Modern Thin) */
        QScrollBar:vertical { border: none; background: #ffffff; width: 10px; }
        QScrollBar::handle:vertical { background: #dcdcdc; min-height: 20px; border-radius: 5px; margin: 2px; }
        QScrollBar::handle:vertical:hover { background: #b0b0b0; }

        QListWidget { background-color: #ffffff; border: 1px solid #dddddd; }
        QListWidget::item { padding: 8px; }
        QListWidget::item:selected { background-color: #007acc; color: #ffffff; }
        QListWidget::item:hover:!selected { background-color: #f0f0f0; }
        """
        self.setStyleSheet(white_qss)
        if hasattr(self, 'terminal_output'):
            self.terminal_output.setStyleSheet("background-color: #ffffff; border: 1px solid #dddddd; color: #212529; padding: 10px; font-family: 'JetBrains Mono', 'Consolas'; font-size: 10pt;")
            self.terminal_input.setStyleSheet("background-color: #ffffff; border: 1px solid #dddddd; border-top: 1px solid #007acc; color: #3b3b3b; padding: 8px;")
        if hasattr(self, 'dashboard'):
            self.dashboard.setStyleSheet(white_qss)
            self.dashboard.refresh_configs()
    def init_ui(self):
        # 1. CENTRAL WORKSPACE (The Code/Data Editor)
        self.dashboard = DashboardWidget()
        self.dashboard.create_new_requested.connect(lambda: self.show_editor())
        self.dashboard.auto_generate_requested.connect(self.auto_generate_pipeline)
        self.dashboard.edit_config_requested.connect(lambda p: self.show_editor(p))
        self.dashboard.run_config_requested.connect(self.run_config_from_dashboard)
        self.stacked_widget.addWidget(self.dashboard)

        # Menubar & Themes
        menubar = self.menuBar()
        view_menu = menubar.addMenu('View')
        self.dock_menu = view_menu.addMenu('Panels')
        theme_menu = view_menu.addMenu('Theme')
        dark_action = QAction('🌙 Dark Mode', self)
        dark_action.triggered.connect(lambda: self.apply_dark_theme())
        theme_menu.addAction(dark_action)
        white_action = QAction('☀️ Light Mode', self)
        white_action.triggered.connect(lambda: self.apply_white_theme())
        theme_menu.addAction(white_action)

        self.editor_central = QWidget()
        editor_main_layout = QVBoxLayout(self.editor_central)
        editor_main_layout.setContentsMargins(0, 0, 0, 0)
        editor_main_layout.setSpacing(0)

        # Top Activity Bar (Compact)
        activity_bar = QHBoxLayout()
        activity_bar.setContentsMargins(10, 5, 10, 5)
        self.lbl_context = QLabel("Workspace: 0 DataFrames")
        self.lbl_context.setStyleSheet("color: #3d5afe; font-weight: bold; font-size: 9pt;")
        activity_bar.addWidget(self.lbl_context)
        activity_bar.addStretch()
        
        self.combo_view = QComboBox()
        self.combo_view.setMinimumWidth(250)
        self.combo_view.setPlaceholderText("Quick Jump to Data...")
        self.combo_view.currentIndexChanged.connect(self.on_view_combo_changed)
        activity_bar.addWidget(self.combo_view)
        editor_main_layout.addLayout(activity_bar)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True) # Modern flat tabs
        self.tabs.setTabsClosable(False)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        editor_main_layout.addWidget(self.tabs)
        self.stacked_widget.addWidget(self.editor_central)

        # 2. MAIN TOOLBAR (IDE Quick Actions)
        toolbar = self.addToolBar("Main Operations")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        act_back = QAction("🏠 Dashboard", self)
        act_back.triggered.connect(lambda: self.show_dashboard())
        toolbar.addAction(act_back)
        toolbar.addSeparator()

        act_save = QAction("💾 Save", self)
        act_save.triggered.connect(lambda: self.save_config())
        toolbar.addAction(act_save)

        act_load = QAction("📂 Open", self)
        act_load.triggered.connect(lambda: self.load_config())
        toolbar.addAction(act_load)
        toolbar.addSeparator()

        act_run = QAction("🚀 RUN PIPELINE", self)
        act_run.triggered.connect(self.run_full_restore)
        toolbar.addAction(act_run)

        # FIX: QToolBar does not have addStretch(). Use a spacer widget instead.
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        act_theme = QAction("🌓 Theme", self)
        theme_menu_btn = QMenu(self)
        theme_menu_btn.addAction(dark_action)
        theme_menu_btn.addAction(white_action)
        act_theme.setMenu(theme_menu_btn)
        toolbar.addAction(act_theme)

        # 3. DOCK: PIPELINE EXPLORER (Left)
        self.dock_pipeline = QDockWidget("Pipeline Explorer", self)
        self.dock_pipeline.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.dock_pipeline.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.dock_pipeline.setMinimumWidth(320)

        explorer_widget = QWidget()
        explorer_layout = QVBoxLayout(explorer_widget)
        explorer_layout.setContentsMargins(10, 10, 10, 10)
        explorer_layout.setSpacing(8)

        # Compact Process Switcher
        proc_layout = QHBoxLayout()
        self.combo_processes = QComboBox()
        self.combo_processes.addItem("Main_Process")
        self.combo_processes.currentTextChanged.connect(self.switch_process)
        proc_layout.addWidget(self.combo_processes, 1)
        
        btn_manage = QPushButton("⚙️")
        btn_manage.setFixedWidth(32)
        btn_manage.clicked.connect(self.manage_processes)
        proc_layout.addWidget(btn_manage)
        explorer_layout.addLayout(proc_layout)

        # Source Control Section
        source_group = QGroupBox("Data Ingestion")
        source_layout = QGridLayout(source_group)
        source_layout.setSpacing(4)
        
        btn_load = QPushButton("📥 Load")
        btn_load.clicked.connect(self.load_data)
        source_layout.addWidget(btn_load, 0, 0)

        btn_extra = QPushButton("📄 Sheet")
        btn_extra.clicked.connect(self.load_existing_file_data)
        source_layout.addWidget(btn_extra, 0, 1)

        btn_batch = QPushButton("📚 Batch")
        btn_batch.clicked.connect(self.load_all_sheets_data)
        source_layout.addWidget(btn_batch, 1, 0)

        btn_map = QPushButton("🔗 Map")
        btn_map.clicked.connect(self.map_columns_dialog)
        source_layout.addWidget(btn_map, 1, 1)
        explorer_layout.addWidget(source_group)

        # Step Sequence
        self.list_steps = DraggableListWidget()
        self.list_steps.itemClicked.connect(self.load_step_into_editor)
        self.list_steps.item_moved.connect(self.on_step_moved)
        explorer_layout.addWidget(self.list_steps)

        btn_export = QPushButton("💾 Export Settings")
        btn_export.setObjectName("btnSecondary")
        btn_export.clicked.connect(self.configure_export)
        explorer_layout.addWidget(btn_export)

        self.dock_pipeline.setWidget(explorer_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_pipeline)

        # 4. DOCK: LOGIC DESIGNER (Right)
        self.dock_sandbox = QDockWidget("Logic Designer", self)
        self.dock_sandbox.setMinimumWidth(400)
        
        logic_widget = QWidget()
        logic_layout = QVBoxLayout(logic_widget)
        logic_layout.setContentsMargins(10, 10, 10, 10)
        logic_layout.setSpacing(10)

        self.combo_action = QComboBox()
        self.combo_action.addItems([
            "Execute Raw Python/Pandas", 
            "Evaluate Excel Formula (Native Math)",
            "Run External .py Script (Entire File)"
        ])
        self.combo_action.currentIndexChanged.connect(self.toggle_inputs)
        logic_layout.addWidget(self.combo_action)

        code_font = QFont("Consolas", 11)
        self.txt_python = QTextEdit()
        self.txt_python.setFont(code_font)
        self.txt_python.setPlaceholderText("Write transformation logic...")
        logic_layout.addWidget(self.txt_python)

        # Excel Logic Panel
        self.widget_excel_formula = QWidget()
        ex_layout = QVBoxLayout(self.widget_excel_formula)
        ex_layout.setContentsMargins(0, 0, 0, 0)
        self.txt_excel_formula = QTextEdit()
        self.txt_excel_formula.setFont(code_font)
        self.txt_excel_formula.setPlaceholderText("Excel Formula...")
        self.txt_excel_formula.setMaximumHeight(100)
        ex_layout.addWidget(self.txt_excel_formula)
        self.txt_excel_target = QLineEdit()
        self.txt_excel_target.setPlaceholderText("Target DataFrame...")
        ex_layout.addWidget(self.txt_excel_target)
        self.txt_excel_column = QLineEdit()
        self.txt_excel_column.setPlaceholderText("Target Column (Optional)...")
        ex_layout.addWidget(self.txt_excel_column)
        self.widget_excel_formula.hide()
        logic_layout.addWidget(self.widget_excel_formula)

        # Script Panel
        self.widget_script_path = QWidget()
        sc_layout = QHBoxLayout(self.widget_script_path)
        sc_layout.setContentsMargins(0, 0, 0, 0)
        self.txt_script_path = QLineEdit()
        btn_br = QPushButton("📁")
        btn_br.setFixedWidth(30)
        btn_br.clicked.connect(self.browse_script)
        sc_layout.addWidget(self.txt_script_path)
        sc_layout.addWidget(btn_br)
        self.widget_script_path.hide()
        logic_layout.addWidget(self.widget_script_path)

        # Logic Controls
        logic_btn_grid = QGridLayout()
        btn_test = QPushButton("🧪 Test")
        btn_test.clicked.connect(self.test_step)
        logic_btn_grid.addWidget(btn_test, 0, 0)

        btn_record = QPushButton("✅ Record")
        btn_record.setObjectName("btnSuccess")
        btn_record.clicked.connect(self.record_step)
        logic_btn_grid.addWidget(btn_record, 0, 1)

        btn_upd = QPushButton("🔄 Update")
        btn_upd.setObjectName("btnActive")
        btn_upd.clicked.connect(self.update_selected_step)
        logic_btn_grid.addWidget(btn_upd, 1, 0)

        btn_del = QPushButton("🗑 Delete")
        btn_del.setObjectName("btnDanger")
        btn_del.clicked.connect(self.delete_step)
        logic_btn_grid.addWidget(btn_del, 1, 1)
        logic_layout.addLayout(logic_btn_grid)

        self.dock_sandbox.setWidget(logic_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_sandbox)

        # 5. DOCK: CONSOLE (Bottom)
        self.dock_terminal = QDockWidget("System Console", self)
        term_widget = QWidget()
        term_layout = QVBoxLayout(term_widget)
        term_layout.setContentsMargins(0, 0, 0, 0)
        term_layout.setSpacing(0)
        
        self.terminal_output = QTextEdit()
        self.terminal_output.setFont(code_font)
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setMinimumHeight(150)
        term_layout.addWidget(self.terminal_output)
        
        self.terminal_input = TerminalInput()
        self.terminal_input.setFont(code_font)
        self.terminal_input.setPlaceholderText(">>> Command Console...")
        self.terminal_input.returnPressed.connect(self.execute_terminal_command)
        term_layout.addWidget(self.terminal_input)
        
        self.dock_terminal.setWidget(term_widget)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_terminal)

        # 6. LAYOUT CONFIGURATION
        self.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)
        self.setTabPosition(Qt.AllDockWidgetAreas, QTabWidget.North)
        
        self.update_tabs()

    def auto_generate_pipeline(self):
        if analyze_workbook is None:
            QMessageBox.critical(self, "Error", "xlwings is required for Auto-Generation. Please run 'pip install xlwings'.")
            return

        if hasattr(self, 'analysis_worker') and self.analysis_worker.isRunning():
            QMessageBox.warning(self, "Running", "Analysis is currently running. Please wait.")
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Select Excel to Reverse-Engineer", "", "Excel Files (*.xlsx *.xlsm)")
        if not file_path: return

        self.analysis_msg = QMessageBox(self)
        self.analysis_msg.setWindowTitle("Working...")
        self.analysis_msg.setText("🔍 Analyzing workbook structure and formulas...\nPlease wait, this may take a moment.")
        self.analysis_msg.setStandardButtons(QMessageBox.NoButton)
        self.analysis_msg.show()

        self.analysis_worker = ExcelAnalysisWorker(file_path)
        self.analysis_worker.result_ready.connect(self.on_analysis_success)
        self.analysis_worker.error_occurred.connect(self.on_analysis_error)
        self.analysis_worker.start()

    def on_analysis_success(self, config):
        if hasattr(self, 'analysis_msg'):
            self.analysis_msg.done(0)
            self.analysis_msg.close()
        
        QApplication.processEvents()
        
        config_dir = "Config"
        if not os.path.exists(config_dir): os.makedirs(config_dir)

        save_path = os.path.join(config_dir, f"{config['pipeline_name']}.json")
        with open(save_path, 'w') as f: json.dump(config, f, indent=4)

        QMessageBox.information(self, "Success", f"Pipeline successfully generated!\nSaved to: {save_path}")
        self.show_editor(save_path)

    def on_analysis_error(self, err_msg):
        if hasattr(self, 'analysis_msg'):
            self.analysis_msg.done(0)
            self.analysis_msg.close()
        QApplication.processEvents()
        QMessageBox.critical(self, "Reverse Engineering Error", f"Failed to analyze workbook:\n{err_msg}")

    def on_view_combo_changed(self, idx):
        if idx >= 0 and idx < self.tabs.count():
            self.tabs.blockSignals(True)
            self.tabs.setCurrentIndex(idx)
            self.tabs.blockSignals(False)

    def on_tab_changed(self, idx):
        if idx >= 0 and idx < self.combo_view.count():
            self.combo_view.blockSignals(True)
            self.combo_view.setCurrentIndex(idx)
            self.combo_view.blockSignals(False)

    def configure_export(self):
        pipeline_dfs = set()
        for proc in self.processes.values():
            for step in proc:
                if step["action"] == "load_file":
                    pipeline_dfs.add(step["params"].get("alias"))
        
        all_possible = sorted(list(set(self.global_dfs.keys()) | pipeline_dfs | set(self.export_dfs)))
        
        dlg = ExportConfigDialog(all_possible, self.export_dfs, self)
        if dlg.exec_() == QDialog.Accepted:
            self.export_dfs = dlg.get_selected()
            QMessageBox.information(self, "Saved", f"Export configuration updated.\n\n{len(self.export_dfs)} DataFrames will be exported.")

    def browse_script(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Python Script", "", "Python Files (*.py);;All Files (*)")
        if file_path:
            custom_dir = "Custom_Scripts"
            if not os.path.exists(custom_dir): os.makedirs(custom_dir)
            dest_path = os.path.join(custom_dir, os.path.basename(file_path))
            
            if os.path.abspath(file_path) != os.path.abspath(dest_path):
                try:
                    shutil.copy2(file_path, dest_path)
                    if hasattr(self, 'terminal_output'): self.terminal_output.append(f"\n>>> Copied script to local project: {dest_path}")
                except Exception as e:
                    QMessageBox.warning(self, "Copy Error", f"Could not copy script:\n{e}")
            self.txt_script_path.setText(dest_path)

    def execute_terminal_command(self):
        cmd = self.terminal_input.text()
        if not cmd.strip(): return
        
        self.terminal_input.add_to_history(cmd)
        self.terminal_output.append(f"\n>>> {cmd}")
        self.terminal_input.clear()
        
        env = {**self.preview_dfs, **self.preview_vars, 'pd': pd, 'np': np, 'os': os, 'prompt_file': prompt_file}
        output = io.StringIO()
        ui_needs_update = False
        
        with contextlib.redirect_stdout(output):
            try:
                res = eval(cmd, {}, env)
                if res is not None: print(res)
            except SyntaxError:
                try:
                    exec(cmd, env, env)
                    ui_needs_update = True
                except Exception as e: print(f"Error: {e}")
            except Exception as e: print(f"Error: {e}")
                
        result_text = output.getvalue().strip()
        if result_text: self.terminal_output.append(result_text)
            
        scrollbar = self.terminal_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        if ui_needs_update:
            self.preview_dfs = {k: v for k, v in env.items() if isinstance(v, pd.DataFrame)}
            self.preview_vars = {k: v for k, v in env.items() if not isinstance(v, pd.DataFrame) and not callable(v) and not k.startswith('_') and str(type(v).__module__) == 'builtins'}
            self.update_tabs()

    def manage_processes(self):
        dialog = ProcessManagerDialog(self.processes, self)
        if dialog.exec_() == QDialog.Accepted:
            mapping = dialog.get_process_mapping()
            new_processes = {}
            for new_name, old_name in mapping:
                if old_name is not None and old_name in self.processes:
                    new_processes[new_name] = self.processes[old_name]
                else:
                    new_processes[new_name] = []
                    
            self.processes = new_processes
            if self.current_process not in self.processes:
                self.current_process = list(self.processes.keys())[0] if self.processes else ""
                
            self.combo_processes.blockSignals(True)
            self.combo_processes.clear()
            self.combo_processes.addItems(list(self.processes.keys()))
            self.combo_processes.setCurrentText(self.current_process)
            self.combo_processes.blockSignals(False)
            self.refresh_step_list()

    def switch_process(self, process_name):
        if not process_name: return
        self.current_process = process_name
        self.refresh_step_list()

    def refresh_step_list(self):
        self.list_steps.clear()
        if self.current_process in self.processes:
            for step in self.processes[self.current_process]:
                prompt_flag = " [Prompt at Runtime]" if step.get('params', {}).get('prompt_at_runtime') else ""
                self.list_steps.addItem(f"[{step['step_id']}] {step['action']}{prompt_flag}")

    def toggle_inputs(self):
        action = self.combo_action.currentText()
        self.txt_python.setVisible(action == "Execute Raw Python/Pandas")
        self.widget_excel_formula.setVisible("Excel Formula" in action)
        self.widget_script_path.setVisible("External" in action)

    def load_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Excel/CSV", "", "Data Files (*.xlsx *.csv)")
        if not file_path: return

        sheet_name = 0
        if file_path.endswith('.xlsx'):
            try:
                xl = pd.ExcelFile(file_path)
                sheet_name, ok = QInputDialog.getItem(self, "Select Sheet", "Select sheet:", xl.sheet_names, 0, False)
                if not ok: return
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
                return

        alias, ok = QInputDialog.getText(self, "DataFrame Alias", "Variable name (e.g. df1):")
        if not ok or not alias.strip(): return
        alias = alias.strip()

        reply = QMessageBox.question(self, 'Dynamic Input',
                                     f"When this pipeline runs automatically, should it STOP and prompt the user to select the file for '{alias}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        prompt_at_runtime = (reply == QMessageBox.Yes)

        try:
            df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path, sheet_name=sheet_name)
            self.global_dfs[alias] = df
            self.preview_dfs = self.global_dfs.copy()
            self.update_tabs()
            
            step = {
                "step_id": len(self.processes[self.current_process]) + 1,
                "action": "load_file",
                "params": {"filepath": file_path, "sheet": sheet_name, "alias": alias, "prompt_at_runtime": prompt_at_runtime}
            }
            self.processes[self.current_process].append(step)
            self.refresh_step_list()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def load_all_sheets_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsx *.xlsm)")
        if not file_path: return

        reply = QMessageBox.question(self, 'Dynamic Input',
                                     f"When this pipeline runs automatically, should it STOP and prompt the user to select the file for this batch load?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        prompt_at_runtime = (reply == QMessageBox.Yes)

        try:
            xl = pd.ExcelFile(file_path)
            for sheet_name in xl.sheet_names:
                df = pd.read_excel(xl, sheet_name=sheet_name)
                self.global_dfs[sheet_name] = df
            
            self.preview_dfs = self.global_dfs.copy()
            self.update_tabs()
            
            step = {
                "step_id": len(self.processes[self.current_process]) + 1,
                "action": "load_all_sheets",
                "params": {"filepath": file_path, "prompt_at_runtime": prompt_at_runtime}
            }
            self.processes[self.current_process].append(step)
            self.refresh_step_list()
            QMessageBox.information(self, "Success", f"Loaded {len(xl.sheet_names)} sheets into memory.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def map_columns_dialog(self):
        if not self.global_dfs:
            QMessageBox.warning(self, "No Data", "Please load at least two DataFrames to use mapping.")
            return

        dlg = MapColumnsDialog(self.global_dfs, self)
        if dlg.exec_() == QDialog.Accepted:
            params = dlg.get_data()
            
            # Record the step
            step = {
                "step_id": len(self.processes[self.current_process]) + 1,
                "action": "map_columns",
                "params": params
            }
            self.processes[self.current_process].append(step)
            self.refresh_step_list()

            # Apply locally for preview
            try:
                target_alias = params['target_df']
                source_alias = params['source_df']
                target_key = params['target_key']
                source_key = params['source_key']
                cols_to_map = params['columns_to_map']
                
                target_df = self.global_dfs[target_alias]
                source_df = self.global_dfs[source_alias]
                
                source_subset = source_df[[source_key] + cols_to_map].drop_duplicates(subset=[source_key])
                
                merged = target_df.merge(
                    source_subset, 
                    left_on=target_key, 
                    right_on=source_key, 
                    how='left',
                    suffixes=('', '_map_temp')
                )
                
                if target_key != source_key and source_key in merged.columns:
                    merged = merged.drop(columns=[source_key])
                
                temp_cols = [c for c in merged.columns if c.endswith('_map_temp')]
                if temp_cols:
                    merged = merged.drop(columns=temp_cols)
                    
                self.global_dfs[target_alias] = merged
                self.preview_dfs = self.global_dfs.copy()
                self.update_tabs()
                
                QMessageBox.information(self, "Success", f"Mapped {len(cols_to_map)} columns from '{source_alias}' to '{target_alias}'.")
            except Exception as e:
                QMessageBox.critical(self, "Mapping Error", f"Step recorded, but failed to apply preview:\n{e}")

    def load_existing_file_data(self):
        active_files = set()
        for proc in self.processes.values():
            for step in proc:
                if step.get("action") == "load_file":
                    fp = step.get("params", {}).get("filepath")
                    if fp and fp.endswith(('.xlsx', '.xlsm')): active_files.add(fp)
        
        if not active_files:
            QMessageBox.information(self, "No Active Files", "No Excel files are currently loaded.")
            return
            
        file_path, ok = QInputDialog.getItem(self, "Select Existing File", "Choose an Excel file:", list(active_files), 0, False)
        if not ok: return
        
        try:
            xl = pd.ExcelFile(file_path)
            sheet_name, ok = QInputDialog.getItem(self, "Select Sheet", f"Select sheet:", xl.sheet_names, 0, False)
            if not ok: return
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not read file: {e}")
            return
            
        alias, ok = QInputDialog.getText(self, "DataFrame Alias", "Variable name:")
        if not ok or not alias.strip(): return
        alias = alias.strip()

        reply = QMessageBox.question(self, 'Dynamic Input',
                                     f"Prompt user to select file for '{alias}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        prompt_at_runtime = (reply == QMessageBox.Yes)

        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            self.global_dfs[alias] = df
            self.preview_dfs = self.global_dfs.copy()
            self.update_tabs()
            
            step = {
                "step_id": len(self.processes[self.current_process]) + 1,
                "action": "load_file",
                "params": {"filepath": file_path, "sheet": sheet_name, "alias": alias, "prompt_at_runtime": prompt_at_runtime}
            }
            self.processes[self.current_process].append(step)
            self.refresh_step_list()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def copy_df_name(self, name, btn):
        QApplication.clipboard().setText(name)
        original_text = btn.text()
        btn.setText("✅ Copied!")
        btn.setStyleSheet("background-color: #2da44e; color: white; border: none;") 
        QTimer.singleShot(1500, lambda: self.reset_copy_btn(btn, original_text))

    def reset_copy_btn(self, btn, text):
        try:
            btn.setText(text)
            btn.setStyleSheet("") 
        except RuntimeError: pass

    def copy_column_name(self, index, df_columns):
        if 0 <= index < len(df_columns):
            col_name = str(df_columns[index])
            QApplication.clipboard().setText(col_name)
            QToolTip.showText(QCursor.pos(), f"✅ Copied Column: '{col_name}'")

    # ==============================================================================
    # EXPLICIT MEMORY LIFECYCLE MANAGEMENT FOR C++ QT OBJECTS
    # ==============================================================================
    def update_tabs(self):
        # 1. Close and explicitly delete active popups
        if hasattr(self, 'active_popup') and self.active_popup:
            self.active_popup.close()
            self.active_popup.deleteLater()
            self.active_popup = None
            
        # 2. SAFELY DESTROY OLD TABS TO PREVENT C++ SEGFAULTS
        while self.tabs.count() > 0:
            widget = self.tabs.widget(0)
            self.tabs.removeTab(0)
            if widget:
                widget.deleteLater() # Safely destroy C++ object
                
        self.combo_view.blockSignals(True)
        self.combo_view.clear()
        
        var_table = QTableWidget(len(self.preview_vars), 3)
        var_table.setHorizontalHeaderLabels(["Variable Name", "Type", "Value"])
        var_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        var_table.verticalHeader().setVisible(False)
        
        row = 0
        for k, v in self.preview_vars.items():
            var_table.setItem(row, 0, QTableWidgetItem(str(k)))
            var_table.setItem(row, 1, QTableWidgetItem(type(v).__name__))
            var_table.setItem(row, 2, QTableWidgetItem(str(v)[:100]))
            row += 1
            
        self.tabs.addTab(var_table, "📦 Variables Explorer")
        self.combo_view.addItem("📦 Variables Explorer")

        for alias, df in self.preview_dfs.items():
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)
            tab_layout.setContentsMargins(5, 5, 5, 5)

            top_bar = QHBoxLayout()
            lbl_alias = QLabel(f"Viewing DataFrame: <b>{alias}</b>")
            lbl_alias.setStyleSheet("font-size: 11pt;")
            top_bar.addWidget(lbl_alias)
            top_bar.addStretch()

            # ----- CUSTOM HEADER & TABLE -----
            table = DataFrameTableView()
            
            # Explicitly tie model lifecycles to the table widget so they destroy safely
            base_model = PandasModel(df, parent=table) 
            proxy_model = MultiFilterProxyModel(parent=table) 
            proxy_model.setSourceModel(base_model)
            table.setModel(proxy_model)
            
            btn_lock = QPushButton("🔒 Locked")
            btn_lock.setCheckable(True)
            btn_lock.setFixedWidth(180)
            btn_lock.setStyleSheet("background-color: #333333; color: white;")
            
            def toggle_lock(checked, model=base_model, btn=btn_lock):
                if checked:
                    btn.setText("🔓 Unlocked (Edit Mode)")
                    btn.setStyleSheet("background-color: #cf222e; color: white; border: none;")
                    model.is_editable = True
                else:
                    btn.setText("🔒 Locked")
                    btn.setStyleSheet("background-color: #333333; color: white;")
                    model.is_editable = False
                    
            btn_lock.toggled.connect(toggle_lock)
            top_bar.addWidget(btn_lock)
            
            # ---------------------------------------------------------
            # NEW: VISIBLE TOGGLE FILTER BUTTON
            # ---------------------------------------------------------
            btn_filter = QPushButton("🔽 Filters")
            btn_filter.setCheckable(True)
            btn_filter.setFixedWidth(140)
            
            # Inject Custom Excel Header tied to table
            header = FilterHeaderView(Qt.Horizontal, parent=table)
            table.setHorizontalHeader(header)
            header.setDefaultSectionSize(120)
            header.setSectionResizeMode(QHeaderView.Interactive)
            
            def toggle_filter_visibility(checked, h=header, p_model=proxy_model, btn=btn_filter):
                h.filters_enabled = checked
                if checked:
                    btn.setText("🔽 Filters (ON)")
                    btn.setStyleSheet("background-color: #007acc; color: white; border: none;")
                else:
                    btn.setText("🔽 Filters (OFF)")
                    btn.setStyleSheet("") # Revert to default stylesheet
                    # Reset all filters if turned off (like Excel does)
                    p_model.value_filters.clear()
                    h.filtered_cols.clear()
                    p_model.invalidateFilter()
                h.viewport().update()
                h.update() # Force full header repaint to be safe
                
            btn_filter.toggled.connect(toggle_filter_visibility)
            top_bar.addWidget(btn_filter)
            # ---------------------------------------------------------

            btn_copy = QPushButton("📋 Copy Name")
            btn_copy.setFixedWidth(120)
            btn_copy.setObjectName("btnPrimary")
            btn_copy.clicked.connect(lambda checked=False, n=alias, b=btn_copy: self.copy_df_name(n, b))
            top_bar.addWidget(btn_copy)
            
            tab_layout.addLayout(top_bar)

            table.verticalHeader().setVisible(False)
            table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
            table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

            # 1. Clicking column text copies name
            safe_cols = list(df.columns)
            header.sectionClicked.connect(
                lambda logicalIndex, columns=safe_cols: self.copy_column_name(logicalIndex, columns)
            )

            # 2. Sync Keyboard Shortcut (Ctrl+Shift+L) directly to the new UI Button
            table.filter_toggled.connect(lambda btn=btn_filter: btn.setChecked(not btn.isChecked()))

            # 3. Popup construction on Arrow Click / Alt+Down
            def handle_filter_click(col, x, y, current_df=df, p_model=proxy_model, h_view=header):
                col_name = current_df.columns[col]
                unique_vals = current_df[col_name].dropna().astype(str).unique().tolist()
                
                # SAFE SORTING (prevents float vs string TypeError crashes in Python 3)
                def safe_sort_key(val):
                    try:
                        return (0, float(val))
                    except ValueError:
                        return (1, str(val))
                        
                unique_vals.sort(key=safe_sort_key)
                unique_vals = unique_vals[:10000]
                
                active_vals = p_model.value_filters.get(col, None)
                
                self.active_popup = FilterPopup(self, col, unique_vals, active_vals, p_model, h_view)
                
                # Align the popup strictly to the mouse cursor to prevent off-screen opening
                self.active_popup.move(QCursor.pos()) 
                self.active_popup.show()

            header.filter_button_clicked.connect(handle_filter_click)

            tab_layout.addWidget(table)
            self.tabs.addTab(tab_widget, f"📊 DF: {alias}")
            self.combo_view.addItem(f"📊 DF: {alias}")
            
            # TURN FILTERS ON BY DEFAULT FOR EXCEL-LIKE EXPERIENCE
            btn_filter.setChecked(True)
            
        self.combo_view.blockSignals(False)
        self.lbl_context.setText(f"Context: DFs ({len(self.preview_dfs)}) | Vars ({len(self.preview_vars)})")

    def get_editor_step_data(self):
        action_type = self.combo_action.currentText()
        step = {"action": ""}
        if action_type == "Execute Raw Python/Pandas":
            step["action"] = "execute_python_logic"
            step["params"] = {"code_block": self.txt_python.toPlainText()}
        elif action_type == "Evaluate Excel Formula (Native Math)":
            step["action"] = "evaluate_excel_formula"
            step["params"] = {
                "formula": self.txt_excel_formula.toPlainText(),
                "target_alias": self.txt_excel_target.text(),
                "target_col": self.txt_excel_column.text() if self.txt_excel_column.text().strip() else None
            }
        elif action_type == "Run External .py Script (Entire File)":
            step["action"] = "run_python_file"
            step["params"] = {"script_path": self.txt_script_path.text()}
        return step

    def test_step(self):
        # Concurrency safety lock
        if hasattr(self, 'worker') and self.worker.isRunning():
            QMessageBox.warning(self, "Running", "A test is currently executing. Please wait.")
            return

        step = self.get_editor_step_data()
        if not step["params"].get("code_block") and step["action"] == "execute_python_logic": return
        
        self.pending_step = step
        self.worker = StepPreviewWorker(self.global_dfs, self.global_vars, step)
        self.worker.result_ready.connect(self.on_test_success)
        self.worker.error_occurred.connect(self.on_test_error)
        self.worker.start()

    def on_test_success(self, new_dfs, new_vars):
        self.preview_dfs = new_dfs
        self.preview_vars = new_vars
        self.update_tabs()
        QMessageBox.information(self, "Test Passed", "Code executed!")

    def on_test_error(self, err_msg):
        QMessageBox.critical(self, "Logic Error", f"Failed to execute:\n\n{err_msg}")

    def record_step(self):
        step = self.get_editor_step_data()
        if step["action"] == "execute_python_logic" and not step["params"].get("code_block", "").strip():
            QMessageBox.warning(self, "Warning", "Code block is empty!")
            return
        elif step["action"] == "run_python_file" and not step["params"].get("script_path", "").strip():
            QMessageBox.warning(self, "Warning", "Script path is empty!")
            return
            
        step["step_id"] = len(self.processes[self.current_process]) + 1
        self.processes[self.current_process].append(step)
        
        if self.pending_step:
            self.global_dfs = self.preview_dfs.copy()
            self.global_vars = self.preview_vars.copy()
            self.pending_step = None
            
        self.refresh_step_list()
        QMessageBox.information(self, "Recorded", f"Step '{step['action']}' successfully recorded.")

    def load_step_into_editor(self, item):
        row_idx = self.list_steps.row(item)
        step = self.processes[self.current_process][row_idx]
        
        if step["action"] == "execute_python_logic":
            self.combo_action.setCurrentText("Execute Raw Python/Pandas")
            self.txt_python.setPlainText(step["params"].get("code_block", ""))
        elif step["action"] == "evaluate_excel_formula":
            self.combo_action.setCurrentText("Evaluate Excel Formula (Native Math)")
            self.txt_excel_formula.setPlainText(step["params"].get("formula", ""))
            self.txt_excel_target.setText(step["params"].get("target_alias", ""))
            self.txt_excel_column.setText(step["params"].get("target_col", ""))
        elif step["action"] == "run_python_file":
            self.combo_action.setCurrentText("Run External .py Script (Entire File)")
            self.txt_script_path.setText(step["params"].get("script_path", ""))

    def on_step_moved(self, old_index, new_index):
        if not (0 <= old_index < len(self.processes[self.current_process])) or not (0 <= new_index < len(self.processes[self.current_process])):
            return
        step_list = self.processes[self.current_process]
        step = step_list.pop(old_index)
        step_list.insert(new_index, step)
        
        for i, s in enumerate(step_list): s["step_id"] = i + 1
        self.refresh_step_list()
        self.list_steps.setCurrentRow(new_index) 

    def update_selected_step(self):
        current_item = self.list_steps.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a step from the list to update.")
            return
            
        row_idx = self.list_steps.row(current_item)
        original_step = self.processes[self.current_process][row_idx]
        
        if original_step["action"] == "load_file":
            active_files = set()
            for proc in self.processes.values():
                for s in proc:
                    if s.get("action") == "load_file":
                        fp = s.get("params", {}).get("filepath")
                        if fp: active_files.add(fp)
            dialog = EditLoadDialog(original_step.get("params", {}), list(active_files), self)
            if dialog.exec_() == QDialog.Accepted:
                original_step["params"] = dialog.get_params()
                self.processes[self.current_process][row_idx] = original_step
                self.refresh_step_list()
            return
            
        new_step_data = self.get_editor_step_data()
        if new_step_data["action"] == "execute_python_logic" and not new_step_data["params"].get("code_block", "").strip():
            QMessageBox.warning(self, "Warning", "Code block is empty!")
            return
            
        new_step_data["step_id"] = original_step["step_id"]
        self.processes[self.current_process][row_idx] = new_step_data
        self.refresh_step_list()
        QMessageBox.information(self, "Success", "Step updated successfully. (Note: Run the pipeline to refresh the visual state)")

    def delete_step(self):
        current_item = self.list_steps.currentItem()
        if not current_item: return
        row_idx = self.list_steps.row(current_item)
        if QMessageBox.question(self, 'Delete', "Delete this step?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            del self.processes[self.current_process][row_idx]
            for i, step in enumerate(self.processes[self.current_process]): step["step_id"] = i + 1
            self.refresh_step_list()

    def run_full_restore(self, export_path=None):
        # Concurrency safety lock
        if hasattr(self, 'restore_worker') and self.restore_worker.isRunning():
            QMessageBox.warning(self, "Running", "Pipeline is currently executing. Please wait.")
            return
            
        if not any(self.processes.values()): return
        
        self.last_export_path = export_path
        self.terminal_output.append("\n>>> Restoring Pipeline Data...")
        self.restore_worker = PipelineRestoreWorker(self.processes)
        self.restore_worker.progress_update.connect(self.terminal_output.append)
        self.restore_worker.result_ready.connect(self.on_restore_success)
        self.restore_worker.error_occurred.connect(self.on_restore_error)
        self.restore_worker.start()

    def on_restore_success(self, dfs, vars):
        self.global_dfs, self.global_vars = dfs.copy(), vars.copy()
        self.preview_dfs, self.preview_vars = dfs.copy(), vars.copy()
        
        # UI Memory refresh
        self.update_tabs()
        self.terminal_output.append(">>> Success!")
        
        if hasattr(self, 'last_export_path') and self.last_export_path:
            self.terminal_output.append(f">>> Exporting results to: {self.last_export_path}")
            try:
                output_file = os.path.join(self.last_export_path, 'Final_Pipeline_Output.xlsx')
                with pd.ExcelWriter(output_file) as writer:
                    exported_count = 0
                    for alias, df in dfs.items():
                        if not self.export_dfs or alias in self.export_dfs:
                            df.to_excel(writer, sheet_name=str(alias)[:31], index=False)
                            exported_count += 1
                self.terminal_output.append(f">>> Export Complete: {exported_count} DataFrames saved.")
            except Exception as e:
                self.terminal_output.append(f">>> Export Error: {e}")
            self.last_export_path = None

    def on_restore_error(self, err):
        self.terminal_output.append(f">>> Error: {err}")

    def load_config_from_path(self, file_path):
        try:
            with open(file_path, 'r') as f: config = json.load(f)
            self.processes = config["processes"]
            self.export_dfs = config.get("export_dfs", [])
            self.current_config_path = file_path
            
            self.combo_processes.blockSignals(True)
            self.combo_processes.clear()
            for n in self.processes.keys(): self.combo_processes.addItem(n)
            self.current_process = list(self.processes.keys())[0]
            self.combo_processes.setCurrentText(self.current_process)
            self.combo_processes.blockSignals(False)
            
            self.refresh_step_list()
            self.update_tabs()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load config:\n{e}")

    def load_config(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Config", "Config", "JSON Files (*.json)")
        if file_path:
            self.load_config_from_path(file_path)
            if QMessageBox.question(self, 'Restore', "Run pipeline now?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                self.run_full_restore()

    def save_config(self):
        default_name = self.current_config_path or "Config/Master_Config.json"
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Pipeline", default_name, "JSON Files (*.json)")
        if file_path:
            config = {
                "pipeline_name": os.path.splitext(os.path.basename(file_path))[0], 
                "export_dfs": self.export_dfs, 
                "processes": self.processes
            }
            with open(file_path, 'w') as f: json.dump(config, f, indent=4)
            self.current_config_path = file_path
            self.setWindowTitle(f"Pipeline Editor - {os.path.basename(file_path)}")
            QMessageBox.information(self, "Saved", f"Saved to {file_path}.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScorecardUI()
    window.show()
    sys.exit(app.exec_())















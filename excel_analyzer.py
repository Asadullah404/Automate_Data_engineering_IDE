# ==============================================================================
# FILE LOCATION: AutomateFlow_Studio/excel_analyzer.py
# ==============================================================================

import os
import json
import pandas as pd
import numpy as np

try:
    import xlwings as xw
except ImportError:
    xw = None

class ExcelReverseEngineer:
    """
    Analyzes an existing Excel workbook and attempts to reconstruct it as a 
    AutomateFlow Pipeline.
    """

    def __init__(self, filepath):
        self.filepath = filepath
        if xw is None:
            raise ImportError("xlwings is required for Auto-Generation. Please run 'pip install xlwings'.")

    def find_header_row(self, sheet):
        """
        Heuristic to find the header row.
        Scans top 50 rows. The header is likely the row immediately 
        preceding the first large block of numeric/standard data, 
        or the row with the most distinct non-empty string values.
        """
        # Read the first 50 rows of the sheet
        used_range = sheet.used_range
        last_col = used_range.last_cell.column
        
        # Limit scan to 50 rows for performance
        max_scan = min(50, used_range.last_cell.row)
        data = sheet.range((1, 1), (max_scan, last_col)).options(ndim=2).value
        
        if not data:
            return 0
            
        best_row_idx = 0
        max_headers = 0
        
        for i, row in enumerate(data):
            if not any(row): continue
            
            # Count string values that look like headers
            header_count = sum(1 for cell in row if isinstance(cell, str) and len(cell.strip()) > 1)
            
            if header_count > max_headers:
                max_headers = header_count
                best_row_idx = i
                
        return best_row_idx

    def extract_column_formulas(self, sheet, header_idx):
        """
        Looks for column-wide formulas in the row immediately following the header.
        """
        # We look at the row immediately after the header (header_idx + 2 because Excel is 1-based and idx is 0-based)
        data_row_idx = header_idx + 2
        try:
            used_range = sheet.used_range
            last_col = used_range.last_cell.column
            
            # Read formulas and values for the first data row
            row_range = sheet.range((data_row_idx, 1), (data_row_idx, last_col))
            raw_formulas = row_range.options(ndim=2).formula
            
            # Standardize to a list of values for the row
            if raw_formulas and len(raw_formulas) > 0:
                row_data = list(raw_formulas[0])
            else:
                row_data = []
                
            # Get headers to know column names
            headers_raw = sheet.range((header_idx + 1, 1), (header_idx + 1, last_col)).options(ndim=2).value
            if headers_raw and len(headers_raw) > 0:
                headers = list(headers_raw[0])
            else:
                headers = []

            formulas = []
            for col_idx, formula in enumerate(row_data):
                if formula and str(formula).startswith('='):
                    # We found a formula!
                    target_alias = sheet.name
                    target_col = headers[col_idx] if col_idx < len(headers) else f"Column_{col_idx+1}"
                    is_external = '[' in str(formula) and ']' in str(formula)
                    
                    formulas.append({
                        "formula": formula,
                        "target_alias": target_alias,
                        "target_col": target_col,
                        "is_external": is_external
                    })
                    
            return formulas
        except Exception as e:
            print(f"Warning: Could not extract formulas for sheet {sheet.name}: {e}")
            return []

    def extract_pivot_tables(self, sheet):
        """
        Attempts to read PivotTable definitions and generate equivalent Pandas code.
        """
        pt_steps = []
        try:
            pts = sheet.api.PivotTables()
            for i in range(1, pts.Count + 1):
                try:
                    pt = pts.Item(i)
                    name = pt.Name
                    
                    # Try to extract the source sheet name from SourceData
                    source_r1c1 = str(pt.SourceData)
                    source_sheet = source_r1c1.split('!')[0].replace("'", "") if '!' in source_r1c1 else "UnknownSheet"
                    
                    row_fields = [f.Name for f in pt.RowFields]
                    col_fields = [f.Name for f in pt.ColumnFields]
                    data_fields = [f.Name for f in pt.DataFields]
                    
                    code = f"# Auto-generated Pandas replication for Pivot Table: {name}\n"
                    code += f"source_df = dfs_dict.get('{source_sheet}')\n"
                    code += "if source_df is not None:\n"
                    code += "    try:\n"
                    code += f"        pivot_result = pd.pivot_table(source_df, index={row_fields}, columns={col_fields}, values={data_fields}, aggfunc='sum')\n"
                    code += f"        dfs_dict['{name}'] = pivot_result.reset_index()\n"
                    code += "    except Exception as e:\n"
                    code += f"        print(f'Pivot Table translation error: {{e}}')\n"
                    
                    pt_steps.append({
                        "action": "execute_python_logic",
                        "params": {
                            "code_block": code
                        }
                    })
                except Exception as e:
                    print(f"Warning: Could not fully extract Pivot Table {i}: {e}")
        except:
            pass
        return pt_steps

    def detect_unsupported_features(self, sheet):
        """
        Checks for Pivot Tables (handled separately now), PowerQuery, etc.
        """
        unsupported = []
        try:
            # QueryTables often represent external data connections / PowerQuery
            qt_count = 0
            try: qt_count = sheet.api.QueryTables.Count
            except: pass
            
            # ListObjects often represent Excel Tables which might have PowerQuery sources
            lo_count = 0
            try: lo_count = sheet.api.ListObjects.Count
            except: pass

            if qt_count > 0 or lo_count > 0:
                unsupported.append(f"Sheet '{sheet.name}' contains External Data Connections or Excel Tables (PowerQuery).")
        except:
            pass
            
        return unsupported

    def analyze(self):
        """
        Main execution loop. Returns a pipeline dictionary.
        """
        app = xw.App(visible=False, add_book=False)
        pipeline = {
            "pipeline_name": os.path.splitext(os.path.basename(self.filepath))[0] + "_AutoGenerated",
            "export_dfs": [],
            "processes": {"Main_Process": []}
        }
        
        try:
            wb = app.books.open(self.filepath, read_only=True)
            steps = []
            total_formulas_found = 0
            has_external_links = False
            
            # Step 1: Load all sheets
            for sheet in wb.sheets:
                # Find header
                header_row = self.find_header_row(sheet)
                
                # Add Load Step
                steps.append({
                    "step_id": len(steps) + 1,
                    "action": "load_file",
                    "params": {
                        "filepath": self.filepath,
                        "sheet": sheet.name,
                        "header": header_row,
                        "alias": sheet.name,
                        "prompt_at_runtime": True # Usually best for autogenerated pipelines
                    }
                })
                pipeline["export_dfs"].append(sheet.name)
                
            # Step 2: Detect Formulas and Pivot Tables
            for sheet in wb.sheets:
                header_row = self.find_header_row(sheet)
                
                # Formulas
                col_formulas = self.extract_column_formulas(sheet, header_row)
                total_formulas_found += len(col_formulas)
                
                for f_data in col_formulas:
                    if f_data.get("is_external"):
                        has_external_links = True
                    steps.append({
                        "step_id": len(steps) + 1,
                        "action": "evaluate_excel_formula",
                        "params": {
                            "formula": f_data["formula"],
                            "target_alias": f_data["target_alias"],
                            "target_col": f_data["target_col"]
                        }
                    })
                
                # Pivot Tables Extraction
                pt_steps = self.extract_pivot_tables(sheet)
                for pt_step in pt_steps:
                    pt_step["step_id"] = len(steps) + 1
                    steps.append(pt_step)

                # Unsupported (Human Intervention)
                unsupported_msgs = self.detect_unsupported_features(sheet)
                for msg in unsupported_msgs:
                    steps.append({
                        "step_id": len(steps) + 1,
                        "action": "human_intervention_required",
                        "params": {
                            "message": msg
                        }
                    })
            
            if has_external_links:
                steps.append({
                    "step_id": len(steps) + 1,
                    "action": "human_intervention_required",
                    "params": {
                        "message": "This workbook contains formulas with external links (e.g. VLOOKUP to other files). You must load the external files explicitly in previous steps for these formulas to work."
                    }
                })

            if total_formulas_found == 0 and len(steps) == len(wb.sheets):
                raise ValueError("No Excel formulas or complex features were detected in this workbook. "
                                 "Auto-Generation requires at least one formula to reverse-engineer logic.")

            pipeline["processes"]["Main_Process"] = steps
            return pipeline
            
        finally:
            try:
                wb.close()
            except:
                pass
            try:
                app.quit()
                # Force kill if it hangs (common with COM)
                app.kill()
            except:
                pass

def analyze_workbook(filepath):
    engineer = ExcelReverseEngineer(filepath)
    return engineer.analyze()

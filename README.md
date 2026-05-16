# Dynamic Scorecard System & Audit IDE

<p align="center">
  <img src="assets/screenshot.png" alt="Dynamic Scorecard IDE Showcase" width="900">
</p>

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/platform-windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

A professional, high-performance "No-Code/Low-Code" automation platform for complex Excel-based audit workflows. This system transforms raw data into merge-ready audit scorecards using a hybrid engine that combines the speed of **Pandas** with the precision of native **Excel Formula Evaluation**.

---

## 🚀 Key Features

### 1. Extreme Performance ("VICE-VERSA" Engine)
*   **Multi-Threaded Pipelines:** Independent audit processes (e.g., Quiz, Attendance, Review) run **simultaneously** on separate CPU threads.
*   **Parallel Ingestion:** Batch loads all sheets from a workbook concurrently, resulting in a **3x to 5x speedup** for large datasets.
*   **Lazy Loading:** Utilizes `pd.ExcelFile` caching to minimize disk I/O during multi-step transformations.

### 2. Advanced Data Ingestion
*   **Batch Load Sheets:** Load an entire Excel workbook (dozens of tabs) into memory with a single click.
*   **Smart Mapping:** A dedicated UI tool for SQL-like **Left Joins**. Match columns across different DataFrames (e.g., matching by Employee ID) and selectively copy data.
*   **Path Resilience:** Automatically detects broken file paths and triggers a fallback prompt at runtime to prevent pipeline crashes.

### 3. Professional Audit IDE (UI/UX)
*   **Excel-Style Interaction:** Native filtering and sorting on every data tab with a high-contrast visual indicator system.
*   **Interactive Terminal:** A built-in Python REPL for real-time data manipulation and debugging during pipeline execution.
*   **Detachable Panels:** Fully flexible layout with detachable, floatable, and stackable docks (Explorer, Logic Designer, Console).
*   **World-Class Themes:** High-density **Matte Dark Mode** and **Paper Light Mode** optimized for long-duration data engineering.

---

## 🏗 System Architecture

The system follows an **In-Memory State Model** controlled by three core layers:

### A. The Engine (`dynamic_engine.py`)
*   **OmniEvaluator:** A sandboxed execution environment that allows running arbitrary Python/Pandas logic on live DataFrames.
*   **ExcelFormulaEngine:** Bridges to `xlwings` to evaluate 100% of native Excel formulas in a background instance—perfect for legacy logic that cannot be easily ported to Python.

### B. The UI (`scorecard_ui.py`)
*   A massive **PyQt5** application serving as the command center.
*   Handles configuration management, pipeline visualization, and provides "Floating Tooltips" for instant data feedback.

### C. The Schema (`Config/*.json`)
*   JSON-based pipeline definitions that map raw files to memory aliases and define the sequence of execution steps.

---

## 🛠 Installation

### Prerequisites
*   Python 3.10 or higher
*   Microsoft Excel (required only if using the Excel Formula Engine)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/dynamic-scorecard-system.git
   cd dynamic-scorecard-system
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 📖 Usage

### Running the App
```bash
python scorecard_ui.py
```

### Creating a Pipeline
1.  **Dashboard:** Create a new pipeline or select an existing JSON config.
2.  **Explorer:** Use "Load Source Data" or "Batch Load Sheets" to bring data into memory.
3.  **Logic Designer:**
    *   **Execute Python:** Write Pandas code like `df['Total'] = df['Price'] * 1.2`.
    *   **Excel Formula:** Enter formulas like `=SUM(Sheet1!A:A)` to run them through Excel.
    *   **Mapping:** Click "🔗 Map" to merge two tables based on a key column.
4.  **Run:** Click "🚀 RUN PIPELINE" to execute all threads in parallel.

---

## 📦 Packaging (Standalone .exe)

To create a portable version of the IDE that doesn't require Python installed:

1.  Run the build script:
    ```powershell
    python build_simple.py
    ```
2.  The standalone file will be generated at: `dist/DynamicScorecard.exe`.

*Note: Ensure the `Config` and `Custom_Scripts` folders are kept in the same directory as the .exe.*

---

## 🛡 License
Distributed under the MIT License. See `LICENSE` for more information.

## 👥 Authors
*   **Initial Analysis & Implementation:** Gemini CLI
*   **Architecture & Design:** [Your Name]

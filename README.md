# Calory Tracker

Calory Tracker is a beginner-friendly desktop nutrition tracker built with Python and Tkinter. It provides a modern app-style interface to log meals, monitor calorie goals, track macros, and review history without losing compatibility with the project's original file-based data.

## Features

- Modern desktop layout with header, sidebar navigation, and responsive main content area
- Dashboard with:
  - Today's calories
  - Remaining calories vs active goal
  - Macro totals (protein, carbs, fat)
  - Weekly calorie bar chart
- Log Entries screen:
  - Add, edit, delete meal entries
  - Friendly validation messages
  - Delete confirmation modal
  - Foods database calorie lookup (`foods.txt`)
- History screen:
  - Date range filtering (`YYYY-MM-DD`)
  - Text search over meal names and notes
  - Empty-state handling
- Settings screen:
  - Unit system (`metric` / `imperial`)
  - Daily/rest/workout goals
  - Active day type (rest/workout)
  - JSON data export
  - Sample data generation
- Keyboard shortcuts:
  - `Ctrl+1` Dashboard
  - `Ctrl+2` Log Entries
  - `Ctrl+3` History
  - `Ctrl+4` Settings
  - `Ctrl+N` Add meal
  - `Ctrl+R` Refresh views
- Backward-compatible persistence:
  - Keeps using `Users_Data/<username>.txt` files
  - Keeps using `foods.txt` meal catalog format

## Screenshots

Add screenshots to this section after running the app.

1. Save screenshots in a folder like `docs/screenshots/`
2. Update the markdown paths below

```md
![Dashboard](docs/screenshots/dashboard.png)
![Log Entries](docs/screenshots/log_entries.png)
![History](docs/screenshots/history.png)
![Settings](docs/screenshots/settings.png)
```

## Tech Stack

- Python 3.10+
- Tkinter + ttk (standard library)
- Dataclasses, pathlib, json, unittest

## Install and Run

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

Alternative module entry:

```bash
python -m calory_tracker
```

## Running Tests

```bash
python -m unittest discover -s tests
```

## Project Structure

```text
Calory Tracker/
├── calory_tracker/
│   ├── models/
│   │   ├── meal_entry.py
│   │   ├── settings.py
│   │   └── user_data.py
│   ├── services/
│   │   ├── calorie_service.py
│   │   ├── storage_service.py
│   │   └── user_service.py
│   ├── ui/
│   │   ├── theme.py
│   │   ├── main_window.py
│   │   └── views/
│   │       ├── dashboard_view.py
│   │       ├── log_view.py
│   │       ├── history_view.py
│   │       └── settings_view.py
│   └── __main__.py
├── Users_Data/
├── tests/
│   └── test_smoke.py
├── foods.txt
├── main.py
├── requirements.txt
├── README.md
└── LICENSE
```

## Roadmap

- Add charts for macro trends (weekly/monthly)
- Add meal templates and quick-add actions
- Add optional SQLite backend for larger datasets
- Add packaged desktop builds (Windows/macOS/Linux)
- Add richer automated UI tests

## License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE).

## Author

Seyedborna Boyafraz

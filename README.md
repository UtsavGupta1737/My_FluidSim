Ball Collision Simulation

Requirements
- Python 3.8+
- pygame (see requirements.txt)

Run

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/Scripts/activate    # Windows (bash)
pip install -r requirements.txt
python main.py
```

Controls
- Left click: add a random ball at the cursor
- Right click: remove nearest ball
- Space: pause/resume
 - Space: pause/resume

Notes
- The physics is approximate and uses simple elastic collision resolution with position correction.
- Data handling uses JSON for save/load and CSV for export.

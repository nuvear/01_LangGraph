"""Create readable printed overviews; detailed Mermaid flowcharts stay unchanged."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OVERVIEWS = {
    "p00": '''flowchart LR
A["Python + packages"] --> B["Local graph"] --> C["Public checks"] --> D["Local report"]
E["Separate API opt-in"] --> F["Remote proof"]
''',
    "l05": '''flowchart LR
A["Four inputs"] --> B{"Operation 1"}
B -->|"+ or -"| C["Pair 1 result"]
C --> D{"Operation 2"}
D -->|"+ or -"| E["Pair 2 result"]
E --> F["Keep both"]
''',
    "l07": '''flowchart LR
A["Read input"] --> B{"Send?"}
B -->|"Yes"| C["Fresh state"] --> D["Anthropic"] --> E["Show reply"]
E --> A
B -->|"Blank or exit"| F["Skip or stop"]
''',
    "l08": '''flowchart LR
A["New turn"] --> B["Full history"] --> C["Select prompt"] --> D["Anthropic"]
D --> E["Append reply"] --> B
E --> F["Text log"]
''',
    "l09": '''flowchart LR
A["Messages"] --> B{"Budget left?"}
B -->|"Yes"| C["Anthropic"]
C -->|"Tool calls"| D["ToolNode"] --> C
C -->|"Final answer"| E["End"]
B -->|"No"| F["Budget error"]
''',
    "l11": '''flowchart LR
A["PDF pages"] --> B["Page chunks"] --> C["Local vectors"]
C --> D["Retrieve"] --> E["Anthropic"] --> F["Cited answer"]
''',
    "u1": '''flowchart LR
A["Thread A or B"] --> B["Graph + model"]
B <--> C[("SQLite file")]
D["Close + reopen"] --> C
C --> E["Inspect snapshots"] --> B
''',
    "u2": '''flowchart LR
A["Thread draft"] --> B["Interrupt"] --> C{"Approve draft?"}
C -->|"Yes"| D["Safe new file"] --> E["Saved"]
C -->|"No or invalid"| F["No write"]
''',
    "s1": '''flowchart LR
A["Synthetic case"] --> B["Graph"] --> C["Reference checks"] --> D["Local report"]
B -.-> E["LangSmith trace"] -.-> F["Separate read-back"]
''',
    "s2": '''flowchart LR
A["Graph + tool"] --> B["Selected callbacks"] --> C["Service submission"]
D["Separate checker"] --> E["HTTP acknowledgment"]
C -.-> F["Inspect dashboard"]
''',
    "c01": '''flowchart LR
A["Request"] --> B["Retrieve"] --> C["Cited draft"] --> D{"Human review"}
D -->|"Revise once"| C
D -->|"Approve"| E["Safe new file"]
D -->|"Reject or error"| F["No save"]
''',
}

if __name__ == "__main__":
    folder = ROOT / "assets/diagrams/overviews"
    folder.mkdir(parents=True, exist_ok=True)
    for name, source in OVERVIEWS.items():
        (folder / f"{name}.mmd").write_text(source)
    print(f"Wrote {len(OVERVIEWS)} compact original overviews to {folder}")

"""Create standalone concept illustrations; no third-party visual assets are used."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIAGRAMS = {
    'l01': '''flowchart LR
A["TypedDict"] -.->|"Documents keys"| B["Input state"]
B --> C["Node function"] --> D["Partial update"]
B --> E["State merge"]
D --> E --> F["Next node"]
''',
    'l02': '''flowchart LR
A["Name input"] --> B["Greeting node"] --> C["Greeting result"]
D["Name input"] --> E["Compliment node"] --> F["Personalized result"]
''',
    'l03': '''flowchart LR
A["Name + integer list"] --> B["Validate inputs"] --> C["Calculate"]
C --> D["Formatted result"]
C -.-> E["Exercise: answer field"]
''',
    'l04': '''flowchart LR
A["Input fields"] --> B["Greeting"] --> C["Age update"] --> D["Skills update"] --> E["Final profile"]
A -.->|"Other fields remain"| E
''',
    'l05': '''flowchart LR
A["Operand pair 1"] --> C["Calculation 1"]
B["Operand pair 2"] --> D["Calculation 2"]
C -->|"Next step"| D
C --> E["Keep both results"]
D --> E
''',
    'l06': '''flowchart LR
A["Current state"] --> B["One work step"] --> C["Update progress"] --> D{"Continue?"}
D -->|"Budget remains"| A
D -->|"Goal or limit reached"| E["Stop safely"]
''',
    'l07': '''flowchart LR
A["First new message"] --> B["Fresh invocation 1"] --> C["Reply 1"]
D["Second new message"] --> E["Fresh invocation 2"] --> F["Reply 2"]
''',
    'l08': '''flowchart LR
A["Full transcript"] --> B["Select prompt"] --> C["Model context"] --> D["New reply"]
D -->|"Append"| A
A --> E["Plain-text log"]
''',
    'l09': '''flowchart LR
A["AI tool request"] --> B["Execute function"] --> C["Tool result"] --> D["Next model turn"]
A -.->|"call-1"| C
''',
    'l10': '''flowchart LR
A["Current draft"] --> B["Human feedback"] --> C["Revise draft"] --> A
B -->|"Save requested"| D["Safety guards"] --> E["New file"]
''',
    'l11': '''flowchart LR
A["PDF pages"] --> B["Chunks + page data"] --> C["Local vector index"] --> D["Retrieved evidence"]
Q["Question"] --> D
D --> E["Anthropic"] --> F["Grounded answer"]
''',
}

if __name__ == '__main__':
    folder = ROOT / 'assets/diagrams'
    folder.mkdir(parents=True, exist_ok=True)
    for ident, source in DIAGRAMS.items():
        (folder / f'{ident}-concept.mmd').write_text(source)
    print(f'Created {len(DIAGRAMS)} original concept diagram sources.')

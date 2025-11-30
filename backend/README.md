# Public Project

A simple Python project using Poetry for dependency management.

## Getting Started

Install dependencies:
```bash
poetry install
```

Run the project:
```bash
poetry run python main.py
```

## Dependencies

- requests
- pandas
- python-dotenv

## Development

To run tests:
```bash
poetry run pytest
```

To format code:
```bash
poetry run black .
```
graph TD
    subgraph LLM [extra LLM functionality]
        E(AI Service: Gemini/OpenAI API)
    end
    
    subgraph Τοπικό Docker Compose
        %% direction LR
        A["FastAPI Application Server (API/Logic/Calculations)"]
        D{PostgreSQL Database / Plain JSON}
    end


    subgraph Frontend Client
        F[Player/DM Browser]
        FRONT[Frontend UI / PLAYER & DM Application]
    end

    %% Ροή: Είσοδος του Request από τον Client
    F -- 1. opens url http://localhost:8000/welcome --> FRONT
    
    %% Ροή: API Request to Backend
    FRONT -- 2. API Request (http://localhost:8000/api/...) --> A
    
    %% Ροή: Λογική της Εφαρμογής & Δεδομένα
    A -- 3. CRUD Operations (Read/Write Char) --> D
    
    %% Ροή: Υπολογισμοί / AI Agent
    A -- 4. Needs Guide/Suggestion (Calculations) --> E
    E -- 5. Returns Result (Guide Text) --> A
    
    %% Ροή: Τελική Απόκριση
    A -- 6. Sends JSON Response (e.g., Final Character Sheet) --> FRONT
    
    %% Ροή: Εμφάνιση
    FRONT -- 7. Displays UI / Guide --> F
    
    %% Ορισμοί
    style A fill:#a2e,stroke:#333,stroke-width:2px
    style D fill:#3c3,stroke:#333,stroke-width:2px
    style E fill:#f99,stroke:#333,stroke-width:2px
    style FRONT fill:#fff8c2,stroke:#333,stroke-width:2px
    style F fill:#9ef,stroke:#333,stroke-width:2px
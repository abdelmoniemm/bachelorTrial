import requests
import tkinter as tk
from tkinter import scrolledtext

# GraphDB configuration
REPO_ID = "bachelor2025"
GRAPHDB_URL = f"http://localhost:7200/repositories/{REPO_ID}"

# SPARQL queries
QUERIES = {
    "Lowest score rule": """
        PREFIX ex: <http://example.org/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        SELECT ?rule ?score
        WHERE {
          {
            SELECT (MIN(xsd:decimal(?s)) AS ?minScore)
            WHERE {
              ?r a ex:DQRule ;
                 ex:score ?s .
            }
          }
          ?rule a ex:DQRule ;
                ex:score ?score .
          FILTER (xsd:decimal(?score) = ?minScore)
        }
    """,
    "All rules and scores": """
        PREFIX ex: <http://example.org/>
        SELECT ?rule ?score
        WHERE {
          ?rule a ex:DQRule ;
                ex:score ?score .
        }
    """,
    "Rules with score > 0.5": """
        PREFIX ex: <http://example.org/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        SELECT ?rule ?score
        WHERE {
          ?rule a ex:DQRule ;
                ex:score ?score .
          FILTER(xsd:decimal(?score) > 0.5)
        }
    """,
    "Average score per database": """
        PREFIX ex: <http://example.org/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        SELECT ?database (AVG(xsd:decimal(?score)) AS ?avgScore)
        WHERE {
          ?rule a ex:DQRule ;
                ex:techSystem ?database ;
                ex:score ?score .
        }
        GROUP BY ?database
        ORDER BY ASC(?avgScore)
    """,
    "Average score per schema": """
        PREFIX ex: <http://example.org/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        SELECT ?schema (AVG(?score) AS ?avgScore)
        WHERE {
          ?rule a ex:DQRule ;
                ex:techGroup ?schema ;
                ex:score ?score .
        }
        GROUP BY ?schema
        ORDER BY ASC(?avgScore)
    """
}

# Function to execute a SPARQL query
def run_query(query):
    response = requests.post(
        GRAPHDB_URL,
        data={"query": query},
        headers={"Accept": "application/sparql-results+json"}
    )
    result_text.delete("1.0", tk.END)

    if response.status_code == 200:
        data = response.json()["results"]["bindings"]
        if not data:
            result_text.insert(tk.END, "No results found.\n")
        else:
            for row in data:
                line = ", ".join(f"{k}: {v['value']}" for k, v in row.items())
                result_text.insert(tk.END, line + "\n")
    else:
        result_text.insert(tk.END, f"❌ Query failed: {response.status_code}\n")
        result_text.insert(tk.END, response.text)

# GUI setup
window = tk.Tk()
window.title("GraphDB SPARQL Interface")

# Button area
button_frame = tk.Frame(window)
button_frame.pack(pady=10)

for label, sparql in QUERIES.items():
    b = tk.Button(button_frame, text=label, width=30, command=lambda q=sparql: run_query(q))
    b.pack(pady=2)

# Results area
result_text = scrolledtext.ScrolledText(window, width=80, height=20)
result_text.pack(padx=10, pady=10)

# Start GUI event loop
window.mainloop()

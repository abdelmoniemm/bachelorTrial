import subprocess

# Define your local folder path
local_path = "C:/Users/Dell/Bachelorproject"

# Docker command 1: YARRRML to RML (rules.yml ➜ rules.rml.ttl)
yarrrml_to_rml = [
    "docker", "run", "--rm", "-it",
    "-v", f"{local_path}:/data",
    "rmlio/yarrrml-parser:1.10.0",
    "-i", "/data/rules.yml",
    "-o", "/data/rules.rml.ttl"
]

# Docker command 2: RML to RDF output (rules.rml.ttl ➜ output.ttl)
rml_to_rdf = [
    "docker", "run", "--rm", "-it",
    "-v", f"{local_path}:/data",
    "rmlio/rmlmapper-java:v7.3.3",
    "-m", "/data/rules.rml.ttl",
    "-o", "/data/output.ttl"
]

# Run commands
print("🔄 Converting YARRRML to RML...")
subprocess.run(yarrrml_to_rml, check=True)

print("✅ rules.rml.ttl generated!")

print("🔄 Generating RDF output...")
subprocess.run(rml_to_rdf, check=True)

print("✅ output.ttl generated successfully!")

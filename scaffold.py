import os
import subprocess

def run_cmd(cmd, cwd="."):
    subprocess.run(cmd, shell=True, cwd=cwd, check=True)

base_dir = r"c:\Users\Haritha\OneDrive\Desktop\Study-APP\Backend"

folders_to_create = [
    "app",
    "app/api",
    "app/api/v1",
    "app/core",
    "app/schemas",
    "app/services",
    "app/services/rag",
    "app/models",
    "app/db",
    "tests"
]

files_to_create = {
    "app/__init__.py": "",
    "app/config.py": "",
    "app/api/__init__.py": "",
    "app/api/v1/__init__.py": "",
    "app/api/v1/router.py": "",
    "app/api/v1/extract.py": "",
    "app/api/v1/generation.py": "",
    "app/api/v1/quiz.py": "",
    "app/api/v1/tutor.py": "",
    "app/api/v1/export.py": "",
    "app/core/__init__.py": "",
    "app/core/security.py": "",
    "app/core/constants.py": "",
    "app/core/exceptions.py": "",
    "app/schemas/__init__.py": "",
    "app/schemas/input.py": "",
    "app/schemas/studypack.py": "",
    "app/schemas/quiz.py": "",
    "app/schemas/tutor.py": "",
    "app/schemas/dashboard.py": "",
    "app/services/__init__.py": "",
    "app/services/pdf_parser.py": "",
    "app/services/progressive_quiz.py": "",
    "app/services/analytics_engine.py": "",
    "app/services/sequencing_engine.py": "",
    "app/services/revision_engine.py": "",
    "app/services/pdf_exporter.py": "",
    "app/services/csv_exporter.py": "",
    "app/services/rag/__init__.py": "",
    "app/services/rag/chunker.py": "",
    "app/services/rag/embedder.py": "",
    "app/services/rag/vector_store.py": "",
    "app/services/rag/retriever.py": "",
    "app/models/__init__.py": "",
    "app/models/user.py": "",
    "app/models/studypack.py": "",
    "app/models/attempt.py": "",
    "app/db/__init__.py": "",
    "app/db/session.py": "",
    "app/db/base.py": "",
    "tests/test_pdf_parser.py": "",
    "tests/test_ai_pipeline.py": "",
    "tests/test_rag_retriever.py": "",
    "tests/test_analytics.py": "",
    "Dockerfile": "",
    ".env.example": ""
}

# Create folders and their __init__.py files first so git can track them
for folder in folders_to_create:
    folder_path = os.path.join(base_dir, folder)
    os.makedirs(folder_path, exist_ok=True)
    # create __init__.py to ensure git tracks it
    init_path = os.path.join(folder_path, "__init__.py")
    if not os.path.exists(init_path):
        open(init_path, 'w').close()
    
    # commit this folder
    run_cmd(f"git add Backend/{folder}", cwd=r"c:\Users\Haritha\OneDrive\Desktop\Study-APP")
    run_cmd(f'git commit -m "feat(arch): setup {folder} module directory structure"', cwd=r"c:\Users\Haritha\OneDrive\Desktop\Study-APP")

# Create the rest of the files
for file_rel, content in files_to_create.items():
    file_path = os.path.join(base_dir, file_rel)
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write(content)

# Move the existing files to their new locations
import shutil

existing_mappings = {
    "main.py": "app/main.py",
    "schemas.py": "app/schemas/studypack.py",
    "ai_pipeline.py": "app/services/ai_pipeline.py",
    "mcp_client.py": "app/services/mcp_client.py" # Assuming mcp client goes to services
}

for src, dst in existing_mappings.items():
    src_path = os.path.join(base_dir, src)
    dst_path = os.path.join(base_dir, dst)
    if os.path.exists(src_path):
        shutil.move(src_path, dst_path)

# Commit the remaining files and relocations
run_cmd("git add Backend", cwd=r"c:\Users\Haritha\OneDrive\Desktop\Study-APP")
run_cmd('git commit -m "feat(arch): populate structured backend files and relocate existing code"', cwd=r"c:\Users\Haritha\OneDrive\Desktop\Study-APP")

print("Scaffolding complete!")

import sqlite3
import os
import argparse
from enum import Enum
from dotenv import load_dotenv

class SQL_STATEMENTS(Enum):
    clear_experiment_tags = """DELETE FROM experiment_tags WHERE experiment_id IN (
        SELECT experiment_id FROM experiments where lifecycle_stage='deleted'
    );"""

    clear_latest_metrics = """DELETE FROM latest_metrics WHERE run_uuid IN (
        SELECT run_uuid FROM runs WHERE experiment_id IN (
            SELECT experiment_id FROM experiments where lifecycle_stage='deleted'
        )
    );"""

    clear_metrics = """DELETE FROM metrics WHERE run_uuid IN (
        SELECT run_uuid FROM runs WHERE experiment_id IN (
            SELECT experiment_id FROM experiments where lifecycle_stage='deleted'
        )
    );"""

    clear_tags = """DELETE FROM tags WHERE run_uuid IN (
        SELECT run_uuid FROM runs WHERE experiment_id IN (
            SELECT experiment_id FROM experiments where lifecycle_stage='deleted'
        )
    );"""

    clear_runs = """DELETE FROM runs WHERE experiment_id IN (
        SELECT experiment_id FROM experiments where lifecycle_stage='deleted'
    );"""

    clear_experiments = "DELETE FROM experiments where lifecycle_stage='deleted';"

    list_experiments = "SELECT name, lifecycle_stage FROM experiments"

def purge_experiments():
    # Clear the experiment_tags table
    cursor.execute(SQL_STATEMENTS.clear_experiment_tags.value)

    # Clear the latest_metrics table
    cursor.execute(SQL_STATEMENTS.clear_latest_metrics.value)

    # Clear the metrics table
    cursor.execute(SQL_STATEMENTS.clear_metrics.value)

    # Clear the tags table
    cursor.execute(SQL_STATEMENTS.clear_tags.value)

    # Clear the runs table
    cursor.execute(SQL_STATEMENTS.clear_runs.value)

    # Clear the experiments table
    cursor.execute(SQL_STATEMENTS.clear_experiments.value)


    # Commit the changes and close the connection
    conn.commit()

def list_experiments():
    # Execute the SQL statement to get all experiment names
    cursor.execute(SQL_STATEMENTS.list_experiments.value)

    # Fetch all rows
    rows = cursor.fetchall()

    # Print the rows
    for row in rows:
        print(row)

def main(action):

    if "list_experiments" in action:
        list_experiments()
    if "purge_experiments" in action:
        purge_experiments()

if __name__ == "__main__":

    if os.path.exists(".env"):
        print("Arquivo .env encontrado, carregando variáveis.")
        # Load environment variables from .env file
        load_dotenv()
    else:
        print("Usando variáveis de ambiente do sistema, ou valores padrão.")

    db_path = os.getenv("DB_PATH", 'infra/volumes/mlflow/sqlite/mlflow.db')

    # Connect to your SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--action",
        nargs="+",
        default=[
            "list_experiments",
            "purge_experiments",
        ],
    )
    args = parser.parse_args()
    main(args.action)

    conn.close()
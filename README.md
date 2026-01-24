# AnalyticsAI

This project implements a **LangGraph-based multi-agent workflow** that takes structured (files / databases), understands user intent, generates SQL queries, executes analytics, creates visualizations, and finally produces **natural-language summaries and reports**.

---

## High-Level Workflow

![Workflow Diagram](workflow.png)

At a high level, the system follows this flow:

1. **Input Understanding** – Classifies the uploaded file or user query
2. **Data Ingestion** – Loads data into a database (SQLite/Postgres)
3. **Schema Discovery** – Extracts tables & relationships
4. **Planning Agent** – Decides what actions are needed (SQL, charts, summaries)
5. **SQL Agent** – Generates, verifies, and executes SQL queries
6. **Decision Node** – Routes output to charts, summaries, or reports
7. **Chart Agent** – Creates visualizations when required
8. **Summarization Agent** – Converts results into human-readable insights
9. **Report Agent** – Generates a structured report and optional PDF
10. **Chat Interface** – Allows conversational interaction at any point

---

## Core Components

### 1. Classify File (`classify_file`)

* Detects input type (CSV, SQL DB, query, etc.)
* Determines whether ingestion or querying is required

---

### 2. Insert Node (`insert_node`)

* Loads files (CSV / Excel) into SQLite or Postgres
* Normalizes schema if required

---

### 3. Schema Extraction (`get_schema`)

* Retrieves full database schema
* Includes:

  * Tables
  * Columns
  * Data types
  * Relationships (foreign keys)

* Then preprocess the schema into a text

Used downstream by the planner and SQL agent.

```
TABLE: sem1_marks
  - roll_no (character varying)
  - student_name (character varying)
  - maths (integer)
  - physics (integer)
  - chemistry (integer)
  - english (integer)

TABLE: sem2_marks
  - roll_no (character varying)
  - student_name (character varying)
  - data_structures (integer)
  - databases (integer)
  - operating_systems (integer)
  - computer_networks (integer)
```

---

### 4. Planner Agent (`planner`)

* Brain of the system 
* Converts user intent into a **structured execution plan**
* Example plan:

```json
{
  "create_sql_query": "Retrieve a list of each student's marks in sem1 by unpivoting the maths, physics, chemistry, and english columns into rows with columns roll_no, student_name, subject, and mark.",
  "verify_sql_query": "Inspect the constructed SQL for syntax errors, proper column references (student_name, maths, physics, chemistry, english), correct arithmetic aggregation, and ensure no unsafe operations. Confirm that the query will return one row per student with exactly the two specified columns.",
  "execute_sql_query": "Run the verified SQL query against the database. Expected output: a table with one row for each student in sem1_marks, containing the columns student_name and total_marks (e.g., 120 rows if 120 students). This result set will be used as the data source for the bar chart.",
  "create_charts": "Generate code for a vertical single‑series bar chart using the executed query result. Chart specifications: • Type: bar chart • X‑axis: student_name (categorical, displayed as readable labels, possibly rotated for many students) • Y‑axis: total_marks (numeric) • Title: \"Total Marks of Students – Semester 1\" • Axis labels: X – \"Student Name\", Y – \"Total Marks\" • Color theme: a single, contrasting color for all bars (e.g., #4A90E2) • Legend: not required (single series) • Output: save chart image to './assets/sem1_total_marks_bar.png' and return the file path.",
  "execute_chart_code": "Execute the chart generation code to produce the bar chart image as specified, ensuring the image file is created at the designated path and is accessible for downstream use.",
  "summarize_with_llm": "Provide a concise summary of the semester‑1 total marks distribution: highlight the number of students, the highest and lowest total marks, and any notable patterns (e.g., range, average). Include a reference to the generated chart image path './assets/sem1_total_marks_bar.png' so the user can view the visual representation."
}
```

---

### 5. SQL Agent (Subgraph)

A dedicated subgraph responsible for **safe and correct SQL execution**.

**Flow:**

* `create_sql_query`
* `verify_sql_query`
* `execute_sql_query`

This separation prevents hallucinated or invalid SQL.

```sql
SELECT
    s.roll_no,
    s.student_name,
    v.subject,
    v.mark
FROM
    sem1_marks AS s
CROSS JOIN LATERAL
    (VALUES
        ('maths',      s.maths),
        ('physics',    s.physics),
        ('chemistry',  s.chemistry),
        ('english',    s.english)
    ) AS v(subject, mark);
```

`verify_sql_query` will conduct four checks:
- Table name checks(Manual)
- Column name checks(Manual)
- Intent checks(LLM)
- Syntax checks(LLM)

and this feedback loop happens for a maximum of 2 times

---


### 6. Chart Agent (Subgraph)

Responsible for:

* Generating chart specifications
* Executing chart code
* Returning visual outputs

Nodes:

* `create_charts`
* `execute_chart_code`

![Chart Diagram](./saved_graphs/Total_Marks_Bar_Chart_20260119_170312.jpg)

---

### 7. Summarization Agent (`summarize_with_llm`)

* Converts raw SQL / chart outputs into insights
* Produces executive-friendly explanations

---

### 8. Report Generation Agent (Subgraph)

Creates a polished report pipeline:

Nodes:

* `report_planner`
* `generate_summaries`
* `generate_report`
* `md_to_pdf`

[Report summary](report.md)

---

### 9. Chat Node (`chat`)

* Allows conversational Q&A
* Can be triggered at any stage
* Uses shared graph memory

---
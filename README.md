### Project Overview

[cite_start]The **Network Recommender** is a lightweight AI system designed to suggest professional connections based on shared institutions, activities, and social graphs[cite: 3]. [cite_start]It processes structured profiles and unstructured bios to identify relationships, leveraging multiple data sources and AI logic to generate personalized recommendations[cite: 4]. [cite_start]This project was built as part of a 10-day beginner-friendly enterprise project[cite: 2].

**Note**: All data used in this project, including user profiles and bios, is **dummy data** for demonstration purposes only. No real or personal information was used.

---

### Features & Technologies

[cite_start]This system provides a multi-modal person lookup using a hybrid AI approach[cite: 74, 89]. The core functionalities and technologies include:

* [cite_start]**Data Ingestion**: Structured user data is loaded into **DuckDB** from CSV files[cite: 12, 21]. [cite_start]Unstructured bios and LinkedIn texts are parsed for further processing[cite: 37, 38].
* [cite_start]**Semantic Search**: Unstructured bios are converted into searchable vectors using **Sentence Transformers** and indexed in a **Qdrant** vector database[cite: 13, 51, 52].
* [cite_start]**Graph Relationships**: A social and organizational graph is built using **Neo4j** to represent connections based on shared schools, workplaces, and other affiliations[cite: 14, 62, 63].
* [cite_start]**Intelligent Routing**: A **LangChain** agent intelligently routes queries to the most appropriate retrieval tool (SQL, Vector, or Graph) based on the user's request[cite: 16, 82, 83, 85].
* [cite_start]**User Interface**: A front-end interface built with **Streamlit** allows users to view ranked recommendations and see how they are related[cite: 15, 90, 96].
* [cite_start]**Feedback System**: Users can provide feedback on recommendations through a simple rating system, which is logged for potential future use[cite: 99, 100, 104].

---

### Setup and Usage

#### Prerequisites

* [cite_start]**Python**: The main programming language for the project[cite: 11].
* **Dependencies**: You will need to install the libraries listed in the `requirements.txt` file.

#### Installation

1.  **Clone the repository**:
    ```bash
    git clone [https://github.com/your-username/network-recommender.git](https://github.com/your-username/network-recommender.git)
    cd network-recommender
    ```

2.  **Set up the Python environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

#### Running the Application

To start the Streamlit UI, navigate to the project's root directory and run the following command:

```bash
streamlit run ui/app.py

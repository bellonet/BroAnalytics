## BroAnalytics

A personal sports and workout dashboard built with Dash and Plotly to visualize training data sourced directly from a Google Sheet.

### 🏃 Features

* KPI Tracking: Displays key performance indicators like Total Days worked out, Total Reps, Total Tonnage (in tonnes), Total Distance (km), and Total Time (hours/minutes).

* Sport-Specific Deep Dive: Allows filtering to analyze a single sport, showing Volume Load (for lifting), Distance vs. Duration (for running/biking), or simple Duration logs.

* Responsive Filtering: Filters data by date range and specific sports in the sidebar.

* Live Data Connection: Reads directly from a published Google Sheet URL—no database required.

### 🚀 How to Use with Your Own Data

You don't need a database - just a Google Sheet.

#### 1. Create your Google Sheet

Create a Google Sheet. It can be multi-tab as the app reads **all** tabs automatically.

Ensure your columns have these headers (order doesn't matter, case-insensitive):

| Column Name | Data Type | Description                             |
| :--- | :--- |:----------------------------------------|
| **Date** | Date | DD/MM/YYYY                              |
| **Activity** | Text | e.g., "Bench Press", "Running", "Squat" |
| **Duration** | Text | e.g., "1h", "45m", "20s"                |
| **Length** | Text/Number | e.g., "5km", "1000m", or just `5`       |
| **Sets** | Number |                                         |
| **Reps** | Number |                                         |
| **Weight** | Number |                                         |

Of course not all fields are required for every activity. For example, running won't have Sets/Reps/Weight.

#### 2. Publish to Web
1.  In Google Sheets, go to **File > Share > Publish to web**.
2.  Under "Link", select **Entire Document** (not just one sheet) and **Microsoft Excel (.xlsx)**.
3.  Click **Publish** and copy the link.

#### 3. Configure and run the dashboard

Open `main.py` and paste your link into the `DATA_SOURCE` variable.

Install dependencies (in a virtual environment):

```
pip install -r requirements.txt
```

And run the app:

```
python main.py
```

### TODO

* Add sport specific KPIs
* Prettify deep dive section
* Clean code
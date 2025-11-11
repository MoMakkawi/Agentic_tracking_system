# data_pipeline

[![PyPI - Version](https://img.shields.io/pypi/v/data-pipeline.svg)](https://pypi.org/project/data-pipeline)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/data-pipeline.svg)](https://pypi.org/project/data-pipeline)

-----

## Table of Contents

- [Overview](#overview)
- [Data Pipeline Agent](#data-pipeline-agent)
- [Tools and Functionalities](#tools-and-functionalities)
- [Workflow](#workflow)
- [Installation](#installation)
- [License](#license)

## Overview

`data_pipeline` is the foundational component of the Agentic Tracking System.  
It provides automated data ingestion, preprocessing, and grouping through modular agents and toolsets, enabling accurate analysis and flexible downstream integration for student/session tracking.

## Data Pipeline Agent

The **Data Pipeline Agent** manages the lifecycle of attendance or activity datasets, operating in `data_pipeline/src/agent/`.  
It automates the early stages of tracking and analysis by invoking a sequence of specialized tools.

## Tools and Functionalities

### fetch_tool
- Downloads raw data from configured sources (URL, path, database).
- Saves the data to disk or designated cloud storage.
- Handles errors in connectivity or data retrieval, logging issues for transparency.

### preprocess_tool
- Cleans and structures raw sessions into standardized formats.
- Parses timestamps and verifies device/student identity attributes.
- Filters redundant or malformed records.
- Outputs validated session objects for analysis.

### group_tool
- Analyzes sessions to identify and group students or users by attendance/activity.
- Uses configured rules to organize and name groups.
- Saves groupings for further processing or reporting.

## Workflow

1. **Fetch**: Acquire the raw dataset using `fetch_tool`.
2. **Preprocess**: Clean and normalize the collected data with `preprocess_tool`.
3. **Group**: Organize and classify participants via `group_tool`.

Steps are executed sequentially; any error halts the workflow to ensure consistency.  
The agent provides data summaries, grouping statistics, and preprocessing insights on completion.

## Installation

```console
pip install data-pipeline
```

## License

`data-pipeline` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

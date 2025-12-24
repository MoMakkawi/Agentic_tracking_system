# data_validation

[![PyPI - Version](https://img.shields.io/pypi/v/data-validation.svg)](https://pypi.org/project/data-validation)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/data-validation.svg)](https://pypi.org/project/data-validation)

-----

## Table of Contents

- [Overview](#overview)
- [Data Validation Agent](#data-validation-agent)
- [Tools and Functionalities](#tools-and-functionalities)
- [Usage and Workflow](#usage-and-workflow)
- [Installation](#installation)
- [License](#license)

## Overview

`data_validation` is a core module of the Agentic Tracking System, providing robust automated validation processes for session, device, timestamp, and identity data. It is designed to ensure data integrity and consistency before analytics or reporting.

## Data Validation Agent

The **Data Validation Agent** (located in `data_validation/src/agent/`) offers a suite of independent validation tools.  
Each tool can be executed individually in any order according to the user's needs—there is no required sequential workflow.

## Tools and Functionalities

### device_validation_tool
- Validates device information within session data.
- Checks device consistency across all sessions.
- Verifies that device records align with stored configurations.

### timestamp_validation_tool
- Ensures all timestamps have correct format and logical consistency.
- Checks the chronological ordering of sessions.
- Detects and flags invalid or anomalous timestamps.

### identity_validation_tool
- Validates student or user identity data in the dataset.
- Verifies identity consistency across multiple sessions.
- Checks identities against stored or expected records.
- Flags duplicate, missing, or conflicting identity entries.

## Usage and Workflow

All validation tools are independent:  
- **You can execute any tool or combination of tools based on your validation requirements.**
- There is **no mandatory execution order**; run only what you need for your use case.
- After running one or more tools, a validation results summary will be provided, highlighting any errors, anomalies, or flagged inconsistencies.

## Installation

```console
pip install data-validation
```

## License

`data-validation` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

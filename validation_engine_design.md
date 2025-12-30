Issue 10: Dataset Validation Engine - Phase 1 Design


​1. Project Summary


The Validation Engine is designed to test incoming data against predefined schemas. Its role is to detect invalid fields, flag malformed records, and ensure only high-quality data enters the pipeline.


​2. Key Requirements


The engine will perform the following core functions:




​Schema Parsing: Reading JSON/YAML definitions to understand the required data structure.


​Field Rule Validation: Checking each record to ensure it follows specific rules (e.g., "Age" must be a number).


​Error Flagging: Automatically marking incomplete or malformed records for review.


​Detailed Reporting: Generating a summary of which records passed and which failed.




​3. Logical Workflow (Pseudo-Code)


The validation process follows this logic:


# Step 1: Load the Schema (the "Rules" file)
# Step 2: Scan each row in the dataset
# Step 3: Check if required fields are missing
# Step 4: Validate data types (Text vs Numbers)
# Step 5: If a row is "Malformed," add it to the "Failure Report"
# Step 6: Output the final validation report

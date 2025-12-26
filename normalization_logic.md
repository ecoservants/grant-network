 Dataset Normalization Framework - Phase 1 Design


​1. Objective


The goal of this project is to build a standard system (framework) that takes raw, messy data from different sources and cleans it into a single, organized format used by the Grant Network.


​2. Core Features (Shared Utilities)


To ensure high data quality, the framework will perform these automated steps:




​Data Cleaning: Automatically removes empty rows and fixes spacing issues in text.


​Field Mapping: Matches labels from outside files to our internal system labels (e.g., changing "UserID" to "universal_id").


​Validation: Checks that dates are in the correct format (YYYY-MM-DD) and ensures numbers are valid.


​Error Reporting: Identifies and logs any data that doesn't fit the rules so it can be fixed later.




​3. Logical Workflow (Pseudo-Code)


The following logic defines how the Python backend will handle the data:


class BaseNormalizer:
    def __init__(self, raw_dataset):
        self.data = raw_dataset

    def execute_cleaning_pipeline(self):
        # Removal of duplicate entries and null record handling
        self.data = self.data.drop_duplicates().dropna(how='all')
        # String standardization: Trimming and case normalization
        self.data = self.data.apply(lambda x: x.str.strip().lower() if x.dtype == "object" else x)
        return self.data

    def validate_schema_integrity(self, mandatory_fields):
        # Verification of required data fields before processing
        for field in mandatory_fields:
            if field not in self.data.columns:
                self.report_error(f"Missing Field: {field}")
        return True

    def report_error(self, message):
        # Internal error logging for failed validation attempts
        print(f"[Normalization Error]: {message}")
# Step 1: Load the raw dataset
# Step 2: Run "Clean" utility to remove duplicates and empty fields
# Step 3: Run "Mapping" utility to rename headers to internal standards
# Step 4: Run "Validation" utility to check date and number formats
# Step 5: Save the clean data as a standardized file (CSV/JSON)
4. Scalability




​Plug-in Handlers: The system is designed to support "Plug-in" modules, allowing us to add new types of data sources in the future without changing the main code.


​Performance: The logic is optimized to handle large datasets quickly and accurately.




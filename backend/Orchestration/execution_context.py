"""
execution_context.py

Shared context that carries data across the complete
loan processing workflow.
"""


class ExecutionContext:
    def __init__(self):
        # Original user request
        self.request = {}

        # Customer Information
        self.customer = {}

        # Loan Information
        self.loan = {}

        # Agent Outputs
        self.sales_result = None
        self.verification_result = None
        self.underwriting_result = None
        self.sanction_result = None

        # Workflow Metadata
        self.metadata = {}

    # ----------------------------
    # Request
    # ----------------------------

    def set_request(self, request: dict):
        self.request = request

    # ----------------------------
    # Customer
    # ----------------------------

    def set_customer(self, customer: dict):
        self.customer = customer

    # ----------------------------
    # Loan
    # ----------------------------

    def set_loan(self, loan: dict):
        self.loan = loan

    # ----------------------------
    # Agent Outputs
    # ----------------------------

    def set_sales_result(self, result):
        self.sales_result = result

    def set_verification_result(self, result):
        self.verification_result = result

    def set_underwriting_result(self, result):
        self.underwriting_result = result

    def set_sanction_result(self, result):
        self.sanction_result = result

    # ----------------------------
    # Metadata
    # ----------------------------

    def add_metadata(self, key, value):
        self.metadata[key] = value

    # ----------------------------
    # Export Complete Context
    # ----------------------------

    def to_dict(self):
        return {
            "request": self.request,
            "customer": self.customer,
            "loan": self.loan,
            "sales_result": self.sales_result,
            "verification_result": self.verification_result,
            "underwriting_result": self.underwriting_result,
            "sanction_result": self.sanction_result,
            "metadata": self.metadata,
        }
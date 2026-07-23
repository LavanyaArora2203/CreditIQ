from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

router = APIRouter(tags=["CRM"])

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CUSTOMERS_PATH = DATA_DIR / "customer_data.json"
KYC_PATH = DATA_DIR / "kyc_data.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


# Unwrap the top-level envelope once, at import time
customers = load_json(CUSTOMERS_PATH)["customers"]      # -> list[dict]
kyc_records = load_json(KYC_PATH)["kyc_records"]         # -> dict[customer_id -> record]


@router.get("/")
def root():
    return {"service": "CRM API", "status": "running"}


@router.get("/customer/{customer_id}")
def get_customer(customer_id: str):
    logger.info(f"Searching customer {customer_id}")

    for customer in customers:
        if customer["customer_id"] == customer_id:   # snake_case key, matches real data
            logger.info("Customer found")
            return customer

    logger.warning("Customer not found")
    raise HTTPException(status_code=404, detail="Customer not found")


@router.get("/kyc/{customer_id}")
def get_customer_kyc(customer_id: str):
    logger.info(f"Searching KYC info for customer {customer_id}")

    record = kyc_records.get(customer_id)
    if record:
        logger.info("KYC found")
        return record

    logger.warning("KYC not found")
    raise HTTPException(status_code=404, detail="KYC not found")




# from fastapi import FastAPI, HTTPException
# from pathlib import Path
# import json
# import logging

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s %(levelname)s %(message)s"
# )

# logger = logging.getLogger(__name__)

# from fastapi import APIRouter

# router = APIRouter(
#     tags=["CRM"]
# )
# from pathlib import Path
# import json

# DATA_DIR = (
#     Path(__file__)
#     .resolve()
#     .parent.parent
#     / "data"
# )

# CUSTOMERS_PATH = DATA_DIR / "customer_data.json"
# KYC_PATH = DATA_DIR / "kyc_data.json"


# def load_json(path):
#     with open(path, "r", encoding="utf-8") as file:
#         return json.load(file)


# customers = load_json(CUSTOMERS_PATH)["customers"]
# kyc_records = load_json(KYC_PATH)["kyc_records"] 


# @router.get("/")
# def root():
#     return {
#         "service": "CRM API",
#         "status": "running"
#     }

# @router.get("/customer/{customer_id}")
# def get_customer(customer_id: str):

#     logger.info(f"Searching customer {customer_id}")

#     for customer in customers:

#         if customer["Customer ID"] == customer_id:

#             logger.info("Customer found")

#             return customer

#     logger.warning("Customer not found")

#     raise HTTPException(
#         status_code=404,
#         detail="Customer not found"
#     )


# @router.get("/kyc/{customer_id}")
# def get_customer_kyc(customer_id: str):

#     logger.info(f"Searching KYC info for customer {customer_id}")

#     record = kyc_records.get(customer_id)

#     if record:

#         logger.info("KYC found")

#         return record

#     logger.warning("KYC not found")

#     raise HTTPException(
#         status_code=404,
#         detail="KYC not found"
#     )
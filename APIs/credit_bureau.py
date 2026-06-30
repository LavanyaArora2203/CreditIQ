from fastapi import FastAPI, HTTPException
from pathlib import Path
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mock Credit Bureau API",
    version="1.0"
)

DATA_PATH = (
    Path(__file__)
    .resolve()
    .parent.parent
    / "Data"
    / "kyc.json"
)


def load_kyc():
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


kyc_data = load_kyc()


@app.get("/")
def root():
    return {
        "service": "Credit Bureau API",
        "status": "running"
    }


@app.get("/kyc/{customer_id}")
def get_kyc(customer_id: str):

    logger.info(f"Checking KYC for {customer_id}")

    if customer_id in kyc_data:

        logger.info("KYC record found")

        return kyc_data[customer_id]

    logger.warning("KYC record not found")

    raise HTTPException(
        status_code=404,
        detail="KYC record not found"
    )
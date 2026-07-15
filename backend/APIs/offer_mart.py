from fastapi import FastAPI, HTTPException
from pathlib import Path

import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)

from fastapi import APIRouter

router = APIRouter(
    tags=["Offer Mart"]
)

DATA_PATH = (
    Path(__file__)
    .resolve()
    .parent.parent
    / "data"
    / "offers.json"
)


def load_offers():
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


offers = load_offers()


@router.get("/")
def root():
    return {
        "service": "OfferMart API",
        "status": "running"
    }


@router.get("/offer/{customer_id}")
def get_offer(customer_id: str):

    logger.info(f"Searching offer for {customer_id}")

    for offer in offers:

        if offer["customer_id"] == customer_id:

            logger.info("Offer found")

            return offer

    logger.warning("Customer not found")

    raise HTTPException(
        status_code=404,
        detail="Offer not found"
    )
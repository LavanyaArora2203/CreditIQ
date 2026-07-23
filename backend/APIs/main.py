from fastapi import FastAPI

from APIs.credit_bureau import router as credit_router
from APIs.crm_api import router as crm_router
from APIs.offer_mart import router as offer_router

app = FastAPI(
    title="AI Credit Analysis Backend"
)

app.include_router(credit_router)
app.include_router(crm_router)
app.include_router(offer_router)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://credit-iq-psi.vercel.app/",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
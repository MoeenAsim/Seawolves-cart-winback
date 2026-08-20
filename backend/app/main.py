from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.api_response import RecommendationResponse
from app.services.data_service import load_carts
from app.services.orchestrator import WinBackOrchestrator


app = FastAPI(
    title="Seawolves Cart Win-Back Agent",
    version="0.1.0",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


@app.get("/carts")
def get_carts():
    return load_carts()


@app.get(
    "/recommendations",
    response_model=list[RecommendationResponse],
)
def get_recommendations():

    carts = load_carts()

    orchestrator = WinBackOrchestrator()

    recommendations = orchestrator.process_carts(
        carts
    )

    # -----------------------------------------------------
    # Combine trusted cart facts with the agent output.
    #
    # The recommendation itself remains untouched.
    # Cart context comes directly from our dataset.
    # -----------------------------------------------------

    responses = []

    for cart, recommendation in zip(
        carts,
        recommendations,
    ):
        responses.append(
            RecommendationResponse.from_cart_and_recommendation(
                cart=cart,
                recommendation=recommendation,
            )
        )

    return responses
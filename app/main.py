from fastapi import FastAPI

app = FastAPI(
    title="Veículos API"
)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "veiculos-api"}
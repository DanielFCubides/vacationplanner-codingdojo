from datetime import date
from typing import Optional, Annotated

import jwt
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.params import Depends
from jwcrypto import jwk
from jwt import ExpiredSignatureError, InvalidTokenError
from pydantic import BaseModel
from starlette import status
from services.flight_scrapper import FlightScrapper
from utils.connector import HTTPConnector

app = FastAPI()
FLIGHT_SCRAPPER_SERVICE = 'localhost:8000/'
http_connector = HTTPConnector(FLIGHT_SCRAPPER_SERVICE)
flight_services = FlightScrapper(http_connector)


class SearchParams(BaseModel):
    origin: str
    destination: str
    arrival_date: date
    passengers: int = 1
    checked_baggage: int = 0
    carry_on_baggage: int = 1
    return_date: Optional[date] = None


def validate_token(authorization):
    print(authorization)
    if authorization.startswith("Bearer ") is False:
        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )
    token = authorization[7:]  # Remove "Bearer " prefix
    if not token:
        raise HTTPException(
            status_code=401,
            detail="No token provided"
        )

    unverified_token = jwt.get_unverified_header(token)
    print("unverified_token: ", unverified_token)
    try:
        import requests
        url = "https://keycloack.dfcubidesc.com/realms/habit-tracker/protocol/openid-connect/certs"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        kids = response.json()
        print("KIDS:", kids)
        if "keys" not in kids or len(kids["keys"]) == 0:
            raise HTTPException(
                status_code=500,
                detail="Keycloak JWKS endpoint returned no keys"
            )
        public_key_jwk = kids["keys"][0]
        print("PUBLIC KEY:", public_key_jwk)
        public_key = jwk.JWK(**public_key_jwk)
        public_key_pem = public_key.export_to_pem(private_key=False)
        print("PUBLIC KEY PEM:", public_key_pem)

        decoded = jwt.decode(
            token,
            public_key_pem,
            algorithms=["RS256"],
            audience='account',
            issuer='https://keycloack.dfcubidesc.com/realms/habit-tracker'
        )
        print("DECODED:", decoded)
        return decoded

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except Exception or InvalidTokenError as e:
        print(e)
        raise HTTPException(
            status_code=401,
            detail=f"Unauthorized !! {e}"
        )


async def authenticate(authorization: Annotated[str, Header()]):
    if not authorization:
        raise HTTPException(status_code=401, detail="Invalid authorization token")
    return validate_token(authorization)


@app.get('/')
def index(claims: Annotated[dict, Depends(authenticate)]) -> tuple[dict[
    str, str], int] | dict:
    if not claims:
        return {'message': 'Unauthorized'}, status.HTTP_401_UNAUTHORIZED
    print(claims)
    return {'message': 'health-check'}, status.HTTP_200_OK


@app.post('/vacation-plan', status_code=status.HTTP_200_OK, )
def get_vacation_plan(search_params: SearchParams, claims: Annotated[dict, Depends(authenticate)]):
    if not claims:
        return {'message': 'Unauthorized'}, status.HTTP_401_UNAUTHORIZED
    print(claims)
    print(search_params)
    return [
        {
            "id": 1,
            "title": f"Weekend in {search_params.destination}",
            "origin": search_params.origin,
            "destination": search_params.destination,
            "departureDate": search_params.arrival_date.isoformat(),
            "returnDate": search_params.return_date.isoformat(),
            "passengers": 2,
            "flightPrice": 925.30,
            "status": "confirmed"
        }
    ]

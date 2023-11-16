from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from auth import oauth2

from db.database import get_db
from db.hash import Hash
from db.models import DbUser
from redis_om import get_redis_connection, HashModel, Field, Migrator
from jose import jwt
import time
import jose

redis = get_redis_connection(
    host='redis-14134.c301.ap-south-1-1.ec2.cloud.redislabs.com',
    port=14134,
    password='YpxDLz9rzszlKI9OfBtNS9maF9HCicaR',
    decode_responses=True
)

SECRET_KEY = '77407c7339a6c00544e51af1101c4abb4aea2a31157ca5f7dfd87da02a628107'


def block_ip(ip):
    # Check if the key (IP) exists in Redis
    if redis.exists(ip):
        count = redis.incr(ip)
    else:
        count = redis.set(ip, 1)

    # Check if the count exceeds the threshold (e.g., 5 failed attempts)
    if count >= 5:
        # Add the IP to the blocklist in Redis
        redis.sadd("blocklist", ip)

        # Set an expiry time of 1 day (24 hours) for the "blocklist" key
        redis.expire("blocklist", 24 * 60 * 60)


class RevokedTokens(HashModel):
    token: str = Field(index=True)

    class Meta:
        database = redis


router = APIRouter(
    tags=['authentication']
)


class MyCustomException(Exception):
    def __init__(self, detail: str):
        self.detail = detail


@router.post('/token')
def get_token(req: Request, request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    client_ip = req.client.host
    if redis.sismember("blocklist", client_ip):
        raise MyCustomException("Too many failed attempts")
    user = db.query(DbUser).filter(DbUser.username == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")
    if not Hash.verify(user.password, request.password):
        # Get the client's IP address from the request

        # Increment the count for the client's IP and check for IP blocking
        block_ip(client_ip)

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect password")

    access_token = oauth2.create_access_token(data={'sub': user.username})

    return {
        'access_token': access_token,
        'token_type': 'bearer',
        'user_id': user.id,
        'username': user.username
    }


@router.post("/revoke-token/{token}")
def revoke_token(token: str):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        expiration_time = decoded_token['exp']
    except jose.exceptions.ExpiredSignatureError:
        # The token has already expired
        raise HTTPException(status_code=400, detail="Token has expired")

    # Save the token and mark it as "revoked" in Redis
    redis.set(token, "revoked")

    # Calculate the remaining time until expiration and set it as the expiration time in Redis
    current_time = int(time.time())
    remaining_time = expiration_time - current_time
    if remaining_time > 0:
        # Set the remaining time as the expiration time for the key in Redis
        redis.expire(token, remaining_time)

    return {"message": "Token revoked with expiry time set"}


Migrator().run()


@router.get("/protected-data")
def get_protected_data(current_token: str):
    revoked = redis.exists(current_token)
    if revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")
    return {"message": revoked}

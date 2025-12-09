#  Portfolio Tracker

Multi-chain cryptocurrency portfolio tracker with FastAPI, MongoDB, and Redis.

## Features

- Multi-chain wallet generation (Ethereum, Bitcoin, BSC, Polygon)
- Real-time prices from Binance API with NGN conversion via Quidax
- Balance fetching via public RPCs
- Redis caching

## Tech Stack

- **Backend**: FastAPI, Python 3.8+
- **Database**: MongoDB with Beanie ODM
- **Cache**: Redis
- **Blockchain**: web3.py, bitcoinlib

## Quick Start

### Prerequisites

- Python 3.8+
- Docker and Docker Compose

### Installation

```bash
cd BlockAi
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
copy .env.example .env
docker-compose up -d
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection | `mongodb://localhost:27017` |
| `MONGODB_DATABASE` | Database name | `blockai` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379` |
| `ENCRYPTION_KEY` | Key for private key encryption | Required |

## API Endpoints

### Wallets

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/wallets/generate` | Generate new wallet |
| GET | `/api/v1/wallets` | List all wallets |
| GET | `/api/v1/wallets/{id}` | Get wallet details |
| GET | `/api/v1/wallets/{id}/balance?asset=USDT` | Get wallet balance |
| GET | `/api/v1/wallets/balance` | Get portfolio value |
| DELETE | `/api/v1/wallets/{id}` | Delete wallet |

### Prices

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/crypto/prices` | Get current prices |

## Supported Networks

- **Ethereum**: ETH, USDT, USDC
- **BSC**: BNB, USDT, USDC
- **Polygon**: MATIC, USDT, USDC
- **Bitcoin**: BTC

## Public RPCs Used

| Network | RPC |
|---------|-----|
| Ethereum | `https://eth.llamarpc.com` |
| BSC | `https://bsc-dataseed.binance.org` |
| Polygon | `https://polygon-rpc.com` |
| Bitcoin | `https://blockstream.info/api` |

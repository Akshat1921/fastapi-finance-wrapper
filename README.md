# FastAPI Kafka Stock Data Application

This application provides stock financial data through FastAPI endpoints and sends updates to Kafka topics for real-time data streaming and processing.

## Project Structure

```
d:\study\kafka\
├── docker-compose.yml          # Docker services configuration
├── .env                       # Environment variables
├── README.md                  # This documentation file
└── FastApi/
    ├── Dockerfile            # FastAPI Docker configuration
    ├── requirements.txt      # Python dependencies
    ├── main.py              # Main FastAPI application
    ├── producer.py          # Kafka producer configuration
    ├── stock.py             # Stock data models and utilities
    ├── peers.py             # Peer stock analysis functionality
    ├── hehe.py              # Additional utilities
    ├── try.py               # Testing/development scripts
    └── data/
        ├── nasdaq.csv       # NASDAQ stock listings
        ├── sp500_companies.csv # S&P 500 company data
        ├── AAPL.json        # Sample Apple stock data
        ├── ctlt_data.json   # Sample financial data
        └── ...              # Other data files
```

## Services

The application consists of the following Docker services:

- **Zookeeper**: Kafka coordination service (port 2181)
- **Kafka**: Message broker (port 9092 for external, 29092 for internal)
- **Kafka UI**: Web interface for monitoring Kafka topics and messages (port 8080)
- **FastAPI**: Stock data API service (port 8000)

## Quick Start

### Prerequisites

- Docker Desktop installed and running
- Ports 2181, 8000, 8080, 9092, and 9101 available

### Option 1: Using Docker (Recommended)

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Wait for services to initialize** (about 30-60 seconds for Kafka to be ready)

3. **Access the services:**
   - FastAPI Application: http://localhost:8000
   - FastAPI Interactive Docs: http://localhost:8000/docs
   - Kafka UI: http://localhost:8080

4. **Stop services:**
   ```bash
   docker-compose down
   ```

### Option 2: Local Development

1. **Start Kafka infrastructure only:**
   ```bash
   docker-compose up -d zookeeper kafka kafka-ui
   ```

2. **Run FastAPI locally:**
   ```bash
   cd FastApi
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8000
   ```

## API Endpoints

### Health Check
```http
GET /
```
Returns basic application status.

### Get Stock Tickers
```http
GET /stocks/tickers
```
Returns available stock tickers from NASDAQ and S&P 500 datasets.

### Get Financial Data
```http
GET /stocks/financials/{ticker}
```
Retrieves comprehensive financial data for a specific stock ticker.

**Example:**
```bash
curl http://localhost:8000/stocks/financials/AAPL
```

### Update Multiple Tickers (Kafka Producer)
```http
POST /get_tickers_update
Content-Type: application/json

[
  {"ticker": "AAPL"},
  {"ticker": "MSFT"},
  {"ticker": "GOOGL"}
]
```

This endpoint fetches financial data for multiple tickers and sends each to Kafka.

**Example:**
```bash
curl -X POST http://localhost:8000/get_tickers_update \
  -H "Content-Type: application/json" \
  -d '[{"ticker": "AAPL"}, {"ticker": "MSFT"}]'
```

## How It Works

### 1. Data Flow Architecture

```
Client Request → FastAPI → Stock Data API → Kafka Producer → Kafka Topic
                    ↓
            JSON Response to Client
```

### 2. Kafka Integration

When you hit the `/get_tickers_update` endpoint:

1. **Data Fetching**: The application fetches financial data for each ticker from external APIs
2. **Data Processing**: Formats and validates the financial data
3. **Kafka Publishing**: Sends each ticker's data as a separate message to the `financial-updates` Kafka topic
4. **Response**: Returns a summary of processing results to the client

### 3. Message Format

Messages sent to Kafka follow this structure:

```json
{
  "ticker": "AAPL",
  "timestamp": "2025-01-28T10:30:00.123456",
  "financials": {
    "company-overview": {
      "Symbol": "AAPL",
      "Name": "Apple Inc.",
      "Exchange": "NASDAQ",
      "Sector": "Technology",
      "Industry": "Consumer Electronics"
    },
    "balance-sheet": { ... },
    "cashflow": { ... },
    "income-statement": { ... }
  }
}
```

### 4. Docker Networking

All services run on the `kafka-network` Docker network:
- **Internal Communication**: Services communicate using service names (e.g., `kafka:29092`)
- **External Access**: Host machine connects via `localhost` ports
- **Kafka Listeners**: Configured for both internal (`kafka:29092`) and external (`localhost:9092`) access

## Monitoring and Debugging

### Kafka UI Dashboard

Visit http://localhost:8080 to:
- View Kafka topics and their messages
- Monitor consumer groups
- Check topic configurations
- Browse message content in real-time

### Application Logs

```bash
# View all service logs
docker-compose logs

# View specific service logs
docker-compose logs fastapi-app
docker-compose logs kafka
docker-compose logs zookeeper

# Follow logs in real-time
docker-compose logs -f fastapi-app
```

### Health Checks

```bash
# Check if services are running
docker-compose ps

# Test FastAPI health
curl http://localhost:8000/

# Test Kafka connectivity
curl http://localhost:8080/
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `KAFKA_BOOTSTRAP_SERVERS` | `kafka:29092` | Kafka server connection for containers |
| `NASDAQ_CSV_PATH` | `./data/nasdaq.csv` | Path to NASDAQ data file |
| `SP500_CSV_PATH` | `./data/sp500_companies.csv` | Path to S&P 500 data file |

## Troubleshooting

### Common Issues

1. **Connection Refused Error**: 
   - Ensure all services are on the same Docker network
   - Wait for Kafka to fully initialize (30-60 seconds)
   
2. **Port Conflicts**: 
   - Make sure ports 8000, 8080, 9092, and 2181 are available
   - Check with `netstat -an | findstr :8000`

3. **Docker Issues**: 
   - Ensure Docker Desktop is running
   - Try `docker-compose down -v` then `docker-compose up -d`

### Useful Commands

```bash
# Check running containers
docker ps

# Restart a specific service
docker-compose restart fastapi-app

# Clean up everything (removes volumes)
docker-compose down -v

# Rebuild and restart
docker-compose up -d --build
```

### Manual Kafka Topic Management

```bash
# List all topics
docker exec kafka kafka-topics --list --bootstrap-server kafka:29092

# Describe a topic
docker exec kafka kafka-topics --describe --topic financial-updates --bootstrap-server kafka:29092

# Create a topic manually
docker exec kafka kafka-topics --create --topic test-topic --bootstrap-server kafka:29092 --partitions 1 --replication-factor 1

# Delete a topic
docker exec kafka kafka-topics --delete --topic financial-updates --bootstrap-server kafka:29092

# Console consumer (to see messages)
docker exec -it kafka kafka-console-consumer --bootstrap-server kafka:29092 --topic financial-updates --from-beginning
```

## Development

### Making Changes

1. **Edit source code** in the [`FastApi/`](FastApi/) directory
2. **If running with Docker**: `docker-compose restart fastapi-app`
3. **If running locally**: The application auto-reloads with uvicorn's `--reload` flag

### Adding New Dependencies

1. Update [`FastApi/requirements.txt`](FastApi/requirements.txt)
2. Rebuild the container: `docker-compose up -d --build fastapi-app`

### Data Files

- **Stock Lists**: Update [`FastApi/data/nasdaq.csv`](FastApi/data/nasdaq.csv) and [`FastApi/data/sp500_companies.csv`](FastApi/data/sp500_companies.csv)
- **Sample Data**: Check [`FastApi/data/AAPL.json`](FastApi/data/AAPL.json) for reference JSON structure

## Use Cases

### Real-Time Stock Monitoring
Set up consumers to process financial updates from Kafka topics for:
- Price alerts and notifications
- Portfolio tracking
- Risk management systems

### Data Analytics Pipeline
Use Kafka as a data pipeline for:
- ETL processes
- Data warehousing
- Machine learning model training

### Microservices Integration
The Kafka topics can feed data to:
- Notification services
- Database updaters
- Analytics engines
- Third-party integrations

## API Response Examples

### Stock Tickers Response
```json
{
  "nasdaq_tickers": ["AAPL", "MSFT", "GOOGL", ...],
  "sp500_tickers": ["AAPL", "MSFT", "AMZN", ...],
  "total_count": 500
}
```

### Financial Data Response
```json
{
  "ticker": "AAPL",
  "company_overview": {
    "Symbol": "AAPL",
    "Name": "Apple Inc.",
    "Exchange": "NASDAQ"
  },
  "financials": {
    "balance_sheet": {...},
    "income_statement": {...},
    "cash_flow": {...}
  }
}
```

---

## Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review Docker and FastAPI logs
3. Ensure all services are properly networked
4. Verify Kafka topics are created and accessible via Kafka UI

For development questions, refer to the FastAPI documentation and Kafka documentation for advanced configurations.
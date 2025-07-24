# Neo4j Setup Instructions

## 1. Install Neo4j

### Option A: Docker (Recommended)
```bash
docker run \
    --name neo4j \
    -p7474:7474 -p7687:7687 \
    -d \
    -v $HOME/neo4j/data:/data \
    -v $HOME/neo4j/logs:/logs \
    -v $HOME/neo4j/import:/var/lib/neo4j/import \
    -v $HOME/neo4j/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/hiddenthread \
    neo4j:latest
```

### Option B: Neo4j Desktop
1. Download from https://neo4j.com/download/
2. Create new database with password "hiddenthread"
3. Start the database

## 2. Update .env file

Add these lines to your `.env` file:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=hiddenthread
```

## 3. Verify Connection

The system will automatically test the Neo4j connection when started.

## 4. Install Python Dependencies

```bash
pip install neo4j

# Or if using the virtual environment:
source .venv/bin/activate
pip install neo4j
```

## 5. Access Neo4j Browser

Visit http://localhost:7474 to access the Neo4j browser interface.
- Username: neo4j
- Password: hiddenthread

You'll be able to visualize the subgraphs created by HiddenThread!

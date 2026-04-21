# API Documentation

## Generate Evaluation Tasks Endpoint

**Endpoint:** `GET /api/generate-evaluation-tasks`

**Description:** Generates evaluation dataset tasks for prompt evaluation. Returns an array of tasks for Python, JSON, or Regex AWS-related exercises.

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `num_tasks` | integer | No | 3 | Number of tasks to generate |

### Response

```json
{
  "tasks": [
    {
      "task": "Write a Python function that parses an AWS S3 bucket URI..."
    },
    {
      "task": "Create a regular expression that matches valid AWS IAM role ARNs..."
    },
    ...
  ]
}
```

### Example Usage

#### cURL
```bash
# With default (3 tasks)
curl http://localhost:8000/api/generate-evaluation-tasks

# With custom number
curl "http://localhost:8000/api/generate-evaluation-tasks?num_tasks=5"
```

#### Python (requests)
```python
import requests

# With default
response = requests.get("http://localhost:8000/api/generate-evaluation-tasks")

# With custom number
response = requests.get(
    "http://localhost:8000/api/generate-evaluation-tasks",
    params={"num_tasks": 5}
)

data = response.json()
for task in data["tasks"]:
    print(f"- {task['task']}")
```

#### JavaScript (fetch)
```javascript
// With default
const response = await fetch('http://localhost:8000/api/generate-evaluation-tasks');

// With custom number
const response = await fetch('http://localhost:8000/api/generate-evaluation-tasks?num_tasks=5');

const data = await response.json();
console.log(data.tasks);
```

### Sample Response

```json
{
  "tasks": [
    {
      "task": "Write a Python function that parses an AWS S3 bucket URI (e.g., 's3://my-bucket/path/to/file.txt') and returns a dictionary with keys 'bucket' and 'key'"
    },
    {
      "task": "Create a regular expression that matches valid AWS IAM role ARNs in the format 'arn:aws:iam::ACCOUNT_ID:role/ROLE_NAME' where ACCOUNT_ID is 12 digits and ROLE_NAME contains alphanumeric characters, hyphens, and underscores"
    }
  ]
}
```

### Implementation Details

- **Model**: claude-haiku-4-5-20251001
- **Temperature**: 0.8 (higher for creative task generation)
- **Max Tokens**: 2048
- **Response Format**: JSON array of task objects
- Focus: Tasks solvable with single Python function, JSON object, or regex
- Domain: AWS-related tasks

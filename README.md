# Dataset Collection and Processing Pipeline

A comprehensive Python library for collecting data from multiple sources (YouTube, Google, web pages, PDFs) and processing text using both API-based (DeepSeek, Mistral) and local models.

## Features

- Multi-source data collection:
  - YouTube videos (title & description)
  - Google search results
  - Web pages (with robots.txt compliance)
  - PDF documents (local and remote)
- Text processing capabilities:
  - Text classification
  - Token classification (Named Entity Recognition)
  - Text summarization
  - Feature extraction
  - Text generation
- Model flexibility:
  - Local models using HuggingFace Transformers
  - API integration with DeepSeek and Mistral
- Data output formats:
  - JSON
  - CSV

## Requirements

- Python 3.7+
- PyTorch
- Required API keys:
  - DeepSeek API key
  - Mistral API key
  - YouTube Data API key
  - Google Custom Search API key
  - Google Custom Search Engine ID (CSE ID)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd datasetzombitx64
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Test the installation:
```bash
python test_system.py
```

This will run a basic functionality test using local models, without requiring API keys. The test processes two sample tasks:
- Sentiment classification of a movie review
- Named entity recognition in a sentence

The test will generate a JSON file with the results in the `datasets` directory.

## Usage

### Basic Example

```python
import asyncio
from datasetzombitx64 import run

# Define your tasks
tasks = [
    {
        "source": "youtube",
        "query": "https://www.youtube.com/watch?v=example",
        "task": "summarization",
        "prompt": "Summarize the video content",
        "use_api": "deepseek"
    },
    {
        "source": "google",
        "query": "AI advancements",
        "task": "text_classification",
        "prompt": "Classify sentiment",
        "use_api": "mistral"
    }
]

# Run the pipeline
output_path = asyncio.run(run(
    tasks,
    name="my_dataset",
    output_format="json",
    deepseek_key="your_deepseek_key",
    mistral_key="your_mistral_key",
    youtube_key="your_youtube_key",
    google_key="your_google_key",
    cse_id="your_cse_id"
))

print(f"Dataset saved at: {output_path}")
```

### Task Configuration

Each task is defined as a dictionary with the following fields:

- `source`: Data source type ("youtube", "google", "web", "pdf", or "direct")
- `query`: URL, search query, or direct text input
- `task`: Processing task type ("text_classification", "token_classification", "summarization", "feature_extraction", "text_generation")
- `prompt`: Optional prompt to guide the processing
- `use_api`: Optional API to use ("deepseek" or "mistral"). If not specified, uses local models

### Supported Tasks

1. **Text Classification**
   - Uses DistilBERT model fine-tuned on SST-2
   - Classifies text sentiment or categories

2. **Token Classification (NER)**
   - Uses BERT model fine-tuned on CoNLL-03
   - Identifies named entities (persons, organizations, locations)

3. **Summarization**
   - Uses BART base model
   - Generates concise summaries of longer texts

4. **Feature Extraction**
   - Uses Sentence Transformers (all-MiniLM-L6-v2)
   - Generates text embeddings for similarity comparison

5. **Text Generation**
   - Uses GPT-2 model
   - Generates text continuations or completions

## Output Format

The generated dataset includes the following information for each task:

```json
{
  "source": "youtube",
  "query": "https://www.youtube.com/watch?v=example",
  "task": "summarization",
  "prompt": "Summarize the video content",
  "content": "Original content...",
  "result": "Processed result...",
  "processed_by": "deepseek"
}
```

## Error Handling

The library includes comprehensive error handling:
- API request failures
- Model loading issues
- Data fetching problems
- File access errors

All errors are logged with clear messages using the Display utility class.

## Security and Compliance

- Robots.txt compliance for web scraping
- Rate limiting for API requests
- Content permission warnings
- Terms of Service compliance checks

## License

This project is licensed under the MIT License - see the LICENSE file for details.

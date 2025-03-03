# Changelog

### v1.0.3 (2025-03-03)

- Enhanced input validation and user experience:
  - Added URL validation for YouTube, web pages, and PDFs
  - Improved error handling for invalid inputs
  - Added empty input checks with helpful messages
  - Enhanced user guidance with format requirements
  - Added input validation loops for better user experience

### v1.0.2 (2025-03-03)

- Added interactive task creation:
  - User-friendly command-line interface for creating tasks
  - Support for optional data sources (YouTube, Google, Web, PDF)
  - Flexible task configuration with default prompts
  - Direct text input option for simple tasks
  - Clear progress indicators and success messages

### v1.0.1 (2025-03-03)

- Enhanced Mistral API error handling and stability:
  - Increased retry attempts from 3 to 5
  - Improved timeout handling with 60s total timeout
  - Implemented exponential backoff starting at 3s
  - Updated to use mistral-large-latest model
  - Optimized request payload size
  - Added better session management
  - Improved error reporting

### v1.0.0 (2025-03-03)

- Initial release of the dataset collection and processing pipeline.
- Added InsightCrafter.ipynb and Insightcrafter_zombitx64.py for data collection and processing
- Implemented support for multiple data sources:
  - YouTube videos
  - Google search results
  - Web pages
  - PDF documents
- Added Mistral API integration for text processing
- Included robust error handling and rate limit management
- Added progress indicators and warning messages for API usage

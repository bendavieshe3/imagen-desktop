# Imagen Desktop

## Project Overview
Imagen Desktop is a PyQt6-based desktop application for running generative AI models, with an early focus on image generation using Replicate's API, to be expanded to other services and media types over time.

## Design Documents
These documents specify the product, and should be referred to as needed to make design design decisions and refactorings:
- For the product vision, see [vision](./docs/vision.md) 
- For the complete planned feature list, see [features](./docs/features.md)
- For the conceptual domain model, see [concepts](./docs/concepts.md)

## Guides
- Getting started information is maintained in the [readme](./README.md). (THIS DOCUMENT)
- Detailed testing information is maintined in the [testing readme](/tests/README.md).
- To contribute to the project see the [contributing](./docs/contributing.md) guide.

## Tech Stack

The product is coded in Python and runs in a virtual environment. 

- UI: PyQt6
- API: Replicate client
- Database: SQLAlchemy with SQLite
- Migration: Alembic
- Testing: pytest
- Image Processing: Pillow

The technology architecture of the product is described in more detail in [technology](./docs/technology.md). Development-only tools are described in [tooling](./docs/tooling.md).

## API Key Setup
Make sure to set up your Replicate API key in a `.env` file:
```
REPLICATE_API_TOKEN=your_api_token_here
```

Alternatively, you can store it in a config file:
```json
// at ~/.imagen-desktop/config.json
{
  "api_key": "your_api_token_here"
}
```

## Running in development

- While running in development, always activate the virtual environment before running commands: `source ./venv/bin/activate` (macOS/Linux) or `./venv/Scripts/activate` (Windows)





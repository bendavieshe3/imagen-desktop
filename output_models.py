import replicate

# Get text-to-image collection
collection = replicate.collections.get("text-to-image")

# List top models
for model in collection.models[:50]:
    print(f"ID: {model.owner}/{model.name}")
    print(f"Version: {model.latest_version.id}")
    print(f"Description: {model.description}")
    print("---")
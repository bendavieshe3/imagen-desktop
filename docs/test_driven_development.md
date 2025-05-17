# Test-Driven Development Guide

## TDD Workflow

Test-Driven Development follows a "Red-Green-Refactor" cycle:

1. **Red**: Write a failing test that defines the functionality you want to implement
2. **Green**: Write the minimal code needed to make the test pass
3. **Refactor**: Clean up the code while keeping the tests passing

## Best Practices

### Writing Tests First

1. **Start with a clear specification**: Understand what you want to build before writing tests
2. **Focus on behavior, not implementation**: Test what the code should do, not how it's done
3. **Small, focused tests**: Each test should verify one specific aspect of behavior
4. **Use descriptive test names**: Name tests according to what they verify

### Example

```python
# Red: Write a failing test
def test_product_factory_validates_parameters():
    # Arrange
    factory = ProductFactory()
    invalid_params = {"width": -100}  # Invalid width
    
    # Act & Assert
    with pytest.raises(ValidationError):
        factory.validate_parameters(invalid_params)

# Green: Write minimal code to pass
def validate_parameters(self, params):
    if "width" in params and params["width"] < 0:
        raise ValidationError("Width must be positive")
    return True

# Refactor: Improve the code while tests pass
def validate_parameters(self, params):
    self._validate_dimensional_parameters(params)
    return True
    
def _validate_dimensional_parameters(self, params):
    for dim in ["width", "height"]:
        if dim in params and params[dim] < 0:
            raise ValidationError(f"{dim.capitalize()} must be positive")
```

## Testing Patterns for Imagen

### Domain Model Testing

Focus on behavior and invariants:

```python
def test_generation_cannot_be_completed_if_not_started():
    # Arrange
    generation = Generation(status=GenerationStatus.PENDING)
    
    # Act & Assert
    with pytest.raises(InvalidStatusTransitionError):
        generation.complete()
```

### Repository Testing

Test repository contract without relying on database implementation:

```python
def test_product_repository_returns_products_for_generation(db_session):
    # Arrange
    generation = GenerationFactory()
    product1 = ProductFactory(generation=generation)
    product2 = ProductFactory(generation=generation)
    db_session.add_all([generation, product1, product2])
    db_session.commit()
    
    repo = ProductRepository(db_session)
    
    # Act
    products = repo.get_by_generation(generation.id)
    
    # Assert
    assert len(products) == 2
    assert all(p.generation_id == generation.id for p in products)
```

### UI Testing

Test presenter logic independently from UI:

```python
def test_gallery_presenter_loads_products_on_initialize():
    # Arrange
    mock_view = Mock()
    mock_repository = Mock()
    mock_repository.get_all.return_value = [ProductFactory(), ProductFactory()]
    
    presenter = GalleryPresenter(mock_view, mock_repository)
    
    # Act
    presenter.initialize()
    
    # Assert
    mock_repository.get_all.assert_called_once()
    assert mock_view.display_products.call_count == 1
    assert len(mock_view.display_products.call_args[0][0]) == 2
```

## Mocking External Services

For tests involving Replicate API:

```python
@pytest.fixture
def mock_replicate_client(mocker):
    mock_client = mocker.Mock()
    mock_client.run.return_value = {
        "output": ["https://example.com/image.jpg"],
        "status": "succeeded"
    }
    return mock_client

def test_replicate_product_factory_creates_products(mock_replicate_client):
    # Arrange
    factory = ReplicateProductFactory(client=mock_replicate_client)
    params = {"prompt": "test prompt", "width": 512, "height": 512}
    
    # Act
    products = factory.create_products(params)
    
    # Assert
    assert len(products) == 1
    assert products[0].url == "https://example.com/image.jpg"
    mock_replicate_client.run.assert_called_once()
```

## Arranging Tests with Factories

Factory fixtures simplify test setup:

```python
# In conftest.py or factories.py
@pytest.fixture
def order_factory():
    def _factory(**kwargs):
        defaults = {
            "status": OrderStatus.PENDING,
            "parameters": {"prompt": "test", "steps": 20}
        }
        defaults.update(kwargs)
        return Order(**defaults)
    return _factory

# In tests
def test_order_can_be_fulfilled(order_factory):
    # Arrange
    order = order_factory(status=OrderStatus.PROCESSING)
    
    # Act
    order.fulfill()
    
    # Assert
    assert order.status == OrderStatus.FULFILLED
```

## UI Test Considerations

When testing PyQt6 components:

1. Use the `pytest-qt` plugin
2. Keep UI tests separate with the `ui` marker
3. Test signals and slots independently when possible
4. Use `qtbot` for simulating user interactions

```python
@pytest.mark.ui
def test_model_selector_emits_signal_on_selection(qtbot):
    # Arrange
    selector = ModelSelector()
    qtbot.addWidget(selector)
    signal_spy = QSignalSpy(selector.modelSelected)
    
    # Act
    selector.select_model("model_1")
    
    # Assert
    assert signal_spy.count() == 1
    assert signal_spy[0][0] == "model_1"
```
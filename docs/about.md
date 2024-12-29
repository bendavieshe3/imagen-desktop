# About Imagen

Imagen is a desktop application for running generative AI models, with a focus on image generation.

# Features



# Entities and Concepts


## Providers

A provider is a service that can be used to generate products (images, videos, etc.)
Each provider has a set of available *models* grouped into *model families*.
Each provider will have their own local or remote API to interact with.

Usage:
- A provider is made available by a provider class.
- A provider has configuration defined such as API keys, etc
- A provider provides *factory* implementations
- A provider provides the *models* it supports grouped by *model type* and *model family*

Examples:
- Replicate
- fal.ai
- civitai

## Model Types

Each model has a model type. This is a simple label or enum value that is used to distinguish the expected input and ouput modalities of the model.

Examples:
- Text-to-Image
- Text-to-Video
- Text-to-Audio
- Image-to-Image
- Image-to-Video

## Model Families

Each model family is a collection of models that share a common set of features and capabilities.

Examples:
- Stable Diffusion
- Midjourney
- OpenAI

## Factory

A factory is an implementation made available by a provider for the purpose of specifying how the provider is used for a specific generative task based on a *model*.

### Implementation
Each factory has a generic interface that is implemented by a factory class.
Each factory is responsible for
- validating and dispatching *generations* to the real service using the provided *generation parameter set* to determine a *actual parameter set*.
- updating the generation with the *return parameter set* and other metadata results
- making avalable the returned digital assets used to create the *products*

Each factory implementation may have a specific inheritance hierachy that is optimised for code reuse and distinguishing *model type*, *model* and *provider* differences.

For example, all factory implementations may shared a base factory class that provides common functionality such as validating *generation parameter set* based on a *parameter set spec*

## Generations

A Generation is a request for one or more *product* to be created by a *factory*, and typically aligns to a single API request to the underlying provider.

Examples:
- A simple API call to generate an image from a provider
- A simple API call to generate a batch of images from a provider

Usage:
- One or more *generations* are created from an *order* using a *base parameter set*
- A *generation* can generate one or more *products*
- A *generation* always has a single *order* and is performed using a single *factory*
- A *generation* has a *generation parameter set* that is used by a *factory* to create an *actual parameter set* used in the API request to the provider

## Orders

An order is a request made by a user to create one or more *products* using a specific *model*, *model type* and *provider*. An order is a container for a *base parameter set* and triggers the creation of one or more *generations*.

## Products

Products are the individual digital outputs (E.g. images, videos, etc.) created by a generation.

Examples:
- A single image
- A single video
- A single audio file

Usage:
- One or more *products* are created from a *generation*
- A *product* may be created from a *generation*
- A *product* may also be imported from an external source
- A *product* may also be used or reference in a *base parameter set*, being specifed by a user as an input to another generation.
- A *product* has a type, such as image, video, audio, etc.

# Parameters

## ParameterSets

A parameter set is a collection of *parameters* used in the application to support the creation of a *generation*.

A parameter set can have different *parameters* based on the *model*, *model type* and *provider*.

Usage:


- A *base parameter set* is assembled from the user input and stored against an *order*
- A *generation parameter set* is created from the *base parameter set* 
- A *generation parameter set* is validated by a *factory*
- A *generation parameter set* maybe combined with a model or provider specific parameter set to create an *actual parameter set*
- A *return parameter set* is created from the return values of the API and represent the parameter values that were actually used to create the *product*. This might include defaults or other values that were not specified by the user and application. 

### Implementation

A parameter set is typically implemented as a dictionary or hash. It may be stored in a database field as a JSON object or other serialised format that can have arbitrary keys and values.

Different database models may use parameter sets in different contexts as per usage. E.g. an *order* may have a *base parameter set*. A *generation* may have a *generation parameter set* and a *return parameter set*.

## ParameterSetSpecs

A parameter set spec is a specification of the parameters that are supported by a *model*, *model type* and *provider*.

## SmartParameters

Smart Parameters are a style of specifying base parameter values that results in an extrapolated, interpolated or otherwise derived value. SmartParameters generally result in an order having more than one generation.

Example:

- To create multiple generations with different values: 
-- User specifies a seed value of '[1,2,3]'. The base parameter seed value is therefore '[1, 2, 3]' but three generations are created with seed values '1', '2' and '3'.
-- User specifies a steps value of '[25..27]'. The base parameter steps value is therefore '[25, 26, 27]' and three generations are created with steps values '25', '26' and '27'.
- To create a single generation with a randomly selected value:
-- User specifies a steps value of '[25|30]'. The base parameter steps value is therefore '[25, 30]' and one generation is created with either generation parameter set step value of '25' or '30'.
- Within a string prompt or negative prompt to generate the same behaviours
-- User specifies a prompt of 'a [brown,black] [cat,dog]'. The base parameter prompt value is therefore 'a [brown,black] [cat,dog]' and four generations are created with prompts 'a brown cat', 'a brown dog', 'a black cat' and 'a black dog'.

The impact of a SmartParameter is dictated by the format:
- values in square brackets and separated by commas are interpreted as a list of values to be used in separate generations
- values in square brackets and separated by a range operator (e.g. '..') are interpreted as a range of values to be used in separate generations
- values in square brackets and separated by a pipe operator (e.g. '|') are interpreted as a list of values to be selected at random to be used in a single generation

## SmartTokens

SmartTokens work like SmartParameters in prompts and negative prompts but use external values.

Example: Given a base parameter prompt value of 'A beautiful image of a [animal]', an Smarttoken values of 'animal' are looked at to generate a list of values to be used in separate generations.

## Projects

Projects are a way to organise orders based on a specific intent, theme or concept. 

## Collections

Collections are adhoc collections of products that the user manually creates, populates and manages. 

# Database Models

All database models are assumed to have an ID, created_at, updated_at and deleted_at fields.

## Models

## 

## Order

- optionally has one or more generations
- optionally has a project
- has a status field: pending, processing, underway, fulfilled, cancelled
- has a parameter set field: base parameter set

## Generation

- has a status field: pending, generating, complete, failed, cancelled
- has a parameter set field: generation parameter set
- has a parameter set field: actual parameter set
- has a parameter set field: return parameter set

## Product

- has an optional generation
- has a type field: image, video, audio, etc.
- has a file field: file path, url, etc.
- has a file size field: bytes, etc.
- has adhoc metadata fields: width, height, 
- may have a binary field for thumbnail, etc.


## Projects

- has a name
- has a description
- has a status: active, archived


## SmartToken


## SmartTokenValues

## Collection


# User Interface

## Projects

A page showing a list of active projects, with a way to create a new project, archive a project etc. Each project has a way to jump to the order page to create a new order in the project
Each project has a way to jump to the gallery page to view the products created in the project.
Each project is displayed with a sample thumbnail of a product created in the project.

## Order Page

A page for creating a new order in a project. Allows the user to select a model, model type, provider and base parameter set. The user can use SmartParameters and SmartTokens to create the base parameter set. By clicking an order button, the order is created and enqueued in the orders table. The user can continue submitting new orders. Products are created asynchronously will appear in the output display when complete. Products created in the current session will appear in a thumbnail strip. 

## Production Page

A page showing a list of recent orders, generations, and products showing the status of each.

## Gallery

A page showing a list of products, with a way to view the product details, navigate to the order page of the product (to re-order it), delete or manipulate the product, show metadata etc. Products may be searched and grouped by type (image, video, audio, etc.), by project and by collection.




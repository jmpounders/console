# Dashboard for Home Office

## Design

- Dashboard is based on `pygame`. This will enable me to create custom components, animations and color schemes.
- Because we are using a game engine, the dashboard will be driven from an event loop in the main function.
- The dashboard will be modular, with each component being an instantiation of a `pygame` surface. This will allow for easy addition of new components.
- Data will  be retrived from multiple locations and integrated.

## Data ingestion

- Each data source will be represented as a `DataSource` object.
- Each `DataSource` will have the following components:
  - Name of the data source,
  - A function to retrieve the data,
  - A refresh rate,
  - A default value.
- Each `DataSource` will have an `update` method that will return the latest data and update it as needed per the refresh rate.
- When updating the data, the `DataSource` will call the retrieval function asynchronously.

> Asynchronous retrieval is being done using `concurrent.futures.ThreadPoolExecutor`. There is a single thread pool that is shared by all data sources, and this pool lasts for the lifetime of the program.

## Turning raw data into visual components

Still a WIP, but essentially each data source will need a presenter/formatter to convert the raw data into a form that can be displayed in a component.
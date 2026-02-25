<!-- DAY 3 -->

# Product Query Engine

## Supported Filters

GET /products

### Query Params

- search → regex search on name & description
- minPrice → minimum price
- maxPrice → maximum price
- tags → comma separated tags (AND condition)
- sort → field:asc | field:desc
- page → pagination
- limit → pagination
- includeDeleted → true/false

## Soft Delete Strategy

DELETE /products/:id

Sets:
deletedAt = current timestamp

Records are excluded by default.
Use includeDeleted=true to fetch them.
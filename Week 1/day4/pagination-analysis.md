# Pagination Analysis – GitHub Repositories API

## Endpoint
GET https://api.github.com/users/octocat/repos

---

## Pagination Parameters

Parameters we use for request:
- `page`: specifies the page number to retrieve
- `per_page`: specifies the number of results per page

## Page 1 Analysis

### Request
curl -i "https://api.github.com/users/octocat/repos?page=1&per_page=5"

### Response Headers
The response includes a `Link` header:
Link: https://api.github.com/user/583231/repos?page=2&per_page=5; rel="next",
https://api.github.com/user/583231/repos?page=2&per_page=5; rel="last"

### Observations
- `rel="next"` provides the URL for the next page of results
- `rel="last"` indicates the final available page
- This confirms that the results are paginated

---

## Page 2 Analysis

### Request
curl -i "https://api.github.com/users/octocat/repos?page=2&per_page=5"

### Response Headers
Link: https://api.github.com/user/583231/repos?page=1&per_page=5; rel="prev",
https://api.github.com/user/583231/repos?page=1&per_page=5; rel="first"


### Observations
- `rel="prev"` allows navigation back to the previous page
- `rel="first"` points to the first page of results
- Absence of `rel="next"` indicates this is the last page

---

## Navigating Pages

Pagination is handled using the `Link` header rather than relying on manually incrementing page numbers.

Recommended navigation process:
1. Request the first page
2. Read the `Link` header in the response
3. Follow the URL labeled `rel="next"` to retrieve subsequent pages
4. Stop when no `rel="next"` link is present

---

## Conclusion

The GitHub API uses HTTP `Link` headers to manage pagination.
Rely on the provided `rel` values to navigate between pages safely and efficiently instead of guessing page numbers.
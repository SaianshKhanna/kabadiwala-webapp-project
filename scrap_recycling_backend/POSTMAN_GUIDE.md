# Postman quick test sequence

1. Import `postman/Scrap_Recycling_Backend.postman_collection.json`.
2. Set collection variable `base_url` to `http://127.0.0.1:5000`.
3. Run **Health check** and **Get categories**.
4. Register a collector. Login as collector.
5. Create a listing, then test **My listings**, **Browse listings**, **Get listing by ID**, edit and delete.
6. Register a recycler. Login as recycler.
7. Create a rate and browse rates.
8. Send a request against an existing available listing.
9. Log in as collector and accept/reject the request.
10. Log in as the recycler who sent it and mark an accepted request completed.
11. Test dashboard and profile for both roles.

Postman stores cookies per domain. Keep requests on the same host (`127.0.0.1`) so the Flask session cookie is sent.

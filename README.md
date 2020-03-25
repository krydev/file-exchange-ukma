# file-exchange-ukma
Flask file exchange web application.
Technologies:
- AWS S3 for storing files
- Redis Queue `worker.py` for scheduling communication with S3 API
- Jwt token authorization in cookies using `flask-jwt-extended`
- JQuery for AJAX and simple DOM manipulation
- Docker and heroku manifest for deployment

Files are uploaded and downloaded using presigned urls directly from client to reduce server load and latency.

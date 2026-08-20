import os

RECIPE_SERVICE_URL = os.environ.get("RECIPE_SERVICE_URL", "http://localhost:8082")
USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "http://localhost:8081")
# online-store-api

## Usage
1. Install dependencies:
   pip install -r requirements.txt

2. Run the server:
   uvicorn main:app --reload

3. Available endpoints:
- GET /products
- POST /cart/{email}
- DELETE /cart/{email}
- POST /order
- PUT /product/{id} (manager/admin)
- POST /product (admin)

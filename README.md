# Shop API
Shopping api written with Python and APIFlask.
This api implements:
* User registration
* Token authentication
* Product creation(admin only)
* Cart creation
* Adding product to the cart
* Product purchases with Stripe Checkout
* OpenAPI specification

### Project documentation is avaliable at http://{your_host}/docs
![](https://codimd.s3.shivering-isles.com/demo/uploads/340e733e-5ea4-444e-b6f3-37fb2e25a452.png)

### To run this project locally follow this steps:
1. Clone this repository:
```
    git clone https://github.com/lymagics/shop-api.git
```
2. Go to project directory and create python virtual invironment:
```
    cd shop-api
    python -m venv venv
```
3. Activate virtual environment and install requiremenst:
```
    venv/Scripts/activate
    pip install -r requirements.txt
```
4. Go to [stripe checkout](https://stripe.com/docs/payments/checkout), create account and get stripe secret key.
5. Create .env file and fill it with .env.example variables. Dismiss STRIPE_WEBHOOK_SECRET for now.
6. Apply database migration:
```
    flask db upgrade
```
7. Populate database with purchase statuses:
```
    flask populate statuses
```
9. Run flask local server:
```
    flask run
```
8. Run ngrok:
```
    ngrok http 5000
```
9. Go back to [stripe checkout](https://stripe.com/docs/payments/checkout), go to dashboard and create webook with your ngrok url.
10. Complite .env file with STRIPE_WEBHOOK_SECRET.
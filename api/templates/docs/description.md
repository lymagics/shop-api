Shop API - project made for educational purpose. API can be used to create Shop application.

## Project configuration
| Variable                         | Default value                  | Description     |
| :---                             |    :----:                      |          ---:   |
| SECRET_KEY                       | -                              | Secret key for data encryption |
| DATABASE_URL                     | "sqlite:///db.sqlite"          | Database connection string |
| REFRESH_TOKEN_IN_BODY            | False                          | Return refresh token in body |
| REFRESH_EXPIRATION_IN_DAYS       | 7                              | Days while refresh token is valid |
| ACCESS_EXPIRATION_IN_MINUTES     | 15                             | Minutes while access token is valid |
| REFRESH_TOKEN_IN_COOKIE          | True                           | Set refresh token in cookie       |
| ADMIN_EMAIL                      | -                              | Admin email address        |
| MAIL_SERVER                      | "smtp.googlemail.com"          | Application mail server      |
| MAIL_PORT                        | 587                            | Application mail port |
| MAIL_USE_TLS                     | True                           | Use Transport layer security for mail |
| MAIL_USERNAME                    | -                              | Application mail username |
| MAIL_PASSWORD                    | -                              | Application mail password |
| STRIPE_SECRET_KEY                | -                              | Stripe secret key for checkout session|
| STRIPE_WEBHOOK_SECRET            | -                              | Stripe secret key for checkout webhook |
| CHECKOUT_SUCCESS                 | "http://localhost:3000/success"| Purchase success page |
| CHECKOUT_FAIL                    | "http://localhost:3000/fail"   | Purchase fail page |
| USERS_PER_PAGE                   | 10                             | Number of users in pagination |
| PRODUCTS_PER_PAGE                | 10                             | Number of products in pagination |
| USE_CORS                         | True                           | Allow Cross origin resource sharing |

## Authentication
Application uses OAuth 2.0 procedure. To authenticate user has to create access and refresh token pair. Access token will be used for user autentication. Refresh token will be used for access token renewal. All the information about authentication you can find in Token endpoint.

## Administration
To grant user administration permission it email has to match "ADMIN_EMAIL" config variable. Administrator has access to Product endpoint.

## Error responses
Application has two type of errors:
* HTTP Error:
    ```json
    {
      "detail": {},
      "message": "string"
    }
    ```
* Validation Error:
    ```json
    {
      "detail": {
        "<location>": {
          "<field_name>": [
            null
          ]
        }
      },
      "message": "string"
    }
    ```
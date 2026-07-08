# Objective : Create the python script to generate fake transactional data.
- Create amount for each cart and quantity of products
- Aggregate the features
- Export the new dataset as a CSV

# Requirements : Generate fake transactionnal data

1. A transaction may contain multiple products

Below is an example of data describing one shopping transaction. A shopper may purchase multiple products. Each transaction includes a date, an order status and a final ati amount, along with details of the cart stored as a list of 'products'. Each product in the cart has a unique id, a unit ati amount and the purchased 'quantity'.

{ "shopper_id": "12345", "transaction_date": "2024-03-01", "order_status": "Confirmed",
"final_ati_amount": "100.00", "products": [{"product_id": "A100", "unit_ati_amount":"50.00", "quantity": 2}] }

2. A product quantity may be equal to 0 which indicates a service.
3. A transaction status may have one of the following values : Confirmed, Cancelled, Pending
4. The fake data should contain some loyal shoppers who monthly purchase goods from this shop.

# Important : Before using the main script "data_generation.py"

 - The .env file must be at the root directory of this project
 - All the variables in the .env file are mandatory 
 - Set the values of all the required variables 
 - The 'Config' class is in charge of reading and loading the enviremental variables
 - The generated data file could be found under the 'output' directory
 - The log file is called 'app.log' and could be found under the 'logs' directory

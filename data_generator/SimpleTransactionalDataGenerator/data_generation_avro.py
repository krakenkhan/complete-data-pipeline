import avro.schema 
from avro.datafile import DataFileWriter
from avro.io import DatumWriter
from datetime import datetime
import random
import string
from datetime import timedelta
import logging
from config import Config

# Configure logging
logging.basicConfig(level=logging.DEBUG,  
                    format='%(asctime)s - %(levelname)s - %(message)s',  # message format
                    filename='logs/app.log',  # log file
                    filemode='w')  

#Constant variables
OUTPUT_FILE_NAME= f"outputs/transactional_data_data_generator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avro"  #output file
SHOPPER_ID_LENGTH=5  #number of digits in the Shopper_id
PRODUCT_ID_LENGTH=3  #number of digits following the first letter in the product_id


# Function to generate a random string of K digits
def generate_shopper_id(length):
    return ''.join(random.choices(string.digits, k=length))

# Function to generate a random string of the format 'XDDD...' where X is a letter and D is a digit, the number of digits 
def generate_product_id(length):
    return random.choice(string.ascii_uppercase) + ''.join(random.choices(string.digits, k=length))

# Function to generate a random date within a given range of days
def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

# Function to generate random data for a product, type == 1, the product is a merchandise
def generate_product(config:Config, type: int):
    product_id = generate_product_id(PRODUCT_ID_LENGTH)
    unit_ati_amount = round(random.uniform(config.unit_ati_amount_range[0], config.unit_ati_amount_range[1]), 2)
    return {"product_id": product_id, "unit_ati_amount": unit_ati_amount, "type": type}

#Function to generate all possible products 
def generate_all_products(config:Config) :
    all_products = []
    total_products = config.total_products 
    # Calculate the maximum number of service products allowed (percent_services of total)
    max_service_products = int(total_products * (config.percent_services /100))
    for i in range(total_products) :
        if i < max_service_products :
            prod = generate_product(config, 2)
        else :
            prod = generate_product(config, 1)

        all_products.append(prod)
    
    # Shuffle the products list to randomize the order of products
    random.shuffle(all_products)
 
    return all_products


def update_products_add_quantity(cart, max_quantity) :
    for prod in cart :
        prod['quantity'] = random.randint(1, max_quantity) if prod['type'] == 1 else None
    return cart

# Function to generate random data for a transaction
def generate_transactions_per_shopper(config:Config,shopper_id, products):

    transaction_date = random_date(config.start_date, config.end_date)
    transaction_status= random.choice(config.transaction_status)
    
    #random number of purchased products
    cart_size = random.randint(1, config.max_cart_size)

    #select a set products for this shopper
    cart = random.sample(products, cart_size)

    #products could be marchandises or services. In the specific case of a service, the product quantity is set to None
    cart= update_products_add_quantity(cart, config.max_prod_quantity)

    #Computing final ati_amount based on purchased products data
    final_ati_amount = round(sum(product['unit_ati_amount'] * (product['quantity'] if product['quantity'] is not None else 1) for product in cart), 2)
                         
    return {"shopper_id": shopper_id, "transaction_date": transaction_date.strftime('%Y-%m-%d'),
            "order_status": transaction_status, "final_ati_amount":final_ati_amount ,
            "products": cart}

# Function to generate data for a set of clients
def generate_data(config:Config, products):
    data = []
    for _ in range(config.num_clients):
        shopper_id=generate_shopper_id(SHOPPER_ID_LENGTH)
        for _ in range(random.randint(1, config.max_transactions)): # random number of transactions per shopper choosen with the fixed rang
            transaction = generate_transactions_per_shopper(config,shopper_id, products)
            data.append(transaction)
    return data

# # Function to save data to a CSV file
# def save_to_csv(data, filename):
#     with open(filename, 'w', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         # Header row
#         writer.writerow(["shopper_id", "transaction_date", "order_status", "final_ati_amount", "product_id", "unit_ati_amount", "quantity"])

#         for transaction in data:
#             # Write each product in the transaction to CSV file
#             for product in transaction["products"]:
#                 writer.writerow([transaction["shopper_id"], transaction["transaction_date"], transaction["order_status"], str(transaction["final_ati_amount"]), product["product_id"], str(product["unit_ati_amount"]), str(product["quantity"])])


# Function that saves the data into an Avro file
def save_to_avro(data, filename):
    schema = avro.schema.parse("""
        {
            "type": "record",
            "name": "Transaction",
            "fields": [
                {"name": "shopper_id", "type": "string"},
                {"name": "transaction_date", "type": "string"},
                {"name": "order_status", "type": "string"},
                {"name": "final_ati_amount", "type": "double"},
                {
                    "name": "products",
                    "type": {
                        "type": "array",
                        "items": {
                            "type": "record",
                            "name": "Product",
                            "fields": [
                                {"name": "product_id", "type": "string"},
                                {"name": "unit_ati_amount", "type": "double"},
                                {"name": "type", "type": "int"},
                                {"name": "quantity", "type": ["int", "null"], "default": null}
                            ]
                        }
                    }
                }
            ]
        }
    """) 
    with open(filename, 'wb') as avrofile:
        writer = DatumWriter(schema)
        writer = DataFileWriter(avrofile, writer, schema)
        for transaction in data:
            writer.append(transaction)



def main():
    try :
        logging.info("Reading the mandatory configuration values required for data generation")
        config=Config()

        logging.info("Start generating the products list")
        products=generate_all_products(config)
        
        count_service=0
        for prod in products :
            if prod['type'] == 2 : count_service+= 1
        logging.info('%d products were generated, where %d are services',len(products), count_service)

        logging.info("Start generating the transactional data")
        data=generate_data(config, products)
        logging.info("%d transactions were generated", len(data))

        
        logging.info("Saving the data into Avro file")
        save_to_avro(data, OUTPUT_FILE_NAME)
        
        logging.info("End of operations")


    except Exception as e :
        logging.error("An error occured during the data generation operation %s", str(e)) 


if __name__ == "__main__":
    main()

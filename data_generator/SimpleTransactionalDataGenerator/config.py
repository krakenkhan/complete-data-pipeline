""" This is a utility class to wrap up the values of different needed variables for the data generation operation
"""

import os
from datetime import datetime
from dotenv  import load_dotenv

class Config:
    def __init__(self, env_file=".env"):
        self.env_file = env_file
        self.load_env_variables()

    def load_env_variables(self):
        #Load the environment variables file
        try :
            load_dotenv(self.env_file, override=True)
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not find the .env file: {self.env_file}")
        
        # Read environment variables and check for missing of None values
        self.start_date = self.read_config_value("START_DATE")
        self.end_date = self.read_config_value("END_DATE")
        self.num_clients = self.read_config_value("NUMBER_CLIENTS")
        self.max_transactions = self.read_config_value("MAX_CLIENT_TRANSACTIONS")
        self.max_cart_size = self.read_config_value("MAX_CART_SIZE")
        self.max_prod_quantity = self.read_config_value("MAX_PRODUCT_QUANTITY")
        self.unit_ati_amount_range = self.read_config_value("UNIT_ATI_AMOUNT_RANGE")
        self.total_products = self.read_config_value("TOTAL_PRODUCTS")
        self.percent_services = self.read_config_value("SERVICES_PERCENT")
        self.transaction_status = self.read_config_value("TRANSACTION_STATUS")
        # Validate and convert variables
        self.validate_and_convert()

    def validate_and_convert(self):
        # Convert variables to appropriate types
        try:
            self.num_clients = int(self.num_clients)
            self.max_transactions= int(self.max_transactions)
            self.max_cart_size = int(self.max_cart_size)
            self.max_prod_quantity = int(self.max_prod_quantity)
            self.total_products = int(self.total_products)
            self.percent_services = int(self.percent_services)
            self.unit_ati_amount_range = list(map(float, self.unit_ati_amount_range.split(',')))
            self.transaction_status = self.transaction_status.split(',')
            
            # Validating date format
            self.start_date= self.validate_date_format("START_DATE")
            self.end_date = self.validate_date_format("END_DATE")
        except ValueError as e:
            raise ValueError(f"Error converting environment variables: {str(e)}")
        
    def read_config_value(self,key) :
        if os.getenv(key) is None or not os.getenv(key) :
            raise ValueError(key+ " value is missing.")
        return os.getenv(key)

    # Function to validate the date format
    def validate_date_format(self, key):
        try:
            return datetime.strptime(os.getenv(key), '%Y-%m-%d')
        except ValueError:
            raise ValueError(key+ "has invalid date format. Please use datetime format 'yyyy-mm-dd'.")

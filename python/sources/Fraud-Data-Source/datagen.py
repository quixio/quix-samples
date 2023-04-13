import pathlib
import os
import json
from multiprocessing import cpu_count
import datagen_transaction
from datagen_customer import main as datagen_customers
from datagen_transaction import main as datagen_transactions


producer_topic_name = os.environ["producer_topic"]

# -n 10 -o '' 01-01-2021 01-02-2022
if __name__ == '__main__':

	nb_customers_value = os.getenv("nb_customers")
	seed_value = 42	 # os.getenv("seed")
	start_date_value = os.getenv("start_date")
	end_date_value = os.getenv("end_date")
	use_transaction_date_as_timestamp_value = os.getenv("use_transaction_date")
	
	num_cust = datagen_transaction.valid_int(nb_customers_value)
	seed_num = datagen_transaction.valid_int(seed_value)
	start_date = datagen_transaction.valid_date(start_date_value)
	end_date = datagen_transaction.valid_date(end_date_value)
	config = "./profiles/main_config.json"	#os.environ["config"]
	customer_file = None
	use_transaction_date_as_timestamp = datagen_transaction.valid_boolean(use_transaction_date_as_timestamp_value)
	
	customers_out_file = customer_file or 'customers.csv'

	if num_cust < 5: 
		print("Minimum of 5 customers required. Defaulting to 5 customers.")
		num_cust = 5;

	# if no customers file provided, generate a customers file
	if customer_file is None and num_cust is not None:
		datagen_customers(num_cust, seed_num, config, customers_out_file)
	if customer_file is None and num_cust is None:
		print('Either a customer file or a number of customers to create must be provided')
		exit(1)
	
	# if we're supplied with a customer file, we need to figure how many we have
	if customer_file is not None:
		num_cust = 0
		with open(customer_file, 'r') as f:
			for row in f.readlines():
				num_cust += 1

	# figure out reasonable chunk size
	num_cpu = cpu_count()
	# num_cpu = 1
	
	print(f"Num CPUs: {num_cpu}")
	chunk_size = max(min(int(num_cust / 5), 1000), 1000 * int(num_cust / (1000 * num_cpu)))
	# because from one profile to another, there may be a 10-50x difference in size, it is best to use small
	# chunk sizes so as to spread the work across all CPUs. Bigger chunks means a core may process small profiles 
	# quickly and then be idle, while other cores process large profiles. Smaller chunks will run faster
	
	# zero padding determination
	zero_pad = len(str(num_cust - 1))

	# read config
	with open(config, 'r') as f:
		configs = json.load(f)

	profile_names = configs.keys()

	# args_array = []
	for profile_file in configs.keys():
		customer_file_offset_start = 0
		customer_file_offset_end = min(num_cust - 1, chunk_size - 1)
		while customer_file_offset_start <= max(num_cust - 1, chunk_size):
			print(f"profile: {profile_file}, chunk size: {chunk_size}, \
				chunk: {customer_file_offset_start}-{customer_file_offset_end}")
			transactions_filename = profile_file.replace('.json',
					f'_{str(customer_file_offset_start).zfill(zero_pad)}-{str(customer_file_offset_end).zfill(zero_pad)}')

			customer_file_offset_start += chunk_size
			customer_file_offset_end = min(num_cust - 1, customer_file_offset_end + chunk_size)

			datagen_transactions(customers_out_file, pathlib.Path(os.path.join('profiles', profile_file)), 
				start_date, end_date, transactions_filename, customer_file_offset_start, 
				customer_file_offset_end, producer_topic_name, use_transaction_date_as_timestamp)


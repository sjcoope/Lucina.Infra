from faker import Factory
import uuid
import boto3, random, csv, tqdm, time, botocore
from botocore.exceptions import ClientError
from tqdm import trange

aws_session = boto3.Session()
db_r = aws_session.resource('dynamodb')

fake = Factory.create()

def generate_item():
    fake_profile = fake.profile()
    operation = random.randint(1,3)

    item = {}
    item['id'] = uuid.uuid4().hex
    item['origin'] = fake.text(max_nb_chars=50)

    if operation == 1:
        item['sex'] = 'M'
        item['name'] = fake.first_name()
    elif operation == 2:
        item['sex'] = 'F'
        item['name'] = fake.first_name_female()
    else:
        item['sex'] = 'A'
        item['name'] = fake.first_name()

    return item

if __name__ == "__main__":

    table_name = raw_input("Enter the name of the table to write data to: ")
    record_count = raw_input("Enter the number of records you would like to create: ")
    print("Create sample data in table: " + table_name)

    # Write to the table
    with db_r.Table(table_name).batch_writer() as batch:
            for c in trange(int(record_count), desc="Generated data..."):
                batch.put_item(Item=generate_item())
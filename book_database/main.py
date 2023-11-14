
import logging

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from question import Question

logger = logging.getLogger(__name__)

class Books:
    """
    DynamoDB Table: Books (table name: bitset-bookshelf)
    """

    def __init__(self, dyn_resource):
        self.dyn_resource = dyn_resource
        self.table = None


    def exists(self, table_name):
        """
        Checks if table exists
        :param table_name: name of the table
        :return: True if table exists, False otherwise
        """
        try:
            table = self.dyn_resource.Table(table_name)
            table.load()
            exists = True
        except ClientError as err:
            if err.response["Error"]["Code"] == "ResourceNotFoundException":
                return False
            else:
                logger.error(
                    "Couldn't check for existence of %sd. Here's why: %s: %s",
                    table_name,
                    err.response["Error"]["Code"],
                    err.response["Error"]["Message"],
                )
                raise err
        else:
            self.table = table
        return exists
            

    def create_table(self, table_name):
        """
        Creates DynamoDB table
        :param table_name: name of the table
        :return: created table
        """
        try:
            self.table = self.dyn_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {"AttributeName": "id", "KeyType": "HASH"}, # Partition key
                    {"AttributeName": "title", "KeyType": "RANGE"} # Sort key
                ],
                AttributeDefinitions=[
                    {"AttributeName": "id", "AttributeType": "N"},
                    {"AttributeName": "title", "AttributeType": "S"}
                ],
                ProvisionedThroughput={
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5
                },
            )
            self.table.wait_until_exists()
        except ClientError as err:
            logger.error(
                "Couldn't create %s. Here's why: %s: %s",
                table_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise err
        else:
            return self.table


    def list_tables(self):
        """
        Lists all DynamoDB tables
        :return: list of tables
        """
        try:
            tables = []
            for table in self.dyn_resource.tables.all():
                tables.append(table)
        except ClientError as err:
            logger.error(
                "Couldn't list tables. Here's why: %s: %s",
                err.response["Error"]["code"],
                err.response["Error"]["Message"],
            )
            raise err
        else:
            return tables
        

    def write_batch(self, books):
        try:
            with self.table.batch_writer() as writer:
                for book in books:
                    writer.put_item(Item=book)
        except ClientError as err:
            logger.error(
                "Couldn't write data into table %s. Here's why: %s: %s",
                self.table.name,
                err.response["Error"]["code"],
                err.response["Error"]["Message"],
            )
            raise err


    def add_book(self, id, title, author, publisher, location=""):
        """
        Adds a book to the table
        :param title: title of the book
        :param author: author of the book
        :param publisher: publisher of the book
        :param location: location of the book
        :return: True if book was added, False otherwise
        """
        try:
            self.table.put_item(
                Item={
                    "id": id,
                    "title": title,
                    "author": author,
                    "publisher": publisher,
                    "location": location
                }
            )
        except ClientError as err:
            logger.error(
                "Couldn't add book %s. Here's why: %s: %s",
                title,
                err.response["Error"]["code"],
                err.response["Error"]["Message"],
            )
            raise err
        else:
            return True


    def get_book(self, title, id):
        """
        Gets a book from the table
        """
        try:
            response = self.table.get_item(Key={"id": id, "title": title})
        except ClientError as err:
            logger.error(
                "Couldn't get movie %s from table %s. Here's why: %s: %s",
                title,
                self.table.name,
                err.response["Error"]["code"],
                err.response["Error"]["Message"],
            )
            raise err
        else:
            return response["Item"]
        
    

if __name__ == "__main__":
    table_name = "bitset-bookshelf"

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    dyn_resource = boto3.resource("dynamodb", region_name="ap-northeast-3") # osaka region
    books = Books(dyn_resource)
    books_exists = books.exists(table_name)
    if not books_exists:
        books.create_table(table_name)
        books_exists = books.exists(table_name)
    
    my_book =  Question.ask_questions(
        [
            Question("id", "What is the id of the book?", Question.is_int),
            Question("title", "What is the title of the book?", Question.non_empty),
            Question("author", "Who is the author of the book?", Question.non_empty),
            Question("publisher", "Who is the publisher of the book?", Question.non_empty),
        ]
    )
    books.add_book(**my_book)
    print(f"\nAdded '{my_book['title']}' to '{books.table.name}'.")
    print("-" * 88)

    

    
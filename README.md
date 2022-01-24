# DynamoDB DynamoDB Replica Data - Real Time

This project aims to replicate real-time data from Production DynamoDB to the Disaster Recovery Environment, maintaining data synchronization between tables in real time, it is worth remembering that the Production environment table must also exist in the Disaster environment Recovery.

### Responsibilities do DynamoDB Replica Data 

The service of this repository is responsible for receiving a record from DynamoDB at each event change, whether the event INSERT, MODIFY and REMOVE, in an orderly manner, generating a new record in the Stream associated with the table.

The service only receives the event, identifies and replicates it to the Disaster Recovery environment, if an error occurs at the time of replication, the service manually moves the message to the SQS and we will receive an alert via DataDog in the DR monitoring group.

The service as a whole includes the following architecture below:

![alt text](https://github.com/jeffersonrodrigues92/dynamodb-stream-sender/blob/master/arquitetura.jpeg)

This project works with the following technologies:

- [AWS Lambda](https://docs.aws.amazon.com/lambda/)
- [AWS SQS FIFO](https://docs.aws.amazon.com/sqs/)
- [AWS DynamoDB](https://docs.aws.amazon.com/dynamodb/)
- [AWS DynamoDB Strems](https://docs.aws.amazon.com/dynamodb/)

### Language

- Python
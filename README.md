# DynamoDB Replicação de Dados em Tempo Real

Esse projeto tem o intuito de replicar dados em tempo real do DynamoDB de Produção para o Ambiente de Disaster Recovery, mantendo a sincronização de dados entre as tabelas em tempo real, vale lembrar que a tabela do ambiente de Produção deve existir também no ambiente de Disaster Recovery.

O serviço ao todo contempla a seguinte arquitetura abaixo:

![alt text](https://github.com/cdt-baas/dynamodb-replica-data/blob/master/arquitetura.jpg)

Esse projeto trabalha com as seguintes tecnologias:

- [AWS Lambda](https://docs.aws.amazon.com/lambda/)
- [AWS SQS FIFO](https://docs.aws.amazon.com/sqs/)
- [AWS DynamoDB](https://docs.aws.amazon.com/dynamodb/)
- [AWS DynamoDB Strems](https://docs.aws.amazon.com/dynamodb/)


### Linguagem de Desenvolvimento

- Python

### Responsabilidades do DynamoDB Replica Data 

O serviço desse reposositório é responsável por receber a cada mudança de evento um registro do DynamoDB, seja o event INSERT, MODIFY e REMOVE, de forma ordenada gerando um novo registro no Stream associado a tabela.

O serviço apenas recebe o evento, idenfica e replica para o ambiente de Disaster Recovery, caso no momento da replicação aconteça algum erro movemos a mensagem manualmente para o SQS e receberemos um alerta via DataDog no grupo de monitoração do DR.


## Author

* **Jefferson Rodrigues** - *Initial work* - [PurpleBooth](https://github.com/jeffersonrodrigues1992)

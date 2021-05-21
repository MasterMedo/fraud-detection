match (account:Account)-[relationship]-()
with account, count(relationship) as cnt
where cnt > 4 and account.type = 'personal'
return account
limit 1;

match (:Account)-[:IDENTIFIES_WITH|:HAS_PHONE]->(shared)<-[]-(:Account)
with distinct shared
match (shared)-[r]-()
with shared, count(r) as relationships
return shared
order by relationships desc
limit 1;

MATCH (:Account)-[:IDENTIFIES_WITH|:HAS_PHONE]->(shared)<-[]-(:Account)
WITH DISTINCT shared
MATCH (shared)<-[]-(:Account)-[]->(:CreditCard)-[]->(transaction:Transaction)
SET transaction.fraudulent = True;

MATCH (person:CreditCard)-[:SENT]->(transaction:Transaction)<-[:RECEIVED]-(business:CreditCard)
CALL distance_calculator.single(person, transaction, 'km') YIELD distance
WITH distance, transaction, person, business
WHERE
  distance > 1000
  AND transaction.amount > 100
  AND transaction.fraudulent = true
RETURN person, transaction
LIMIT 1

MATCH (:Account {type: 'business'})-->(business:CreditCard)
      -[r]->(transaction:Transaction)
WITH business,
     collect(transaction) AS transactions,
     sum(CASE WHEN transaction.fraudulent THEN 1 ELSE 0 END) AS amount
WHERE ALL(transaction IN transactions WHERE transaction.amount < 200)
WITH business
ORDER BY amount DESC
LIMIT 1
MATCH (business)-->(:Transaction {fraudulent: True})<-[:SENT]-(person)
MATCH (business)-[received]->(btransaction:Transaction)
MATCH (person)-[sent]->(ptransaction:Transaction)
RETURN business, person, btransaction, ptransaction, sent, received

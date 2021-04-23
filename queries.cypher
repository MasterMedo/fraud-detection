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

match (:Account)-[:IDENTIFIES_WITH|:HAS_PHONE]->(shared)<-[]-(:Account)
with distinct shared
match (shared)<-[]-(:Account)-[]->(:CreditCard)-[]->(transaction:Transaction)
set transaction.fraudulent = True;

match (account:Account {type: 'business'})
return account
limit 1;

match (location:Location)<--(Account)-->(CreditCard)
      -[:SENT]->(transaction:Transaction)
call distance_calculator.single(location, transaction, 'km') yield distance
with distance, transaction, location
where
  distance > 200
  and transaction.amount > 100
  and transaction.fraudulent = true
return transaction, location
limit 1

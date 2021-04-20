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

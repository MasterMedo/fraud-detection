CREATE INDEX ON :Account(id);
CREATE INDEX ON :Identification(id);
CREATE INDEX ON :Location(id);
CREATE INDEX ON :CreditCard(id);
CREATE INDEX ON :PhoneNumber(id);
CREATE INDEX ON :Transaction(id);

CREATE CONSTRAINT ON (n:Account) ASSERT n.id IS UNIQUE;
CREATE CONSTRAINT ON (n:Identification) ASSERT n.id IS UNIQUE;
CREATE CONSTRAINT ON (n:Location) ASSERT n.id IS UNIQUE;
CREATE CONSTRAINT ON (n:CreditCard) ASSERT n.id IS UNIQUE;
CREATE CONSTRAINT ON (n:PhoneNumber) ASSERT n.id IS UNIQUE;
CREATE CONSTRAINT ON (n:Transaction) ASSERT n.id IS UNIQUE;

LOAD CSV FROM '/accounts.csv' WITH HEADER AS row
CREATE (account:Account {id: row.account_id})
CREATE (card:CreditCard {id: row.card_number})
MERGE (identification:Identification {id: row.identification_id})
MERGE (location:Location {id: row.zipcode})
MERGE (phone:PhoneNumber {id: row.phone})
SET account += {
  type: row.account_type,
  created: tofloat(row.created)
}

SET identification += {
  name: row.name,
  birthday: tofloat(row.birthday)
}
SET location += {
  zipcode: row.zipcode,
  city: row.city,
  state: row.state,
  lng: tofloat(row.longitude),
  lat: tofloat(row.latitude)
}
SET card += {
  number: row.card_number,
  type: row.card_type,
  lng: tofloat(row.longitude),
  lat: tofloat(row.latitude)
}
SET phone += {
  number: row.phone
}
CREATE (account)-[:IDENTIFIES_WITH]->(identification)
CREATE (account)-[:HAS_PHONE]->(phone)
CREATE (account)-[:LOCATED_IN]->(location)
CREATE (account)-[:HAS_CARD]->(card);

LOAD CSV FROM '/transactions.csv' WITH HEADER AS row
MATCH (card_from:CreditCard {id: row.from})
MATCH (card_to:CreditCard {id: row.to})
      <-[:HAS_CARD]-()
      -[:LOCATED_IN]->(location)
CREATE (transaction:Transaction {
  id: row.id,
  created: tofloat(row.created),
  amount: tofloat(row.amount),
  lat: tofloat(location.lat),
  lng: tofloat(location.lng)
})
CREATE (card_from)-[:SENT]->(transaction)<-[:RECEIVED]-(card_to);

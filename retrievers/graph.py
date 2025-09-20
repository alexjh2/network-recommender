from neo4j import GraphDatabase

def find_connections_2_hops(uri, user, password, user_id):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    """
    query = '''
        MATCH (p:Person {id: $user_id})-[:ATTENDED*1..2]-(connection:Person)
        WHERE connection.id <> $user_id
        RETURN DISTINCT connection.id AS user_id
    '''
    
    query = '''
        MATCH (p:Person)
        WHERE toString(p.id) = $user_id
        MATCH (p)-[:ATTENDED*1..2]-(connection:Person)
        WHERE toString(connection.id) <> $user_id
        RETURN DISTINCT toString(connection.id) AS user_id
    '''
    """

    query = '''
        MATCH (p:Person)-[:ATTENDED]->(o:Org)<-[:ATTENDED]-(other:Person)
        WHERE toString(p.id) = $user_id AND toString(other.id) <> $user_id
        RETURN DISTINCT toString(p.id) AS from_id, toString(o.name) AS rel_type, toString(other.id) AS to_id
    '''

    with driver.session() as session:
        results = session.run(query, user_id=user_id)
        return [(record["from_id"], record["rel_type"], record["to_id"]) for record in results]
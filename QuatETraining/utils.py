import numpy as np
import pandas as pd
import pandas as pd
import rdflib

def load_ttl_files(pathfilename):
    tmp = []
    df = pd.DataFrame(columns=['s', 'p', 'o'])
    g = rdflib.Graph()
    g.parse(pathfilename, format = 'ttl')
    for s, p, o in g:
      tmp.append((s, p, o))
    df = pd.DataFrame(tmp, columns=['s', 'p', 'o'])
 
    return df

#check for ¬∃s, o : skos:related(s, o) ∧ skos:broader(s, o) constraint
#remove and store violating ones separetely
def has_hierarcy_associative_clash(df):
    violating_triples = []
    negative_df = pd.DataFrame(columns=['s', 'p', 'o'])
    updated_kg = pd.DataFrame(columns=['s', 'p', 'o'])
    related = rdflib.URIRef("http://www.w3.org/2004/02/skos/core#related")
    broader = rdflib.URIRef("http://www.w3.org/2004/02/skos/core#broader")

    for _, row in df.iterrows():
        concept = row['s']
        relation = row['p']
        other_concept = row['o']
 
        if relation == related :
            
            if df[(df['s'] == other_concept) & (df['p'] == broader ) & (df['o'] == concept)].shape[0] > 0:
                violating_triples.append((concept, relation, other_concept))
                violating_triples.append((other_concept, broader, concept))
       

    if violating_triples:
      updated_kg, negative_df = remove_and_update_kg(df,negative_df,violating_triples)     
  
    else:
      print("Hiearchy is consistent in terms of hierarcical & associative links clashes")

    return updated_kg, negative_df 


def remove_and_update_kg(kg, negative_df, violating_triples):
    violating_triples = pd.DataFrame(violating_triples, columns=['s', 'p', 'o'])

    for _, violating_triple in violating_triples.iterrows():
        s = violating_triple['s']
        p = violating_triple['p']
        o = violating_triple['o']
        kg = kg[~((kg['s'] == s) & (kg['p'] == p) & (kg['o'] == o))].reset_index(drop=True)

        negative_df = negative_df.append(violating_triple, ignore_index=True)

    return kg, negative_df


#train,test and valid set splits
def split_dataset(df):
    df_shuffled = df.sample(frac=1, random_state=42)
    
    total_samples = df_shuffled.shape[0]
    train_size = int(0.8 * total_samples)
    valid_size = int(0.1 * total_samples)
    test_size = total_samples - train_size - valid_size
    
    df_train = df_shuffled.iloc[:train_size]
    df_valid = df_shuffled.iloc[train_size:train_size + valid_size]
    df_test = df_shuffled.iloc[train_size + valid_size:]
    
    return df_train, df_valid, df_test


#entity and rel to id
def convert_to_id_files(df):
    entities_s = pd.DataFrame({'e':[]})
    entities_o = pd.DataFrame({'e':[]})
    # Extract unique entities and relations
    entities_s['e'] = df['s'] 
    entities_o['e'] = df['o'] 
    entities_all = pd.concat([entities_s ,entities_o],ignore_index=True).reset_index()
    relations = df['p'].drop_duplicates() 
    entities = entities_all['e'].drop_duplicates() 

    e_to_id = {}
    rel_to_id = {}

    # Save entity IDs to a text file
    with open('entity2id.txt', 'w') as entity_file:
        entity_file.write(f"{len(entities)}\n")
        for idx, entity in enumerate(entities):
            entity_file.write(f"{entity}\t{idx}\n")
            e_to_id[entity] = idx

    # Save relation IDs to a text file
    with open('relation2id.txt', 'w') as relation_file:
        relation_file.write(f"{len(relations)}\n")
        for idx, relation in enumerate(relations):
            relation_file.write(f"{relation}\t{idx}\n")
            rel_to_id[relation] = idx
    return e_to_id, rel_to_id

#train,test and valid to id
def convert_triples_to_id_files(entity_to_id, relation_to_id,df,text_df):

    # Save triple IDs to a text file
    with open(text_df, 'w') as triples_file:
        triples_file.write(f"{len(df)}\n")
        for _, row in df.iterrows():
            subject_id = entity_to_id[row['s']]
            relation_id = relation_to_id[row['p']]
            object_id = entity_to_id[row['o']]
            triples_file.write(f"{subject_id}\t{object_id}\t{relation_id}\n")

#for inferring TPR-followed implicit true positives
#L0 and L1 levels of hiearchy manually constracted 
#we are considering these levels noise-free
def top_2_hierarchy_triples(kg_df):
    broader = rdflib.URIRef("http://www.w3.org/2004/02/skos/core#broader")
    broader_triples = kg_df[(kg_df['p'] == broader)]

    bottom_h_entities = set(kg_df['o']) - set(broader_triples['s'])
    triples_generator = find_top_2_hierarchy(bottom_h_entities, 0, broader_triples)
    top_2_hierarchy_triples = pd.DataFrame(triples_generator, columns=['s', 'p', 'o'])
    return top_2_hierarchy_triples

def find_top_2_hierarchy(entities, level, kg_df):
    if level == 2:  # Limit the depth to 2 levels
        return
    next_entities = set()
    for entity in entities:
        rows = kg_df[kg_df['o'] == entity]
        for _, row in rows.iterrows():
            yield (row['s'], row['p'], row['o'])
            next_entities.add(row['s'])
    yield from find_top_2_hierarchy(next_entities, level + 1, kg_df)



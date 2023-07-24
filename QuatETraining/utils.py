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


def has_hierarcy_associative_clash(df):
    violating_triples = []
    negative_df = pd.DataFrame(columns=['s', 'p', 'o'])
    updated_kg = pd.DataFrame(columns=['s', 'p', 'o'])

    for _, row in df.iterrows():
        concept = row['s']
        relation = row['p']
        other_concept = row['o']

        if relation == "http://www.w3.org/2004/02/skos/core#related" :
            if df[(df['s'] == other_concept) & (df['p'] == "http://www.w3.org/2004/02/skos/core#broader" ) & (df['o'] == concept)].shape[0] > 0:
                violating_triples.append((concept, relation, other_concept))
                violating_triples.append((other_concept, "http://www.w3.org/2004/02/skos/core#broader", concept))


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



def convert_to_id_files(df):
    # Extract unique entities and relations
    entities = df['entity'].unique()
    relations = df['relation'].unique()

    # Save entity IDs to a text file
    with open('entity_ids.txt', 'w') as entity_file:
        for idx, entity in enumerate(entities):
            entity_file.write(f"{entity}\t{idx}\n")

    # Save relation IDs to a text file
    with open('relation_ids.txt', 'w') as relation_file:
        for idx, relation in enumerate(relations):
            relation_file.write(f"{relation}\t{idx}\n")

def convert_triples_to_id_files(df,text_df):
    # Create dictionaries to map entities and relations to their IDs
    entity_to_id = {}
    relation_to_id = {}

    # Extract unique entities and relations
    entities = df['entity'].unique()
    relations = df['relation'].unique()

    # Assign IDs to entities and relations
    for idx, entity in enumerate(entities):
        entity_to_id[entity] = idx

    for idx, relation in enumerate(relations):
        relation_to_id[relation] = idx

    # Save triple IDs to a text file
    with open(text_df, 'w') as triples_file:
        for _, row in df.iterrows():
            subject_id = entity_to_id[row['entity']]
            relation_id = relation_to_id[row['relation']]
            object_id = entity_to_id[row['object']]
            triples_file.write(f"{subject_id}\t{object_id}\t{relation_id}\n")

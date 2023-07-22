import numpy as np
import pandas as pd

def load_ttl_files(pathfilename):
    
    nt_file = open(pathfilename,'r')
    lines   = nt_file.readlines()

    entity_dict = dict({'s':[],'o':[],'p':[]})

    for line in lines:
      init_part = line[0]
      if init_part == '\n' or init_part == '\t' or init_part == '@':
        continue
      else:
        parts = line.split(' ')
        entity_dict['s'].append(parts[0])
        entity_dict['p'].append(parts[1])
        entity_dict['o'].append(parts[2])

    df = pd.DataFrame(entity_dict)

    return df


def has_hierarcy_associative_clash(df):
    violating_triples = []
    negative_data = {
        's': [],
        'p': [],
        'o': []
    }
    negative_df = pd.DataFrame(negative_data)

    negative_df = []
    for _, row in df.iterrows():
        concept = row['s']
        relation = row['p']
        related_concept = row['o']

        if relation.startswith("skos:"):
            opposite_relation = "skos:related" if relation == "skos:broader" else "skos:broader"
            if df[(df['s'] == concept) & (df['p'] == opposite_relation) & (df['o'] == related_concept)].shape[0] > 0:
                violating_triples.append((concept, relation, related_concept))
                violating_triples.append((concept, opposite_relation, related_concept))
            clashes = df[(df['s'] == concept) & (df['p'] == 'skos:related')]['o']
            if related_concept in clashes.values:
                violating_triples.append((concept, relation, related_concept))
                violating_triples.append((concept, opposite_relation, related_concept))

    if violating_triples:
        updated_kg, negative_df = remove_and_update_kg(df,negative_df,violating_triples)
  
    else:
      print("Hiearchy is consistent in terms of hierarcical & associative links clashes")

    return updated_kg, negative_df 


def remove_and_update_kg(kg, negative_df, violating_triples):
    for violating_triple in violating_triples:
        condition = (
            (kg['s'] == violating_triple['s']) &
            (kg['p'] == violating_triple['p']) &
            (kg['o'] == violating_triple['o'])
        )
        kg = kg[~condition].reset_index(drop=True)

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

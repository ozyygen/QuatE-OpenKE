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


def convert_to_df_dict(df):
    hierarchy_dict = {}

    for _, row in df.iterrows():
        concept = row['s']
        relation = row['p']
        other_concept = row['o']
        if concept in hierarchy_dict:
        # append the new number to the existing array at this slot
          hierarchy_dict[concept].append(line[1])
        else:
        # create a new array in this slot
          hierarchy_dict[line[0]] = [line[1]]
      
    
    return hierarchy_dict


def has_hierarcy_associative_clash(df):
    inconsistent_triples = []

    for _, row in df.iterrows():
        concept = row['s']
        relation = row['p']
        related_concept = row['o']

        if relation.startswith("skos:"):
            opposite_relation = "skos:related" if relation == "skos:broader" else "skos:broader"
            if df[(df['s'] == concept) & (df['p'] == opposite_relation) & (df['o'] == related_concept)].shape[0] > 0:
                inconsistent_triples.append((concept, relation, related_concept))
                inconsistent_triples.append((concept, opposite_relation, related_concept))
            clashes = df[(df['s'] == concept) & (df['p'] == 'skos:related')]['o']
            if related_concept in clashes.values:
                inconsistent_triples.append((concept, relation, related_concept))
                inconsistent_triples.append((concept, opposite_relation, related_concept))

    if inconsistent_triples:
        print("Inconsistent Triples:")
        count = 0
        for triple in inconsistent_triples:
            count = count + 1
            print(f"{triple[0]} {triple[1]} {triple[2]}")
            if count == 2:
              break
    else:
      print("Hiearchy is consistent in terms of hierarcical & associative links clashes")


def has_transitive(df):
    violations = []

    for _, row in df.iterrows():
        concept = row['s']
        relation = row['p']
        related_concept = row['o']

        if relation == "skos:broader":
            transitive_concepts = df[df['s'] == related_concept]['o']
            related_concepts = df[df['s'] == concept]['o']
            
            i = list(set(transitive_concepts).intersection(related_concepts))
            for element in i:
              if (df[df['s'] == element]['p'] == "skos:broader") and ( df[df['s'] == element]['s'] == concept):
                  violations.append((concept, relation, related_concept))
                  violations.append((concept, relation, i[0]))
        
    if violations:
      print("Transitivity Violations:")
      count = 0
      for violation in violations:
        count = count + 1
        #print(f"{violation[0]} {violation[1]} {violation[2]}")
        if count == 3:
              break
    else:
      print("Hiearachy is consistent in terms of transitivity") 


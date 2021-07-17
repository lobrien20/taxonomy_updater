#!/usr/bin/envs python3
# updates the taxonomy of scripts. FIrst argument is the list of strains/species. Second argument is output directory

# "_" indented list!!!
import sys,os

from ete3 import NCBITaxa
import os.path
ncbi = NCBITaxa()

# Checks if output directory exists as folder or file
dir_made_or_not = os.path.isdir(sys.argv[2]) # boolean for if it exists as directory
is_file = os.path.isfile(sys.argv[2]) # boolean for if it exists as file

if dir_made_or_not == False: # is its not already a directory
    
    if is_file == False: # if its not already a file
        os.mkdir(sys.argv[2]) # creates directory
        print("Creating directory" + " " + sys.argv[2])
    else: # if it is already a file, runs exit
        print("There is a file where the directory is. Exiting.")
        exit()

else:
    print("Directory already exists. Continuing anyway...")

# Give a list as a txt file and loop over this list to identify the full taxonomic lineage

strain_file = open(sys.argv[1], "r")
strain_list = strain_file.readlines()

failed_taxos_list = []
taxo_dict = {}

taxa_csv_path = sys.argv[2] + "/" + "identified_taxonomies.csv"
taxonomy_list = open(taxa_csv_path, "w") # Generates new taxonomy list in tsv format
taxonomy_list.write("kingdom,phyla,class,order,family,genus,species,strain\n") # Adds columns to this

old_name_list = [] # to create list of original names
new_name_list = [] # to create list of new names

for strain in strain_list: # loops over the stains on list 

    strain_stripped = strain.strip() # removes any crap '\n' etc.
    print(strain_stripped)
    split_name = strain_stripped.split("_") # splits the name by the hyphen indented list 


    number_of_splits = len(split_name) # length of split names
    failed_taxo_count = 0 # Count for how many times the next loop has checked whether the name given has been searhced through the ncbi taxonomy
    # Next loop works via counting the number of hyphens in the name, then checking the name through the ncbi taxononmy. First as full name, then with the last hyphen part removed etc etc
    # idea is want the most taxonomic information, thus start from the end. 
    for i in range(number_of_splits): 
        ni = 0 - i
        if ni == 0:
            testing_list = split_name[0:]
        else:
            testing_list = split_name[0:ni]

        testing_name = ' '.join(testing_list)
        print(testing_name)

        name2taxid = ncbi.get_name_translator([testing_name]) # this is what checks it in the ncbi taxonomy

        try:
            item = name2taxid[testing_name] # if it found something taxonomy will be activated
            is_fail = 0

            break # breaks the loop because it found the best taxonomy
        
        except KeyError: # When no taxa found

            failed_taxo_count = failed_taxo_count + 1 # counts how many times

            if failed_taxo_count == number_of_splits: # if it has checked every piece of the name, it will add it to the failed taxonomy list
                
                failed_taxos_list.append(strain_stripped) 
                is_fail = 1
                break
            

                continue
    
    if is_fail == 1:
            continue

    
    item_proper = item[0]
    
    lineage = ncbi.get_lineage(item_proper) # Gets the full taxonommic information in number id form

    names = ncbi.get_taxid_translator(lineage) # converts this full taxa info into names


    for id,taxonomy in names.items(): # Basically finds id of the specific taxonomic item into taxonomic rank
        
        taxo = ncbi.get_rank([id]) # finds rank of taxonomy eg. { 21389 : 'species' }
        taxa = taxo[id] # grabs the exact taxa
        taxo_dict[taxa] = taxonomy # Finds the name
    
    taxonomy_error_check = 0
    # creates default strings
    
    
    superkingdom = "na"
    phylum = "na"
    clazz = "na"
    order = "na"
    family = "na"
    genus = "na"
    spec = "na"
    species = "na"
    
    for taxo,actual in taxo_dict.items(): # Loops over dictionary and checks rank
        
        if taxo == 'superkingdom': # eg if this dict item is a superkingdom
            superkingdom = actual # eg. superkingdom variable is saved

        if taxo == 'phylum':
            phylum = actual

        if taxo == 'class':
            clazz = actual

        if taxo == 'order':
            order = actual
        if taxo == 'family':
            family = actual
    
        if taxo == 'species':
            spec = actual
            species = spec.replace(" ", "_")
        
        if taxo == 'genus':
            genus = actual


    # if it cant identify the species, it calls this a fail. Because it should be able to if it has gotten this far.
    if species == "na": # so if species name is still na
        taxo_dict.clear()
        failed_taxos_list.append(strain_stripped)
        continue
    

    # Next part is identification of new name
    
    new_name = species
    if number_of_splits == 3: # checks whether we have strain information based on original name (can be common that the strain isn't in the ncbi taxonomy)
        
        strain_val = str(split_name[-1])
        new_name = species + "_" + strain_val # ADDS THE NEW SPECIES TO THE ORIGINAL STRAIN VAL!!!
        testing_rpts = new_name.split("_")
        
        if testing_rpts[-1].upper() == testing_rpts[-2].upper(): # Stops new name having repeats. In some cases this occurs

            rpts_rem = "_".join(testing_rpts[:-1])
            new_name = rpts_rem
       
        if testing_rpts[-1].upper() == testing_rpts[-3].upper() and testing_rpts[-2].upper() == testing_rpts[-4].upper(): # Same as above, except if repeat is two 'words'
            
            rpts_rem = "_".join(testing_rpts[-2])
            new_name = rpts_rem
    
    elif number_of_splits >= 4: # if the original name was split four times, it will likely mean that the strain name is two words
        
        strain_preval = split_name[-2:]
        strain_val = '_'.join(strain_preval)
        new_name = species + "_" + strain_val # ADDS THE NEW SPECIES TO THE ORIGINAL STRAIN VAL!!!
        testing_rpts = new_name.split("_")
        
        if testing_rpts[-1].upper() == testing_rpts[-2].upper():
            
            rpts_rem = "_".join(testing_rpts[:-1])
            new_name = rpts_rem 
        
        if testing_rpts[-1].upper() == testing_rpts[-3].upper() and testing_rpts[-2].upper() == testing_rpts[-4].upper():
            
            rpts_rem = "_".join(testing_rpts[:-2])
            new_name = rpts_rem

    else: # if there was no strain given (because a two word item on the original list likely is just genera + species)
       
        strain_val = "na"
        new_name = species
    
  #  if split_name[-2] == "sp." or split_name[-2] == "bacterium":

   #     new_name = species



    # writes taxonomic information to taxonomy file
    taxonomy_list.write(superkingdom + "," + phylum + "," + clazz + "," + order + "," + family + "," + genus + "," + species + "," + strain_val + "\n")

    old_name_list.append(strain_stripped) # adds original name to list because this has worked
    new_name_list.append(new_name)

    taxo_dict.clear()
# Obtain lineage

taxonomy_list.close()

# Saves list of failed taxonomies in output directory

failed_taxo_path = sys.argv[2] + "/" + "failed_taxos.txt"
failed_taxos = open(failed_taxo_path, "w")
failed_taxos.write("Failed taxonomies")

for fail in failed_taxos_list:
    
    failed_taxos.write("\n")
    failed_taxos.write(fail)

# Save to file

failed_taxos.close()


# Saves csv list of changes taxonomies in output directory


name_change_path = sys.argv[2] + "/" + "name_changes_summary.csv"
name_changes = open(name_change_path, "w")
act_names_changed = []
changed_count = 0
unchanged_count = 0

for old, new in zip(old_name_list, new_name_list):
    
    if old.upper() == new.upper():
        unchanged_count = unchanged_count + 1
    
    else:
        changed_count = changed_count + 1
        act_changed = "\n" + old + "," + new
        act_names_changed.append(act_changed)

name_changes.write("unchanged_count:" + str(unchanged_count) + "," + "changed_count:" + str(changed_count) + "\n")

name_changes.write("old_name,new_name")

for old, new in zip(old_name_list, new_name_list):
    to_write = "\n" + old + "," + new
    name_changes.write(to_write)


name_changes.close()

# Saves list of names actually changed to output directory


act_name_change_path = sys.argv[2] + "/" + "names_changes.csv"  # For the path of the actual name change file

act_file = open(act_name_change_path, "w") # opens actual name file
act_file.write("old_name,new_name") # writes column

for changes in act_names_changed: # iterates over list of actual name changes

    act_file.write(changes) # writes to actual name change file

act_file.close() # closes file




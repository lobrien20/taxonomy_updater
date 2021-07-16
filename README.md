# bact_taxa_update

Given a list of bacterial genera, species, strain names as a text file (each taxa rank in the name split by "_"), updates their taxonomy to current NCBI using ete3 toolkit.

Eg.
"Ruminococcus_flavefaciens_FD-1"

Output is following files:


- Full taxonomic lineages of each name
- Names which failed to be identified
- Text file of all names (including those unchanged)
- Text file of all names changed (so, excluding those unchanged)


Requires ete3, used with python 3.9.4.

to work on:

- allow spaces instead of "_"
- convert to GTDB taxonomy/alternative taxonomies


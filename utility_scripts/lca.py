from libs.python_modules.taxonomy.LCAComputation import LCAComputation
import sys




print 'hello'

print sys.argv[1]

lca = LCAComputation(sys.argv[1])

taxons = [
#"Bacteria;Firmicutes;Bacilli;Bacillales;Staphylococcaceae;Staphylococcus;uncultured Staphylococcus sp.",
#"Bacteria;Firmicutes;Bacilli;Bacillales;Staphylococcaceae;Staphylococcus;uncultured bacterium",
#"Bacteria;Firmicutes;Bacilli;Bacillales;Staphylococcaceae;Staphylococcus;unidentified marine bacterioplankton",
#"Bacteria;Firmicutes;Bacilli;Bacillales;Staphylococcaceae;Staphylococcus;unidentified marine bacterioplankton",
#"Bacteria;Firmicutes;Bacilli;Bacillales;Staphylococcaceae;Staphylococcus;unidentified marine bacterioplankton",
#"Bacteria;Firmicutes;Bacilli;Bacillales;Staphylococcaceae;Staphylococcus;uncultured Staphylococcus sp.",
#"Bacteria;Firmicutes;Bacilli;Bacillales;Staphylococcaceae;Staphylococcus;uncultured bacterium",
#"Bacteria;Firmicutes;Bacilli;Bacillales;Staphylococcaceae;Staphylococcus;unidentified marine bacterioplankton",
#"Bacteria;Firmicutes;Bacilli;Bacillales;Staphylococcaceae;Staphylococcus;unidentified marine bacterioplankton",
#"Bacteria;Firmicutes;Bacilli;Bacillales;Staphylococcaceae;Staphylococcus;unidentified marine bacterioplankton",

#"Bacteria;Firmicutes;Bacilli;Bacillales;Staphylococcaceae;Staphylococcus;uncultured bacterium",
#"Bacteria;Firmicutes;Bacilli;Bacillales;Staphylococcaceae;Staphylococcus;unidentified marine bacterioplankton",

"Bacteria;Firmicutes;Bacilli;Bacillales;Staphylococcaceae;Staphylococcus;unidentified marine bacterioplankton",
"Bacteria;Firmicutes;Bacilli;Bacillales;Staphylococcaceae;Staphylococcus;unidentified marine bacterioplankton",
"Bacteria;Firmicutes;Bacilli;Bacillales;Staphylococcaceae;Staphylococcus;uncultured Staphylococcus sp.",

#"Bacteria;Firmicutes;Bacilli;Bacillales;Staphylococcaceae;Staphylococcus;uncultured Staphylococcus sp.",
#"Bacteria;Firmicutes;Bacilli;Bacillales;Staphylococcaceae;Staphylococcus;uncultured bacterium",
#"Bacteria;Firmicutes;Bacilli;Bacillales;Staphylococcaceae;Staphylococcus;uncultured bacterium",
#"Bacteria;Firmicutes;Bacilli;Bacillales;Staphylococcaceae;Staphylococcus;uncultured Staphylococcus sp.",
#"Bacteria;Firmicutes;Bacilli;Bacillales;Staphylococcaceae;Staphylococcus;uncultured bacterium",
         ]

print lca.getTaxonomy(taxons)

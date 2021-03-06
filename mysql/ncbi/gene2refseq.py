import sys
import os
import os.path
import csv
import MySQLdb
import json
import gzip

def main(argv):
        if len(sys.argv) < 2:
                sys.exit()

        host = "xxx"
        user = "xxx"
        pwd = "xxx"
        database = "xxx"

        configfile = "config.json"

        if sys.argv[2] :
                configfile = sys.argv[2]

        with open(configfile) as json_data_file:
                data = json.load(json_data_file)

        if data.has_key("mysql"):
                if data["mysql"].has_key("db"):
                        database = data["mysql"]["db"]
                if data["mysql"].has_key("host"):
                        host = data["mysql"]["host"]
                if data["mysql"].has_key("user"):
                        user = data["mysql"]["user"]
                if data["mysql"].has_key("password"):
                        pwd = data["mysql"]["password"]
        
        db=MySQLdb.connect(host=host,user=user,
                  passwd=pwd,db=database)
        
        
        cursor = db.cursor()

        cursor.execute("DROP TABLE IF EXISTS gene2refseq")
        sql = """CREATE TABLE `gene2refseq` (
`GeneID` int(11) NOT NULL default '0',
`status` varchar(20) NOT NULL default '',
`RNA_nucleotide_acc` varchar(20) NOT NULL default '',
`RNA_nucleotide_gi` varchar(16) NOT NULL default '',
`protein_acc` varchar(20) NOT NULL default '',
`protein_gi` varchar(16) NOT NULL default '',
`genomic_nucleotide_acc` varchar(20) NOT NULL default '',
`genomic_nucleotide_gi` varchar(16) NOT NULL default '', 
KEY `index_geneid` (`GeneID`),
KEY `index_status` (`status`),
KEY `index_protein_acc` (`protein_acc`),
KEY `index_genomic_nucleotide_acc` (`genomic_nucleotide_acc`),
KEY `index_RNA_nucleotide_acc` (`RNA_nucleotide_acc`),
KEY `index_protein_gi` (`protein_gi`),
KEY `index_genomic_nucleotide_gi` (`genomic_nucleotide_gi`),
KEY `index_RNA_nucleotide_gi` (`RNA_nucleotide_gi`)
) ENGINE=MyISAM;"""
        cursor.execute(sql)

        cursor.execute("SET autocommit=0;")
        cursor.execute("SET unique_checks=0;")
        cursor.execute("SET foreign_key_checks=0;")

        i = 0
        limit = 10000

        with gzip.open(sys.argv[1],'r') as f:
                reader=csv.reader(f,delimiter='\t')
                for row in reader:
                        if ( row[0].startswith('#') ): #Avoid row with !
                                continue

                        cursor.execute('INSERT INTO gene2refseq VALUES( %s, %s, %s, %s, %s, %s, %s, %s )', ( row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8] ) )
                        i = i+1
                        if (i == limit):
                                i=0
                                db.commit()

        db.commit()
        cursor.close()
        

if __name__ == "__main__":
        main(sys.argv[1:])

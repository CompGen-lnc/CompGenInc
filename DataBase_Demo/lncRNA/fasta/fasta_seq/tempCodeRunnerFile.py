from Bio import SeqIO

def fix_seq(seq):
    seq = seq.replace('t', 'T')
    seq = seq.replace('a', 'A')
    seq = seq.replace('c', 'C')
    seq = seq.replace('g', 'G')
    seq = seq.replace('u', 'T')
    seq = seq.replace('U', 'T')

    return seq

def read_fa(path):
    res = {}
    rescords = list(SeqIO.parse(path, format="fasta"))
    for x in rescords:
        id = str(x.id)
        seq = fix_seq(str(x.seq))
        res[id] = seq
    return res

lncrna = read_fa("outLncRNA.fa")

f = open("outLncRNA_new.fa","w")
for k,v in lncrna.items():
    f.write(">"+k+"\n")
    f.write(v+"\n")
f.close()
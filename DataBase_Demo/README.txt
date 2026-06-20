Contenido de Archivos

fasta/fasta_seq/lncRNA.fa: Secuencias completas para lncRNA.
fasta/fasta_seq/miRNA.fa: Secuencias completas para miRNA.
fasta/fasta_2d/lncRNA_2d_ss.fa: Estructuras 2D para lncRNA.

kmers/lnc_kmer_dict.txt: Diccionario de 1-mer, 2-mer, 3-mer y 4-mer en un solo vector para los lncRNA.
kmers/mir_kmer_dict.txt: Diccionario de los 1-mer, 2-mer, 3-mer y 4-mer para los miRNA.

sequences/: Todos los archivos de lncRNA que unen la secuencia con su estructura 2D.
	Formato: 'seq+ss_join_NONHSATXXXXXX.X.txt'

characterization/: Todos los archivos de lncRNA con la caracterización de subestructuras y sus energías.
	Formato: 'loops_NONHSATXXXXXX.X.txt'
	
txt_interac/mirnas_lncrnas_validated_positive_pairs.txt: Lista de pares de lncRNA con miRNA que tienen interacción positiva.
txt_interac/negative_pairs.txt: Lista de pares de lncRNA con miRNA que tienen interacción negativa.

lnc_features.csv: Cantidad de stacks, hairpins, multiciclos y energía total para cada lncRNA.

binding_features_dic.txt:
	Descripción de las columnas:
		1- Nombre de la interacción
		2- Número de inter loops 
		3- Número de hairpins
		4- Número de multiciclos
		5- Energía en el sitio de unión (Corresponde a las energías de las subestructuras en el sitio de únion divididas entre 100)
		6- Energía de interacción (Es la que se obtiene con miRanda)
		7- Energía total (Debe coincidir con el valor que se encuentra en paréntesis al final del loops_NONHSATXXXXXX que corresponde)

		Nota: Tanto el número de inter loops, hairpins y multiciclos, solo se toman en cuenta si se encuentran dentro de los límites R obtenidos con miRanda.
		Ejemplo: R:402 to 423

	Ejemplo de las columnas: 
		NONHSAT000179.2_hsa-miR-25-3p,10,1,0,-12.0,-23.530001,-172.8
		
		1- Nombre de la interacción: NONHSAT000179.2_hsa-miR-25-3p
		2- Número de inter loops: 10
		3- Número de hairpins: 1
		4- Número de multiciclos: 
		5- Energía en el sitio de unión -12.0
		6- Energía de interacción -23.530001 ===> El valor obtenido con miRanda es:    Energy:  -23.530001 kCal/Mol
		7- Energía total: -172.8 ===> El valor que viene al final de loops_NONHSATXXXXXX es: (-172.80)
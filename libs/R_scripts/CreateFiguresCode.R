
#     process the command line arguments 
args <- commandArgs(trailingOnly=TRUE)



#     set input/output directories
input_txt <- args[1]
output_pdf <- args[2]

exp<-read.table(input_txt, header=TRUE, sep='\t')
exp2<-colSums(exp[,-1])
barcode_rank<-rank(-exp2)

pdf(output_pdf)
plot(barcode_rank, exp2, xlim=c(1,  length(exp2)*.3))
dev.off()



library(plyr)
library(rgenoud)
library(ggplot2)
library(FactoMineR)

visualizePCA <- function(generations=10,runs=3,seed_length=8,file.path="/Users/malte/Documents/ENSAEA2/Ant_sim_8/allResults.csv"){

	generations=generations+1 #because of counting error in genopt.py
	allSortedResults<- read.csv(file=file.path, head=FALSE, sep=",")
	onlyBestResults<-allSortedResults[seq(1,nrow(allSortedResults),by=seed_length),2:5]

		
	##make PCA
	res.PCA<-PCA(onlyBestResults,scale.unit=TRUE,ncp=2)
	res.PCA
	
	## add classification (Runs)
	values<-data.frame(res.PCA$ind$coord, Run=rep(paste("Run",1:runs), each=generations))
	withGen <- data.frame(values,Generation=rep(1:generations))
	end <- withGen[which(withGen$Generation==generations),]
		
	## plot by classification
	g<-ggplot(data=values, aes(x=Dim.1, y=Dim.2, colour= Run, group=Run))+geom_path()
	
	
	g+geom_point(data=end, size=5, aes(x=Dim.1, y=Dim.2)) + scale_x_continuous('Principal Component 1') + scale_y_continuous('Principal Component 2') 
}

visualizePCA(generations=10,runs=7,seed_length=10,file.path="/Users/malte/Downloads/python 5/allResultscollected.csv")
visualizePCA(generations=15,runs=6,seed_length=10,file.path="/Users/malte/Desktop/Genetic Algo Obstacle Without Problem/allResults1.csv")


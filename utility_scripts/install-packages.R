## Create the personal library if it doesn't exist. Ignore a warning if the directory already exists.
dir.create(Sys.getenv("R_LIBS_USER"), showWarnings = FALSE, recursive = TRUE)

install.packages("pvclust", Sys.getenv("R_LIBS_USER"), repos = "http://cran.case.edu")
install.packages("dplyr", Sys.getenv("R_LIBS_USER"), repos = "http://cran.case.edu")
install.packages("vegan", Sys.getenv("R_LIBS_USER"), repos = "http://cran.case.edu")
install.packages("pheatmap", Sys.getenv("R_LIBS_USER"), repos = "http://cran.case.edu")
install.packages("doBy", Sys.getenv("R_LIBS_USER"), repos = "http://cran.case.edu")
install.packages("ecodist", Sys.getenv("R_LIBS_USER"), repos = "http://cran.case.edu")
install.packages("reshape2", Sys.getenv("R_LIBS_USER"), repos = "http://cran.case.edu")
install.packages("ggplot2", Sys.getenv("R_LIBS_USER"), repos = "http://cran.case.edu")
install.packages("splitstackshape", Sys.getenv("R_LIBS_USER"), repos = "http://cran.case.edu")
install.packages("gridExtra", Sys.getenv("R_LIBS_USER"),  repos="http://R-Forge.R-project.org") 
install.packages("geiger", Sys.getenv("R_LIBS_USER"))


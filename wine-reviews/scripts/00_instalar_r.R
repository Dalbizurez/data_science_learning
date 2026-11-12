# Instala los paquetes de R necesarios (ejecutar una vez)
pkgs <- c("tidyverse","reticulate","skimr","rstatix","scales","knitr",
          "patchwork","ggrepel","moments")
install.packages(setdiff(pkgs, rownames(installed.packages())))

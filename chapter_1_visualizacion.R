#install.packages("tidyverse")
#install.packages("palmerpenguins")
#install.packages("ggthemes")

library(tidyverse)

library(palmerpenguins)
library(ggthemes)

# Generating a plot 
ggplot(
  data=penguins, # Data source
  mapping = aes(x = flipper_length_mm, y = body_mass_g) # Indication of which variables go to each axis
) + 
  geom_point(mapping = aes(color = species, shape = species)) +
  geom_smooth(method = "lm") +
  labs(
    title = "Body mass and flipper length",
    subtitle = "Dimensions for Adelie, Chinstrap, and Gentoo Penguins",
    x = "Flipper length (mm)", y = "Body mass (g)",
    color ="Species", shape = "Species",
    caption = "Data come from the palmerpenguins package"
  ) +
  scale_color_colorblind()

# Excercises
# 1.
penguins # 344*8
# 3.
ggplot(
 data = penguins,
 mapping = aes(x = bill_length_mm, y = bill_depth_mm)
) +
  geom_point(mapping = aes(color = species))
# 4.
ggplot(
  data = penguins,
  mapping = aes(x = bill_depth_mm, y = species)
) + 
  geom_col()
# 5.there's no mapping, no indication of axis and specific data
# 6.
ggplot(
  data = penguins,
  mapping = aes(x = flipper_length_mm, y = body_mass_g) )+
    geom_point(na.rm = TRUE)

# 8.
ggplot(
  data = penguins,
  mapping = aes(x = flipper_length_mm, y = body_mass_g)
) +
  geom_point(mapping = aes(color = bill_depth_mm)) +
  geom_smooth(method = "gam")

# 9.
ggplot(
  data = penguins,
  mapping = aes(x = flipper_length_mm, y = body_mass_g, color = island)
) +
  geom_point() +
  geom_smooth(se = FALSE)


---
title: "Roads and Growth in Peru's Periphery: District-Level Evidence from Nighttime-Light GDP"
author: "Álvaro Alexander Yllu Socualaya"
date: "Working paper, November 2026"
thanks: "This paper develops the author's undergraduate research thesis (Lima, 2025). I thank Julio Aguirre for his supervision."
---

<div class="abstract" markdown="1">

**Abstract.** This paper estimates the causal effect of road infrastructure on economic growth across Peruvian districts located away from departmental capitals. Official subnational GDP statistics are scarce and unreliable in a country where most employment is informal, so I use district GDP per capita estimated from nighttime lights by Seminario and Palomino (2022). Road placement is endogenous, so I instrument district road density with the distance from each district to the pre-Columbian Inca road network (Qhapaq Ñan), whose routes follow terrain that modern roads also use. A second candidate instrument, the distance to a hypothetical minimum-cost network linking the departmental capitals, turns out to be weak. For 1,141 peripheral districts over 2007 to 2018, ordinary least squares shows a positive and significant association between road density and growth in GDP per capita. The two-stage least squares estimates are not significantly different from zero, and a spatial-error model that allows for strong spatial dependence gives the same result. The instrumental-variable estimates are imprecise, however. They rule out large effects: one standard deviation more road density raised 2007 to 2018 growth by at most about 6 log points. But they cannot distinguish a zero effect from the small positive association found by least squares. I find no evidence that road density raised growth in Peru's peripheral districts over this period, but the data cannot rule out a modest positive effect.

**Keywords:** infrastructure, regional development, two-stage least squares, spatial econometrics, nighttime lights, Peru.<br>
**JEL:** O18, R11, R42, H54.

</div>

## 1. Introduction

Between 2007 and 2017 Peru grew fast and built roads fast. Real GDP rose by about 60 percent, and the national and departmental road networks grew from 38,275 to 54,273 kilometres, an increase of 41.8 percent (Baylón, 2025). Institutional reforms made this expansion possible, among them the 2008 framework law for public-private partnerships and agencies such as Provías Nacional and ProInversión. Regional inequality did not fall over the same period: Lima's share of national output kept rising (Seminario et al., 2019). Castillo (2020) finds lower income inequality between 2007 and 2017, but that need not mean that economic activity became less concentrated. Figure 1 shows both developments: the asphalted national road network and district GDP per km² in 2007 and 2017.

{{FIGURE:fig1_roads_gdp|Figure 1. Asphalted national roads and GDP per km², 2007 and 2017|GDP per km²: Seminario and Palomino (2022), seven quantile classes per year; white: no data. Roads: asphalted segments of the MTC national road network files for 2007 and 2017; red: asphalted segments in 2017 more than 250 m from any asphalted segment in 2007.}}

A large literature links infrastructure investment to growth through lower transport costs and better access to markets, health and education. Cross-country and national studies find positive effects (Esfahani and Ramírez, 2003; Achour and Belloumi, 2015; Zhang and Cheng, 2023), and Peruvian studies find effects of roads on poverty, schooling and regional growth (Valdivia, 2011; Vásquez and Bendezú, 2008; Urrunaga and Aparicio, 2012; Machado and Toma, 2017). Most of this work uses official GDP figures. In Peru their accuracy is doubtful at small geographic scales because the unobserved economy is large: INEI (2024) puts informal employment at 70.9 percent of the labour force.

Satellite data on nighttime lights offer a way around this problem (Elvidge et al., 1997; Henderson et al., 2011; Chen and Nordhaus, 2011). Seminario and Palomino (2022) use them to estimate GDP for every Peruvian district from 1993 to 2018. These estimates have not yet been used to evaluate the causal effect of roads at the district level. This paper does so and asks: what is the causal effect of road infrastructure on economic activity in Peru's peripheral districts?

The paper makes two contributions. It provides one of the first district-level estimates of this effect for Peru, which allows a closer look at local dynamics and rural gaps than regional data do. It also addresses the endogeneity of road placement with an instrumental-variable strategy that exploits the historical Inca road network, following Martincus et al. (2016), and checks the result with a spatial econometric model that allows for dependence across neighbouring districts. A hypothetical least-cost network in the spirit of Faber (2014) is also considered but proves too weak to use.

The main result is a null effect, estimated with limited precision. Ordinary least squares shows that districts with denser road networks grew faster. The instrumental-variable estimates are not significantly different from zero, and the spatial model agrees. The confidence intervals rule out large growth effects of road density, but they also contain the least-squares estimate, so the data cannot tell whether the positive correlation reflects where roads were placed or a small genuine effect.

## 2. Related literature

**Roads and growth.** Transport infrastructure is expected to raise output by lowering transport costs, integrating markets and easing the movement of labour and capital (Hine et al., 2019; Esfahani and Ramírez, 2003). Positive aggregate effects are reported for the United Kingdom (Zhang and Cheng, 2023), Ghana (Owusu-Manu et al., 2019) and Nigeria (Babatunde, 2018). The distributional effects are less clear. Highways can narrow urban-rural income gaps (Huang et al., 2020), but Faber (2014) shows that connecting peripheral Chinese counties to the national trunk highway system reduced their GDP growth, as activity moved towards larger markets. Banerjee et al. (2012) find no local growth effect of access to historical transport networks in China. Road quality matters as well as road length (Gertler et al., 2016), and India's large rural roads programme moved workers out of agriculture with little effect on income (Asher and Novosad, 2020).

**Identification.** Roads are not placed at random: they go where economic potential or political influence is high. Studies deal with this through difference-in-differences (Mu and van de Walle, 2011; Zhang et al., 2019), regression discontinuity around programme eligibility rules (Casaburi et al., 2012; Asher and Novosad, 2020), dynamic panels (Urrunaga and Aparicio, 2012) and instrumental variables. Banerjee et al. (2012) instrument with straight lines between historical cities; Faber (2014) builds a hypothetical least-cost network that connects targeted cities; Martincus et al. (2016) use the Inca road network as a source of exogenous variation in Peru; and Zhang et al. (2019) use 1936 postal routes in China.

**Nighttime lights as a measure of output.** Elvidge et al. (1997) document a strong correlation between lit area, population and economic activity, and Henderson et al. (2011) and Chen and Nordhaus (2011) formalise lights as a proxy for GDP. Lights have since been used to estimate subnational GDP in Paraguay (McCord and Rodriguez-Heredia, 2022) and Peru (Seminario and Palomino, 2022) and to evaluate social transfers in Colombia (Villa, 2016). The data have known limits. Older DMSP sensors saturate in bright urban areas and are hard to compare with VIIRS data without calibration (Zhang and Gibson, 2022; Gibson, 2021). Lights understate agricultural activity (Gibson and Boe-Gibson, 2021), and they predict differences across space better than changes over time (Zhang and Gibson, 2022; Gibson, 2021), which calls for caution when estimating growth effects over short periods.

## 3. Data

**Outcome.** The dependent variable is the growth of district GDP per capita between 2007 and 2018, measured as the log difference ln(GDP per capita 2018) − ln(GDP per capita 2007). District GDP per capita comes from Seminario and Palomino (2022), who estimate it from nighttime lights for 1993 to 2018. The end year, 2018, is the last year of their series.

**Road density.** Following Aguirre et al. (2018), road density is the total length of national and departmental roads in a district divided by the district's area (km of road per km²). It measures the stock of road infrastructure, not its change. Road lengths come from the georeferenced road networks of the Ministry of Transport and Communications (MTC). The stored densities match the 2017 network better than the earlier one, so the regressor is best read as the road stock at the end of the period. The paper therefore estimates how growth relates to the road stock a district had by 2017, not the effect of the roads added between 2007 and 2017.

**Controls.** The controls describe each district in 2007: the share of the population with complete secondary education or more and the share of workers in agriculture, both from the 2007 Census; the log of urban population, also from the 2007 Census; a dummy for mining activity; and the number of micro and small enterprises (MYPEs). The agricultural share also helps absorb the tendency of light-based GDP to understate farm output. All regressions include department fixed effects.

**Sample.** Proximity to a regional capital is closely tied to economic development, so I exclude districts whose centroid lies within about 50 km of a departmental capital.[^1] After this exclusion and listwise deletion of districts with missing data, the sample has 1,141 districts, or 1,140 when the controls are included. Figure 2 maps the districts in the sample. Table 1 compares the study districts with the excluded districts near departmental capitals. Districts in the sample are poorer, more agricultural and much less urban.

[^1]: The exclusion flag was built in GIS from district centroids, so it keeps some districts that have part of their territory within 50 km of a capital. Section 5.3 shows that the 2SLS estimate is similar with a stricter version of the flag.

{{FIGURE:fig2_study_districts|Figure 2. Study districts|Districts in the estimation sample (blue) and excluded districts near departmental capitals or without data (white).}}

{{TABLE:table1}}

## 4. Empirical strategy

The equation of interest is the cross-section

<div class="eq">growth<sub>id</sub> = α + β density<sub>id</sub> + X′<sub>id</sub>γ + μ<sub>d</sub> + ε<sub>id</sub>,&emsp;(1)</div>

where *growth*<sub>id</sub> is the 2007 to 2018 growth of GDP per capita in district *i* of department *d*, *density*<sub>id</sub> is road density, *X*<sub>id</sub> are the 2007 controls, and μ<sub>d</sub> are department fixed effects. Ordinary least squares estimates of β are likely biased: the state may prioritise districts with greater growth potential, political weight or favourable geography, and unobserved factors may drive both road building and growth.

**Instruments.** I consider two instruments, each measured as the log distance from the district centroid to a network. The first is the pre-Columbian Inca road network, the Qhapaq Ñan (Figure 3). Its routes followed valleys and gentle slopes, and this favourable terrain is likely to have shaped the layout of modern roads as well (Martincus et al., 2016). The second is a hypothetical least-cost network: the minimum spanning tree that links Peru's departmental capitals, computed with Kruskal's (1956) algorithm on link costs that account for terrain (Figure 4). Each link is drawn as a straight line between the two capitals it connects, and the instrument is the distance to these lines. It reflects the cost-minimising logic a planner connecting the capitals might follow (Faber, 2014). The first stage is

<div class="eq">density<sub>id</sub> = π<sub>0</sub> + π<sub>1</sub> Z<sub>id</sub> + X′<sub>id</sub>θ + μ<sub>d</sub> + v<sub>id</sub>.&emsp;(2)</div>

Relevance requires π<sub>1</sub> ≠ 0. The exclusion restriction requires that distance to the network affects growth only through road provision. For the Inca road this requires that any economic advantage from pre-Columbian routes, other than their influence on where modern roads were built, has faded or is negligible today. This is a substantive assumption: settlement patterns and terrain that favoured the Inca routes could also affect growth directly, and the department fixed effects and 2007 controls only partly address this. For the Kruskal network the restriction is more plausible, because the network is a geometric construction with no direct economic role, but, as shown below, it does not predict road density.

{{FIGURE:fig3_inca_road|Figure 3. Inca road network (Qhapaq Ñan)|Source: Qhapaq Ñan layer (CC0).}}

{{FIGURE:fig4_kruskal_network|Figure 4. Hypothetical Kruskal network|Minimum spanning tree linking the departmental capitals, computed with terrain-based link costs; links drawn as straight lines.}}

**Spatial dependence.** Road effects may spill over to neighbouring districts, and growth shocks are likely to be correlated across space. I test the residuals of equation (1) for spatial autocorrelation with Moran's I and Lagrange multiplier (LM) tests, using a first-order contiguity matrix *W*. Depending on the tests, the model is extended to a spatial-error model (SEM), *u* = λ*Wu* + ε, estimated by generalised spatial two-stage least squares with road density instrumented as before (Drukker, Prucha and Raciborski, 2013).

## 5. Results

### 5.1 First stage

Table 2 reports the first stage. Distance to the Inca road is a strong predictor of road density: districts closer to the Qhapaq Ñan have denser modern roads (coefficient −0.0207 on log distance, robust first-stage F = 28.8). Districts with a larger share of agricultural employment and mining districts have lower road density. Distance to the hypothetical Kruskal network does not predict road density once controls and department effects are included (F = 0.53), so it is a weak instrument. One reason may be that terrain enters only the choice of which capitals to link: each link is a straight line, so the network does not follow the valleys and passes that dominate where roads can be built in Peru. I therefore use only the Inca road instrument in the second stage. With the Kruskal instrument the 2SLS estimate is uninformative (coefficient 4.3, standard error 6.0).

{{TABLE:table2}}

### 5.2 OLS and 2SLS

Table 3 presents the main estimates. Without controls (column 1), OLS shows a positive and significant association: an increase of 1 km of road per km² is associated with 15 log points of additional growth over 2007 to 2018. With controls (column 2) the coefficient falls to 0.115 but remains significant.

The 2SLS estimates in columns 3 and 4 tell a different story. The instrument is strong (first-stage F of 33.0 and 28.8), but the coefficient on road density falls to 0.130 without controls and to −0.045 with controls, with standard errors of 0.22 to 0.25. Neither is distinguishable from zero. Among the controls, districts with a larger agricultural share in 2007 grew less (−0.135), and districts with more educated populations grew more (0.200). The log of urban population is positive and significant only at the 10 percent level, while MYPEs and mining are not significant.

The fall from the OLS to the 2SLS estimate is consistent with roads having been placed in districts that were already likely to grow. However, as Section 5.3 shows, the 2SLS estimate is too imprecise to reject the OLS value, so the data do not establish that the OLS association is due to placement.

{{TABLE:table3}}

### 5.3 What the null result rules out

A non-significant estimate is not evidence of no effect, so Table 6 reports what the instrumental-variable estimates can and cannot exclude. The reduced form shows why 2SLS is null: distance to the Inca road predicts road density but has no association with growth (coefficient 0.0009, standard error 0.0053). The 95 percent confidence interval of the 2SLS estimate runs from −0.54 to 0.45. The Anderson-Rubin confidence set, which stays valid even if the instrument is weak, is similar: −0.62 to 0.47.

One standard deviation of road density is 0.13 km per km². At the upper bound of either interval, it would raise 2007 to 2018 growth by about 6 log points, or roughly half a percentage point a year. Effects larger than that are ruled out. The OLS estimate of 0.115, about 1.5 log points per standard deviation, lies well inside the 2SLS interval. A Wu-Hausman test does not reject the exogeneity of road density (p = 0.51). The data therefore cannot tell whether the OLS association is placement bias or a small causal effect. Finally, the 2SLS estimate does not depend on the exact sample: with a stricter version of the exclusion flag (939 districts) it is 0.104 (standard error 0.216).

{{TABLE:table6}}

### 5.4 Spatial dependence

The residuals of equation (1) are strongly spatially correlated (Table 4). Moran's I is positive and highly significant, and both LM tests reject the null of no spatial dependence. The robust LM tests discriminate between the two forms: the robust LM-error test remains large and significant, while the robust LM-lag test is close to zero. Following the usual decision rule (Anselin et al., 1996), I estimate a spatial-error model.

{{TABLE:table4}}

Table 5 reports the spatial-error model with road density instrumented by distance to the Inca road. The spatial error parameter is large (λ = 0.80), confirming strong dependence in unobserved shocks across neighbouring districts. Road density remains insignificant (0.266, standard error 0.208). Agriculture is no longer significant once spatially correlated errors are accounted for, while education keeps a positive effect that is significant at the 10 percent level. The spatial-error model corrects inference for correlated shocks, but it does not estimate spillovers: it contains no term for neighbours' roads. Whether roads in one district affect growth in its neighbours is left open.

{{TABLE:table5}}

## 6. Discussion

The results do not establish a causal effect of road density on GDP growth in Peru's peripheral districts. They rule out large effects, but not modest ones, and they cannot separate placement bias from a small genuine effect. The main methodological challenge is simultaneity, because roads are built where growth is already expected. The instrument used here addresses it only under the assumption that, conditional on department and 2007 characteristics, the Inca road matters for today's growth only through modern roads. Since the Inca routes followed long-settled valleys, that assumption could fail, and the estimates should be read with this caveat.

Districts with a larger agricultural base grew less. This is a correlation, not a causal estimate, and part of it may reflect the undercounting of farm output in light-based GDP. It is consistent with the view that connectivity alone does not transform low-productivity economic structures. Without complementary policies that build capital, technology and skills, a new road may mainly make resource extraction or out-migration easier rather than spur local development, but this paper does not test that mechanism.

The contrast with Faber (2014) is instructive. In China, connecting peripheral counties to large metropolitan areas reduced their growth as capital and skilled labour moved to the centres. In Peru's peripheral districts there may be few mobile productive factors to lose, which could explain why the estimates show no negative effect either. The lower bound of the confidence interval, however, does not rule out modest negative effects.

The results have further limits. Road density is measured as a stock at the end of the period, not as the 2007 to 2017 expansion. The GDP series ends in 2018, so the study window is little more than a decade, which may be too short for infrastructure effects to appear. Light-based GDP understates agricultural activity, so part of the negative agricultural coefficient may reflect measurement rather than slower growth, and modest positive effects of roads on agriculture (Aguirre et al., 2018) or on small firms (Cama and Lago, 2024) could be masked.

## 7. Conclusions

This paper asked whether road infrastructure raised economic activity in Peru's peripheral districts. Using light-based district GDP and the historical Inca road network as an instrument, I find no statistical evidence that greater road density raised growth between 2007 and 2018, and this holds once spatially correlated shocks are modelled. The estimates rule out large effects: about 6 log points over the period per standard deviation of road density at most. They cannot rule out a modest positive effect of the size suggested by least squares. Spillovers to neighbouring districts were not tested. Taken together, the evidence does not support the expectation that road density by itself drove growth in these districts, but a definitive answer requires more precise identification.

For policymakers such as the Ministry of Transport and Communications and ProInversión, the cautious implication is that large growth returns from road density alone should not be expected in peripheral districts, and that road building is more likely to pay off alongside complementary policies. Regional inequality in Peru is historical and persistent (Seminario et al., 2019), and a road by itself is unlikely to reverse it. Future work could use the change in road stocks rather than their level, test spillovers directly with a spatial Durbin or SLX specification, look for instruments with a more secure exclusion restriction, extend the period beyond 2018, combine light-based GDP with household and agricultural survey data (ENAHO), and study how roads interact with complementary policies such as productive development programmes, credit and agricultural extension, as Aguirre et al. (2018), Martincus et al. (2016) and Cama and Lago (2024) begin to do.

## Data and code availability

The code and data that produce every table and figure are available at https://github.com/AAYlluS/carreteras-pbi-peru. The district GDP estimates of Seminario and Palomino (2022) are public: the code downloads them from Universidad del Pacífico, which publishes them with the book. All other data are public as well: INEI census and district boundaries, MTC road networks, and the Qhapaq Ñan layer (CC0).

## References

Achour, H., & Belloumi, M. (2015). Investigating the causal relationship between transport infrastructure, transport energy consumption and economic growth in Tunisia. *Renewable and Sustainable Energy Reviews*, 56, 988–998.

Aguirre, J., Campana, Y., Guerrero, E., & De La Torre Ugarte, D. (2018). Roads and agriculture: Impacts of connectivity in Peru. *Rivista Internazionale di Economia dei Trasporti*, 45(4).

Anselin, L., Bera, A. K., Florax, R., & Yoon, M. J. (1996). Simple diagnostic tests for spatial dependence. *Regional Science and Urban Economics*, 26(1), 77–104.

Asher, S., & Novosad, P. (2020). Rural roads and local economic development. *American Economic Review*, 110(3), 797–823.

Babatunde, S. A. (2018). Government spending on infrastructure and economic growth in Nigeria. *Economic Research-Ekonomska Istraživanja*, 31(1), 997–1014.

Banerjee, A. V., Duflo, E., & Qian, N. (2012). On the road: Access to transportation infrastructure and economic growth in China. *SSRN Electronic Journal*.

Baylón, M. J. P. (2025). Historia de las carreteras en el Perú, 1896-2024. *Tiempo y Economía*, 12(1), 1–21.

Cama, H., & Lago, N. (2024). Carreteras y efectos spillovers: impacto de la conectividad vial en el crecimiento del stock de micro y pequeñas empresas. Universidad del Pacífico.

Casaburi, L., Glennerster, R., & Suri, T. (2012). Rural roads and intermediated trade: Regression discontinuity evidence from Sierra Leone. *SSRN Electronic Journal*.

Castillo, L. (2020). Regional dynamics of income inequality in Peru. Working Paper 2020-004, Banco Central de Reserva del Perú.

Chen, X., & Nordhaus, W. D. (2011). Using luminosity data as a proxy for economic statistics. *Proceedings of the National Academy of Sciences*, 108(21), 8589–8594.

Drukker, D. M., Prucha, I. R., & Raciborski, R. (2013). A command for estimating spatial-autoregressive models with spatial-autoregressive disturbances and additional endogenous variables. *Stata Journal*, 13(2), 287–301.

Elvidge, C. D., Baugh, K. E., Kihn, E. A., Kroehl, H. W., Davis, E. R., & Davis, C. W. (1997). Relation between satellite observed visible-near infrared emissions, population, economic activity and electric power consumption. *International Journal of Remote Sensing*, 18(6), 1373–1380.

Esfahani, H. S., & Ramírez, M. T. (2003). Institutions, infrastructure, and economic growth. *Journal of Development Economics*, 70(2), 443–477.

Faber, B. (2014). Trade integration, market size, and industrialization: Evidence from China's National Trunk Highway System. *Review of Economic Studies*, 81(3), 1046–1070.

Gertler, P. J., Gonzalez-Navarro, M., Gracner, T., & Rothenberg, A. D. (2016). Road quality, local economic activity, and welfare: Evidence from Indonesia's highways. Working paper.

Gibson, J. (2021). Better night lights data, for longer. *Oxford Bulletin of Economics and Statistics*, 83(3), 770–791.

Gibson, J., & Boe-Gibson, G. (2021). Nighttime lights and county-level economic activity in the United States: 2001 to 2019. *Remote Sensing*, 13(14), 2741.

Henderson, V., Storeygard, A., & Weil, D. N. (2011). A bright idea for measuring economic growth. *American Economic Review*, 101(3), 194–199.

Hine, J., Sasidharan, M., Torbaghan, M., Burrow, M., & Usman, K. (2019). Evidence of the impact of rural road investment on poverty reduction and economic development. Institute of Development Studies.

Huang, Z., Xu, H., Li, J., & Luo, N. (2020). Has highway construction narrowed the urban–rural income gap? *Papers in Regional Science*, 99(3), 705–723.

INEI (2024). Perú: Comportamiento de los indicadores del mercado laboral a nivel nacional y en 27 ciudades. Instituto Nacional de Estadística e Informática.

Kruskal, J. (1956). On the shortest spanning subtree of a graph and the traveling salesman problem. *Proceedings of the American Mathematical Society*, 7, 48–50.

Machado, R., & Toma, H. (2017). Crecimiento económico e infraestructura de transportes y comunicaciones en el Perú. *Economía*, 40(79), 9–46.

Martincus, C. V., Carballo, J., & Cusolito, A. (2016). Roads, exports and employment: Evidence from a developing country. *Journal of Development Economics*, 125, 21–39.

McCord, G. C., & Rodriguez-Heredia, M. (2022). Nightlights and subnational economic activity: Estimating departmental GDP in Paraguay. *Remote Sensing*, 14(5), 1150.

Mu, R., & van de Walle, D. (2011). Rural roads and local market development in Vietnam. *Journal of Development Studies*, 47(5), 709–734.

Owusu-Manu, D., Jehuri, A. B., Edwards, D. J., Boateng, F., & Asumadu, G. (2019). The impact of infrastructure development on economic growth in sub-Saharan Africa with special focus on Ghana. *Journal of Financial Management of Property and Construction*, 24(3), 253–273.

Seminario, B., & Palomino, L. (2022). *Estimación del PIB a nivel subnacional utilizando datos satelitales de luminosidad: Perú, 1993-2018*. Universidad del Pacífico. https://doi.org/10.21678/978-9972-57-493-1

Seminario, B., Zegarra, M. A., & Palomino, L. (2019). Evolución del PBI departamental y análisis de la desigualdad regional en el Perú: 1795-2017. Inter-American Development Bank.

Urrunaga, R., & Aparicio, C. (2012). Infraestructura y crecimiento económico en el Perú. *Revista de la CEPAL*, 107, 157–177.

Valdivia, M. (2011). Contracting the road to development: Early impacts of a rural roads program. *SSRN Electronic Journal*.

Vásquez, A., & Bendezú, L. (2008). Ensayos sobre el rol de la infraestructura vial en el crecimiento económico del Perú. Banco Central de Reserva del Perú.

Villa, J. M. (2016). Social transfers and growth: Evidence from luminosity data. *Economic Development and Cultural Change*, 65(1), 39–61.

Zhang, X., Hu, Y., & Lin, Y. (2019). The influence of highway on local economy: Evidence from China's Yangtze River Delta region. *Journal of Transport Geography*, 82, 102600.

Zhang, X., & Gibson, J. (2022). Using multi-source nighttime lights data to proxy for county-level economic activity in China from 2012 to 2019. *Remote Sensing*, 14(5), 1282.

Zhang, Y., & Cheng, L. (2023). The role of transport infrastructure in economic growth: Empirical evidence in the UK. *Transport Policy*, 133, 223–233.

setwd("./")

MapBog = readOGR("MapF.shp")
TBdata = read_rds("DataREGNew.rds")
TBdata = TBdata[order(TBdata$date,TBdata$CodigoLOC),]

MapBog = MapBog[order(MapBog$Idntfcd),]
row.names(MapBog) <- as.character(MapBog$Idntfcd)

head(encuesta)

fex <- encuesta$fex_p
fec <- encuesta$fex_c

DataBGT <- merge(TBdata, encuesta, duplicateGeoms = T)

#NEIGHBOORS

nb <- poly2nb(MapBog)
seed = 1702
set.seed(seed) # Set the seed (found in the Master script).

# Part One: Setup

# Set up necessary data for the ICAR prior.

adjacency = unlist(nb)
n_adj     = card(nb)
l_adj     = length(adjacency)
weights   = rep(1,l_adj)

TB_N      = length(TBdata$Rmed) # number of observations.
n_regions = length(n_adj)       # number of regions.


# Set up index for spatial parameters rho and delta.
region_index = numeric(n_regions)

for(i in 1:n_regions){
  region_index[i] = which(MapBog$Idntfcd==TBdata$CodigoLOC[i])
}

region_index = rep(region_index,length(unique(TBdata$date)))


# Part Two: Execution

# Model code.

SB_code=nimbleCode({
  tau   ~ dnorm(0,   sd=0.01)
  sigma ~ dnorm(0.1, sd=0.01)


  for(i in 1:n){


    z.pred[i]<-a[1]+GraSiz[i]*a[2]+MOVIN[i]*a[3]+MOVOUT[i]*a[4]+NumPer[i]*a[5]+PMWe[i]*a[6]+PorcINT[i]*a[7]+HogM[i]*a[8]+DormP[i]*a[9]+CUAR[i]+theta[index[i]]+phi[index[i]]
    z[i] ~ dnorm(z.pred[i],sd=sigma)

  }

  for(i in 1:R){
    theta[i] ~ dnorm(0,sd=sigma)
  }
  phi[1:R] ~ dcar_normal(adj=adj[1:l_adj], num=n_adj[1:R], tau=tau,zero_mean=1)

  for (i in 1:9){
    a[i] ~ dnorm(0.1,sd=0.01)
  }
})

print("Model done")
# Set up data for NIMBLE.
SB_constants = list(n=TB_N,n_adj=n_adj,
                  adj=adjacency,GraSiz=TBdata$GraSiz,MOVIN=TBdata$MOVIN,MOVOUT=TBdata$MOVOUT,NumPer=TBdata$NumPer,PMWe=TBdata$PMWe,
                  PorcINT=TBdata$PorcINT,HogM=TBdata$HogM,DormP=TBdata$DormP,CUAR=TBdata$CUAR,R=n_regions,index=region_index,w=weights,l_adj=length(adjacency))

SB_data = list(z=TBdata$Rmed)

# Set initial values.
#SB_inits1=list(sigma=0.25,tau=1,a=c(0.5,0.5,0.5,0.5,0.5),
#               theta=rnorm(n_regions,0,0.25),phi=rnorm(n_regions,0,0.05))
#SB_inits2=list(sigma=0.5,tau=0.1,a=c(0.1,0.1,0.1,0.1,0.1),
#               theta=rnorm(n_regions,2,0.5),phi=rnorm(n_regions,0,0.5))
#SB_inits3=list(sigma=0.25,tau=1,a=c(1,1,1,1,1),
#               theta=rnorm(n_regions,0,0.25),phi=rnorm(n_regions,0,0.05))
#SB_inits4=list(sigma=0.5,tau=0.1,a=c(0.01,0.01,0.01,0.01,0.01),
#               theta=rnorm(n_regions,2,0.5),phi=rnorm(n_regions,0,0.5))

SB_inits1=list(sigma=0.75,a=c(0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1),
               theta=rnorm(n_regions,0,0.75),phi=rnorm(n_regions,0,0.75),tau=0.75)

SB_inits2=list(sigma=10,a=c(5,5,5,5,5,5,5,5,5),
               theta=rnorm(n_regions,0,1),phi=rnorm(n_regions,0,1),tau=1)

SB_inits3=list(sigma=25,tau=0.25,a=c(1,1,1,1,1,1,1,1,1),
               theta=rnorm(n_regions,0,0.25),phi=rnorm(n_regions,0,0.05))

SB_inits4=list(sigma=0.5,tau=0.5,a=c(0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01),
               theta=rnorm(n_regions,0,0.5),phi=rnorm(n_regions,0,0.5))

SB_inits=list(chain1=SB_inits1,chain2=SB_inits2,chain3=SB_inits3,chain4=SB_inits4)

SB_model <- nimbleModel(SB_code, SB_constants,SB_data,SB_inits)
SB_compiled_model <- compileNimble(SB_model,resetFunctions = TRUE,showCompilerOutput=T)
SB_model$initializeInfo()

# Set up samplers.
SB_mcmc_conf <- configureMCMC(SB_model, monitors=c('a[1]','a[2]','a[3]','a[4]','a[5]','a[6]','a[7]','a[8]','a[9]','sigma',
                                                  'theta','tau','phi','z[i]'),useConjugacy = TRUE)


SB_mcmc          <- buildMCMC(SB_mcmc_conf)
SB_compiled_mcmc <- compileNimble(SB_mcmc, project = SB_model,resetFunctions = TRUE)

print("Running")
SB_samples  = runMCMC(SB_compiled_mcmc,inits=SB_inits,
                   nchains = 4,
                   nburnin = 80000,
                   niter   = 160000,
                   samplesAsCodaMCMC = TRUE,
                   thin    = 40,
                   summary = FALSE,
                   WAIC    = FALSE,
                   setSeed = c(seed,2*seed,3*seed,4*seed))

gelman.diag(SB_samples[,c('a[1]','a[2]','a[3]','a[4]','a[5]','a[6]','a[7]','a[8]','a[9]','tau','sigma')])

# Combine MCMC chains.
TB_mcmc = do.call('rbind',SB_samples)

